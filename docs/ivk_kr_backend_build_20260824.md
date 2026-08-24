# IVK Korea Backend Ecosystem Build — 2026-08-24

## Result

- Intake: `intakes/new/kr_후공정.json`
- Run-ID: `IVK-20260824-KR-BACKEND-BUILD-001`
- Terminal state: `VERIFIED`
- Live Neo4j write: completed
- Idempotency replay: `PASS`

## Source and routing

All five companies were resolved with live DART company-overview calls. The inferred region pack is `kr@1.0.0`. Every seed task uses `dart` and `company_ir`; no TIKR adapter is present.

The requested `semiconductor_backend` sector does not yet have a reusable pack, so this run used `bootstrap_semiconductor_backend@0.0.0` with the `matrix@1.0.0` frame. This is a structural onboarding build, not an STI-grade enrichment run.

## Neo4j results

- ValueChain: `vc:korea-backend-ecosystem`
- Company members: 5
- complete Evidence: 5/5
- confirmed assertions: 0
- duplicate IDs: 0
- failed batches: 0

Existing identity reused:

- `KR:131290` 티에스이 → `company:tse`

New country-scoped identities created:

- `KR:131970` 두산테스나 → `company:kr:131970`
- `KR:183300` 코미코 → `company:kr:183300`
- `KR:059090` 미코 → `company:kr:059090`
- `KR:330860` 네패스아크 → `company:kr:330860`

Direct live read-back found exactly one Company per ticker/security ID. Each Company has KOSDAQ exchange metadata, DART provider/corporate ID, one candidate membership, and one linked Evidence node.

## Protected-data guard

Post-write counts remained unchanged:

- `FinancialPeriod`: 55
- `InventorySnapshot`: 56
- `SegmentResult`: 148
- `BusinessSegment`: 33
- `MonthlyRevenue`: 18
- `ManagementCommentary`: 6

## Quality boundary and next work

The build proves Intake normalization, KR routing, one legacy-ID reuse, four new Company creations, provenance, live write, replay, and duplicate prevention. It deliberately does not create unsupported products, processes, drivers, bottlenecks, beneficiaries, financial periods, segments, inventory, or CAPEX facts.

To reach STI quality, create a reusable `semiconductor_backend` sector pack and run the source-collection/enrichment gates for five-quarter financials, segment results, inventory, CAPEX, company products/processes, end markets, counter-evidence, and reviewed causal links.

## Proof artifacts

- `runs/IVK-20260824-KR-BACKEND-BUILD-001/write_receipt.json`
- `runs/IVK-20260824-KR-BACKEND-BUILD-001/readback.json`
- `runs/IVK-20260824-KR-BACKEND-BUILD-001/source_plan.json`
- `runs/IVK-20260824-KR-BACKEND-BUILD-001/write_manifest.json`
- `runs/IVK-20260824-KR-BACKEND-BUILD-001/verify.json`
