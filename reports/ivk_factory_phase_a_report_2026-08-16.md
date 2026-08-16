# IVK Factory Phase A Implementation Report

- Run-ID: `IVK-FACTORY-A-20260816-01`
- Result: **PASS**
- Scope: Pack Registry, Global Evidence Store, Token Ledger, Blueprint → Source Plan

## Implemented

### Versioned Pack Registry

- Independent Frame, Sector, and Region packs
- Alias resolution and compatibility validation
- Exact pack versions persisted in every Source Plan
- Initial composition: `sponsor_valuechain_bottleneck@1.0.0` + `semiconductor_optical@1.0.0` + `us@1.0.0`

### Global Evidence Store

- SQLite standard-library implementation
- SHA-256 content deduplication across Value Chains
- Separate source-occurrence provenance when identical content appears at multiple URLs
- Document sections and extractor-version result cache
- No credential or source body committed

### Token Ledger

- Run/Value Chain/stage/model usage records
- Input, cached input, output, document, fact, retry counters
- Non-negative and cached-input validation
- Per-stage budget status and exceed gate

### Blueprint → Source Plan

- Consumes `ivk-blueprint-1.0`
- Retains unresolved seeds as entity-resolution tasks
- Generates per-seed evidence-collection and per-question evidence tasks
- Binds region-specific source adapters
- Enforces primary-source-first, content-hash reuse, official Neo4j read, and `auto_confirm=false`
- Emits machine-readable `ivk-source-plan-1.0`

## E2E Result

Input: `artifacts/140_ai_optical_cpo_blueprint.json`

Output: `artifacts/140_ai_optical_cpo_source_plan.json`

Measured result:

- validated seed count: 4
- unresolved entity-resolution tasks: 4
- total source tasks: 11
- pack manifest: Frame/Sector/US versions fixed
- configured total stage budget: 85,000 tokens
- auto-confirm: false
- LLM calls in Phase A: 0
- Neo4j writes in Phase A: 0

## Files

- `scripts/ivk_factory.py`
- `registry/ivk_factory_packs.json`
- `packs/frames/sponsor_valuechain_bottleneck.json`
- `packs/sectors/semiconductor_optical.json`
- `packs/regions/us.json`
- `schemas/ivk_source_plan.schema.json`
- `artifacts/140_ai_optical_cpo_source_plan.json`
- `tests/test_ivk_factory.py`
- `docs/ivk_factory_phase_a.md`

## Validation

- IVK Factory + Intake + IVK v2 + Neo4j wrapper focused regression: **17/17 PASS**
- Python compile: **PASS**
- Source Plan JSON Schema validation: **PASS**
- Pack JSON parsing: **PASS**
- CLI E2E generation: **PASS**
- `git diff --check`: **PASS**

## Isolation

The following pre-existing or separately generated working-tree items were excluded from this implementation and must not be included in its commit:

- `scripts/order_inbox_consumer.py`
- `tests/test_order_inbox_consumer.py`
- `docs/hermes_grok_integration_plan.md`

The previously authored IVK architecture review document is included as Phase A design context:

- `docs/IVK_CURRENT_STATE_AND_EXTENSIBLE_FACTORY_REVIEW_2026-08-16.md`

## Next Gate

Phase B should add Blueprint/Source Plan-driven source adapters and Evidence Packet extraction, beginning with the existing STI Golden Example. It must reuse the Evidence Store, record every LLM call in the Token Ledger, and stop at budget or review gates rather than auto-confirming causal claims.
