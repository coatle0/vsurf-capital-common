"""Validate and normalize IVK NEW intake, then build a review-gated blueprint."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED = ("name", "seed", "frame", "thesis")
LIST_FIELDS = ("seed", "questions", "known_links", "limitations", "references")
EPISTEMIC = {"fact", "graph_observation", "inference", "hypothesis"}
REVIEW = {"pending", "accepted", "rejected", "deferred"}
FRAME_NICKNAMES = {
    "svb": {"id": "sponsor_valuechain_bottleneck", "version": "1.0.0", "label": "Sponsor→Value Chain→Bottleneck"},
    "sponsor_vcb": {"id": "sponsor_valuechain_bottleneck", "version": "1.0.0", "label": "Sponsor→Value Chain→Bottleneck"},
}


class IntakeValidationError(ValueError):
    """An explicit, user-correctable intake contract violation."""


def _nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str):
        raise IntakeValidationError(f"{field} must be a string")
    value = value.strip()
    if not value:
        raise IntakeValidationError(f"{field} must not be empty")
    return value


def validate_intake(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise IntakeValidationError("intake must be an object")
    missing = [field for field in REQUIRED if field not in raw]
    if missing:
        raise IntakeValidationError(f"missing required field(s): {', '.join(missing)}")
    unknown = sorted(set(raw) - set(REQUIRED) - set(LIST_FIELDS))
    if unknown:
        raise IntakeValidationError(f"unknown field(s): {', '.join(unknown)}")
    for field in ("name", "frame", "thesis"):
        _nonempty_string(raw[field], field)
    for field in LIST_FIELDS:
        if field in raw and not isinstance(raw[field], list):
            raise IntakeValidationError(f"{field} must be an array")
        for index, item in enumerate(raw.get(field, [])):
            _nonempty_string(item, f"{field}[{index}]")
    if not raw["seed"]:
        raise IntakeValidationError("seed must contain at least one value")
    canonical = [_canonical_seed(item) for item in raw["seed"]]
    duplicates = sorted({item for item in canonical if canonical.count(item) > 1})
    if duplicates:
        raise IntakeValidationError(f"duplicate seed(s): {', '.join(duplicates)}")
    return deepcopy(raw)


def _canonical_seed(value: str) -> str:
    value = " ".join(value.strip().split())
    return value.upper() if " " not in value else value


def _frame_key(value: str) -> str:
    return "_".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


def resolve_frame(value: str) -> dict[str, Any]:
    """Resolve a short frame nickname without making the intake verbose."""
    key = _frame_key(value)
    resolved = FRAME_NICKNAMES.get(key)
    if resolved:
        return {"input": value.strip(), "nickname": key, **resolved}
    if key in {"sponsor_valuechain_bottleneck", "sponsor_value_chain_bottleneck"}:
        return {"input": value.strip(), "nickname": None, **FRAME_NICKNAMES["svb"]}
    return {"input": value.strip(), "nickname": None, "id": None, "version": None, "label": value.strip()}


def _normalize_intake_legacy(raw: Any) -> dict[str, Any]:
    validated = validate_intake(raw)
    frames = [part.strip() for part in validated["frame"].split("→") if part.strip()]
    return {
        "identity": {"name": validated["name"].strip(), "slug": _slug(validated["name"])},
        "validated_seeds": [
            {"input": item, "canonical_id": _canonical_seed(item), "kind": "ticker_or_company_id", "role": "starting_point"}
            for item in validated["seed"]
        ],
        "primary_frame": validated["frame"].strip(),
        "secondary_frame_candidates": frames[1:] if len(frames) > 1 else [],
        "thesis": validated["thesis"].strip(),
        "questions": [item.strip() for item in validated.get("questions", [])],
        "known_links": [item.strip() for item in validated.get("known_links", [])],
        "limitations": [item.strip() for item in validated.get("limitations", [])],
        "references": [item.strip() for item in validated.get("references", [])],
    }


def normalize_intake(raw: Any) -> dict[str, Any]:
    """Validate input and expand a frame nickname to a versioned frame reference."""
    validated = validate_intake(raw)
    frame = resolve_frame(validated["frame"])
    frames = [part.strip() for part in validated["frame"].split("→") if part.strip()]
    return {
        "identity": {"name": validated["name"].strip(), "slug": _slug(validated["name"])},
        "validated_seeds": [
            {"input": item, "canonical_id": _canonical_seed(item), "kind": "ticker_or_company_id", "role": "starting_point"}
            for item in validated["seed"]
        ],
        "primary_frame": frame["label"],
        "frame_ref": {"id": frame["id"], "version": frame["version"], "nickname": frame["nickname"], "input": frame["input"]},
        "secondary_frame_candidates": frames[1:] if len(frames) > 1 else [],
        "thesis": validated["thesis"].strip(),
        "questions": [item.strip() for item in validated.get("questions", [])],
        "known_links": [item.strip() for item in validated.get("known_links", [])],
        "limitations": [item.strip() for item in validated.get("limitations", [])],
        "references": [item.strip() for item in validated.get("references", [])],
    }


def _slug(value: str) -> str:
    return "-".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


def existing_graph_query() -> str:
    return """UNWIND $seeds AS seed
