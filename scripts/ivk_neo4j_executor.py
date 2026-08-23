"""Execute approved IVK MERGE batches and produce live Neo4j proof artifacts.

This module never prints credentials. Run it with a Python environment that has
the official ``neo4j`` driver installed.
"""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from neo4j import GraphDatabase


def _user_env(name: str) -> str | None:
    value = os.environ.get(name)
    if value:
        return value
    if os.name != "nt":
        return None
    import winreg

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return str(value) if value else None
    except OSError:
        return None


def _write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(f".{path.name}.tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)


def _read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def _execute_batches(driver, database: str, batches: list[dict]) -> list[dict]:
    results: list[dict] = []
    with driver.session(database=database) as session:
        for batch in batches:
            records = session.run(batch["query"], batch.get("params") or {}).data()
            results.append({"name": batch["name"], "ok": True, "row_count": len(records)})
    return results


def _readback(driver, database: str, *, run_id: str, vc_id: str) -> dict:
    with driver.session(database=database) as session:
        vc = session.run(
            "MATCH (v:ValueChain {id:$vc_id}) "
            "OPTIONAL MATCH (m)-[:CANDIDATE_IN]->(v) "
            "RETURN count(DISTINCT v) AS count, v.nickname AS nickname, "
            "count(DISTINCT m) AS members",
            vc_id=vc_id,
        ).single()
        evidence = session.run(
            "MATCH (e:Evidence {run_id:$run_id}) "
            "RETURN count(DISTINCT e) AS evidence, "
            "count(DISTINCT CASE WHEN e.source_ref IS NOT NULL "
            "AND e.content_hash IS NOT NULL AND e.source_date IS NOT NULL "
            "AND e.collected_at IS NOT NULL THEN e END) AS evidence_complete",
            run_id=run_id,
        ).single()
        confirmed = session.run(
            "MATCH (a:Assertion {run_id:$run_id}) "
            "WHERE toLower(coalesce(a.status,'')) = 'confirmed' "
            "RETURN count(DISTINCT a) AS count",
            run_id=run_id,
        ).single()
        duplicates = session.run(
            "MATCH (n {run_id:$run_id}) WITH labels(n) AS labels, n.id AS id, count(*) AS c "
            "WHERE id IS NOT NULL AND c > 1 RETURN count(*) AS count",
            run_id=run_id,
        ).single()
    return {
        "value_chain": {
            "id": vc_id,
            "count": int(vc["count"] if vc else 0),
            "nickname": vc["nickname"] if vc else None,
        },
        "members": int(vc["members"] if vc else 0),
        "evidence": int(evidence["evidence"] if evidence else 0),
        "evidence_complete": int(evidence["evidence_complete"] if evidence else 0),
        "confirmed_assertions": int(confirmed["count"] if confirmed else 0),
        "duplicate_ids": int(duplicates["count"] if duplicates else 0),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--batches", type=Path, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    parser.add_argument("--readback", type=Path, required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--vc-id", required=True)
    args = parser.parse_args()

    uri = os.environ.get("NEO4J_URI", "bolt://127.0.0.1:7687")
    username = os.environ.get("NEO4J_USERNAME") or os.environ.get("NEO4J_USER") or "neo4j"
    password = _user_env("NEO4J_PASSWORD")
    database = os.environ.get("NEO4J_DATABASE", "neo4j")
    if not password:
        raise SystemExit("NEO4J_PASSWORD is missing from process and HKCU\\Environment")

    batches = _read_json(args.batches)
    if not isinstance(batches, list) or not batches:
        raise SystemExit("write_batches.json must contain a non-empty array")

    driver = GraphDatabase.driver(uri, auth=(username, password))
    try:
        driver.verify_connectivity()
        first = _execute_batches(driver, database, batches)
        before = _readback(driver, database, run_id=args.run_id, vc_id=args.vc_id)
        second = _execute_batches(driver, database, batches)
        after = _readback(driver, database, run_id=args.run_id, vc_id=args.vc_id)
    finally:
        driver.close()

    stable_keys = ("members", "evidence", "evidence_complete", "confirmed_assertions", "duplicate_ids")
    idempotent = all(before[key] == after[key] for key in stable_keys)
    ok = (
        after["value_chain"]["count"] == 1
        and after["evidence_complete"] >= 1
        and after["confirmed_assertions"] == 0
        and after["duplicate_ids"] == 0
        and idempotent
    )
    observed = datetime.now(timezone.utc).isoformat()
    identity = uri.split("@")[-1]
    receipt = {
        "contract_version": "ivk-write-receipt-0.1",
        "run_id": args.run_id,
        "executed_at": observed,
        "database": database,
        "identity": identity,
        "tool": "ivk.neo4j-driver",
        "batches": first,
        "idempotency_replay": second,
        "failed_batches": [],
    }
    readback = {
        "contract_version": "ivk-readback-0.1",
        "run_id": args.run_id,
        "ok": ok,
        "observed_at": observed,
        "database": database,
        "identity": identity,
        "tool": "ivk.neo4j-driver",
        **after,
        "idempotency_replay": "PASS" if idempotent else "FAIL",
    }
    _write_json(args.receipt, receipt)
    _write_json(args.readback, readback)
    print(json.dumps({"ok": ok, "run_id": args.run_id, "status": "VERIFIED" if ok else "FAILED"}))
    if not ok:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
