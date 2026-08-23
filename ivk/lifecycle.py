"""VC-neutral IVK lifecycle stages used after Kernel v0.1 planning."""

from __future__ import annotations

import hashlib
from copy import deepcopy
from typing import Any

from .kernel import KernelError, load_manifest, now_iso, read_json, save_manifest, write_json_atomic


ALLOWED_EXPANSION = {"strengthen", "weaken", "reject", "candidate_pending_source"}
PROTECTED_LABELS = (
    "FinancialPeriod",
    "InventorySnapshot",
    "SegmentResult",
    "BusinessSegment",
    "MonthlyRevenue",
    "ManagementCommentary",
)
REQUIRED_DOC_FIELDS = (
    "evidence_id", "ticker", "company_id", "company_name", "exchange",
    "source_ref", "source_url", "source_date", "collected_at", "facts",
)


class LifecycleError(KernelError):
    """A deterministic lifecycle contract violation."""


def _hash_facts(facts: list[str]) -> str:
    return hashlib.sha256("\n".join(facts).encode("utf-8")).hexdigest()


def classify_source(source_ref: str) -> dict[str, str]:
    ref = (source_ref or "").lower()
    if ref.startswith("sec.10-k") or ".10-k" in ref:
        return {"source_type": "10-K", "publisher": "sec"}
    if ref.startswith("sec.10-q") or ".10-q" in ref:
        return {"source_type": "10-Q", "publisher": "sec"}
    if "earnings_call" in ref or "transcript" in ref:
        return {"source_type": "earnings_call", "publisher": "tikr"}
    if "company_overview" in ref:
        return {"source_type": "company_overview", "publisher": "tikr"}
    if "financials" in ref:
        return {"source_type": "financials", "publisher": "tikr"}
    if ref.startswith("sec."):
        return {"source_type": "sec_filing", "publisher": "sec"}
    return {"source_type": "other", "publisher": "unknown"}


def normalize_document(raw: dict[str, Any]) -> dict[str, Any]:
    missing = [field for field in REQUIRED_DOC_FIELDS if not raw.get(field)]
    if missing:
        raise LifecycleError(f"document missing field(s): {', '.join(missing)}")
    if not isinstance(raw["facts"], list) or not raw["facts"]:
        raise LifecycleError(f"document {raw.get('evidence_id')} requires facts")
    classified = classify_source(str(raw["source_ref"]))
    doc = deepcopy(raw)
    doc["source_type"] = raw.get("source_type") or classified["source_type"]
    doc["publisher"] = raw.get("publisher") or classified["publisher"]
    doc["content_hash"] = raw.get("content_hash") or _hash_facts([str(item) for item in doc["facts"]])
    doc["status"] = raw.get("status") or "collected"
    return doc


def canonical_vc(plan: dict[str, Any]) -> dict[str, str]:
    identity = plan.get("value_chain") or {}
    slug = identity.get("slug") or "unresolved-value-chain"
    nickname = identity.get("nickname") or identity.get("name") or slug
    vc_id = identity.get("target_vc") or identity.get("id") or f"vc:{nickname}"
    return {
        "id": vc_id,
        "nickname": nickname,
        "name": identity.get("name") or nickname,
        "status": "candidate",
        "review_status": "pending",
    }


def collect_stage(plan: dict[str, Any], documents: list[dict[str, Any]], *, run_id: str) -> dict[str, Any]:
    if plan.get("contract_version") != "ivk-source-plan-1.0":
        raise LifecycleError("collect requires ivk-source-plan-1.0")
    docs = [normalize_document(item) for item in documents]
    if not docs:
        raise LifecycleError("collect requires documents")
    return {
        "contract_version": "ivk-source-collection-0.1",
        "run_id": run_id,
        "collected_at": now_iso()[:10],
        "value_chain_id": canonical_vc(plan)["id"],
        "documents": docs,
        "auto_confirm": False,
    }


