# IVK Factory Phase A

Phase A turns an `ivk-blueprint-1.0` artifact into a versioned `ivk-source-plan-1.0` without collecting sources or calling an LLM.

## Components

- `PackRegistry`: composes independently versioned Frame, Sector, and Region packs and rejects unsupported selections.
- `EvidenceStore`: SQLite document/section store with SHA-256 deduplication, source-occurrence provenance, and extractor-version cache reuse across Value Chains.
- `TokenLedger`: records stage/model token counters and evaluates per-stage budget gates.
- `build_source_plan`: creates entity-resolution, evidence-collection, and question-evidence tasks from a Blueprint.

## Example

```powershell
python scripts\ivk_factory.py plan artifacts\140_ai_optical_cpo_blueprint.json `
  --registry registry\ivk_factory_packs.json `
  --sector semiconductor_optical --region us `
  --output artifacts\140_ai_optical_cpo_source_plan.json
```

The plan retains unresolved seeds, binds every run to exact pack versions, sets source adapters, and enforces `auto_confirm=false`. It is the input contract for later Source Collection and Knowledge Engineering phases.

Phase A does not fetch sources, invoke an LLM, approve hypotheses, or write to Neo4j.
