Run-ID: RUN-129-01

# Order 129 — IVK Phase 1-B STI v2 blocker closure

## Governance ACTIVE v1.2 preflight

Measured immediately before implementation on 2026-08-15 KST.

| Check | Result |
|---|---|
| Git latest-order | PASS — `129_ivk-phase1b-sti-v2-blocker-closure.md` is the highest canonical order; starting HEAD `d3cbdf7`. |
| Git duplicate | PASS — one `129_*.md`; no duplicated three-digit IDs in `orders/`. |
| Slack active-order | PASS — task `C0BNWS9QKDK-1786769114.198739` exists in claimed state and its outbox is `DISPATCHING` for order 129. |
| Globally unused | PASS at issuance boundary — the only Order 129 Git history/reference was canonical registration commit `d3cbdf7`; no prior report/implementation or competing active number was found. No new order number was created. |

## investment-kg / live Neo4j parity

The four mandated MCP calls were actually executed in the current runtime: `get_company_graph(FormFactor)`, `get_company_graph(티에스이)`, `get_company_graph(WinWay)`, and `trace_demand_driver(HBM)`. Every call returned the MCP error `user cancelled MCP tool call`. The live canonical endpoint remained readable through `neo4j-official`, but direct Neo4j reads are not treated as an MCP substitute. Therefore relation parity is **BLOCKED**, not PASS. The failure occurs before a typed graph payload/path is returned, so endpoint/type/path equality cannot be evaluated and no safe code/DB-target correction can be inferred from this workspace.

The canonical live reads still return the expected company IDs `company:form`, `company:tse`, `company:winway`; HBM exposure is 11/11; the assertion gate is 43 relationships, missing source 0, confirmed 0; duplicate endpoint/type tuples are 0. These measurements establish the live side only.

## Source-less REQUIRES disposition

Live inspection found exactly one source-less edge: `Process(stage:wafer_test)-[:REQUIRES]->Product(product:probe_card)`, with no relationship properties. No existing relationship evidence supported promoting it. Because live writes were prohibited, `data/129_requires_remediation.csv` explicitly marks it `disabled_deferred` and `active_assertion=false`; the active `REQUIRES` read in `queries/127_sti_reconciliation.cypher` now requires both source and evidence, so this edge is excluded from assertions until sourced or removed. It was not confirmed.

## G1 human-decision packet

`data/129_bu030_decision_packet.csv` contains the 12 unresolved Order 127 items (11 deferred plus the rejected Megatouch total). Every row includes recommendation, alternative, adoption impact, defer impact, evidence, and confidence. Two unambiguous rows are deterministic-eligible: Megatouch development-cost rows cannot be taxonomy leaves, and aggregate totals must be rejected. The Micro2Nano footnote rows have deterministic normalization guidance but remain human decisions because period-specific identity must be retained. Ambiguous business taxonomy remains unconfirmed.

## Causal migration dry-run and prototype replay

`migration_dry_run()` validates all required `EarningsDriverLink`, `Bottleneck`, and `BeneficiaryAssessment` fields, epistemic/review status, source/evidence, confidence and counter-evidence; rejects duplicate IDs and accepted inference/hypothesis; and emits an ID-scoped rollback plan without a live write. The nine prototype records yield write count 9, rollback count 9, duplicate 0, auto-confirm 0.

`queries/129_causal_chain_dry_run.cypher` is a read-only replay template for the three companies. It returns Demand Driver and graph expansion sources/status alongside causal kind (Earnings Driver/Bottleneck/Beneficiary), metric, causal evidence, epistemic/review status, confidence, and counter-evidence. Link Expansion is exposed through sourced process/product collections. The data provides all requested stages, though live MCP reproduction remains blocked as above.

## Golden Example gates

| Gate | Result | Exact blocker / evidence |
|---|---|---|
| Relation parity | BLOCKED | All four real investment-kg calls cancelled before payload; live reads cannot substitute. |
| G1 decision readiness | PASS | 12/12 decision rows complete; two deterministic-eligible; ambiguous rows remain deferred. |
| HBM coverage | PASS | Live Neo4j 11/11 with source. |
| Causal schema readiness | PASS | Dry-run/rollback and validation guards pass; no live write. |
| Source coverage | PASS | Active assertions missing source/evidence 0; source-less REQUIRES explicitly excluded/disabled. |
| Duplicate 0 | PASS | Live endpoint/type duplicates 0; prototype IDs duplicate 0. |
| Auto-confirm 0 | PASS | Live confirmed 0; prototype unsupported accepted count 0. |

## Phase 1-C entry decision

**FAIL / NOT READY.** The next step is `STI Discovery/Expansion Loop 1회 완주`, but its mandatory relation-parity gate is BLOCKED. Source-less-edge treatment and causal migration dry-run pass. The remaining pure human G1 taxonomy decisions do not need to block a new Pack by themselves because they are isolated, explicitly deferred, and excluded from confirmed rollups; however, no expansion may begin until investment-kg parity passes.

## Validation

- `python -m unittest -v tests.test_ivk_v2` — PASS, 5 tests.
- Live `neo4j-official` canonical reads — PASS for HBM 11/11, active missing source 0, duplicate 0, confirmed 0; one source-less REQUIRES identified.
- investment-kg four-call parity — BLOCKED; all four actual calls cancelled and were not bypassed.

## Changed files

- `scripts/ivk_v2.py`
- `tests/test_ivk_v2.py`
- `queries/127_sti_reconciliation.cypher`
- `queries/129_causal_chain_dry_run.cypher`
- `data/129_requires_remediation.csv`
- `data/129_bu030_decision_packet.csv`
- `reports/129_report.md`

No commit or push was performed; dispatcher owns Git finalization.