OPTIONAL MATCH (c:Company)
WHERE toUpper(coalesce(c.ticker,'')) = seed OR toUpper(coalesce(c.id,'')) = seed
   OR toUpper(coalesce(c.name_en,'')) = seed OR toUpper(coalesce(c.name,'')) = seed
WITH seed, collect(DISTINCT c) AS companies
UNWIND CASE WHEN size(companies)=0 THEN [null] ELSE companies END AS c
OPTIONAL MATCH (c)-[r:PRODUCES|OPERATES_IN|EXPOSED_TO]->(entity)
OPTIONAL MATCH (a:CausalAssertion)-[:ASSERTED_FOR]->(c)
RETURN seed,
 CASE WHEN c IS NULL THEN null ELSE {id:c.id,ticker:c.ticker,name:coalesce(c.name_en,c.name,c.name_local)} END AS company,
 collect(DISTINCT CASE WHEN entity IS NULL THEN null ELSE {relationship:type(r),entity_type:head(labels(entity)),id:entity.id,name:entity.name,status:r.status} END) AS value_chain,
 collect(DISTINCT CASE WHEN a IS NULL THEN null ELSE {id:a.id,kind:a.kind,status:a.status,review_status:a.review_status,source_present:a.source IS NOT NULL,evidence_present:a.evidence IS NOT NULL} END) AS assertions
ORDER BY seed"""


def build_blueprint(raw: Any, graph_rows: Any, *, observed_at: str | None = None) -> dict[str, Any]:
    normalized = normalize_intake(raw)
    if not isinstance(graph_rows, list):
        raise IntakeValidationError("existing graph result must be an array")
    by_seed = {row.get("seed"): row for row in graph_rows if isinstance(row, dict)}
    findings, unresolved = [], []
    for seed in normalized["validated_seeds"]:
        canonical = seed["canonical_id"]
        row = deepcopy(by_seed.get(canonical, {"seed": canonical, "company": None, "value_chain": [], "assertions": []}))
        row["epistemic_status"] = "graph_observation"
        row["review_status"] = "pending"
        findings.append(row)
        if not row.get("company"):
            unresolved.append({"seed": canonical, "reason": "no matching Company in live canonical read", "disposition": "retain_as_starting_point"})
    blueprint = {
        "contract_version": "ivk-blueprint-1.0",
        "raw_input": deepcopy(raw),
        "normalized": normalized,
        "unresolved_seeds": unresolved,
        "excluded_seeds": [],
        "existing_graph": {"read_path": "neo4j-official.read_cypher", "observed_at": observed_at or datetime.now(timezone.utc).isoformat(), "findings": findings},
        "initial_value_chain": {"nodes": [], "links": [], "status": "hypothesis", "review_status": "pending"},
        "candidate_slots": {kind: [] for kind in ("drivers", "bottlenecks", "beneficiaries")},
        "link_expansion_frontier": [],
        "source_requirements": [{"question": q, "status": "required", "evidence": []} for q in normalized["questions"]],
        "epistemic_policy": {"allowed_status": sorted(EPISTEMIC), "allowed_review_status": sorted(REVIEW), "auto_confirm": False},
        "review_status": "pending",
    }
    validate_blueprint(blueprint)
    return blueprint


def validate_blueprint(blueprint: dict[str, Any]) -> None:
    required = {"contract_version", "raw_input", "normalized", "unresolved_seeds", "excluded_seeds", "existing_graph", "initial_value_chain", "candidate_slots", "link_expansion_frontier", "source_requirements", "epistemic_policy", "review_status"}
    missing = sorted(required - set(blueprint))
    if missing:
        raise IntakeValidationError(f"blueprint missing field(s): {', '.join(missing)}")
    if blueprint["epistemic_policy"].get("auto_confirm") is not False:
        raise IntakeValidationError("blueprint candidates must not auto-confirm")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--graph-results", type=Path, required=True, help="JSON rows returned by neo4j-official.read_cypher")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding="utf-8"))
    graph = json.loads(args.graph_results.read_text(encoding="utf-8"))
    args.output.write_text(json.dumps(build_blueprint(raw, graph), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
