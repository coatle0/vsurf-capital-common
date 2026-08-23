"""Validate and normalize IVK NEW intake, then build a review-gated blueprint."""

from __future__ import annotations

import argparse
import json
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

LEGACY_REQUIRED = ("name", "seed", "frame", "thesis")
LIST_FIELDS = ("seed", "questions", "scope", "known_links", "limitations", "references")
OPERATIONS = {"new", "add", "update", "expand"}
V1_FIELDS = {
    "contract_version", "operation", "target_vc", "name", "seed", "frame",
    "thesis", "questions", "scope", "known_links", "limitations",
    "references", "options", "market",
}
V1_REQUIRED_FIELDS = V1_FIELDS - {"market"}
OPTION_FIELDS = {
    "periods", "since", "max_depth", "max_candidates", "auto_expand",
    "write_policy",
}
EPISTEMIC = {"fact", "graph_observation", "inference", "hypothesis"}
REVIEW = {"pending", "accepted", "rejected", "deferred"}
FRAME_NICKNAMES = {
    "svb": {"id": "sponsor_valuechain_bottleneck", "version": "1.0.0", "label": "Sponsor→Value Chain→Bottleneck"},
    "sponsor_vcb": {"id": "sponsor_valuechain_bottleneck", "version": "1.0.0", "label": "Sponsor→Value Chain→Bottleneck"},
    "matrix": {"id": "matrix", "version": "1.0.0", "label": "Matrix"},
    "cluster": {"id": "matrix", "version": "1.0.0", "label": "Matrix"},
    "stream": {"id": "upstream_midstream_downstream", "version": "1.0.0", "label": "Upstream→Midstream→Downstream"},
}
MARKETS = {"mixed", "us", "kr", "jp", "tw"}
MARKET_ALIASES = {
    "mixed": "mixed", "us": "us", "usa": "us",
    "kr": "kr", "korea": "kr", "krx": "kr",
    "jp": "jp", "japan": "jp", "tse": "jp",
    "tw": "tw", "taiwan": "tw", "twse": "tw",
}
PREFIX_MARKETS = {
    "KR": ("kr", "KRX"), "KRX": ("kr", "KRX"),
    "JP": ("jp", "TSE"), "TSE": ("jp", "TSE"),
    "TW": ("tw", "TWSE"), "TWSE": ("tw", "TWSE"),
}
US_EXCHANGES = {"US", "NASDAQ", "NYSE", "AMEX"}


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
    legacy = "contract_version" not in raw and "operation" not in raw
    if legacy:
        missing = [field for field in LEGACY_REQUIRED if field not in raw]
        if missing:
            raise IntakeValidationError(f"missing required field(s): {', '.join(missing)}")
        allowed = set(LEGACY_REQUIRED) | {"questions", "known_links", "limitations", "references", "market"}
        unknown = sorted(set(raw) - allowed)
        if unknown:
            raise IntakeValidationError(f"unknown field(s): {', '.join(unknown)}")
        value = {
            "contract_version": "ivk-intake-1.0",
            "operation": "new",
            "target_vc": None,
            "name": raw["name"],
            "seed": raw["seed"],
            "frame": raw["frame"],
            "thesis": raw["thesis"],
            "questions": raw.get("questions", []),
            "scope": [],
            "known_links": raw.get("known_links", []),
            "limitations": raw.get("limitations", []),
            "references": raw.get("references", []),
            "market": raw.get("market", "mixed"),
            "options": {"periods": 5, "auto_expand": False, "write_policy": "approval_required"},
        }
    else:
        missing = sorted(V1_REQUIRED_FIELDS - set(raw))
        if missing:
            raise IntakeValidationError(f"missing required field(s): {', '.join(missing)}")
        unknown = sorted(set(raw) - V1_FIELDS)
        if unknown:
            raise IntakeValidationError(f"unknown field(s): {', '.join(unknown)}")
        value = deepcopy(raw)
        value.setdefault("market", "mixed")

    if value["contract_version"] != "ivk-intake-1.0":
        raise IntakeValidationError("contract_version must be ivk-intake-1.0")
    operation = _nonempty_string(value["operation"], "operation").lower()
    if operation not in OPERATIONS:
        raise IntakeValidationError(f"unsupported operation: {operation}")
    value["operation"] = operation
    market_input = _nonempty_string(value["market"], "market").lower()
    market = MARKET_ALIASES.get(market_input)
    if market not in MARKETS:
        raise IntakeValidationError("market must be mixed, us, kr, jp, or tw")
    value["market"] = market
    _nonempty_string(value["thesis"], "thesis")
    for field in ("name", "frame", "target_vc"):
        if value[field] is not None:
            _nonempty_string(value[field], field)
    for field in LIST_FIELDS:
        if not isinstance(value[field], list):
            raise IntakeValidationError(f"{field} must be an array")
        for index, item in enumerate(value[field]):
            _nonempty_string(item, f"{field}[{index}]")

    if operation == "new":
        if value["target_vc"] is not None:
            raise IntakeValidationError("new operation requires target_vc=null")
        _nonempty_string(value["name"], "name")
        _nonempty_string(value["frame"], "frame")
    else:
        _nonempty_string(value["target_vc"], "target_vc")
    if operation in {"new", "add", "expand"} and not value["seed"]:
        raise IntakeValidationError(f"{operation} operation requires at least one seed")
    if operation in {"add", "expand"}:
        _nonempty_string(value["frame"], "frame")

    canonical = [_seed_identity(item, value["market"])["canonical_id"] for item in value["seed"]]
    duplicates = sorted({item for item in canonical if canonical.count(item) > 1})
    if duplicates:
        raise IntakeValidationError(f"duplicate seed(s): {', '.join(duplicates)}")

    options = value["options"]
    if not isinstance(options, dict):
        raise IntakeValidationError("options must be an object")
    unknown_options = sorted(set(options) - OPTION_FIELDS)
    if unknown_options:
        raise IntakeValidationError(f"unknown option(s): {', '.join(unknown_options)}")
    for field in ("periods", "max_depth", "max_candidates"):
        if field in options and (not isinstance(options[field], int) or isinstance(options[field], bool) or options[field] < 1):
            raise IntakeValidationError(f"options.{field} must be a positive integer")
    if "auto_expand" in options and not isinstance(options["auto_expand"], bool):
        raise IntakeValidationError("options.auto_expand must be a boolean")
    if options.get("write_policy") not in {"approval_required", "dry_run"}:
        raise IntakeValidationError("options.write_policy must be approval_required or dry_run")
    if "since" in options:
        _nonempty_string(options["since"], "options.since")
    return value


