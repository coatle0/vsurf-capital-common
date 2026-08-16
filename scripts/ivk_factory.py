"""IVK Factory Phase A: packs, evidence reuse, token ledger, and source plans."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


class FactoryValidationError(ValueError):
    """A deterministic, user-correctable Factory contract violation."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def stable_hash(value: str | bytes) -> str:
    raw = value.encode("utf-8") if isinstance(value, str) else value
    return hashlib.sha256(raw).hexdigest()


def _key(value: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


@dataclass(frozen=True)
class PackSelection:
    frame: dict[str, Any]
    sector: dict[str, Any]
    regions: tuple[dict[str, Any], ...]

    def manifest(self) -> dict[str, Any]:
        return {
            "frame": f"{self.frame['id']}@{self.frame['version']}",
            "sector": f"{self.sector['id']}@{self.sector['version']}",
            "regions": [f"{p['id']}@{p['version']}" for p in self.regions],
        }


class PackRegistry:
    def __init__(self, registry_path: str | Path) -> None:
        self.path = Path(registry_path)
        raw = json.loads(self.path.read_text(encoding="utf-8"))
        if raw.get("contract_version") != "ivk-pack-registry-1.0":
            raise FactoryValidationError("unsupported pack registry contract")
        self.raw = raw
        self.packs: dict[str, dict[str, dict[str, Any]]] = {}
        for entry in raw.get("packs", []):
            pack_path = (self.path.parent / entry["path"]).resolve()
            pack = json.loads(pack_path.read_text(encoding="utf-8"))
            kind, pack_id = pack.get("kind"), pack.get("id")
            if kind not in {"frame", "sector", "region"} or not pack_id or not pack.get("version"):
                raise FactoryValidationError(f"invalid pack: {pack_path}")
            self.packs.setdefault(kind, {})[pack_id] = pack

    def resolve(self, kind: str, selector: str) -> dict[str, Any]:
        wanted = _key(selector)
        for pack in self.packs.get(kind, {}).values():
            names = [pack["id"], *pack.get("aliases", [])]
            if wanted in {_key(name) for name in names}:
                return pack
        raise FactoryValidationError(f"unknown {kind} pack: {selector}")

    def resolve_sector(self, selector: str) -> dict[str, Any]:
        """Resolve a reusable sector pack or return an explicit empty bootstrap pack."""
        try:
            return self.resolve("sector", selector)
        except FactoryValidationError:
            return {
                "kind": "sector",
                "id": f"bootstrap_{_key(selector) or 'unspecified'}",
                "version": "0.0.0",
                "aliases": [],
                "required_topics": [],
                "metrics": [],
                "allowed_extensions": [],
                "token_budget_overrides": {},
                "pack_mode": "bootstrap",
                "requested_selector": selector,
                "reusable": False,
            }

    def select(self, *, frame: str, sector: str, regions: Iterable[str]) -> PackSelection:
        selected = PackSelection(
            frame=self.resolve("frame", frame),
            sector=self.resolve_sector(sector),
            regions=tuple(self.resolve("region", item) for item in regions),
        )
        compatibility = self.raw.get("compatibility", {})
        allowed = compatibility.get("sector_frames", {}).get(selected.sector["id"], [])
        if allowed and selected.frame["id"] not in allowed:
            raise FactoryValidationError(
                f"frame {selected.frame['id']} is not compatible with sector {selected.sector['id']}"
            )
        return selected


class EvidenceStore:
    """SQLite evidence cache shared across Value Chains."""

    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute("PRAGMA foreign_keys=ON")
        self._create_schema()

    def __enter__(self) -> "EvidenceStore":
        return self

    def __exit__(self, *_: Any) -> None:
        self.db.close()

    def _create_schema(self) -> None:
        self.db.executescript(
            """
            CREATE TABLE IF NOT EXISTS documents (
              document_id TEXT PRIMARY KEY, company_id TEXT, source_type TEXT NOT NULL,
              source_url TEXT NOT NULL, published_at TEXT, content_hash TEXT NOT NULL UNIQUE,
              metadata_json TEXT NOT NULL, collected_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS sections (
              section_id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(document_id),
              heading TEXT, content_hash TEXT NOT NULL, text TEXT NOT NULL,
              UNIQUE(document_id, content_hash)
            );
            CREATE TABLE IF NOT EXISTS source_occurrences (
              occurrence_id TEXT PRIMARY KEY, document_id TEXT NOT NULL REFERENCES documents(document_id),
              company_id TEXT, source_type TEXT NOT NULL, source_url TEXT NOT NULL,
              published_at TEXT, metadata_json TEXT NOT NULL, collected_at TEXT NOT NULL,
              UNIQUE(document_id, source_url)
            );
            CREATE TABLE IF NOT EXISTS extraction_cache (
              section_hash TEXT NOT NULL, extractor_version TEXT NOT NULL,
              result_json TEXT NOT NULL, created_at TEXT NOT NULL,
              PRIMARY KEY(section_hash, extractor_version)
            );
            """
        )
        self.db.commit()

    def put_document(self, *, company_id: str | None, source_type: str, source_url: str,
                     content: str, published_at: str | None = None,
                     metadata: dict[str, Any] | None = None) -> tuple[str, bool]:
        digest = stable_hash(content)
        row = self.db.execute("SELECT document_id FROM documents WHERE content_hash=?", (digest,)).fetchone()
        if row:
            self._put_occurrence(row[0], company_id, source_type, source_url, published_at, metadata)
            return row[0], False
        document_id = f"doc:{digest[:24]}"
        self.db.execute(
            "INSERT INTO documents VALUES (?,?,?,?,?,?,?,?)",
            (document_id, company_id, source_type, source_url, published_at, digest,
             json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True), now_iso()),
        )
        self.db.commit()
        self._put_occurrence(document_id, company_id, source_type, source_url, published_at, metadata)
        return document_id, True

    def _put_occurrence(self, document_id: str, company_id: str | None, source_type: str,
                        source_url: str, published_at: str | None,
                        metadata: dict[str, Any] | None) -> None:
        occurrence_id = f"src:{stable_hash(document_id + ':' + source_url)[:24]}"
        self.db.execute(
            "INSERT OR IGNORE INTO source_occurrences VALUES (?,?,?,?,?,?,?,?)",
            (occurrence_id, document_id, company_id, source_type, source_url, published_at,
             json.dumps(metadata or {}, ensure_ascii=False, sort_keys=True), now_iso()),
        )
        self.db.commit()

    def put_section(self, document_id: str, text: str, *, heading: str | None = None) -> tuple[str, bool]:
        digest = stable_hash(text)
        row = self.db.execute(
            "SELECT section_id FROM sections WHERE document_id=? AND content_hash=?", (document_id, digest)
        ).fetchone()
        if row:
            return row[0], False
        section_id = f"sec:{stable_hash(document_id + ':' + digest)[:24]}"
        self.db.execute("INSERT INTO sections VALUES (?,?,?,?,?)", (section_id, document_id, heading, digest, text))
        self.db.commit()
        return section_id, True

    def cache_extraction(self, section_hash: str, extractor_version: str, result: Any) -> None:
        self.db.execute(
            "INSERT OR REPLACE INTO extraction_cache VALUES (?,?,?,?)",
            (section_hash, extractor_version, json.dumps(result, ensure_ascii=False, sort_keys=True), now_iso()),
        )
        self.db.commit()

    def get_extraction(self, section_hash: str, extractor_version: str) -> Any | None:
        row = self.db.execute(
            "SELECT result_json FROM extraction_cache WHERE section_hash=? AND extractor_version=?",
            (section_hash, extractor_version),
        ).fetchone()
        return json.loads(row[0]) if row else None