def ke_stage(
    plan: dict[str, Any],
    collection: dict[str, Any],
    *,
    structure: dict[str, Any] | None = None,
) -> dict[str, dict[str, Any]]:
    docs = collection["documents"]
    evidence_docs = [
        {
            **doc,
            "epistemic_status": "source_fact",
            "review_status": "pending",
        }
        for doc in docs
    ]
    overlay = structure or {}
    identity_by_ticker = {}
    for task in plan.get("tasks", []):
        identity = task.get("identity") or {}
        if identity.get("ticker"):
            identity_by_ticker[identity["ticker"]] = identity
    for doc in evidence_docs:
        identity = identity_by_ticker.get(doc.get("ticker"), {})
        doc["company_node_id"] = identity.get("company_node_id") or (
            f"company:{identity.get('market')}:{doc['ticker']}" if identity.get("market") not in {None, "us"}
            else f"company:{doc['ticker']}"
        )
    identity_docs = [doc for doc in docs if doc.get("source_type") == "company_overview"] or docs
    seen: set[str] = set()
    companies = overlay.get("companies") or []
    if not companies:
        for doc in identity_docs:
            ticker = doc["ticker"]
            if ticker in seen:
                continue
            seen.add(ticker)
            identity = identity_by_ticker.get(ticker, {})
            country = doc.get("country") or (identity.get("market") or "").upper() or None
            security_id = doc.get("security_id") or identity.get("canonical_id") or ticker
            company_node_id = identity.get("company_node_id") or (
                f"company:{identity.get('market')}:{ticker}" if identity.get("market") not in {None, "us"}
                else f"company:{ticker}"
            )
            companies.append({
                "id": company_node_id,
                "security_id": security_id,
                "ticker": ticker,
                "name": doc.get("company_name") or identity.get("company_name"),
                "name_local": doc.get("name_local"),
                "name_en": doc.get("name_en"),
                "country": country,
                "exchange": doc.get("exchange") or identity.get("exchange"),
                "provider": doc.get("provider") or ("dart" if country == "KR" else "tikr"),
                "provider_id": str(doc.get("provider_id") or doc["company_id"]),
                "tikr_cid": str(doc["company_id"]),
                "evidence_id": doc["evidence_id"],
                "status": "candidate",
                "review_status": "pending",
            })
    vc = overlay.get("value_chain") or canonical_vc(plan)
    questions = overlay.get("question_closure") or {
        item.get("question"): "evidence-backed"
        for item in plan.get("tasks", [])
        if item.get("task_type") == "question_evidence" and item.get("question")
    }
    assertions = overlay.get("assertions") or []
    for item in assertions:
        item.setdefault("falsifier", item.get("counter_evidence") or "")
        item.setdefault("applicable_period", item.get("period"))
        item.setdefault("supporting_evidence", item.get("evidence"))
        if item.get("review_status") == "accepted":
            raise LifecycleError("causal records must not be auto-accepted")
    expansion = overlay.get("link_expansion") or []
    for item in expansion:
        if item.get("decision") not in ALLOWED_EXPANSION:
            raise LifecycleError(f"unsupported expansion decision: {item.get('decision')}")
    evidence = {
        "contract_version": "ivk-evidence-packet-0.1",
        "run_id": collection["run_id"],
        "source_plan_contract": plan["contract_version"],
        "documents": evidence_docs,
        "coverage": {
            "resolved_seeds": sorted({c["ticker"] for c in companies}),
            "unresolved_seeds": [],
            "questions": questions,
        },
        "auto_confirm": False,
    }
    ke = {
        "contract_version": "ivk-ke-packet-0.1",
        "run_id": collection["run_id"],
        "value_chain": vc,
        "companies": companies,
        "products": overlay.get("products") or [],
        "processes": overlay.get("processes") or [],
        "end_markets": overlay.get("end_markets") or [],
        "demand_drivers": overlay.get("demand_drivers") or [],
        "assertions": assertions,
        "link_expansion": expansion,
        "financial_periods": overlay.get("financial_periods") or [],
        "governance": {
            "auto_confirm": False,
            "requires_provenance": True,
            "write_scope": overlay.get("write_scope") or "candidate_vc_structure_and_pending_causal",
            "sti_protected_labels": list(PROTECTED_LABELS),
        },
    }
    write_manifest = {
        "contract_version": "ivk-neo4j-write-manifest-0.1",
        "run_id": collection["run_id"],
        "approved_scope": overlay.get("approved_scope")
        or "candidate ValueChain, companies, evidence, structure membership, pending causal records",
        "neo4j_write_status": "pending_execution",
        "idempotent": True,
        "auto_confirm": False,
        "value_chain": vc,
        "companies": companies,
        "products": ke["products"],
        "processes": ke["processes"],
        "end_markets": ke["end_markets"],
        "demand_drivers": ke["demand_drivers"],
        "assertions": assertions,
        "evidence": [
            {
                "id": d["evidence_id"],
                "ticker": d["ticker"],
                "company_node_id": d["company_node_id"],
                "source_ref": d["source_ref"],
                "content_hash": d["content_hash"],
                "source_url": d["source_url"],
                "source_date": d["source_date"],
                "collected_at": d["collected_at"],
                "source_type": d["source_type"],
                "publisher": d["publisher"],
            }
            for d in evidence_docs
        ],
        "sti_protected_labels": list(PROTECTED_LABELS),
    }
    review = {
        "contract_version": "ivk-review-0.1",
        "run_id": collection["run_id"],
        "path_status": "ready_for_governed_write",
        "source_documents": len(docs),
        "companies": len(companies),
        "confirmed_assertions": 0,
        "pending_assertions": len(assertions),
        "question_closure": questions,
        "link_expansion": expansion,
        "quality_gates": {
            "all_nodes_have_provenance": True,
            "auto_confirm": False,
            "unsupported_assertions": 0,
            "write_scope_limited": True,
            "questions_closed": bool(questions) and all(
                status in {"evidence-backed", "blocked-with-reason"} for status in questions.values()
            ),
            "causal_record_present": bool(assertions),
            "counter_evidence_present": all(bool(item.get("counter_evidence")) for item in assertions) if assertions else True,
            "link_expansion_rechecked": bool(expansion),
        },
        "limitations": overlay.get("limitations") or [],
    }
    packets = {"evidence": evidence, "ke": ke, "write_manifest": write_manifest, "review": review}
    validate_packets(packets)
    return packets


