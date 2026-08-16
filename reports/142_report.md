# Order 142 — STI vs Power Semiconductor quality-gap benchmark

- Run-ID: `ORDER-142-BENCHMARK-01`
- Date: 2026-08-16
- Verdict: **FAIL — Power Semiconductor does not meet STI Golden Example quality parity**
- Scope: quality diagnosis only; the Order 141 E2E transport PASS is not reversed.

## Executive finding

Order 141 successfully moved a new intake through Blueprint, planning, collection, evidence hashing, KE, governed Neo4j write, and review. Its usable output, however, stops at five sourced company identities and candidate ValueChain memberships. The STI Golden Example contains primary filings/calls, five-quarter and segment/product evidence, three reviewable causal chains, counter-evidence, and three source-rechecked expansion frontiers. Power Semi therefore scores **5/24 versus STI 23/24**, or **21.7% of the STI baseline** under the equal-weight six-axis rubric.

The gap is not a missing Sector Pack. The immediate causes are (1) planned deep sources were not executed, and (2) the full-path contracts permit KE/review to complete without causal or discovery-loop outputs.

## Evidence boundary and scoring

Scores use one anchored ordinal scale: 0 absent; 1 identity/bootstrap only; 2 partial structure/coverage; 3 decision-useful with material gaps; 4 evidence-linked representative loop complete. Relative quality is `Power / STI × 100`; no item required N/A because both test cases expose comparable investment questions. Counts alone do not earn quality credit.

STI evidence is taken from `data/127_causal_prototypes.json`, `data/132_discovery_loop.json`, `reports/127_report.md`, and `reports/132_report.md`. Power evidence is taken from the Order 141 Blueprint, source/evidence/KE/write/review artifacts and `reports/141_phase1_full_path_report.md`. No missing STI content was inferred.

Fresh read-only Neo4j evidence on 2026-08-16 returned 358 nodes and 378 relationships globally. STI has 11/11 sourced `EXPOSED_TO → DRAM / HBM` edges and three pending, evidence-bearing `CausalAssertion` nodes for WinWay. Power Semi has five companies, five Evidence nodes, and five `CANDIDATE_IN` memberships; each membership has `status=candidate`, `review_status=pending`, and an evidence ID. It has no semantic/causal chain. The relationship uses property `status`, not `membership_status`; the report treats that as the actual contract.

## Six-axis benchmark

| Axis | STI | Power | Relative | Evidence-based finding |
|---|---:|---:|---:|---|
| Source depth | 4 | 1 | 25.0% | STI: filings, earnings-call/issuer commentary, five-quarter financial/inventory and segment/product data for three companies. Power: five `company_overview` documents only. |
| Evidence provenance / coverage | 4 | 2 | 50.0% | Both preserve provenance and pending status. STI covers causal fields and counter-evidence; Power hashes all identity evidence but leaves 4/4 questions pending. |
| Value Chain structure quality | 4 | 1 | 25.0% | STI links demand→test process→product/component→constraint→earnings. Power has a bootstrap VC and memberships; Blueprint nodes/links/analytical slots are empty. |
| Driver / bottleneck / beneficiary evidence | 4 | 0 | 0% | STI has 3/3 representative chains with falsifiers. Power KE `assertions=[]`; review explicitly defers these claims. |
| Link Expansion quality | 4 | 0 | 0% | STI has three connected frontiers with two strengthen and one weaken rechecks. Power has a planned question and empty frontier only. |
| Neo4j completeness / reviewability | 3 | 1 | 33.3% | STI has sourced semantic paths and a live WinWay causal pilot, but not all three structured chains live. Power graph is reviewable only at identity/membership level. |

## Required coverage check

| Coverage | STI | Power Semi |
|---|---|---|
| Filing / earnings call | Covered for representative companies | Absent |
| Segment / financial time series | Five-quarter plus segment/product metrics | Absent |
| Earnings driver | 3/3 representative chains | 0 |
| Bottleneck | 3/3 with counter-evidence | 0 |
| Beneficiary | 3/3 with falsification conditions | 0 |
| Counter-evidence | Every representative chain | 0 |
| Link expansion | 3 rechecked frontiers | Planned question only |
| Human-review readiness | Structured pending records are reviewable | Identity/membership reviewable; 4 analytical questions pending |

## Quality gap matrix

| Direction | Element | Primary cause | Evidence |
|---|---|---|---|
| STI present, Power absent | filing/call and multi-quarter depth | Evidence depth | `data/132_discovery_loop.json`; Order 141 full-path limits |
| STI present, Power absent | governed driver/bottleneck/beneficiary plus counter-evidence | Factory/contract | STI chains versus Power KE empty assertions |
| STI present, Power absent | connected expansion frontier and source recheck decision | Factory/contract | Order 132 expansion loop versus Power empty frontier |
| Power improved over STI | one deterministic NEW→write artifact chain with content hashes and write manifest | Test-case/process difference | Order 141 full-path artifacts |
| Power improved over STI | all five cold-start seeds resolved and written as candidate memberships in one run | Test-case/process difference | Order 141 review plus fresh graph read-back |

The cold-start versus matured-Golden-Example difference explains part of the absolute depth gap. It does not make the missing fields incomparable: both Blueprints ask for drivers, bottlenecks, beneficiaries, and link expansion, so zeros are warranted rather than N/A.

## Root-cause classification

- **Factory/contract:** the full path has no required output contract for causal records, counter-evidence, expansion decisions, or analytical review completeness. It can finish with candidate identities alone.
- **Evidence depth:** Order 141's plan named SEC, company IR, and earnings calls, but execution collected only TIKR company overviews.
- **Test-case difference:** STI accumulated maturity across Orders 127–132, while Power Semi is a first cold-start run. This affects fairness of absolute totals, not the observed decision-readiness gap.

## Phase 2 top-three minimal priorities

1. **Make thesis-question coverage an execution/stop gate.** Each question must have primary-source evidence or an explicit blocked result before KE/review passes. This prevents identity-only completion without requiring a new Sector Pack.
2. **Emit at least one governed causal review record per supported chain.** Reuse existing IVK v2 fields for driver, bottleneck, beneficiary, counter-evidence, confidence, epistemic status, and review status. Live confirmation is not required.
3. **Close one evidence-led link-expansion recheck.** Pick one connected frontier, state the missing source, re-read a primary source, and record strengthen/weaken/reject.

These are the smallest changes with E2E leverage. Reproducing all STI content is not the goal.

## Sector Pack and limits

Sector Pack is **not a prerequisite**. Useful follow-up material from the dry run is limited to role taxonomy (power equipment/generation/semiconductor), SiC device/material vocabulary, and the grid→distribution→UPS/conversion→load path.

Limits: STI evidence spans multiple orders rather than one cold-start run; only WinWay's causal pilot is live in Neo4j; no external refresh or Neo4j write was performed; ordinal scores are transparent review judgments, not statistical estimates.

## Validation and disposition

The machine-readable source of truth is `artifacts/142_quality_gap_benchmark.json`. Its structure, totals, evidence paths, top-three cardinality, and verdict are validated locally. Repository JSON parsing and `git diff --check` are also required before handoff.

**Final disposition: FAIL for STI quality parity; PASS for producing the requested evidence-linked benchmark and priorities.**
