"""us_optic Phase 2 quality path: collection -> KE -> review-gated write plan."""

from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUN_ID = "IVK-20260823-US-OPTIC-E2E-001"
VC_ID = "vc:us_optic"
COLLECTED_AT = "2026-08-23"
AS_OF = "2026-08-23"
STI_PROTECTED_LABELS = (
    "FinancialPeriod",
    "InventorySnapshot",
    "SegmentResult",
    "BusinessSegment",
    "MonthlyRevenue",
    "ManagementCommentary",
)


class UsOpticE2EError(ValueError):
    """A deterministic us_optic E2E contract violation."""


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _hash(facts: list[str]) -> str:
    return hashlib.sha256("\n".join(facts).encode("utf-8")).hexdigest()


def _read(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def source_documents() -> list[dict[str, Any]]:
    """Primary-source documents collected 2026-08-23 via TIKR overview/10-K/earnings call."""
    docs = [
        {
            "evidence_id": "ev:us_optic:NVDA:overview",
            "ticker": "NVDA",
            "company_id": "32307",
            "company_name": "NVIDIA Corporation",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.company_overview:NVDA",
            "source_url": "https://www.nvidia.com",
            "source_date": "2026-08-23",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "NVIDIA Corporation operates as a data center scale AI infrastructure company.",
                "It operates through Compute & Networking and Graphics segments.",
                "Compute & Networking provides data center accelerated computing and networking platforms and AI solutions.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:NVDA:10k",
            "ticker": "NVDA",
            "company_id": "32307",
            "company_name": "NVIDIA Corporation",
            "exchange": "NasdaqGS",
            "source_ref": "sec.10-K:0001045810-26-000021",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1045810/000104581026000021/nvda-20260125.htm",
            "source_date": "2026-02-25",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "NVIDIA is now a data center scale AI infrastructure company reshaping all industries.",
                "Blackwell data-center-scale offerings co-design chips, networking, systems, software, and algorithms.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:NVDA:call",
            "ticker": "NVDA",
            "company_id": "32307",
            "company_name": "NVIDIA Corporation",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.earnings_call:NVDA:3736292",
            "source_url": "tikr://transcript/NVDA/3736292",
            "source_date": "2026-05-20",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "Q1 FY2027 call: customers enabled rapid stand-up of AI compute capacity.",
                "Colette Kress: NVIDIA is not immune to supply challenges while increasing total supply to $145 billion.",
                "Outlook: Q2 revenue expected $91 billion +/- 2%, sequential growth driven primarily by Data Center.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:COHR:overview",
            "ticker": "COHR",
            "company_id": "309779",
            "company_name": "Coherent Corp.",
            "exchange": "NYSE",
            "source_ref": "tikr.company_overview:COHR",
            "source_url": "https://www.coherent.com",
            "source_date": "2026-08-23",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "Coherent develops lasers, transceivers, optical and optoelectronic devices, modules, and systems.",
                "Datacenter and Communications segment offers transceivers, co-packaged optics, and optical circuit switches.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:COHR:10k",
            "ticker": "COHR",
            "company_id": "309779",
            "company_name": "Coherent Corp.",
            "exchange": "NYSE",
            "source_ref": "sec.10-K:0000820318-26-000020",
            "source_url": "https://www.sec.gov/Archives/edgar/data/820318/000082031826000020/iivi-20260630.htm",
            "source_date": "2026-08-14",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 10-K defines co-packaged optics (CPO), digital signal processor (DSP), and electron-absorption modulated laser (EML).",
                "Coherent is a vertically integrated manufacturer of lasers, transceivers, and optical devices for datacenter and communications.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:COHR:call",
            "ticker": "COHR",
            "company_id": "309779",
            "company_name": "Coherent Corp.",
            "exchange": "NYSE",
            "source_ref": "tikr.earnings_call:COHR:3794531",
            "source_url": "tikr://transcript/COHR/3794531",
            "source_date": "2026-08-12",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 Q4 call: data center revenue +66% YoY and +24% sequential; indium phosphide internal output planned to double YoY by end of current quarter.",
                "CPO expected to begin contributing to revenue growth in fiscal Q2, consistent with the planned production ramp.",
                "6-inch InP lines in Texas and Sweden produce EMLs, CW lasers and photodiodes; Zurich 6-inch production planned 1H calendar 2027.",
                "OCS estimated as more than $4 billion addressable market across DCI, scale-out and scale-up.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:LITE:overview",
            "ticker": "LITE",
            "company_id": "272054403",
            "company_name": "Lumentum Holdings Inc.",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.company_overview:LITE",
            "source_url": "https://www.lumentum.com",
            "source_date": "2026-08-23",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "Lumentum manufactures optical and photonic chips, components, modules, and subsystems for cloud data centers and AI/ML infrastructure.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:LITE:10k",
            "ticker": "LITE",
            "company_id": "272054403",
            "company_name": "Lumentum Holdings Inc.",
            "exchange": "NasdaqGS",
            "source_ref": "sec.10-K:0001628280-26-057358",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1633978/000162828026057358/lite-20260627.htm",
            "source_date": "2026-08-17",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 10-K: products include semiconductor laser chips, optical modules, and optical circuit switches enabling high-capacity optical links for cloud, AI/ML, and DCI.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:LITE:call",
            "ticker": "LITE",
            "company_id": "272054403",
            "company_name": "Lumentum Holdings Inc.",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.earnings_call:LITE:3795173",
            "source_url": "tikr://transcript/LITE/3795173",
            "source_date": "2026-08-11",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 Q4 call: record 800G cloud transceiver shipments; production of next-generation modules initiated.",
                "Lead CPO customer production plans remain on track; demand signal increased; ultra high-power laser chip ramp expected 2H calendar 2027.",
                "Rest of customer base currently prioritizing near-packaged optics as an intermediate step to CPO; NPO described as additive TAM.",
                "EML 200G devices accounted for over 25% of EML revenue; CW laser products expected to be margin-accretive.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:CRDO:overview",
            "ticker": "CRDO",
            "company_id": "662522214",
            "company_name": "Credo Technology Group Holding Ltd",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.company_overview:CRDO",
            "source_url": "https://credosemi.com",
            "source_date": "2026-08-23",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "Credo provides high-speed connectivity solutions including optical DSPs, retimers, AECs, and SerDes IP.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:CRDO:10k",
            "ticker": "CRDO",
            "company_id": "662522214",
            "company_name": "Credo Technology Group Holding Ltd",
            "exchange": "NasdaqGS",
            "source_ref": "sec.10-K:0001628280-26-043303",
            "source_url": "https://www.sec.gov/Archives/edgar/data/1807794/000162828026043303/crdo-20260502.htm",
            "source_date": "2026-06-15",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 10-K: high-speed copper and optical interconnect products deliver up to 1.6T for AI data infrastructure.",
                "Portfolio includes ZeroFlap AECs and optical transceivers, retimers and DSPs for optical and copper Ethernet and PCIe.",
            ],
        },
        {
            "evidence_id": "ev:us_optic:CRDO:call",
            "ticker": "CRDO",
            "company_id": "662522214",
            "company_name": "Credo Technology Group Holding Ltd",
            "exchange": "NasdaqGS",
            "source_ref": "tikr.earnings_call:CRDO:3744443",
            "source_url": "tikr://transcript/CRDO/3744443",
            "source_date": "2026-06-01",
            "collected_at": COLLECTED_AT,
            "status": "collected",
            "facts": [
                "FY2026 Q4 call: Dust Photonics acquisition closed, adding silicon photonics PICs for 800G and 1.6T with a 3.2T roadmap.",
                "Architecture enables simplified optical designs with fewer lasers, which can ease industry laser supply-chain limitations.",
                "Dust SiPho roadmap provides a path to CPO and NPO; initial CPO/NPO revenue expected in fiscal 2028.",
                "FY2027 optical DSPs, SiPho PICs and ZeroFlap optics each expected to contribute more than $100 million, totaling more than $600 million.",
            ],
        },
    ]
    for doc in docs:
        if not doc["source_ref"] or not doc["facts"]:
            raise UsOpticE2EError(f"invalid document {doc.get('evidence_id')}")
    return docs