def _canonical_seed(value: str) -> str:
    return _seed_identity(value, "mixed")["canonical_id"]


def _seed_identity(value: str, default_market: str) -> dict[str, Any]:
    normalized = " ".join(value.strip().split())
    upper = normalized.upper() if " " not in normalized else normalized
    if ":" in upper:
        prefix, ticker = upper.split(":", 1)
        if not ticker:
            raise IntakeValidationError(f"seed has an empty ticker: {value}")
        if prefix in US_EXCHANGES:
            return {"canonical_id": ticker, "market": "us", "exchange": prefix if prefix != "US" else None,
                    "ticker": ticker, "provider_ids": {"tikr": ticker}}
        if prefix not in PREFIX_MARKETS:
            raise IntakeValidationError(f"unsupported seed market prefix: {prefix}")
        market, exchange = PREFIX_MARKETS[prefix]
        provider = f"A{ticker}" if market == "kr" else ticker
        return {"canonical_id": f"{exchange}:{ticker}", "market": market, "exchange": exchange,
                "ticker": ticker, "provider_ids": {"tikr": provider}}
    if " " in upper:
        return {"canonical_id": upper, "market": None, "exchange": None, "ticker": None, "provider_ids": {}}
    if default_market == "mixed":
        if upper.isdigit():
            raise IntakeValidationError(
                f"numeric seed '{value}' requires KR:, JP:, or TW: when market=mixed"
            )
        market, exchange = "us", None
    elif default_market == "us":
        market, exchange = "us", None
    else:
        exchange = {"kr": "KRX", "jp": "TSE", "tw": "TWSE"}[default_market]
        market = default_market
    canonical = upper if market == "us" else f"{exchange}:{upper}"
    provider = f"A{upper}" if market == "kr" else upper
    return {"canonical_id": canonical, "market": market, "exchange": exchange, "ticker": upper,
            "provider_ids": {"tikr": provider}}


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
            {"input": item, **_seed_identity(item, validated["market"]), "kind": "ticker_or_company_id", "role": "starting_point"}
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
    frame = resolve_frame(validated["frame"]) if validated["frame"] is not None else None
    frames = [part.strip() for part in validated["frame"].split("→") if part.strip()] if validated["frame"] else []
    identity_name = validated["name"] or validated["target_vc"]
    return {
        "operation": validated["operation"],
        "market": validated["market"],
        "target_vc": validated["target_vc"],
        "identity": {"name": identity_name.strip(), "slug": _slug(identity_name)},
        "validated_seeds": [
            {"input": item, **_seed_identity(item, validated["market"]), "kind": "ticker_or_company_id", "role": "starting_point"}
            for item in validated["seed"]
        ],
        "primary_frame": frame["label"] if frame else None,
        "frame_ref": ({"id": frame["id"], "version": frame["version"], "nickname": frame["nickname"], "input": frame["input"]}
                      if frame else {"id": None, "version": None, "nickname": None, "input": None}),
        "secondary_frame_candidates": frames[1:] if len(frames) > 1 else [],
        "thesis": validated["thesis"].strip(),
        "questions": [item.strip() for item in validated.get("questions", [])],
        "scope": [item.strip() for item in validated.get("scope", [])],
        "known_links": [item.strip() for item in validated.get("known_links", [])],
        "limitations": [item.strip() for item in validated.get("limitations", [])],
        "references": [item.strip() for item in validated.get("references", [])],
        "options": deepcopy(validated["options"]),
    }


def _slug(value: str) -> str:
    return "-".join("".join(c.lower() if c.isalnum() else " " for c in value).split())


def existing_graph_query() -> str:
    return """UNWIND $seeds AS seed
WITH seed, last(split(seed, ':')) AS ticker
OPTIONAL MATCH (c:Company)
WHERE toUpper(coalesce(c.ticker,'')) = ticker OR toUpper(coalesce(c.id,'')) = seed
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
