Run-ID: RUN-127-01

# Order 127 — IVK Phase 1-A STI v2 foundation

## Governance v1.2 preflight

Measured before implementation on 2026-08-15 KST.

| Check | Result |
|---|---|
| Git latest-order | PASS — `127_ivk-phase1a-sti-v2-foundation.md` is the highest numbered canonical order; HEAD at start was `667e0ef`. |
| Git duplicate | PASS — exactly one `127_*.md`; no duplicated three-digit order IDs. |
| Slack active-order | PASS — task `C0BNWS9QKDK-1786767575.296789` exists in claimed and outbox state, and outbox status was `DISPATCHING` for order 127. |
| Globally unused | PASS at issuance boundary — repository search before outputs found no Order 127 implementation/report references outside the canonical order. No new order number was allocated. |

## Relationship source of truth and reconciliation

The measured live Neo4j database is the current relationship source of truth. Its schema and assertion properties are directly readable through `neo4j-official`. The `investment-kg` read path is intended to query that same database, but all four attempted reads (`get_company_graph` for FormFactor, 티에스이, WinWay and `trace_demand_driver(HBM)`) returned `user cancelled MCP tool call`; therefore endpoint-by-endpoint equality could not be re-measured or changed in this workspace. This is the unresolved synchronization blocker, not evidence that either graph result is correct.

`queries/127_sti_reconciliation.cypher` defines the canonical live reads that the adapter must mirror: 11-company HBM exposure, HBM process/product/component coordinates, evidence and auto-confirm gates, and duplicate detection. It avoids loader changes and unsupported relationship creation. Live sample resolution found `company:form`, `company:tse`, and `company:winway`; the HBM→Wafer Test Cell→Probe Card path exists, including `샘씨엔에스 → Ceramic STF → Probe Card`. The earlier apparent 샘씨엔에스 gap was a query-shape artifact: a direct Product-only check omitted the valid Component→Product route.

Live assertion measurements: 43 assertion-bearing relationships across DRIVES/EXPOSED_TO/OPERATES_IN/PRODUCES/PART_OF/COMPETES_WITH; source/evidence missing 0; endpoint/type duplicates 0; status `confirmed` 0. A separate `REQUIRES` edge has no source and is intentionally excluded from assertion use pending remediation.

## G1 taxonomy review packet

`data/127_bu030_taxonomy_review.csv` contains 33/33 live BusinessSegment rows with current label, proposed taxonomy, evidence, recommended decision, reason, rollup, and special-case marker. Recommendations are 21 accepted, 11 deferred, and 1 rejected; these are review recommendations, not database confirmations.

The required unresolved categories are individually marked: Yamaichi Test Solution; WinWay Optoelectronic Products Test Fixtures; Yamaichi Optical and JEM Electron Tube; generic Other rows; Micro2Nano note rows 1 and 2; and the rejected Megatouch total row. Human owners must decide every deferred row before loading.

## IVK v2 causal model and prototype

`scripts/ivk_v2.py` implements validated `EarningsDriverLink`, `Bottleneck`, and `BeneficiaryAssessment` records preserving period, affected metric, direction, lag, source, evidence, confidence, counter-evidence, epistemic status, and review status. It rejects missing evidence, duplicate IDs, invalid confidence/status, and accepted inference/hypothesis records. `queries/127_ivk_v2_schema.cypher` is the executable review-gated migration/loader/read template; it was not applied to live Neo4j because approval was not provided.

`data/127_causal_prototypes.json` contains nine records (three kinds × three companies), all pending and source-bearing. DB facts are quoted as facts inside each evidence field; causal effects and bottlenecks remain inference/hypothesis.

| Company | Demand driver → earnings/metric | Bottleneck candidate | Beneficiary assessment | Counter-evidence |
|---|---|---|---|---|
| FormFactor | HBM exposure → inferred revenue effect; 2026Q1 revenue 226.144 | Probe-card availability, hypothesis | Operating-income benefit, inference | NAND and Foundry/Logic exposures prevent isolation. |
| 티에스이 | HBM/Wafer Test Cell/Probe Card → inferred revenue effect; 2026Q1 revenue 150671280313 | Probe-card availability, hypothesis | Operating-income benefit, inference | Test Socket/Interface Board mix; no product profit split. |
| WinWay | HBM exposure/Test Socket/Vertical Probe Card → inferred revenue effect; 2026Q1 revenue 2980.415 | Interface availability, hypothesis | Operating-income benefit, inference | No canonical Wafer Test Cell edge or product profit split. |

Link Expansion frontiers are candidates only: FormFactor—Product `Probe Card`, EndMarkets NAND and Foundry/Logic, adjacent JEM/Micronics; 티에스이—Products Test Socket/Interface Board, Process Wafer Test Cell, adjacent FormFactor/Micro2Nano; WinWay—Products Vertical Probe Card/Test Socket and HBM EndMarket. Their relationship sources are preserved in the prototype evidence/counter-evidence; no candidate is confirmed and no unsupported edge was written. No Capacity or Technology candidate was asserted because the existing graph supplied no adequate source.

## HBM 11-company coverage

Live Neo4j returns 11/11 companies with sourced `EXPOSED_TO → DRAM / HBM`: FormFactor, Japan Electronic Materials, MPI, Micronics Japan, WinWay, Yamaichi, 리노공업, 마이크로투나노, 메가터치, 샘씨엔에스, 티에스이. Only MPI, 마이크로투나노, and 티에스이 have direct `OPERATES_IN → Wafer Test Cell`; this narrower 3/11 coordinate is reported rather than filled with unsupported edges. Six companies directly produce canonical `Probe Card`; WinWay produces `Vertical Probe Card`; 샘씨엔에스 reaches Probe Card through sourced `Ceramic STF → PART_OF → Probe Card`.

## Validation and measured results

- `python -m unittest tests.test_ivk_v2` — validates 33 rows, required special cases, three-company/three-kind causal coverage, evidence completeness, duplicate zero, and the no-auto-accept guard.
- `python -m unittest discover -s tests -p 'test_*.py'` — repository-wide attempt reached the existing suite but exceeded the 120-second command budget after six additional tests; it is not counted as a pass.
- Live read queries — 11 Company nodes, 33 BusinessSegment nodes, HBM exposure 11/11, core assertion missing-source 0, duplicates 0, confirmed 0.
- `investment-kg` parity calls — blocked/cancelled as described above; not counted as passing.

## Changed files

- `scripts/ivk_v2.py`
- `tests/test_ivk_v2.py`
- `queries/127_sti_reconciliation.cypher`
- `queries/127_ivk_v2_schema.cypher`
- `data/127_bu030_taxonomy_review.csv`
- `data/127_causal_prototypes.json`
- `reports/127_report.md`

## Remaining human decisions / Phase 1-B blockers

1. Resolve the 12 deferred taxonomy recommendations; no recommendation was loaded or confirmed.
2. Re-enable/authorize `investment-kg` reads, confirm its database/configuration target, and run exact sample parity against the canonical Cypher output.
3. Decide whether the source-less `REQUIRES` edge should receive existing evidence or be removed; do not use it as an assertion meanwhile.
4. Approve migration application and causal review workflow before any live write.
5. Capacity/Technology frontier expansion needs existing sourced records; this order did not collect new external data.

No commit or push was performed; dispatcher owns Git finalization.
