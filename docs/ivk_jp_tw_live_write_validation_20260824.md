# IVK JP/TW Live Neo4j Write Validation — 2026-08-24

## Result

- Run-ID: `IVK-20260824-JP-TW-WRITE-001`
- Terminal state: `VERIFIED`
- Targets: existing `company:jem` (JP:6855) and `company:winway` (TW:6515)
- Inferred region packs: `jp@1.0.0`, `tw@1.0.0`
- Write scope: two existing Companies, one candidate ValueChain, two official company-profile Evidence nodes, and their relationships

## Source-routing verification

- JP: `tikr`, `jpx`, `company_ir`, `earnings_call`
- TW: `tikr`, `twse_tpex`, `mops`, `company_ir`, `monthly_revenue`

The Intake contains no `market` field and no explicit `--region` was supplied. Both region packs were inferred from `JP:6855` and `TW:6515`.

## Live write and replay

The official Neo4j driver executed the approved `value_chain`, `companies`, and `evidence` MERGE batches and replayed the identical batches.

- first pass: 1 ValueChain row, 2 Company rows, 2 Evidence rows
- replay: the same row counts
- failed batches: 0
- ValueChain count after replay: 1
- candidate members: 2
- complete Evidence nodes: 2/2
- confirmed assertions: 0
- duplicate IDs in the run: 0
- idempotency replay: `PASS`

## Identity read-back

### Japan

- node ID: `company:jem` (legacy ID reused)
- security ID: `JP:6855`
- ticker: `6855`
- country/exchange: `JP` / `TSE`
- official source: `https://www.jem-net.co.jp/en/profile/outline`
- matching Company count by ticker or security ID: 1

### Taiwan

- node ID: `company:winway` (legacy ID reused)
- security ID: `TW:6515`
- ticker: `6515`
- country/exchange: `TW` / `TWSE`
- official source: `https://www.winwayglobal.com/about`
- matching Company count by ticker or security ID: 1

No `company:jp:6855` or `company:tw:6515` duplicate was created.

## STI protected-data guard

Post-write counts remain equal to the prior KR validation and the 2026-08-23 baseline:

- `FinancialPeriod`: 55
- `InventorySnapshot`: 56
- `SegmentResult`: 148
- `BusinessSegment`: 33
- `MonthlyRevenue`: 18
- `ManagementCommentary`: 6

## Proof artifacts

- `runs/IVK-20260824-JP-TW-WRITE-001/write_receipt.json`
- `runs/IVK-20260824-JP-TW-WRITE-001/readback.json`
- `runs/IVK-20260824-JP-TW-WRITE-001/source_plan.json`
- `runs/IVK-20260824-JP-TW-WRITE-001/write_manifest.json`
- `runs/IVK-20260824-JP-TW-WRITE-001/verify.json`

## Remaining release gate

The existing-node paths now pass for KR, JP, and TW. New-company creation remains unproven in live Neo4j. Before general release, run one evidence-backed new-company pilot per non-US market and require country-scoped IDs, actual exchange resolution, duplicate-free replay, and exact provenance read-back.
