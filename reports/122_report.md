Run-ID: RUN-122-01

# Order 122 — GS MCP dispatcher enablement

## Result

**FAIL** — dispatcher configuration and focused regression validation pass, but the required live DoD could not be completed in this executor environment. The isolated Codex process could not reach the OpenAI Responses endpoint, and direct read-only GS bridge calls stopped because the active R library lacks `quantmod`.

## Changed files

- `scripts/order_dispatcher.py`
- `tests/test_order_dispatcher.py`
- `reports/122_report.md`

## Generated Codex command/config

The Codex command retains `--ignore-user-config`, `approval_policy="never"`, `windows.sandbox="elevated"`, `--sandbox workspace-write`, the existing three `mcp_servers.tikr` overrides, and `--add-dir C:\lab\vsurf_capital\common`.

The following GS overrides are now appended after the preserved TIKR overrides (resolved values measured on this PC):

```text
-c mcp_servers.gs.command="C:\\Python314\\python.exe"
-c mcp_servers.gs.args=["C:\\autoai\\gs-toolkit\\gs_mcp_server.py"]
-c mcp_servers.gs.default_tools_approval_mode="approve"
-c mcp_servers.gs.env.APPDATA=<current APPDATA path>
-c mcp_servers.gs.env.LOCALAPPDATA=<current LOCALAPPDATA path>
-c mcp_servers.gs.env.USERPROFILE=<current USERPROFILE path>
-c mcp_servers.gs.env.R_USER=<current R_USER or USERPROFILE path>
-c mcp_servers.gs.env.GS_RSCRIPT="C:\\Program Files\\R\\R-4.5.2\\bin\\Rscript.exe"
```

No credential-bearing values are injected or recorded. Python comes from `GS_PYTHON` or the dispatcher runtime; the server comes from `GS_MCP_SERVER`, `AUTOAI_ROOT`, or the current system drive's `autoai/gs-toolkit`; Rscript comes from `GS_RSCRIPT` or executable discovery. The server script must exist before command creation.

## Tool exposure smoke test

An actual non-interactive `codex exec` was launched using the dispatcher-generated isolated configuration. It exited 1 before a model turn because outbound WebSocket and HTTPS connections to the OpenAI Responses endpoint were denied by the execution environment. Consequently none of the following can be certified as exposed/callable in that session:

| Tool | Exposure result |
|---|---|
| `gs_read_bgdgs` | Not observed — Codex transport blocked |
| `gs_read_bgdidx` | Not observed — Codex transport blocked |
| `gs_read_sggs` | Not observed — Codex transport blocked |
| `gs_read_idx` | Not observed — Codex transport blocked |

## Read-only sheet smoke tests

As a fallback diagnostic, the same four bridge functions were invoked directly. This did not write Google Sheets and did not run `BGD.R` or `alltheidx*.R`. All stopped in `gs_reader.R` startup with R return code 1: package `quantmod` is unavailable. No CSV body was printed or stored.

| Tool | Sheet | success | ok | rows | cols | warning | header |
|---|---|---:|---:|---:|---:|---|---|
| `gs_read_bgdgs` | `bgd_th` | false | false | — | — | R dependency missing | — |
| `gs_read_sggs` | `kidx-Q` | false | false | — | — | R dependency missing | — |
| `gs_read_idx` | `kr_idx` | false | false | — | — | R dependency missing | — |
| `gs_read_bgdidx` | `etf_idx` | false | false | — | — | R dependency missing | — |

No `R exit 3221225477`/usable-data combination or `etf_idx` coercion warning occurred, so the conditional NA check was not applicable.

## Regression validation

Focused unit tests passed:

```text
python -m unittest \
  tests.test_order_dispatcher.ParseRequestTests.test_codex_command_uses_isolated_safe_config \
  tests.test_order_dispatcher.ParseRequestTests.test_gs_config_uses_environment_overrides_and_checks_server \
  tests.test_order_dispatcher.ParseRequestTests.test_gs_config_rejects_missing_server_script

Ran 3 tests in 0.044s — OK
```

The command-construction test confirms the existing TIKR settings remain present and all required GS settings are added. The resolver tests confirm explicit PC-specific overrides and rejection of a nonexistent GS server. A full dispatcher test invocation was attempted but exceeded the 120-second executor timeout after beginning successfully; it is not counted as passing.

## Remaining risks and limits

- Live non-interactive tool discovery must be repeated where the Codex CLI can reach the OpenAI API.
- The R environment used by GS MCP must provide `quantmod` (and any subsequent declared dependencies) before the four sheet reads can return `ok=true`.
- Because the four required reads did not return `ok=true`, Order 122 does not meet its DoD in this run.
- Per dispatcher instructions, the executor did not commit or push; Git finalization and Slack response remain dispatcher-owned.
