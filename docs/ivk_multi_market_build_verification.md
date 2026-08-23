# IVK Multi-Market Build Verification Plan

## Gate 0 — static and contract tests

- Compile IVK parser, factory, kernel, CLI, lifecycle, and Neo4j executor.
- Run mixed-seed normalization tests for US, KR, JP, and TW.
- Confirm numeric seeds without a country prefix are rejected.
- Confirm company names survive normalization.

## Gate 1 — source routing dry run

- Omit `--region` and verify region packs are inferred from seeds.
- KR company tasks must contain DART and must not contain TIKR.
- JP tasks must contain TIKR/JPX and preserve fiscal and calendar period labels.
- TW tasks must contain TWSE/TPEX resolution and monthly-revenue collection.
- US tasks must retain the existing TIKR/SEC/earnings-call path.

## Gate 2 — identity and duplicate prevention

- Capture live `neo4j-official.read_cypher` results before build.
- For an existing company, verify `company_node_id` equals the live legacy ID.
- For a new non-US company, verify the proposed ID is country-scoped (`company:kr:131970`, etc.).
- Generate write batches twice and verify byte-equivalent identity decisions.
- Reject a run if two live Company nodes match the same country+ticker/security ID.

## Gate 3 — BATCH_READY review

- Run `ivk build` without `--execute-neo4j`.
- Inspect Company rows, Evidence `company_node_id`, Product producer, Process operator, and assertion company references.
- Confirm all relationships target the resolved Company ID rather than `company:` plus ticker.
- Confirm no accepted/confirmed causal assertion is created automatically.

## Gate 4 — controlled live write

- Start with one existing company and one new company per market.
- Record pre-write Company/node/relationship counts.
- Execute approved batches, then replay the identical batches.
- Require second-run node counts to remain unchanged.
- Read back `security_id`, ticker, names, country, actual exchange, provider, evidence, and VC membership.

## Gate 5 — market-specific quality

- KR: DART-only company evidence, cumulative-to-standalone derivation flags, five quarters, inventory and CAPEX.
- JP: fiscal/calendar quarter dual labels and JPY unit normalization.
- TW: actual TWSE/TPEX exchange, TWD units, quarterly results, and monthly revenue nodes.
- US: regression comparison against the existing verified optical path.

## Release criterion

Promote multi-market `build --execute-neo4j` only when all four markets pass duplicate-free replay and live read-back. `VERIFIED` remains structural E2E proof; STI-grade requires the separate financial, segment, inventory, CAPEX, provenance, and reviewed-causal coverage gates.