class TokenLedger:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.path)
        self.db.execute(
            """CREATE TABLE IF NOT EXISTS usage (
            id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL, value_chain_id TEXT NOT NULL,
            stage TEXT NOT NULL, model TEXT NOT NULL, input_tokens INTEGER NOT NULL,
            cached_input_tokens INTEGER NOT NULL, output_tokens INTEGER NOT NULL,
            documents_considered INTEGER NOT NULL, documents_sent INTEGER NOT NULL,
            facts_created INTEGER NOT NULL, facts_accepted INTEGER NOT NULL,
            retry_count INTEGER NOT NULL, recorded_at TEXT NOT NULL)"""
        )
        self.db.commit()

    def __enter__(self) -> "TokenLedger":
        return self

    def __exit__(self, *_: Any) -> None:
        self.db.close()

    def record(self, *, run_id: str, value_chain_id: str, stage: str, model: str,
               input_tokens: int, cached_input_tokens: int = 0, output_tokens: int = 0,
               documents_considered: int = 0, documents_sent: int = 0,
               facts_created: int = 0, facts_accepted: int = 0, retry_count: int = 0) -> None:
        values = (input_tokens, cached_input_tokens, output_tokens, documents_considered,
                  documents_sent, facts_created, facts_accepted, retry_count)
        if any(not isinstance(v, int) or v < 0 for v in values):
            raise FactoryValidationError("token ledger counters must be non-negative integers")
        if cached_input_tokens > input_tokens:
            raise FactoryValidationError("cached_input_tokens cannot exceed input_tokens")
        self.db.execute(
            "INSERT INTO usage(run_id,value_chain_id,stage,model,input_tokens,cached_input_tokens,output_tokens,documents_considered,documents_sent,facts_created,facts_accepted,retry_count,recorded_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (run_id, value_chain_id, stage, model, *values, now_iso()),
        )
        self.db.commit()

    def totals(self, run_id: str) -> dict[str, int]:
        row = self.db.execute(
            "SELECT COALESCE(SUM(input_tokens),0),COALESCE(SUM(cached_input_tokens),0),COALESCE(SUM(output_tokens),0),COALESCE(SUM(facts_accepted),0) FROM usage WHERE run_id=?",
            (run_id,),
        ).fetchone()
        return dict(zip(("input_tokens", "cached_input_tokens", "output_tokens", "facts_accepted"), row))

    def budget_status(self, run_id: str, budgets: dict[str, int]) -> dict[str, Any]:
        rows = self.db.execute(
            "SELECT stage,COALESCE(SUM(input_tokens+output_tokens),0) FROM usage WHERE run_id=? GROUP BY stage",
            (run_id,),
        ).fetchall()
        used = dict(rows)
        stages = {stage: {"used": used.get(stage, 0), "budget": limit,
                          "exceeded": used.get(stage, 0) > limit} for stage, limit in budgets.items()}
        return {"stages": stages, "exceeded": any(item["exceeded"] for item in stages.values())}


