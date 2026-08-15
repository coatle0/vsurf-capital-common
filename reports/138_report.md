Run-ID: RUN-138-02

# Order 138 — IVK WinWay live E2E write validation

## Result

**PASS.** The previously cancelled Neo4j write was rerun against the configured
local canonical database using the official Neo4j Python driver from the
`neo4j-official` MCP virtual environment. The existing parameterized,
idempotent loader in `queries/133_winway_live_pilot.cypher` and the unchanged
three-row payload in `data/133_winway_live_pilot.json` were used.

The active chat runtime did not expose the `neo4j-official` MCP tool namespace,
so the write was performed through the equivalent Bolt driver path to the same
URI/database. No credentials were written to files or logs.

## Live counts

| Measure | Baseline | After first write | After identical rerun |
|---|---:|---:|---:|
| Total nodes | 344 | 347 | 347 |
| Total relationships | 365 | 368 | 368 |
| `CausalAssertion` nodes | 0 | 3 | 3 |
| `ASSERTED_FOR` relationships | 0 | 3 | 3 |
| Pilot assertion IDs present | 0 | 3 | 3 |

The first write produced the expected `+3` nodes and `+3` relationships. The
second identical write produced no count change, proving idempotency.

## Live readback

| ID | Type | Company | Status | Review | Source/evidence |
|---|---|---|---|---|---|
| `133-winway-earnings-driver` | `EarningsDriverLink` | `company:winway` | inference | pending | present on node and relationship |
| `133-winway-capacity-bottleneck` | `Bottleneck` | `company:winway` | inference | pending | present on node and relationship |
| `133-winway-beneficiary` | `BeneficiaryAssessment` | `company:winway` | inference | pending | present on node and relationship |

All three records retain the issuer source
`https://www.winwayglobal.com/zh-TW/news-detail/KBKS8WFigLqhZKba`, their original
evidence text, and the unchanged epistemic/review states.

## Integrity validation

| Check | Result |
|---|---:|
| Pilot nodes | 3 |
| Duplicate assertion/company groups | 0 |
| Orphan assertions | 0 |
| Missing source or evidence | 0 |
| Wrong company mappings | 0 |
| Unsupported inference/hypothesis auto-confirm | 0 |
| Second-write count delta | 0 |

## Validation path

- Input: unchanged Order 133 JSON payload, 3/3 admissible records.
- Write: parameterized `UNWIND` + guarded `MERGE`, scoped to the three WinWay IDs.
- Readback: assertion ID, kind, company endpoint, node/relationship source and
  evidence, epistemic status, and review status.
- Integrity: duplicate, orphan, source/evidence, mapping, and unsupported
  auto-confirm checks.
- Idempotency: identical write executed twice; second run left all counts stable.

## Closure

The approval-cancellation blocker is resolved and the Order 138 live E2E DoD is
satisfied. Follow-on Intake/Blueprint work may proceed from this validated pilot.
