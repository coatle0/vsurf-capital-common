# IVK KR Live Neo4j Write Validation — 2026-08-24

## Result

- Run-ID: `IVK-20260824-KR-TSE-WRITE-001`
- Terminal state: `VERIFIED`
- Target: existing `Company {id: "company:tse"}` and a new candidate validation VC
- Source route: KR pack with DART evidence; no TIKR task
- Write scope: one existing Company, one candidate ValueChain, one Evidence node, and their relationships

## Live write and replay

The official Neo4j driver executed the approved `value_chain`, `companies`, and `evidence` MERGE batches. It then replayed the same batches. Both passes returned one row per batch with no failed batch.

Read-back after replay:

- ValueChain count: 1
- candidate members: 1
- complete Evidence nodes: 1/1
- confirmed assertions: 0
- duplicate IDs in the run: 0
- idempotency replay: `PASS`

## Identity read-back

The live database returned exactly one Company matching ticker `131290` or security ID `KR:131290`:

- node ID: `company:tse` (legacy ID reused)
- security ID: `KR:131290`
- ticker: `131290`
- country/exchange: `KR` / `KOSDAQ`
- provider/provider ID: `dart` / `00132757`
- candidate VC membership: 1
- linked validation Evidence: 1

No `company:kr:131290` duplicate was created.

## STI protected-data guard

The post-write live counts match the prior 2026-08-23 validation artifact:

- `FinancialPeriod`: 55
- `InventorySnapshot`: 56
- `SegmentResult`: 148
- `BusinessSegment`: 33
- `MonthlyRevenue`: 18
- `ManagementCommentary`: 6

The validation batch did not target these labels.

## Proof artifacts

- `runs/IVK-20260824-KR-TSE-WRITE-001/write_receipt.json`
- `runs/IVK-20260824-KR-TSE-WRITE-001/readback.json`
- `runs/IVK-20260824-KR-TSE-WRITE-001/write_manifest.json`
- `runs/IVK-20260824-KR-TSE-WRITE-001/verify.json`

## Remaining release gates

This proves the KR existing-node path and live write/replay/read-back behavior. It does not yet prove new-company creation or the JP/TW market paths. Before declaring the multi-market writer generally released, repeat the controlled pilot with one evidence-backed new company in KR and one existing plus one new company in JP and TW. Require exact identity read-back, actual exchange resolution, and duplicate-free replay for every market.
