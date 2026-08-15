# IVK NEW Intake → Blueprint contract

`scripts/ivk_new_intake.py` validates an intake JSON, normalizes seed identifiers, combines it with an official Neo4j read snapshot, and emits a Knowledge Engineering-ready Blueprint JSON.

Required input fields are `name`, `seed`, `frame`, and `thesis`. `questions` is recommended; `known_links`, `limitations`, and `references` are optional arrays. Unknown fields, missing or blank required values, an empty seed array, normalized duplicate seeds, non-string entries, and malformed field types are rejected with `IntakeValidationError`. The Blueprint retains `raw_input` alongside `normalized`.

Existing graph reads must use `neo4j-official.read_cypher`. Call `existing_graph_query()` with `params={"seeds": [...]}` and save the returned row array as JSON. The CLI deliberately accepts only this captured result; it does not fall back to an investment-kg API or write to Neo4j.

Example:

```powershell
python scripts/ivk_new_intake.py examples/140_ai_optical_cpo_intake.json --graph-results examples/140_ai_optical_cpo_graph.json --output artifacts/140_ai_optical_cpo_blueprint.json
```

The Blueprint separates live `graph_observation` findings from `hypothesis` slots. All candidate and overall review states begin `pending`; `epistemic_policy.auto_confirm` is always false. Seeds absent from the graph are retained as starting points under `unresolved_seeds`, not excluded as value-chain boundaries. Knowledge Engineering consumes `normalized`, `existing_graph`, `source_requirements`, candidate slots, and `link_expansion_frontier`, then adds evidence without changing `contract_version`.
