# Order 140 — IVK NEW Intake → Blueprint

Run-ID: `RUN-140-01`  
Result: **PASS with stated validation limit**  
Executed: 2026-08-16

## Governance and scope

- Preflight worktree was clean; `master` was one dispatcher-owned Order registration commit ahead of `origin/master`.
- `reports/139_report.md` records `RUN-139-02` as PASS/closed, and Git history contains `109cac0 Complete ORDER 139` plus its follow-up dispatcher correction.
- No source collection, Neo4j write, Golden Example change, unrelated refactor, commit, or push was performed.
- The order-referenced `IVK_HANDOVER_2026-08-15.md` was not present in the repository. The canonical Order 140 field and process contract was therefore used directly.

## Implementation files

- `scripts/ivk_new_intake.py` — parser/validator, normalization, canonical read query, Blueprint construction/validation, CLI.
- `schemas/ivk_new_intake.schema.json` — machine-readable intake schema.
- `schemas/ivk_blueprint.schema.json` — downstream Blueprint contract.
- `examples/140_ai_optical_cpo_intake.json` — new onboarding input.
- `examples/140_ai_optical_cpo_graph.json` — captured official live-read rows.
- `artifacts/140_ai_optical_cpo_blueprint.json` — generated KE-consumable artifact.
- `tests/test_ivk_new_intake.py` — positive E2E and negative validation tests.
- `docs/ivk_new_intake_blueprint.md` — locations, execution, input/output and error rules.

## Intake Schema

Required: `name`, non-empty `seed` array, `frame`, `thesis`. Recommended: `questions`. Optional: `known_links`, `limitations`, `references`. The validator rejects a non-object intake, unknown fields, missing/blank required fields, empty seeds, normalized duplicate seeds, malformed array types, and non-string/blank array entries. `raw_input` is retained in the output.

Normalization canonicalizes ticker/company identifiers (trim/collapse whitespace and uppercase ticker-like IDs), emits a unique ordered `validated_seeds` list, marks every seed as a `starting_point`, derives normalized identity, selects the submitted frame as primary, and records later arrow-separated frame components as secondary candidates.

## Blueprint Schema

The `ivk-blueprint-1.0` contract includes raw and normalized identity/input, validated seeds, unresolved/excluded seeds and reasons, primary/secondary frame, thesis/questions/known links, official existing-graph findings, initial value-chain slots, Driver/Bottleneck/Beneficiary candidate slots, Link Expansion frontier, source requirements, and epistemic/review policy.

Graph results use `graph_observation`; unresearched structure begins as `hypothesis`. Review begins `pending`, and `epistemic_policy.auto_confirm` is false. No candidate is promoted to confirmed/accepted.

## Example E2E result

Input: `AI Optical / CPO`, seeds NVDA/COHR/LITE/CRDO, `Sponsor→Value Chain→Bottleneck`, optical/CPO expansion thesis, and bottleneck/beneficiary/expansion questions.

Normalized seeds: `NVDA`, `COHR`, `LITE`, `CRDO` (ordered and unique). A live `neo4j-official.read_cypher` query on 2026-08-16 returned no matching Company node for all four seeds and therefore no associated product/process/end-market relationship or CausalAssertion evidence. The artifact contains four graph findings and four unresolved entries with disposition `retain_as_starting_point`; none are excluded.

The parser → normalize → official graph snapshot → Blueprint CLI completed and produced `artifacts/140_ai_optical_cpo_blueprint.json`. Artifact inspection confirmed contract `ivk-blueprint-1.0`, 4 findings, 4 unresolved seeds, `auto_confirm=false`, and `review_status=pending`.

## Live Neo4j read path

Canonical path: `neo4j-official.read_cypher`. `existing_graph_query()` uses parameterized seeds and reads Company identity, `PRODUCES`/`OPERATES_IN`/`EXPOSED_TO` value-chain observations, and `CausalAssertion`/`ASSERTED_FOR` metadata. The CLI consumes the captured official response; it provides no investment-kg fallback and performs no write.

## Validation

- `python -m unittest tests.test_ivk_new_intake -v` — PASS, 5/5.
- Negative cases PASS: missing required field, duplicate normalized seed, empty seed, malformed field type.
- `python -m py_compile scripts\ivk_new_intake.py tests\test_ivk_new_intake.py` — PASS.
- CLI E2E generation and artifact assertions — PASS.
- `git diff --check` — PASS.
- Full `python -m unittest discover -s tests -v` — not completed within 120 seconds; all Order 140, IVK v2, Neo4j wrapper, and initial dispatcher tests shown before the cap passed. This timeout is the remaining validation limit.

## Next-stage input contract

Knowledge Engineering should consume the generated Blueprint JSON, preserve `contract_version`, use `normalized` and `existing_graph` as its starting context, fill `source_requirements`, candidate slots, value-chain structure, and `link_expansion_frontier` with evidence-bearing records, and preserve epistemic/review separation. Unresolved seeds require entity resolution but remain valid expansion starts.

Blockers: none for Order 140. The missing handover source file and repository-wide test timeout are recorded limits; neither invalidates the canonical-order contract or focused E2E result.