def build_source_plan(blueprint: dict[str, Any], selection: PackSelection) -> dict[str, Any]:
    if blueprint.get("contract_version") != "ivk-blueprint-1.0":
        raise FactoryValidationError("source planner requires ivk-blueprint-1.0")
    normalized = blueprint.get("normalized", {})
    seeds = normalized.get("validated_seeds", [])
    if not seeds:
        raise FactoryValidationError("blueprint has no validated seeds")
    unresolved = {item.get("seed") for item in blueprint.get("unresolved_seeds", [])}
    topics = list(dict.fromkeys([
        *selection.frame.get("required_slots", []),
        *selection.sector.get("required_topics", []),
    ]))
    adapters = []
    for region in selection.regions:
        adapters.extend(region.get("source_adapters", []))
    adapters = list(dict.fromkeys(adapters))
    tasks = []
    for seed in seeds:
        canonical = seed["canonical_id"]
        if canonical in unresolved:
            tasks.append({"seed": canonical, "task_type": "entity_resolution", "priority": 1,
                          "topics": ["identity", "exchange", "ticker"], "source_adapters": adapters})
        tasks.append({"seed": canonical, "task_type": "evidence_collection", "priority": 2,
                      "topics": topics, "source_adapters": adapters})
    for index, item in enumerate(blueprint.get("source_requirements", []), start=1):
        tasks.append({"seed": None, "task_type": "question_evidence", "priority": 3,
                      "requirement_id": f"question:{index}", "question": item.get("question"),
                      "source_adapters": adapters})
    budgets = {
        "source_planning": 5000,
        "evidence_extraction": 50000,
        "synthesis": 15000,
        "exception_review": 10000,
        "final_report": 5000,
    }
    budgets.update(selection.sector.get("token_budget_overrides", {}))
    plan = {
        "contract_version": "ivk-source-plan-1.0",
        "created_at": now_iso(),
        "value_chain": normalized.get("identity"),
        "blueprint_contract": blueprint["contract_version"],
        "pack_manifest": selection.manifest(),
        "pack_policy": {
            "mode": selection.sector.get("pack_mode", "reused"),
            "requested_sector": selection.sector.get("requested_selector", selection.sector["id"]),
            "reusable_sector_pack": selection.sector.get("reusable", True),
            "core_revision_required": False,
            "review_status": "bootstrap_pending" if selection.sector.get("pack_mode") == "bootstrap"
            else "accepted_for_planning",
        },
        "evidence_policy": {"primary_source_first": True, "reuse_by_content_hash": True,
                            "auto_confirm": False, "canonical_graph_read": "neo4j-official.read_cypher"},
        "tasks": tasks,
        "token_budgets": budgets,
        "stop_conditions": list(dict.fromkeys(selection.frame.get("stop_conditions", []))),
        "status": "planned",
    }
    validate_source_plan(plan)
    return plan


def validate_source_plan(plan: dict[str, Any]) -> None:
    required = {"contract_version", "value_chain", "pack_manifest", "evidence_policy", "tasks", "token_budgets", "status"}
    missing = sorted(required - set(plan))
    if missing:
        raise FactoryValidationError(f"source plan missing field(s): {', '.join(missing)}")
    if not plan["tasks"]:
        raise FactoryValidationError("source plan must contain tasks")
    if plan["evidence_policy"].get("auto_confirm") is not False:
        raise FactoryValidationError("source plan must not auto-confirm evidence")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    plan = sub.add_parser("plan")
    plan.add_argument("blueprint", type=Path)
    plan.add_argument("--registry", type=Path, required=True)
    plan.add_argument("--sector", required=True)
    plan.add_argument("--region", action="append", required=True)
    plan.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if args.command == "plan":
        blueprint = json.loads(args.blueprint.read_text(encoding="utf-8"))
        registry = PackRegistry(args.registry)
        selection = registry.select(frame=blueprint["normalized"]["primary_frame"], sector=args.sector, regions=args.region)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(build_source_plan(blueprint, selection), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
