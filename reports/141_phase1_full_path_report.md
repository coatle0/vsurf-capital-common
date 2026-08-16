# Order 141 continuation — Power Semiconductor full-path dry run

- Run-ID: `ORDER-141-PHASE1-01`
- Date: 2026-08-16
- Result: **PASS — first minimal full-path completion**

## Path completed

`IVK NEW → Blueprint → Source Plan → Source Collection → Evidence Packet → KE → governed Neo4j write → Review/Report`

The existing Order 141 intake, Blueprint, and Source Plan were reused. No new Value Chain fixture was introduced.

## Minimal stage results

- Source Collection: five live `tikr.company_overview` responses for VRT, ETN, VST, ON, and WOLF.
- Evidence Packet: five provenance-bearing documents with SHA-256 content hashes; all five seed identities resolved.
- KE: five candidate Company identities and one bootstrap ValueChain; causal assertions remain empty.
- Governed write: limited to candidate Company identities, Evidence nodes, `SUPPORTED_BY`, and candidate `CANDIDATE_IN` membership.
- Review: all five memberships remain `candidate/pending`; four thesis questions remain pending deeper evidence.

## Neo4j verification

Canonical `neo4j-official.write_cypher` wrote five companies, five evidence records, and five candidate links. Canonical `read_cypher` returned all five rows with matching ticker, company, evidence ID, source reference, content hash, `membership_status=candidate`, and `review_status=pending`.

During the first write call, manually supplied hashes did not match the generated Evidence Packet. They were immediately corrected from the canonical packet and the final read-back verifies all five exact hashes. No assertion or confirmed relationship was written during either call.

## Quality and governance

- `auto_confirm=false`
- confirmed assertions: 0
- unsupported assertions: 0
- every written candidate Company has a linked Evidence record
- provenance: `tikr.company_overview:<ticker>`
- Neo4j write scope remained candidate identity and membership only

## Validation

- `python -m unittest tests.test_ivk_phase1_dry_run tests.test_ivk_factory tests.test_order_141 tests.test_ivk_new_intake -v` — **PASS, 16/16**
- Python compile, JSON parse, and `git diff --check` — **PASS**
- Neo4j write/read-back — **PASS, 5/5**

## Limits exposed for Phase 2

The first path completion proves contracts and governed movement, not investment-grade depth. Company overviews support identity and business-scope facts only. Filings, earnings calls, financial time series, bottleneck evidence, beneficiary ranking, counter-evidence, and human acceptance remain future quality work. The reusable power-semiconductor Sector Pack also remains bootstrap pending.
