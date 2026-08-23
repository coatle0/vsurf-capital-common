# us_optic IVK Factory E2E

- Run-ID: `IVK-20260823-US-OPTIC-E2E-001`
- Date: 2026-08-23
- Executor: Grok / PC2
- Result: **PASS with stated quality limits**

## Purpose

Use `us_optic` as a new Value Chain to run IVK Intake through governed Neo4j registration. STI was not repaired first. Power Semiconductor VC was not recreated.

## Input (ORDER)

- nickname: `us_optic`
- seed: NVDA, COHR, LITE, CRDO
- frame: Sponsor → Value Chain → Bottleneck (`sponsor_valuechain_bottleneck@1.0.0`)
- thesis: AI datacenter optical/CPO expansion creates optical-component, DSP, laser, and packaging bottlenecks and beneficiaries

Existing PLANNED run `IVK-20260823-US-OPTIC-001` was **not reused** as the execution snapshot: it is the GS `optic_idx` intake (LITE/CRDO/COHR/AAOI, `matrix`). It remains on disk unchanged.

## Path

`Intake validate → Normalize → neo4j-official.read_cypher → Blueprint → Source Plan → Source Collection → Evidence Packet → KE → review gate → write-cypher → read-back → second MERGE → quality table`

## Collection

12 primary-source documents (3 per seed):

| Ticker | Overview | 10-K | Earnings call |
|---|---|---|---|
| NVDA | tikr.company_overview | 0001045810-26-000021 (2026-02-25) | Q1 FY2027, 2026-05-20 |
| COHR | tikr.company_overview | 0000820318-26-000020 (2026-08-14) | Q4 FY2026, 2026-08-12 |
| LITE | tikr.company_overview | 0001628280-26-057358 (2026-08-17) | Q4 FY2026, 2026-08-11 |
| CRDO | tikr.company_overview | 0001628280-26-043303 (2026-06-15) | Q4 FY2026, 2026-06-01 |

Every fact has `source_ref`, `source_url`, `source_date`, `collected_at`, SHA-256 `content_hash`. `auto_confirm=false`.

## KE / review

- Canonical `(:ValueChain {id:'vc:us_optic', nickname:'us_optic'})` status=`candidate`
- 4 candidate companies, 8 products, 2 processes, 1 end-market, 1 demand driver
- 3 pending causal records (driver / bottleneck / beneficiary), each with counter-evidence
- Confirmed assertions: **0**
- Questions: all three `evidence-backed` (pending review, not confirmed)
- Link expansion: AVGO **strengthen** (not written), MRVL **weaken**, AAOI **reject**

Bottleneck (hypothesis, pending): 6-inch InP / EML / high-power laser-chip supply.
Beneficiaries (hypothesis, pending): LITE laser chips and COHR CPO/InP ramp; CRDO CPO/NPO guided to FY2028.

## Neo4j read-back

| Check | Result |
|---|---|
| `vc:us_optic` | 1, nickname `us_optic` |
| seed companies | NVDA, COHR, LITE, CRDO |
| membership | `CANDIDATE_IN` status=`candidate`, review=`pending` |
| Evidence | 12, all `SUPPORTED_BY` linked |
| Products / processes | 8 / 2 us_optic-prefixed |
| CausalAssertion | 3 us_optic pending + 3 STI WinWay intact |
| duplicates | none |
| orphans | none |
| confirmed assertions | 0 |
| second MERGE | companies=4, memberships=4, label counts unchanged |

### STI protected counts (pre = post)

| Label | Count |
|---|---:|
| FinancialPeriod | 55 |
| InventorySnapshot | 56 |
| SegmentResult | 148 |
| BusinessSegment | 33 |
| MonthlyRevenue | 18 |
| ManagementCommentary | 6 |
| CapacityExpansion | 3 |

STI companies (leeno/tse/winway/FORM/…) remain. No VRT/ETN/VST/ON/WOLF write.

## Quality vs STI (Order 142 rubric)

| Axis | STI | us_optic |
|---|---:|---:|
| Source depth | 4 | 3 |
| Evidence provenance / coverage | 4 | 3 |
| Value Chain structure | 4 | 3 |
| Driver / bottleneck / beneficiary | 4 | 3 |
| Link Expansion | 4 | 3 |
| Neo4j completeness / reviewability | 3 | 3 |
| **Total** | **23** | **18 (78.3%)** |

Verdict: `PASS_STRUCTURE_NOT_STI_PARITY`.

Unmet: five-quarter segment/inventory series; confirmed causal review; AVGO primary-source collection.

## Tests

```
python -m py_compile scripts\ivk_us_optic_e2e.py tests\test_us_optic_e2e.py
python -m unittest tests.test_us_optic_e2e tests.test_ivk_new_intake tests.test_ivk_phase1_dry_run tests.test_ivk_factory -v
```

`tests.test_us_optic_e2e` 4/4 PASS. Related IVK tests 23/23 PASS after the power-string assertion fix.

## Artifacts

- `examples/us_optic_e2e_intake.json`
- `runs/IVK-20260823-US-OPTIC-E2E-001/`
- `scripts/ivk_us_optic_e2e.py`
- `tests/test_us_optic_e2e.py`

## Limits

- No us_optic FinancialPeriod / inventory / segment nodes were written (STI time series left untouched).
- AVGO was not collected or registered as a member.
- Causal records are inference/hypothesis + pending, not accepted.
