# us_optic correction + IVK Lifecycle CLI

- Follow-up to `IVK-20260823-US-OPTIC-E2E-001`
- Date: 2026-08-23
- Executor: Grok / PC2
- Result: **PASS with stated limits**

## Order read

`#vsurf-code-reports` `ts` 1787456233.560929.  
`[EXECUTE FOLLOW-UP — Grok | us_optic 교정 + IVK Lifecycle CLI 일반화]`

## Corrections

1. AVGO decision: `strengthen` → `candidate_pending_source`. No Broadcom 10-K/call was collected, so it is not re-judged as strengthen.
2. Live Evidence 12/12 now have `source_url`, `content_hash`, `collected_at`, `source_type`, `publisher`.
3. Product, Process, EndMarket, DemandDriver now `CANDIDATE_IN` `vc:us_optic`. Canonical query returns Company+Product+Process+EndMarket+DemandDriver; members=16; `ValueChain` count=1.

## Public Lifecycle CLI

New stages in `python -m ivk`: `collect`, `ke`, `review`, `write`, `verify`, `enrich`, `benchmark`, `repair`.

Common logic lives in `ivk/lifecycle.py`. No `us_optic` / ticker / optical literals in that module or `ivk/cli.py`.

us_optic JSON was replayed through the public CLI. Dedicated `scripts/ivk_us_optic_e2e.py` is no longer required for the path.

## Fixture generalization

Independent synthetic VC `fixture_demo` (AAA/BBB) ran `new → collect → ke → review → write → verify` in a temp runs-dir. Live Neo4j write was not executed. Status `VERIFIED`.

## Financial enrichment

TIKR financials for NVDA/COHR/LITE/CRDO stored in `financial_enrichment.json` (20 reported periods: annual-dominant + latest quarter). Segment payload empty → `blocked-with-reason`. No STI `FinancialPeriod` nodes written.

## Causal fields

Each us_optic assertion now has supporting evidence, counter-evidence, falsifier, confidence, applicable period. All remain `pending`. Confirmed=0.

## Neo4j / STI

| Check | Result |
|---|---|
| vc:us_optic count | 1 |
| Evidence completeness | 12/12 |
| structure membership | 16 members |
| CausalAssertion | 3 us_optic pending + 3 STI WinWay intact |
| FinancialPeriod / Inventory / SegmentResult | 55 / 56 / 148 unchanged |
| second MERGE | Product n=8 unchanged |
| Power Semi | not recreated |

## Independent STI rescore (0-4)

| Axis | STI | us_optic |
|---|---:|---:|
| Source depth | 4 | 3 |
| Evidence provenance / coverage | 4 | 3 |
| Value Chain structure | 4 | 3 |
| Driver / bottleneck / beneficiary | 4 | 3 |
| Link Expansion | 4 | 2 |
| Neo4j completeness / reviewability | 3 | 3 |
| **Total** | **23** | **17 (73.9%)** |

Link Expansion fell from 3 to 2 because AVGO was corrected off `strengthen`.

## Tests

`python -m unittest tests.test_ivk_lifecycle tests.test_ivk_kernel tests.test_us_optic_e2e tests.test_ivk_new_intake tests.test_ivk_factory tests.test_ivk_phase1_dry_run -v` — **29/29 PASS**

## Limits

- TIKR financials payload is not a true 5-quarter series.
- Segment/inventory detail nodes were not written (STI counts protected).
- AVGO remains pending source.
- Causal records are not confirmed.