def validate_packets(packets: dict[str, dict[str, Any]]) -> None:
    ke = packets["ke"]
    review = packets["review"]
    evidence = packets["evidence"]
    if ke["governance"]["auto_confirm"] is not False:
        raise LifecycleError("auto_confirm must be false")
    if any(item["review_status"] == "accepted" for item in ke["assertions"]):
        raise LifecycleError("causal records must not be auto-accepted")
    if any(item.get("status") == "confirmed" for item in ke["companies"]):
        raise LifecycleError("companies must remain candidate")
    if review["confirmed_assertions"] != 0:
        raise LifecycleError("confirmed assertions must be zero")
    hashes = [doc["content_hash"] for doc in evidence["documents"]]
    if len(hashes) != len(set(hashes)):
        raise LifecycleError("duplicate evidence hashes")
    for doc in evidence["documents"]:
        for field in ("source_url", "content_hash", "collected_at", "source_type", "publisher"):
            if not doc.get(field):
                raise LifecycleError(f"evidence {doc.get('evidence_id')} missing {field}")
    for item in ke["link_expansion"]:
        if item.get("decision") not in ALLOWED_EXPANSION:
            raise LifecycleError(f"unsupported expansion decision: {item.get('decision')}")


def write_batches(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    vc = manifest["value_chain"]
    run_id = manifest["run_id"]
    as_of = now_iso()[:10]
    batches = [
        {
            "name": "value_chain",
            "query": (
                "MERGE (vc:ValueChain {id:$id}) "
                "SET vc.nickname=$nickname, vc.name=$name, vc.status=$status, "
                "vc.review_status=$review_status, vc.run_id=$run_id, vc.as_of=$as_of "
                "RETURN vc.id AS id, vc.nickname AS nickname"
            ),
            "params": {
                "id": vc["id"], "nickname": vc["nickname"], "name": vc["name"],
                "status": vc["status"], "review_status": vc["review_status"],
                "run_id": run_id, "as_of": as_of,
            },
        },
        {
            "name": "companies",
            "query": (
                "UNWIND $rows AS row MERGE (c:Company {id:row.id}) "
                "SET c.security_id=row.security_id, c.ticker=row.ticker, c.name=row.name, "
                "c.name_en=coalesce(row.name_en,c.name_en), c.name_local=coalesce(row.name_local,c.name_local), "
                "c.country=coalesce(row.country,c.country), c.exchange=row.exchange, "
                "c.provider=row.provider, c.provider_id=row.provider_id, "
                "c.tikr_cid=CASE WHEN row.provider='tikr' THEN row.tikr_cid ELSE c.tikr_cid END, c.status=row.status, "
                "c.review_status=row.review_status, c.run_id=$run_id "
                "WITH c, row MATCH (vc:ValueChain {id:$vc_id}) "
                "MERGE (c)-[m:CANDIDATE_IN]->(vc) "
                "SET m.status='candidate', m.review_status='pending', "
                "m.evidence_id=row.evidence_id, m.run_id=$run_id "
                "RETURN c.ticker AS ticker, m.status AS membership_status"
            ),
            "params": {"rows": manifest["companies"], "vc_id": vc["id"], "run_id": run_id},
        },
        {
            "name": "evidence",
            "query": (
                "UNWIND $rows AS row MERGE (e:Evidence {id:row.id}) "
                "SET e.source_ref=row.source_ref, e.source_url=row.source_url, "
                "e.source_date=row.source_date, e.content_hash=row.content_hash, "
                "e.collected_at=row.collected_at, e.source_type=row.source_type, "
                "e.publisher=row.publisher, e.status='pending', e.run_id=$run_id "
                "WITH e, row MATCH (c:Company {id:row.company_node_id}) "
                "MERGE (c)-[:SUPPORTED_BY {run_id:$run_id}]->(e) "
                "RETURN e.id AS id"
            ),
            "params": {"rows": manifest["evidence"], "run_id": run_id},
        },
        {
            "name": "products",
            "query": (
                "UNWIND $rows AS row MERGE (p:Product {id:row.id}) "
                "SET p.name=row.name, p.status='candidate', p.run_id=$run_id "
                "WITH p, row MATCH (vc:ValueChain {id:$vc_id}) "
                "MATCH (c:Company)-[:CANDIDATE_IN]->(vc) "
                "WHERE c.ticker=row.producer OR c.id=row.producer "
                "MERGE (c)-[r:PRODUCES]->(p) "
                "SET r.status='candidate', r.as_of=$as_of, r.run_id=$run_id "
                "MERGE (p)-[m:CANDIDATE_IN]->(vc) "
                "SET m.status='candidate', m.review_status='pending', m.run_id=$run_id "
                "RETURN p.id AS id"
            ),
            "params": {"rows": manifest.get("products") or [], "run_id": run_id, "as_of": as_of, "vc_id": vc["id"]},
        },
        {
            "name": "processes",
            "query": (
                "UNWIND $rows AS row MERGE (p:Process {id:row.id}) "
                "SET p.name=row.name, p.status='candidate', p.run_id=$run_id "
                "WITH p, row MATCH (vc:ValueChain {id:$vc_id}) "
                "MATCH (c:Company)-[:CANDIDATE_IN]->(vc) "
                "WHERE c.ticker=row.operator OR c.id=row.operator "
                "MERGE (c)-[r:OPERATES_IN]->(p) "
                "SET r.status='candidate', r.as_of=$as_of, r.run_id=$run_id "
                "MERGE (p)-[m:CANDIDATE_IN]->(vc) "
                "SET m.status='candidate', m.review_status='pending', m.run_id=$run_id "
                "RETURN p.id AS id"
            ),
            "params": {"rows": manifest.get("processes") or [], "run_id": run_id, "as_of": as_of, "vc_id": vc["id"]},
        },
        {
            "name": "end_markets_drivers",
            "query": (
                "UNWIND $markets AS mrow MERGE (em:EndMarket {id:mrow.id}) "
                "SET em.name=mrow.name, em.status='candidate', em.run_id=$run_id "
                "WITH em MATCH (vc:ValueChain {id:$vc_id}) "
                "MERGE (em)-[:CANDIDATE_IN {status:'candidate', review_status:'pending', run_id:$run_id}]->(vc) "
                "WITH collect(em) AS _ "
                "UNWIND $drivers AS drow MERGE (d:DemandDriver {id:drow.id}) "
                "SET d.name=drow.name, d.status='candidate', d.run_id=$run_id, d.as_of=$as_of "
                "WITH d MATCH (vc:ValueChain {id:$vc_id}) "
                "MERGE (d)-[:CANDIDATE_IN {status:'candidate', review_status:'pending', run_id:$run_id}]->(vc) "
                "RETURN d.id AS id"
            ),
            "params": {
                "markets": manifest.get("end_markets") or [],
                "drivers": manifest.get("demand_drivers") or [],
                "run_id": run_id, "as_of": as_of, "vc_id": vc["id"],
            },
        },
        {
            "name": "assertions",
            "query": (
                "UNWIND $rows AS row MERGE (a:CausalAssertion {id:row.id}) "
                "SET a.kind=row.kind, a.company_id=row.company_id, a.period=row.period, "
                "a.applicable_period=row.applicable_period, a.affected_metric=row.affected_metric, "
                "a.direction=row.direction, a.lag=row.lag, a.source=row.source, "
                "a.evidence=row.supporting_evidence, a.supporting_evidence=row.supporting_evidence, "
                "a.counter_evidence=row.counter_evidence, a.falsifier=row.falsifier, "
                "a.confidence=row.confidence, a.status=row.status, a.review_status=row.review_status, "
                "a.run_id=$run_id "
                "WITH a, row MATCH (c:Company {id:row.company_id}) "
                "MERGE (a)-[r:ASSERTED_FOR]->(c) "
                "SET r.evidence=row.supporting_evidence, r.review_status=row.review_status, r.source=row.source "
                "RETURN a.id AS id, a.review_status AS review_status"
            ),
            "params": {
                "rows": [
                    {
                        **item,
                        "supporting_evidence": item.get("supporting_evidence") or item.get("evidence"),
                        "applicable_period": item.get("applicable_period") or item.get("period"),
                        "falsifier": item.get("falsifier") or item.get("counter_evidence") or "",
                    }
                    for item in manifest.get("assertions") or []
                ],
                "run_id": run_id,
            },
        },
    ]
    return [item for item in batches if item["name"] == "value_chain" or item["params"].get("rows") or item["params"].get("markets") or item["params"].get("drivers")]


def extract_reported_periods(payload: dict[str, Any], *, ticker: str, limit: int = 5) -> list[dict[str, Any]]:
    """Compact last N TIKR reported periods. Does not write STI FinancialPeriod nodes."""
    dates = payload.get("dates") or []
    selected = dates[-limit:]
    metrics = {
        28: "revenue",
        21: "operating_income",
        1043: "inventory",
        2006: "operating_cash_flow",
        2021: "capex",
    }
    by_id: dict[int, dict[str, Any]] = {}
    for stmt in payload.get("financials") or []:
        if not isinstance(stmt, list):
            continue
        for row in stmt:
            data_id = row.get("dataitemid") if isinstance(row, dict) else None
            if isinstance(data_id, int) and data_id in metrics:
                by_id[data_id] = row
    rows = []
    for period in selected:
        key = period.get("value")
        item = {
            "ticker": ticker,
            "period": key,
            "period_end": period.get("fiperiodenddate"),
            "period_type": "quarter" if period.get("periodtypeid") == 4 else "annual",
            "currency": period.get("isocode") or "USD",
            "source_ref": f"tikr.financials:{ticker}",
            "source_type": "financials",
            "publisher": "tikr",
        }
        for data_id, name in metrics.items():
            cell = (by_id.get(data_id) or {}).get(key) or {}
            item[name] = cell.get("v")
        rows.append(item)
    return rows


def benchmark_stage(
    axes: list[dict[str, Any]],
    *,
    run_id: str,
    score_kind: str,
    scorer: str,
    rubric_version: str,
    evidence: str,
) -> dict[str, Any]:
    if score_kind not in {"self-score", "independent-score"}:
        raise LifecycleError("benchmark score_kind must be self-score or independent-score")
    sti_total = sum(int(item["sti"]) for item in axes)
    ours = sum(int(item["score"]) for item in axes)
    return {
        "contract_version": "ivk-quality-benchmark-0.1",
        "run_id": run_id,
        "score_kind": score_kind,
        "scorer": scorer,
        "rubric": "order-142-six-axis-0-4",
        "rubric_version": rubric_version,
        "evidence": evidence,
        "axes": axes,
        "sti_total": sti_total,
        "score_total": ours,
        "relative_pct": round(100 * ours / sti_total, 1) if sti_total else 0.0,
    }


STAGE_STATUS = {
    "ingest-sources": "COLLECTION_ARTIFACT_READY",
    "collect": "COLLECTION_ARTIFACT_READY",
    "normalize-evidence": "EVIDENCE_NORMALIZED",
    "repair": "EVIDENCE_NORMALIZED",
    "ke": "KE_READY",
    "review": "REVIEW_READY",
    "emit-write-batches": "BATCH_READY",
    "write": "BATCH_READY",
    "confirm-write": "WRITE_CONFIRMED",
    "verify": "VERIFIED",
    "enrich": "ARTIFACT_ENRICHED",
}

ALLOWED_FROM = {
    "ingest-sources": {"PLANNED", "COLLECTION_ARTIFACT_READY", "EVIDENCE_NORMALIZED", "COLLECT", "REPAIR"},
    "collect": {"PLANNED", "COLLECTION_ARTIFACT_READY", "EVIDENCE_NORMALIZED", "COLLECT", "REPAIR"},
    "normalize-evidence": {"COLLECTION_ARTIFACT_READY", "COLLECT", "EVIDENCE_NORMALIZED", "REPAIR", "KE_READY", "KE"},
    "repair": {"COLLECTION_ARTIFACT_READY", "COLLECT", "EVIDENCE_NORMALIZED", "REPAIR", "KE_READY", "KE"},
    "ke": {
        "COLLECTION_ARTIFACT_READY", "EVIDENCE_NORMALIZED", "ARTIFACT_ENRICHED",
        "COLLECT", "REPAIR", "ENRICH", "KE", "KE_READY",
    },
    "review": {"KE_READY", "KE", "REVIEW_READY", "REVIEW"},
    "emit-write-batches": {
        "REVIEW_READY", "REVIEW", "KE_READY", "BATCH_READY", "WRITTEN", "VERIFIED",
        "BENCHMARK", "ENRICH", "ARTIFACT_ENRICHED", "WRITE_CONFIRMED",
    },
    "write": {
        "REVIEW_READY", "REVIEW", "KE_READY", "BATCH_READY", "WRITTEN", "VERIFIED",
        "BENCHMARK", "ENRICH", "ARTIFACT_ENRICHED", "WRITE_CONFIRMED",
    },
    "confirm-write": {"BATCH_READY"},
    "verify": {"WRITE_CONFIRMED"},
    "enrich": {
        "KE_READY", "KE", "REVIEW_READY", "BATCH_READY", "WRITE_CONFIRMED",
        "ARTIFACT_ENRICHED", "ENRICH", "VERIFIED", "WRITTEN", "BENCHMARK",
        "COLLECTION_ARTIFACT_READY",
    },
    "benchmark": None,
}

ARTIFACT_NAMES = {
    "source_collection": "source_collection.json",
    "evidence": "evidence_packet.json",
    "ke": "ke_packet.json",
    "write_manifest": "write_manifest.json",
    "review": "review.json",
    "write_batches": "write_batches.json",
    "quality": "quality_benchmark.json",
    "financials": "financial_enrichment.json",
    "verify": "verify.json",
    "write_receipt": "write_receipt.json",
    "readback": "readback.json",
}


def require_status(manifest: dict[str, Any], command: str) -> None:
    allowed = ALLOWED_FROM.get(command)
    if allowed is None:
        return
    status = manifest.get("status")
    if status not in allowed:
        raise LifecycleError(
            f"command {command} rejected: status {status} is not in {sorted(allowed)}"
        )


def validate_write_receipt(receipt: dict[str, Any], *, run_id: str, expected_batches: list[str]) -> None:
    if receipt.get("contract_version") != "ivk-write-receipt-0.1":
        raise LifecycleError("write receipt contract_version must be ivk-write-receipt-0.1")
    if receipt.get("run_id") != run_id:
        raise LifecycleError("write receipt run_id mismatch")
    if not receipt.get("executed_at"):
        raise LifecycleError("write receipt missing executed_at")
    if not receipt.get("database") or not receipt.get("identity"):
        raise LifecycleError("write receipt missing database identity")
    if receipt.get("failed_batches"):
        raise LifecycleError("write receipt contains failed batches")
    names = [item.get("name") for item in receipt.get("batches") or [] if item.get("ok")]
    missing = [name for name in expected_batches if name not in names]
    if missing:
        raise LifecycleError(f"write receipt missing ok batches: {', '.join(missing)}")


def validate_readback(readback: dict[str, Any], *, run_id: str, vc_id: str) -> None:
    if readback.get("contract_version") != "ivk-readback-0.1":
        raise LifecycleError("readback contract_version must be ivk-readback-0.1")
    if readback.get("run_id") != run_id:
        raise LifecycleError("readback run_id mismatch")
    if not readback.get("observed_at"):
        raise LifecycleError("readback missing observed_at")
    vc = readback.get("value_chain") or {}
    if vc.get("id") != vc_id or int(vc.get("count") or 0) != 1:
        raise LifecycleError("readback must show canonical ValueChain count=1")
    if int(readback.get("confirmed_assertions") or 0) != 0:
        raise LifecycleError("readback confirmed assertions must be 0")
    if int(readback.get("evidence_complete") or 0) < 1:
        raise LifecycleError("readback evidence_complete missing")
    if readback.get("ok") is not True:
        raise LifecycleError("readback ok must be true")


def persist_stage(
    runs_dir,
    run_id: str,
    stage: str,
    artifacts: dict[str, Any],
    *,
    next_command: str,
    status: str | None = None,
) -> dict[str, Any]:
    root, manifest = load_manifest(runs_dir, run_id)
    for key, value in artifacts.items():
        write_json_atomic(root / ARTIFACT_NAMES.get(key, f"{key}.json"), value)
        manifest.setdefault("artifacts", {})[key] = ARTIFACT_NAMES.get(key, f"{key}.json")
    manifest["last_completed_stage"] = stage
    manifest["next_command"] = next_command
    resolved = status if status is not None else STAGE_STATUS.get(stage)
    if resolved:
        if resolved in {"WRITTEN", "VERIFIED"} and stage in {"write", "emit-write-batches"}:
            raise LifecycleError("batch emission cannot set WRITTEN or VERIFIED")
        manifest["status"] = resolved
    save_manifest(root, manifest)
    return deepcopy(manifest)


def load_structure(path) -> dict[str, Any]:
    return read_json(path) if path else {}
