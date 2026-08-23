# IVK NEW Intake → Blueprint contract

`scripts/ivk_new_intake.py` validates an intake JSON, normalizes seed identifiers, combines it with an official Neo4j read snapshot, and emits a Knowledge Engineering-ready Blueprint JSON.

Required input fields are `name`, `seed`, `frame`, and `thesis`. `questions` is recommended; `known_links`, `limitations`, and `references` are optional arrays. Unknown fields, missing or blank required values, an empty seed array, normalized duplicate seeds, non-string entries, and malformed field types are rejected with `IntakeValidationError`. The Blueprint retains `raw_input` alongside `normalized`.

The Intake is always mixed-market and has no `market` field. US symbols remain plain (`NVDA`, `FORM`) while numeric Asian symbols use a country prefix: `KR:131290`, `JP:6855`, or `TW:6515`. These country-scoped IDs remain canonical; the actual exchange (for example KOSDAQ, TSE, TWSE, or TPEX) is resolved from a source instead of guessed from the prefix. Korean identifiers route to DART as the six-digit code. A numeric seed without a prefix is rejected instead of being assigned to a country.

For non-US numeric securities, retain the human-readable company name with `|`: `KR:131290|티에스이`, `JP:6855|Japan Electronic Materials`, `TW:6515|WinWay Technology`. Normalization preserves `canonical_id`, `ticker`, `company_name`, market/exchange, and provider routing. Korean seeds route to DART; US, Japanese, and Taiwanese listed-company seeds route to TIKR/market sources. The Neo4j writer keeps the legacy `Company.id` while adding `security_id`, country, exchange, local/English names, provider, and provider ID.

Existing graph reads must use `neo4j-official.read_cypher`. Call `existing_graph_query()` with `params={"seeds": [...]}` and save the returned row array as JSON. The CLI deliberately accepts only this captured result; it does not fall back to an investment-kg API or write to Neo4j.

Example:

```powershell
python scripts/ivk_new_intake.py examples/140_ai_optical_cpo_intake.json --graph-results examples/140_ai_optical_cpo_graph.json --output artifacts/140_ai_optical_cpo_blueprint.json
```

The Blueprint separates live `graph_observation` findings from `hypothesis` slots. All candidate and overall review states begin `pending`; `epistemic_policy.auto_confirm` is always false. Seeds absent from the graph are retained as starting points under `unresolved_seeds`, not excluded as value-chain boundaries. Knowledge Engineering consumes `normalized`, `existing_graph`, `source_requirements`, candidate slots, and `link_expansion_frontier`, then adds evidence without changing `contract_version`.
