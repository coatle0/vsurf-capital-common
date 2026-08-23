"""Minimal governed Source Collection -> Evidence -> KE -> write manifest -> Review path."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any


class DryRunValidationError(ValueError):
    pass


def _read(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def build_outputs(plan: dict[str, Any], collection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    if plan.get("contract_version") != "ivk-source-plan-1.0":
        raise DryRunValidationError("invalid source plan contract")
    if collection.get("contract_version") != "ivk-source-collection-0.1":
        raise DryRunValidationError("invalid source collection contract")
    docs = collection.get("documents")
    if not isinstance(docs, list) or not docs:
        raise DryRunValidationError("source collection requires documents")
    required = {"evidence_id", "ticker", "company_id", "company_name", "exchange", "source_ref", "facts"}
    for doc in docs:
        missing = required - set(doc)
        if missing or not doc["source_ref"] or not doc["facts"]:
            raise DryRunValidationError(f"invalid provenance document: {doc.get('ticker', '?')}")

    seeds = [task["seed"] for task in plan["tasks"] if task["task_type"] == "entity_resolution"]
    by_ticker = {doc["ticker"]: doc for doc in docs}
    unresolved = [seed for seed in seeds if seed not in by_ticker]
    evidence = {
        "contract_version": "ivk-evidence-packet-0.1",
        "run_id": collection["run_id"],
        "source_plan_contract": plan["contract_version"],
        "documents": [
            {**doc, "content_hash": hashlib.sha256("\n".join(doc["facts"]).encode()).hexdigest(),
             "epistemic_status": "source_fact", "review_status": "pending"}
            for doc in docs
        ],
        "coverage": {"resolved_seeds": sorted(set(seeds) - set(unresolved)), "unresolved_seeds": unresolved,
                     "questions": "pending_review"},
        "auto_confirm": False,
    }
    planned_vc = plan.get("value_chain", {})
    vc_id = planned_vc.get("target_vc") or f"vc:{planned_vc.get('slug', 'unresolved-value-chain')}"
    ke = {
        "contract_version": "ivk-ke-packet-0.1",
        "run_id": collection["run_id"],
        "value_chain": {"id": vc_id, "name": plan["value_chain"]["name"], "status": "bootstrap"},
        "companies": [
            {"id": f"company:{doc['ticker']}", "ticker": doc["ticker"], "name": doc["company_name"],
             "exchange": doc["exchange"], "tikr_cid": doc["company_id"], "evidence_id": doc["evidence_id"],
             "status": "candidate", "review_status": "pending"}
            for doc in docs
        ],
        "assertions": [],
        "governance": {"auto_confirm": False, "requires_provenance": True, "write_scope": "candidate_identity_only"},
    }
    write_manifest = {
        "contract_version": "ivk-neo4j-write-manifest-0.1",
        "run_id": collection["run_id"],
        "approved_scope": "candidate company identities, evidence records, and candidate VC membership only",
        "neo4j_write_status": "pending_execution",
        "value_chain": ke["value_chain"],
        "companies": ke["companies"],
        "evidence": [{"id": d["evidence_id"], "source_ref": d["source_ref"], "content_hash": d["content_hash"]}
                     for d in evidence["documents"]],
    }
    review = {
        "contract_version": "ivk-review-0.1", "run_id": collection["run_id"],
        "path_status": "ready_for_governed_write", "source_documents": len(docs),
        "companies": len(ke["companies"]), "confirmed_assertions": 0,
        "pending_questions": len([t for t in plan["tasks"] if t["task_type"] == "question_evidence"]),
        "quality_gates": {"all_nodes_have_provenance": True, "auto_confirm": False,
                          "unsupported_assertions": 0, "write_scope_limited": True},
        "limitations": ["TIKR company overviews establish identity and business scope only.",
                        "Bottleneck, beneficiary, and causal claims remain pending deeper filings and earnings-call evidence."],
    }
    return {"evidence": evidence, "ke": ke, "write_manifest": write_manifest, "review": review}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--collection", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    outputs = build_outputs(_read(args.plan), _read(args.collection))
    names = {"evidence": "evidence_packet.json",
             "ke": "ke_packet.json",
             "write_manifest": "write_manifest.json",
             "review": "review.json"}
    for key, name in names.items():
        _write(args.output_dir / name, outputs[key])


if __name__ == "__main__":
    main()