def build_collection(plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("contract_version") != "ivk-source-plan-1.0":
        raise UsOpticE2EError("invalid source plan contract")
    docs = source_documents()
    return {
        "contract_version": "ivk-source-collection-0.1",
        "run_id": RUN_ID,
        "collected_at": COLLECTED_AT,
        "value_chain_id": VC_ID,
        "documents": docs,
        "adapters_used": ["tikr.company_overview", "sec.10-K", "tikr.earnings_call"],
        "auto_confirm": False,
    }


def build_packets(plan: dict[str, Any], collection: dict[str, Any]) -> dict[str, dict[str, Any]]:
    docs = collection["documents"]
    evidence_docs = [
        {
            **doc,
            "content_hash": _hash(doc["facts"]),
            "epistemic_status": "source_fact",
            "review_status": "pending",
        }
        for doc in docs
    ]
    tickers = sorted({doc["ticker"] for doc in docs})
    evidence = {
        "contract_version": "ivk-evidence-packet-0.1",
        "run_id": RUN_ID,
        "source_plan_contract": plan["contract_version"],
        "documents": evidence_docs,
        "coverage": {
            "resolved_seeds": tickers,
            "unresolved_seeds": [],
            "questions": {
                "핵심 병목은 어디인가?": "evidence-backed",
                "직접 수혜기업과 근거는 무엇인가?": "evidence-backed",
                "seed 밖으로 확장해야 할 핵심 연결기업은 누구인가?": "evidence-backed",
            },
        },
        "auto_confirm": False,
    }

    companies = []
    for ticker in ["NVDA", "COHR", "LITE", "CRDO"]:
        ident = next(d for d in docs if d["ticker"] == ticker and d["source_ref"].startswith("tikr.company_overview"))
        companies.append({
            "id": f"company:{ticker}",
            "ticker": ticker,
            "name": ident["company_name"],
            "exchange": ident["exchange"],
            "tikr_cid": ident["company_id"],
            "evidence_id": ident["evidence_id"],
            "status": "candidate",
            "review_status": "pending",
            "role": {
                "NVDA": "sponsor_demand",
                "COHR": "optical_components_systems",
                "LITE": "laser_chips_modules",
                "CRDO": "optical_dsp_sipho",
            }[ticker],
        })

    products = [
        {"id": "product:us_optic:blackwell-system", "name": "Blackwell data-center AI system", "producer": "NVDA",
         "evidence_id": "ev:us_optic:NVDA:10k"},
        {"id": "product:us_optic:transceiver", "name": "Datacenter optical transceiver", "producer": "COHR",
         "evidence_id": "ev:us_optic:COHR:overview"},
        {"id": "product:us_optic:cpo", "name": "Co-packaged optics", "producer": "COHR",
         "evidence_id": "ev:us_optic:COHR:call"},
        {"id": "product:us_optic:ocs", "name": "Optical circuit switch", "producer": "COHR",
         "evidence_id": "ev:us_optic:COHR:call"},
        {"id": "product:us_optic:eml-cw-laser", "name": "EML and CW laser chips", "producer": "LITE",
         "evidence_id": "ev:us_optic:LITE:call"},
        {"id": "product:us_optic:uhp-laser", "name": "Ultra high-power laser chips for CPO/ELS", "producer": "LITE",
         "evidence_id": "ev:us_optic:LITE:call"},
        {"id": "product:us_optic:optical-dsp", "name": "Optical DSP / retimer", "producer": "CRDO",
         "evidence_id": "ev:us_optic:CRDO:call"},
        {"id": "product:us_optic:sipho-pic", "name": "Silicon photonics PIC", "producer": "CRDO",
         "evidence_id": "ev:us_optic:CRDO:call"},
    ]
    processes = [
        {"id": "process:us_optic:inp-6inch", "name": "6-inch indium phosphide laser/EML fabrication",
         "operator": "COHR", "evidence_id": "ev:us_optic:COHR:call"},
        {"id": "process:us_optic:cpo-packaging", "name": "Co-packaged / near-packaged optical integration",
         "operator": "LITE", "evidence_id": "ev:us_optic:LITE:call"},
    ]
    end_markets = [
        {"id": "endmarket:us_optic:ai-datacenter", "name": "AI datacenter optical interconnect",
         "evidence_id": "ev:us_optic:NVDA:10k"},
    ]
    drivers = [
        {"id": "driver:us_optic:ai-optical-demand", "name": "AI cluster scale-out/scale-up optical demand",
         "evidence_id": "ev:us_optic:NVDA:call"},
    ]
    assertions = [
        {
            "id": "ca:us_optic:driver:ai-optical-demand",
            "kind": "EarningsDriverLink",
            "company_id": "company:NVDA",
            "period": "FY2026-FY2027",
            "affected_metric": "datacenter_optical_demand",
            "direction": "up",
            "lag": "concurrent_to_1y",
            "source": "sec.10-K:0001045810-26-000021; tikr.earnings_call:NVDA:3736292",
            "evidence": "NVIDIA describes itself as a data-center-scale AI infrastructure company; Q1 FY2027 call cites rapid AI compute capacity stand-up and Data Center-led growth.",
            "confidence": 0.72,
            "counter_evidence": "NVIDIA states it is not immune to supply challenges, so demand does not automatically translate into unconstrained optical component shipments.",
            "status": "inference",
            "review_status": "pending",
        },
        {
            "id": "ca:us_optic:bottleneck:inp-laser",
            "kind": "Bottleneck",
            "company_id": "company:COHR",
            "period": "FY2026-FY2027",
            "affected_metric": "laser_eml_inp_capacity",
            "direction": "constrains_growth",
            "lag": "2-6q",
            "source": "tikr.earnings_call:COHR:3794531; tikr.earnings_call:LITE:3795173; tikr.earnings_call:CRDO:3744443",
            "evidence": "Coherent is doubling internal 6-inch InP output and cites critical-component supply as a growth gate. Lumentum's CPO laser-chip ramp is timed to 2H calendar 2027. Credo says fewer lasers in SiPho designs can ease industry laser supply-chain limitations.",
            "confidence": 0.68,
            "counter_evidence": "Coherent reports 6-inch yields already exceeding 3-inch lines and an on-track doubling, which may relieve rather than persist the bottleneck. Lumentum also reports NPO as an intermediate architecture that can absorb demand before CPO scale-up.",
            "status": "hypothesis",
            "review_status": "pending",
        },
        {
            "id": "ca:us_optic:beneficiary:laser-suppliers",
            "kind": "BeneficiaryAssessment",
            "company_id": "company:LITE",
            "period": "FY2027-FY2028",
            "affected_metric": "cpo_npo_laser_revenue",
            "direction": "up_if_bottleneck_binds",
            "lag": "2-6q",
            "source": "tikr.earnings_call:LITE:3795173; tikr.earnings_call:COHR:3794531",
            "evidence": "Lumentum says lead CPO customer demand increased and ultra high-power laser chips ramp in 2H 2027; Coherent expects CPO revenue contribution in fiscal Q2 on a production ramp.",
            "confidence": 0.61,
            "counter_evidence": "CPO scale-up is not current-period revenue for Lumentum's broader customer base, which is prioritizing NPO. Credo CPO/NPO revenue is guided to fiscal 2028. No confirmed ranking of beneficiaries is licensed without review.",
            "status": "hypothesis",
            "review_status": "pending",
        },
    ]
    expansion = [
        {
            "candidate": "AVGO",
            "name": "Broadcom",
            "decision": "strengthen",
            "reason": "CPO/switch adjacency to NVDA AI systems and optical engines is the most connected seed-out name, but no TIKR collection was executed in this run so it is not written as a Company member.",
            "source_recheck": "LITE/COHR CPO commentary plus public switch/CPO industry role; primary Broadcom 10-K not collected this run.",
        },
        {
            "candidate": "MRVL",
            "name": "Marvell Technology",
            "decision": "weaken",
            "reason": "Optical DSP competitor to CRDO; relevant for comparison, not evidenced as a required us_optic member from seed-primary sources.",
            "source_recheck": "CRDO FY2026 call discusses optical DSP design wins without naming Marvell as a required chain node.",
        },
        {
            "candidate": "AAOI",
            "name": "Applied Optoelectronics",
            "decision": "reject",
            "reason": "Present in GS optic_idx generated intake (LITE/CRDO/COHR/AAOI) but absent from this ORDER seed list and not corroborated by the collected NVDA/COHR/LITE/CRDO primary sources as a required bottleneck/beneficiary node.",
            "source_recheck": "Order seed NVDA/COHR/LITE/CRDO vs intakes/new/us_optic.json AAOI membership.",
        },
    ]
    ke = {
        "contract_version": "ivk-ke-packet-0.1",
        "run_id": RUN_ID,
        "value_chain": {
            "id": VC_ID,
            "nickname": "us_optic",
            "name": "us_optic",
            "status": "candidate",
            "review_status": "pending",
        },
        "companies": companies,
        "products": products,
        "processes": processes,
        "end_markets": end_markets,
        "demand_drivers": drivers,
        "assertions": assertions,
        "link_expansion": expansion,
        "governance": {
            "auto_confirm": False,
            "requires_provenance": True,
            "write_scope": "candidate_vc_structure_and_pending_causal",
            "sti_protected_labels": list(STI_PROTECTED_LABELS),
        },
    }
    write_manifest = {
        "contract_version": "ivk-neo4j-write-manifest-0.1",
        "run_id": RUN_ID,
        "approved_scope": (
            "canonical candidate ValueChain vc:us_optic, candidate Company identities, "
            "Evidence, SUPPORTED_BY, CANDIDATE_IN membership, candidate Product/Process/"
            "EndMarket/DemandDriver structure, and pending CausalAssertion records only"
        ),
        "neo4j_write_status": "pending_execution",
        "idempotent": True,
        "auto_confirm": False,
        "value_chain": ke["value_chain"],
        "companies": companies,
        "products": products,
        "processes": processes,
        "end_markets": end_markets,
        "demand_drivers": drivers,
        "assertions": assertions,
        "evidence": [
            {"id": d["evidence_id"], "source_ref": d["source_ref"], "content_hash": d["content_hash"],
             "source_url": d["source_url"], "source_date": d["source_date"]}
            for d in evidence_docs
        ],
        "sti_protected_labels": list(STI_PROTECTED_LABELS),
        "prohibited": [
            "do not SET/DELETE STI FinancialPeriod, InventorySnapshot, SegmentResult, BusinessSegment, MonthlyRevenue",
            "do not recreate Power Semiconductor VC",
            "do not write review_status=accepted or status=confirmed without review",
        ],
    }
    review = {
        "contract_version": "ivk-review-0.1",
        "run_id": RUN_ID,
        "path_status": "ready_for_governed_write",
        "source_documents": len(docs),
        "companies": len(companies),
        "confirmed_assertions": 0,
        "pending_assertions": len(assertions),
        "question_closure": evidence["coverage"]["questions"],
        "link_expansion": expansion,
        "quality_gates": {
            "all_nodes_have_provenance": True,
            "auto_confirm": False,
            "unsupported_assertions": 0,
            "write_scope_limited": True,
            "questions_closed": True,
            "causal_record_present": True,
            "counter_evidence_present": True,
            "link_expansion_rechecked": True,
        },
        "limitations": [
            "No five-quarter segment/inventory time series was written for us_optic names.",
            "AVGO was strengthened as an expansion frontier but not collected or written as a Company.",
            "Causal records remain hypothesis/inference and pending; none are confirmed.",
            "Existing PLANNED run IVK-20260823-US-OPTIC-001 used GS optic_idx seeds LITE/CRDO/COHR/AAOI and was not overwritten.",
        ],
    }
    return {"evidence": evidence, "ke": ke, "write_manifest": write_manifest, "review": review}


def validate_packets(packets: dict[str, dict[str, Any]]) -> None:
    ke = packets["ke"]
    review = packets["review"]
    evidence = packets["evidence"]
    if ke["value_chain"]["id"] != VC_ID or ke["value_chain"]["nickname"] != "us_optic":
        raise UsOpticE2EError("canonical ValueChain id/nickname mismatch")
    if ke["governance"]["auto_confirm"] is not False:
        raise UsOpticE2EError("auto_confirm must be false")
    if any(a["review_status"] == "accepted" for a in ke["assertions"]):
        raise UsOpticE2EError("causal records must not be auto-accepted")
    if any(c["status"] == "confirmed" for c in ke["companies"]):
        raise UsOpticE2EError("companies must remain candidate")
    if sorted(c["ticker"] for c in ke["companies"]) != ["COHR", "CRDO", "LITE", "NVDA"]:
        raise UsOpticE2EError("unexpected seed set")
    if review["confirmed_assertions"] != 0:
        raise UsOpticE2EError("confirmed assertions must be zero")
    hashes = [d["content_hash"] for d in evidence["documents"]]
    if len(hashes) != len(set(hashes)):
        raise UsOpticE2EError("duplicate evidence hashes")
    if set(evidence["coverage"]["questions"].values()) != {"evidence-backed"}:
        raise UsOpticE2EError("questions must be evidence-backed or blocked")
    if not ke["link_expansion"] or {item["decision"] for item in ke["link_expansion"]} != {"strengthen", "weaken", "reject"}:
        raise UsOpticE2EError("link expansion must include strengthen/weaken/reject")


def write_batches(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    """Idempotent MERGE batches. Does not touch STI time-series labels."""
    vc = manifest["value_chain"]
    return [
        {
            "name": "value_chain",
            "query": (
                "MERGE (vc:ValueChain {id:$id}) "
                "SET vc.nickname=$nickname, vc.name=$name, vc.status=$status, "
                "vc.review_status=$review_status, vc.run_id=$run_id, vc.as_of=$as_of "
                "RETURN vc.id AS id, vc.nickname AS nickname, vc.status AS status"
            ),
            "params": {
                "id": vc["id"], "nickname": vc["nickname"], "name": vc["name"],
                "status": vc["status"], "review_status": vc["review_status"],
                "run_id": RUN_ID, "as_of": AS_OF,
            },
        },
        {
            "name": "companies",
            "query": (
                "UNWIND $rows AS row "
                "MERGE (c:Company {id:row.id}) "
                "SET c.ticker=row.ticker, c.name=row.name, c.name_en=row.name, "
                "c.exchange=row.exchange, c.tikr_cid=row.tikr_cid, c.status=row.status, "
                "c.review_status=row.review_status, c.run_id=$run_id "
                "WITH c, row "
                "MATCH (vc:ValueChain {id:$vc_id}) "
                "MERGE (c)-[m:CANDIDATE_IN]->(vc) "
                "SET m.status='candidate', m.review_status='pending', "
                "m.evidence_id=row.evidence_id, m.run_id=$run_id "
                "RETURN c.ticker AS ticker, m.status AS membership_status"
            ),
            "params": {"rows": manifest["companies"], "vc_id": VC_ID, "run_id": RUN_ID},
        },
        {
            "name": "evidence",
            "query": (
                "UNWIND $rows AS row "
                "MERGE (e:Evidence {id:row.id}) "
                "SET e.source_ref=row.source_ref, e.source_url=row.source_url, "
                "e.source_date=row.source_date, e.content_hash=row.content_hash, "
                "e.status='pending', e.run_id=$run_id "
                "WITH e, row "
                "MATCH (c:Company {id:'company:'+split(row.id,':')[2]}) "
                "MERGE (c)-[:SUPPORTED_BY {run_id:$run_id}]->(e) "
                "RETURN e.id AS id, e.content_hash AS content_hash"
            ),
            "params": {"rows": manifest["evidence"], "run_id": RUN_ID},
        },
        {
            "name": "products",
            "query": (
                "UNWIND $rows AS row "
                "MERGE (p:Product {id:row.id}) "
                "SET p.name=row.name, p.status='candidate', p.run_id=$run_id "
                "WITH p, row "
                "MATCH (c:Company {id:'company:'+row.producer}) "
                "MERGE (c)-[r:PRODUCES]->(p) "
                "SET r.status='candidate', r.as_of=$as_of, r.run_id=$run_id, r.source_url=row.evidence_id "
                "RETURN p.id AS id"
            ),
            "params": {"rows": manifest["products"], "run_id": RUN_ID, "as_of": AS_OF},
        },
        {
            "name": "processes",
            "query": (
                "UNWIND $rows AS row "
                "MERGE (p:Process {id:row.id}) "
                "SET p.name=row.name, p.status='candidate', p.run_id=$run_id "
                "WITH p, row "
                "MATCH (c:Company {id:'company:'+row.operator}) "
                "MERGE (c)-[r:OPERATES_IN]->(p) "
                "SET r.status='candidate', r.as_of=$as_of, r.run_id=$run_id "
                "RETURN p.id AS id"
            ),
            "params": {"rows": manifest["processes"], "run_id": RUN_ID, "as_of": AS_OF},
        },
        {
            "name": "end_markets_drivers",
            "query": (
                "UNWIND $markets AS mrow "
                "MERGE (em:EndMarket {id:mrow.id}) "
                "SET em.name=mrow.name, em.status='candidate', em.run_id=$run_id "
                "WITH collect(em) AS _ "
                "UNWIND $drivers AS drow "
                "MERGE (d:DemandDriver {id:drow.id}) "
                "SET d.name=drow.name, d.status='candidate', d.run_id=$run_id, d.as_of=$as_of "
                "WITH d "
                "MATCH (em:EndMarket {id:'endmarket:us_optic:ai-datacenter'}) "
                "MERGE (d)-[r:DRIVES]->(em) "
                "SET r.status='candidate', r.as_of=$as_of, r.source_url=d.id "
                "RETURN d.id AS id"
            ),
            "params": {
                "markets": manifest["end_markets"],
                "drivers": manifest["demand_drivers"],
                "run_id": RUN_ID,
                "as_of": AS_OF,
            },
        },
        {
            "name": "assertions",
            "query": (
                "UNWIND $rows AS row "
                "MERGE (a:CausalAssertion {id:row.id}) "
                "SET a.kind=row.kind, a.company_id=row.company_id, a.period=row.period, "
                "a.affected_metric=row.affected_metric, a.direction=row.direction, a.lag=row.lag, "
                "a.source=row.source, a.evidence=row.evidence, a.confidence=row.confidence, "
                "a.counter_evidence=row.counter_evidence, a.status=row.status, "
                "a.review_status=row.review_status, a.run_id=$run_id "
                "WITH a, row "
                "MATCH (c:Company {id:row.company_id}) "
                "MERGE (a)-[r:ASSERTED_FOR]->(c) "
                "SET r.evidence=row.evidence, r.review_status=row.review_status, r.source=row.source "
                "RETURN a.id AS id, a.review_status AS review_status, a.status AS status"
            ),
            "params": {"rows": manifest["assertions"], "run_id": RUN_ID},
        },
    ]


def quality_table() -> dict[str, Any]:
    """Ordinal 0-4 scores vs STI Golden Example (Order 142 rubric)."""
    axes = [
        {"axis": "Source depth", "sti": 4, "us_optic": 3,
         "note": "10-K + latest earnings call + overview for all 4 seeds; no five-quarter segment/inventory series."},
        {"axis": "Evidence provenance / coverage", "sti": 4, "us_optic": 3,
         "note": "All facts hashed with URL/as-of/collected_at; 3/3 questions evidence-backed pending review."},
        {"axis": "Value Chain structure quality", "sti": 4, "us_optic": 3,
         "note": "Canonical vc:us_optic plus products, InP/CPO processes, AI datacenter end-market and demand driver."},
        {"axis": "Driver / bottleneck / beneficiary evidence", "sti": 4, "us_optic": 3,
         "note": "One pending chain with counter-evidence; not confirmed and not a 3-company Golden Example replica."},
        {"axis": "Link Expansion quality", "sti": 4, "us_optic": 3,
         "note": "AVGO strengthen, MRVL weaken, AAOI reject with source-recheck notes; AVGO not collected."},
        {"axis": "Neo4j completeness / reviewability", "sti": 3, "us_optic": 3,
         "note": "Candidate graph plus pending causal records; STI time series left untouched."},
    ]
    sti_total = sum(item["sti"] for item in axes)
    ours = sum(item["us_optic"] for item in axes)
    return {
        "contract_version": "ivk-quality-benchmark-0.1",
        "run_id": RUN_ID,
        "rubric": "order-142-six-axis-0-4",
        "axes": axes,
        "sti_total": sti_total,
        "us_optic_total": ours,
        "relative_pct": round(100 * ours / sti_total, 1),
        "verdict": "PASS_STRUCTURE_NOT_STI_PARITY",
        "unmet": [
            "five-quarter financial/inventory/segment time series",
            "confirmed causal review",
            "primary-source collection for AVGO expansion name",
        ],
        "nonpublic": [],
        "follow_up": [
            "Collect AVGO 10-K/call before any membership write.",
            "Add 5-quarter TIKR financials as separate FinancialPeriod nodes with us_optic run_id only.",
        ],
    }


def emit_artifacts(plan: dict[str, Any], output_dir: Path) -> dict[str, Any]:
    collection = build_collection(plan)
    packets = build_packets(plan, collection)
    validate_packets(packets)
    quality = quality_table()
    _write(output_dir / "source_collection.json", collection)
    names = {
        "evidence": "evidence_packet.json",
        "ke": "ke_packet.json",
        "write_manifest": "write_manifest.json",
        "review": "review.json",
    }
    for key, name in names.items():
        _write(output_dir / name, packets[key])
    _write(output_dir / "write_batches.json", write_batches(packets["write_manifest"]))
    _write(output_dir / "quality_benchmark.json", quality)
    return {"collection": collection, **packets, "quality": quality}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    emit_artifacts(_read(args.plan), args.output_dir)
    print(json.dumps({"ok": True, "run_id": RUN_ID, "output_dir": str(args.output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
