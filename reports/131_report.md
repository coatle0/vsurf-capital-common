Run-ID: RUN-131-01

# Order 131 — investment-kg parity root-cause fix

## Governance ACTIVE v1.2 preflight

Rechecked immediately before execution on 2026-08-15 KST.

| Check | Result |
|---|---|
| Git latest-order | PASS — `131_ivk-investment-kg-parity-root-cause-fix.md` is the highest canonical order; starting HEAD `b8eb892`. |
| Git duplicate | PASS — exactly one `131_*.md`; no duplicate three-digit IDs in `orders/`. |
| Slack active-order | PASS — task `C0BNWS9QKDK-1786769538.503639` is present in `claimed` and its outbox status is `DISPATCHING` for order 131. |
| Globally unused | PASS at issuance boundary — Order 131 occurs only in its canonical registration commit/order and active dispatcher state; there was no prior report or completion. No new order number was created. |

## Runtime/config/source diagnosis

The configured Codex registration is `[mcp_servers.investment-kg]`, command `C:\Python314\python.exe`, argument `C:\lab\knowgraph\investment_workbench\kg_mcp_server.py`, stdio transport. No environment override or explicit database target is registered. Consequently the server uses its source default `KG_DB_PATH=<server-root>/data/workbench.db` and reads a local SQLite `Store`; it does not use the live Neo4j URI/database.

The registration also lacks `default_tools_approval_mode = "approve"`, unlike the working `gs` registration. This explains the prior unattended Codex-layer `user cancelled MCP tool call`: the call is stopped at the client approval/UI boundary before an MCP request reaches the server. It is not a server startup, timeout, transport, tool-schema, or database exception.

Layer isolation evidence:

| Layer | Measurement | Result |
|---|---|---|
| Client approval | registration has no approval default; prior four client calls all returned `user cancelled MCP tool call` before payload | ROOT CAUSE of cancellation |
| Process/startup | configured command and source exist; direct process initialization returned server `investment-kg` version `1.27.1` | PASS |
| Transport | JSON-RPC initialization and notification over stdio succeeded | PASS |
| Tool exposure/schema | `tools/list` exposed 12 tools, including both required tool names | PASS |
| Same-runtime calls | four `tools/call` requests returned typed payloads without RPC/tool errors | PASS |
| Data target | source resolves `KG_DB_PATH` to local `data/workbench.db`; no Neo4j client/URI/database is used | ROOT CAUSE of parity failure |
| Canonical wrapper | configured `neo4j-official` virtual environment currently fails before startup because its interpreter path refers to an unavailable Python 3.12 executable | BLOCKED for fresh canonical MCP replay |

No source/config change was made. The active user-level MCP registration and the `investment-kg` source are outside the Order's writable project root, and changing the checked-in configuration snapshot would not alter the active runtime. A SQLite adapter cannot safely be made Neo4j-canonical through a small in-repository patch.

## Required four-call replay

The configured `investment-kg` process was launched directly and called through MCP stdio (not by importing its functions and not by substituting a direct Neo4j query).

| Call | Actual MCP payload summary | Status |
|---|---|---|
| `get_company_graph(FormFactor)` | `ok=true`, `company=FormFactor`, `hops=2`, nodes `0`, relations `0` | payload returned |
| `get_company_graph(티에스이)` | `ok=true`, `company=티에스이`, `hops=2`, nodes `0`, relations `0` | payload returned |
| `get_company_graph(WinWay)` | `ok=true`, `company=WinWay`, `hops=2`, nodes `0`, relations `0` | payload returned |
| `trace_demand_driver(HBM)` | `ok=true`; driver `demand:hbm`, `drives_process_id=stage:wafer_test`, `requires_product_id=product:probe_card`, one source URL, company coverage `11` | payload returned |

## Parity matrix

The canonical reference is `queries/127_sti_reconciliation.cypher` plus the last successful live measurements in `reports/129_report.md`. A fresh live canonical replay could not be performed in this shell because the registered official wrapper cannot start; historical values are clearly labeled and are not represented as a fresh validation.

| Criterion | investment-kg actual | Canonical live reference | Parity |
|---|---|---|---|
| Company IDs | no nodes for all three calls | `company:form`, `company:tse`, `company:winway` (Order 129 live measurement) | FAIL |
| Relation types/endpoints | no relations for all three calls | assertion-bearing Neo4j relations; 43 total (Order 129 live measurement) | FAIL |
| HBM path | manifest IDs `demand:hbm -> stage:wafer_test -> product:probe_card` | Cypher path uses `DRAM / HBM`, `Wafer Test Cell`, `Probe Card` | PARTIAL semantic coordinate match; not graph-relation parity |
| HBM coverage | 11 companies | 11/11 companies (Order 129 live measurement) | count-only match |
| Source/evidence | HBM driver has source URL; empty company graphs have none | active assertions missing source/evidence `0` (Order 129 live measurement) | FAIL / not comparable for empty graphs |

All four calls now return payloads, but relation parity is **FAIL**, not PASS. The empty SQLite company graphs cannot equal the canonical Neo4j relationships, and the direct MCP replay proves this is a data-target/adapter mismatch rather than a cancellation or transport problem.

## Phase 1-C gate

**FAIL / NOT READY.** `STI Discovery/Expansion Loop 1회 완주` remains the next stage, but it must not start until relation parity passes.

Minimum external actions:

1. Set the active `investment-kg` registration to non-interactive read approval (`default_tools_approval_mode = "approve"`) so dispatcher calls do not stop at the approval boundary.
2. Point `investment-kg` at the live canonical Neo4j database, or replace its graph read implementation with a read-only Neo4j adapter. Merely setting `KG_DB_PATH` cannot solve this because the current `Store` is SQLite-only.
3. Repair/recreate the `neo4j-official` virtual environment using an installed interpreter, then verify its tool list and canonical Cypher output.
4. Restart/reload the MCP client and repeat the same four calls plus the canonical query; require non-empty endpoint/type/source equality for all three companies and semantic HBM path equality.

## Validation

- Direct MCP stdio initialize + `tools/list` — PASS; server version `1.27.1`, 12 tools exposed.
- Four actual MCP `tools/call` requests — PASS for transport/payload return; relation content FAIL as recorded above.
- `neo4j-official` direct startup — FAIL/BLOCKED before MCP initialize due unavailable configured Python interpreter.
- Report first-line/required-section validation and `git diff --check` — PASS.
- `python -m unittest -v tests.test_order_dispatcher` — INCOMPLETE: the command timed out after 120 seconds while entering `CommitPendingRegistrationTests`; the first three prompt-building tests passed. This suite is ancillary to the MCP adapter and is not reported as passing.

## Changed files

- `reports/131_report.md`

No commit or push was performed; dispatcher owns Git finalization.
