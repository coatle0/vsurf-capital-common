"""Contract-driven Universal/Unique enrichment planning for IVK."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from scripts.ivk_factory import PackRegistry, now_iso
from scripts.ivk_new_intake import normalize_intake, validate_intake

from .kernel import read_json, write_json_atomic


CONTRACT_VERSION = "ivk-analysis-contract-0.1"
QA_VERSION = "ivk-enrichment-qa-0.1"
INVESTOR_QUESTIONS = (
    ("earning_mechanism", "이 기업은 어떻게 돈을 버는가?"),
    ("state_transition", "지금의 상태와 미래의 상태는 어떠한가?"),
    ("evidence_gap", "그 상태를 확인하기 위해 무엇을 더 봐야 하는가?"),
)


class EnrichmentValidationError(ValueError):
    """Raised when an enrichment Q&A or frame contract is invalid."""


def _strings(value: Any, field: str) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or any(not isinstance(item, str) or not item.strip() for item in value):
        raise EnrichmentValidationError(f"{field} must be an array of non-empty strings")
    return list(dict.fromkeys(item.strip() for item in value))


def validate_qa(raw: Any) -> dict[str, Any]:
    if not isinstance(raw, dict):
        raise EnrichmentValidationError("Q&A must be an object")
    required = ("contract_version", "value_chain_id", "objective")
    missing = [key for key in required if not raw.get(key)]
    if missing:
        raise EnrichmentValidationError(f"Q&A missing field(s): {', '.join(missing)}")
    if raw["contract_version"] != QA_VERSION:
        raise EnrichmentValidationError(f"unsupported Q&A contract: {raw['contract_version']}")
    gates = raw.get("completion_gates") or {}
    if not isinstance(gates, dict):
        raise EnrichmentValidationError("completion_gates must be an object")
    secondary = _strings(raw.get("secondary_frames"), "secondary_frames")
    extensions = raw.get("extensions") or {}
    if not isinstance(extensions, dict):
        raise EnrichmentValidationError("extensions must be an object")
    return {
        "contract_version": QA_VERSION,
        "value_chain_id": str(raw["value_chain_id"]).strip(),
        "objective": str(raw["objective"]).strip(),
        "secondary_frames": secondary,
        "completion_gates": deepcopy(gates),
        "extensions": {
            "universal_requirements": _strings(extensions.get("universal_requirements"), "extensions.universal_requirements"),
            "unique_outputs": _strings(extensions.get("unique_outputs"), "extensions.unique_outputs"),
            "questions": _strings(extensions.get("questions"), "extensions.questions"),
            "relationship_types": _strings(extensions.get("relationship_types"), "extensions.relationship_types"),
        },
    }


def _frame_contract(pack: dict[str, Any]) -> dict[str, Any]:
    required = (
        "investor_questions", "universal_requirements", "unique_outputs",
        "allowed_unique_relationships", "extension_points",
    )
    missing = [key for key in required if not pack.get(key)]
    if missing:
        raise EnrichmentValidationError(
            f"frame {pack.get('id')} missing enrichment field(s): {', '.join(missing)}"
        )
    questions = pack["investor_questions"]
    if not isinstance(questions, dict) or set(questions) != {key for key, _ in INVESTOR_QUESTIONS}:
        raise EnrichmentValidationError(f"frame {pack.get('id')} must define all three investor questions")
    return {
        "id": pack["id"],
        "version": pack["version"],
        "nickname": pack.get("nickname") or pack["id"],
        "definition": pack.get("definition") or "",
        "investor_questions": deepcopy(questions),
        "universal_requirements": _strings(pack["universal_requirements"], "universal_requirements"),
        "unique_outputs": _strings(pack["unique_outputs"], "unique_outputs"),
        "allowed_unique_relationships": _strings(pack["allowed_unique_relationships"], "allowed_unique_relationships"),
        "extension_points": deepcopy(pack["extension_points"]),
    }


def prepare_enrichment(
    intake_raw: Any,
    qa_raw: Any,
    *,
    registry_path: str | Path,
) -> dict[str, Any]:
    intake = validate_intake(intake_raw)
    normalized = normalize_intake(intake)
    qa = validate_qa(qa_raw)
    registry = PackRegistry(registry_path)
    primary_pack = registry.resolve("frame", normalized["primary_frame"])
    primary = _frame_contract(primary_pack)
    secondary = [_frame_contract(registry.resolve("frame", item)) for item in qa["secondary_frames"]]
    if any(item["id"] == primary["id"] for item in secondary):
        raise EnrichmentValidationError("primary frame cannot also be a secondary frame")

    ext = qa["extensions"]
    secondary_universal_requirements = [
        requirement
        for frame in secondary
        for requirement in frame["universal_requirements"]
    ]
    universal_requirements = list(dict.fromkeys(
        primary["universal_requirements"]
        + secondary_universal_requirements
        + ext["universal_requirements"]
    ))
    unique_outputs = list(dict.fromkeys(primary["unique_outputs"] + ext["unique_outputs"]))
    relationships = list(dict.fromkeys(primary["allowed_unique_relationships"] + ext["relationship_types"]))
    seeds = [
        {
            "canonical_id": item["canonical_id"],
            "ticker": item.get("ticker") or item["canonical_id"],
            "company_name": item.get("company_name"),
            "market": item.get("market") or "us",
        }
        for item in normalized["validated_seeds"]
    ]
    questions = []
    for key, text in INVESTOR_QUESTIONS:
        questions.append({
            "id": key,
            "question": text,
            "frame_subquestions": deepcopy(primary["investor_questions"][key]),
            "status": "unanswered",
        })
    questions.extend({"id": f"custom:{i}", "question": q, "frame_subquestions": [], "status": "unanswered"}
                     for i, q in enumerate(ext["questions"], 1))

    gates = {
        "minimum_periods": 5,
        "question_coverage_pct": 100,
        "require_primary_source": True,
        "require_counter_evidence": True,
        "allow_auto_confirm": False,
        **qa["completion_gates"],
    }
    if gates["allow_auto_confirm"] is not False:
        raise EnrichmentValidationError("allow_auto_confirm must remain false")
    contract = {
        "contract_version": CONTRACT_VERSION,
        "created_at": now_iso(),
        "value_chain_id": qa["value_chain_id"],
        "objective": qa["objective"],
        "investor_questions": questions,
        "primary_frame": primary,
        "secondary_frames": secondary,
        "seeds": seeds,
        "universal_requirements": universal_requirements,
        "unique_requirements": {
            "outputs": unique_outputs,
            "allowed_relationship_types": relationships,
            "must_reference_universal_fact_ids": True,
            "must_include_value_chain_id": True,
            "epistemic_status": ["fact", "inference", "hypothesis"],
            "review_status": ["pending", "accepted", "rejected", "deferred"],
        },
        "completion_gates": gates,
        "extension_points": {
            "frame": deepcopy(primary["extension_points"]),
            "sector": "add reusable requirements only after repeated evidence-backed use",
            "source_adapter": "register market/source adapter without changing analysis contracts",
            "quality_gate": "add versioned benchmark axes without changing stored facts",
            "secondary_view": "add a frame-specific view without overwriting the primary interpretation",
        },
    }
    universal_plan = {
        "contract_version": "ivk-universal-plan-0.1",
        "value_chain_id": qa["value_chain_id"],
        "ownership": "company_fact_layer_shared_across_value_chains",
        "reuse_policy": "reuse_by_company_fact_identity_and_content_hash",
        "facts_must_not_contain": ["vc_role", "beneficiary_rank", "investment_rating", "frame_position"],
        "companies": [{**seed, "requirements": universal_requirements, "status": "coverage_check_required"} for seed in seeds],
    }
    unique_plan = {
        "contract_version": "ivk-unique-plan-0.1",
        "value_chain_id": qa["value_chain_id"],
        "primary_frame": f"{primary['id']}@{primary['version']}",
        "secondary_frames": [f"{item['id']}@{item['version']}" for item in secondary],
        "secondary_view_plans": [
            {
                "frame": f"{item['id']}@{item['version']}",
                "outputs": item["unique_outputs"],
                "allowed_relationship_types": item["allowed_unique_relationships"],
                "investor_questions": item["investor_questions"],
                "status": "planned_secondary",
                "policy": "must not overwrite the primary-frame interpretation",
            }
            for item in secondary
        ],
        "consume": "UniversalFact IDs only; do not copy or mutate shared facts",
        "outputs": unique_outputs,
        "allowed_relationship_types": relationships,
        "questions": questions,
        "status": "planned",
    }
    gaps = {
        "contract_version": "ivk-evidence-gap-register-0.1",
        "value_chain_id": qa["value_chain_id"],
        "policy": "create source tasks only after checking shared Universal coverage",
        "gaps": [
            {
                "id": f"gap:{qa['value_chain_id'].removeprefix('vc:')}:{requirement}",
                "requirement": requirement,
                "applies_to": [seed["canonical_id"] for seed in seeds],
                "status": "coverage_check_required",
                "source_task": None,
                "revalidate_unique": True,
            }
            for requirement in universal_requirements
        ],
    }
    return {
        "analysis_contract": contract,
        "universal_plan": universal_plan,
        "unique_plan": unique_plan,
        "evidence_gaps": gaps,
    }


def write_enrichment_bundle(bundle: dict[str, Any], output_dir: str | Path) -> dict[str, Any]:
    root = Path(output_dir)
    paths = {
        "analysis_contract": root / "analysis_contract.json",
        "universal_plan": root / "universal_plan.json",
        "unique_plan": root / "unique_plan.json",
        "evidence_gaps": root / "evidence_gaps.json",
    }
    for key, path in paths.items():
        write_json_atomic(path, bundle[key])
    return {
        "ok": True,
        "status": "ENRICHMENT_PLANNED",
        "value_chain_id": bundle["analysis_contract"]["value_chain_id"],
        "primary_frame": bundle["unique_plan"]["primary_frame"],
        "artifacts": {key: str(path) for key, path in paths.items()},
    }
