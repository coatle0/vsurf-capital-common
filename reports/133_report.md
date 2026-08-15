Run-ID: RUN-133-01

# Order 133 — IVK STI/IIKG live pilot

## Governance ACTIVE v1.2 preflight

Measured on 2026-08-15 KST before artifact creation.

| Check | Result |
|---|---|
| Git latest-order | PASS — Order 133 is the highest canonical order; starting HEAD `3649a9a` is its registration commit. The worktree was clean and `master` was one registration commit ahead of `origin/master`. |
| Git duplicate | PASS — exactly one `orders/133_*.md`; no competing Order 133 report or implementation existed. |
| Slack active-order | PASS — task `C0BNWS9QKDK-1786773150.988359` is the sole claimed task found for Order 133 and its outbox identifies order 133. |
| Globally unused | PASS at issuance boundary — Git references were limited to the canonical registration, and runtime references were limited to this task. No new order number was allocated. |

## Pilot selection and source execution

WinWay (`company:winway`) was selected as the minimum one-company pilot because Order 132 already established a sourced HBM/AI-HPC demand chain, live `EXPOSED_TO` and `PRODUCES` relationships, and a named Renwu capacity frontier. The static Golden Example files were not modified.

Fresh in-client `investment-kg` calls for five-quarter financials, capacity expansions, management commentary, and the company graph were attempted. All four were cancelled at the known client approval boundary with `user cancelled MCP tool call`; no typed payload was returned. The pilot input therefore reuses the already sourced and validated Order 132 WinWay record rather than claiming a fresh source refresh.

`data/133_winway_live_pilot.json` is the resulting three-record IIKG batch: one earnings-driver link, one bottleneck, and one beneficiary assessment. All are evidence-bearing, explicitly `inference`, and `pending`; none is auto-confirmed. `scripts/ivk_v2.py` successfully loads and validates the batch and produces an idempotent three-node dry-run/rollback plan.

## Live Neo4j baseline and write blocker

Fresh read-only measurements before the intended write:

| Measure | Before | After |
|---|---:|---:|
| Total nodes | 344 | 344 |
| Total relationships | 365 | 365 |
| `CausalAssertion` nodes | 0 | 0 |
| Order 133 `CausalAssertion` nodes | 0 | 0 |
| `ASSERTED_FOR` relationships | 0 | 0 |

The live write is **BLOCKED**. The only available canonical Neo4j MCP tools in this executor are `get_schema` and `read_cypher`; no `write_cypher` tool is exposed. The repository contains no credential-safe live writer, and the active Python environment does not have the Neo4j driver installed. Credentials were not read, printed, copied, or embedded. Consequently no node or relationship was created or updated, and end-to-end live completion is not claimed.

`queries/133_winway_live_pilot.cypher` is the exact idempotent loader and post-write verification query for an approved write-capable client. It matches the existing `company:winway`, merges three `CausalAssertion` nodes, attaches three evidence-bearing `ASSERTED_FOR` relationships, preserves epistemic/review status, and cannot auto-accept inference/hypothesis rows.

Reproduction: load `data/133_winway_live_pilot.json` as parameter `$rows`, then execute `queries/133_winway_live_pilot.cypher` with the approved write-capable Neo4j client. Do not run it through the currently exposed `read_cypher` tool. Expected delta on the measured baseline is nodes `+3`, relationships `+3`, with existing entities unchanged.

## Integrity validation

Fresh live read checks returned:

- Assertion-bearing core relationships: 43; missing `source_url`: 0; `confirmed`: 0.
- Duplicate endpoint/type groups: 0; excess relationships: 0.
- Orphan relationships: 0.
- WinWay resolves uniquely to `company:winway` and retains sourced HBM exposure plus Test Socket and Vertical Probe Card production paths.
- Pilot payload IDs: 3 distinct; missing node source/evidence: 0; auto-confirmed unsupported assertions: 0.

Because the write did not occur, post-write duplicate, orphan, relationship-evidence, and company-mapping checks cannot be represented as passed. The unchanged after counts prove only that no partial mutation occurred.

## Validation commands

- `python -m unittest -v tests.test_ivk_v2` — PASS, 5 tests.
- `python -c "from scripts.ivk_v2 import load_records,migration_dry_run; ..."` against `data/133_winway_live_pilot.json` — PASS: 3 writes planned, 3 rollback statements, duplicate 0, auto-confirm 0.
- `git diff --check` — PASS.
- Fresh `neo4j-official.read_cypher` baseline and integrity queries — PASS for the read-only measurements above.
- Four fresh `investment-kg` calls — BLOCKED/cancelled; not counted as passing.

## Changed files and remaining limit

- `data/133_winway_live_pilot.json`
- `queries/133_winway_live_pilot.cypher`
- `reports/133_report.md`

Order 133 is **partial / not DoD-complete**: canonical uniqueness, minimal input construction, dry-run pipeline validation, live baseline measurement, and integrity prechecks are complete; the required live graph write and its post-write verification remain blocked until a write-capable Neo4j client is exposed. Current commit SHA remains the registration commit `3649a9a`; no commit or push was performed because dispatcher owns Git finalization.
