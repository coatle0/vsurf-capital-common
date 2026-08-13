Run-ID: RUN-112-01

# Order 112 — Codex MCP configuration check

## 1. User configuration

Path: `C:\Users\coatl\.codex\config.toml`

The file exists. Its complete content is reproduced below. Credential-bearing values are masked only on their own lines.

```toml
sandbox_mode = "danger-full-access"
approval_policy = "never"
disable_wsl = true

[windows]
sandbox = "elevated"

[marketplaces.openai-bundled]
last_updated = "2026-05-17T01:34:42Z"
source_type = "local"
source = '\\?\C:\Users\coatl\.codex\.tmp\bundled-marketplaces\openai-bundled'

[marketplaces.openai-primary-runtime]
last_updated = "2026-05-17T01:35:57Z"
source_type = "local"
source = '\\?\C:\Users\coatl\.cache\codex-runtimes\codex-primary-runtime\plugins\openai-primary-runtime'

[plugins."browser@openai-bundled"]
enabled = true

[plugins."documents@openai-primary-runtime"]
enabled = true

[plugins."spreadsheets@openai-primary-runtime"]
enabled = true

[plugins."presentations@openai-primary-runtime"]
enabled = true

[projects.'c:\lab']
trust_level = "trusted"

[projects.'c:\lab\vsurf_capital\common']
trust_level = "trusted"

[projects.'c:\users\coatl\appdata\local\temp\claude\c--lab\c5914dd8-cd3c-4233-baad-6c9334a8b349\scratchpad\step0_codex_sandbox_test']
trust_level = "trusted"

[tui.model_availability_nux]
"gpt-5.6-sol" = 4

[mcp_servers.tikr]
command = 'C:\Python314\python.exe'
args = ['C:\autoai\tikr-toolkit\tikr_mcp_server.py']
default_tools_approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_company_overview]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_financials]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_get_filing]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_get_report_doc]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_get_transcript]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_list_earnings_calls]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_list_filings]
approval_mode = "approve"

[mcp_servers.tikr.tools.tikr_list_reports]
approval_mode = "approve"

[mcp_servers.dart]
command = 'C:\Python314\python.exe'
args = ['C:\autoai\dart-toolkit\dart_mcp_server.py']
default_tools_approval_mode = "approve"

[mcp_servers.github]
url = "https://api.githubcopilot.com/mcp/"
bearer_token_env_var = "<REDACTED>"

[mcp_servers.gs]
command = 'C:\Python314\python.exe'
args = ['C:\autoai\gs-toolkit\gs_mcp_server.py']
default_tools_approval_mode = "approve"

[mcp_servers.gs.env]
APPDATA = 'C:\Users\coatl\AppData\Roaming'
GS_RSCRIPT = 'C:\Program Files\R\R-4.5.2\bin\x64\Rscript.exe'
LOCALAPPDATA = 'C:\Users\coatl\AppData\Local'
R_USER = 'C:\Users\coatl'
USERPROFILE = 'C:\Users\coatl'

[mcp_servers.investment-kg]
command = 'C:\Python314\python.exe'
args = ['C:\lab\knowgraph\investment_workbench\kg_mcp_server.py']

[mcp_servers.neo4j-official]
command = 'C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe'
args = ['C:\lab\knowgraph\investment_workbench\neo4j_mcp_wrapper.py']

[mcp_servers.telegram-research]
command = 'C:\lab\knowgraph\vendor\telegram-research\.venv\Scripts\python.exe'
args = ['C:\lab\knowgraph\investment_workbench\telegram_research_mcp_wrapper.py']

[mcp_servers.telegram-mcp]
command = 'C:\lab\telegram-mcp.exe'

[mcp_servers.telegram-mcp.env]
TG_API_HASH = "<REDACTED>"
TG_APP_ID = "<REDACTED>"
TG_SESSION_PATH = 'C:\Users\coatl\.telegram-mcp\session.json'

[hooks.state]

[hooks.state.'C:\Users\coatl\.codex\hooks.json:pre_tool_use:0:0']
trusted_hash = "sha256:b96f206d8fcdbea022c3d52c9f099db413d48026982c33beefeb69d67c01df00"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:permission_request:0:0']
trusted_hash = "sha256:19f15d2c9f1f4f0719425b4168b81460353e99d1d6fe1fc4ffbc1dd3a08f34df"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:post_tool_use:0:0']
trusted_hash = "sha256:172b2a6ac5f5fee49723065f6aacec830aade94f91376d05b6eb97fcfc4ff3ec"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:session_start:0:0']
trusted_hash = "sha256:6e11aafeca5ea0a2ca1282d9a99e4657782819bad09f6ce4085a706ea515afe9"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:user_prompt_submit:0:0']
trusted_hash = "sha256:256e05a86944bedc89f52173b057c8e455ec2c02defc73e5a8a44a41487f96ae"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:subagent_start:0:0']
trusted_hash = "sha256:f9dbeda8f9a716ce0acab7bf7deff179c04d15278e7e941000b1666e10256440"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:subagent_stop:0:0']
trusted_hash = "sha256:98b140ff1931536f4ea2de66147fb97e59f14d8512093577ec77b9eee97726c7"

[hooks.state.'C:\Users\coatl\.codex\hooks.json:stop:0:0']
trusted_hash = "sha256:f50200dd28c4f3a43d4d7e88f1a011be8e3f235b4262b50424a43129d92a59f7"
```

## 2. Project-scoped configuration

No config file exists at either checked project-scoped candidate:

- `C:\lab\vsurf_capital\common\.codex\config.toml`
- `C:\lab\vsurf_capital\common.codex\config.toml`

## 3. MCP findings

- The user config contains multiple `mcp_servers` sections.
- `mcp_servers.tikr` exists and points to `C:\autoai\tikr-toolkit\tikr_mcp_server.py`.
- Neither the `tikr` server nor its listed tools has an explicit `enabled` value. The only per-tool setting is `approval_mode = "approve"`; the server has `default_tools_approval_mode = "approve"`.
- No `tikr` tool is exposed in this running session's available-tool inventory.

## 4. Dispatcher/config-loading explanation

`scripts/order_dispatcher.py` constructs Codex executions with `--ignore-user-config`. Its adjacent source comment explicitly says this strips `~/.codex/config.toml` entirely. It then restores only `approval_policy="never"` and `windows.sandbox="elevated"` through `-c`, adds the common repository as an allowed directory, and selects `workspace-write` sandboxing.

Therefore the registered user-level `mcp_servers.tikr` section is not loaded for dispatcher-launched Order sessions. The observed session is consistent with that implementation: its sandbox is workspace-write, the common project is writable, `.git` metadata and other non-allowed locations remain non-writable, and no `tikr` tools appear in the tool inventory. The cause of Order 111's missing `tikr` MCP is thus the dispatcher's deliberate `--ignore-user-config`, not absence or explicit disabling of `tikr` in the user config.

## Validation and limits

- Dispatcher dry-run for the supplied Order 112 payload returned `VALIDATED`.
- Confirmed this report starts with the required Run-ID and contains the configuration and findings above.
- `git pull --ff-only` was attempted but could not update `.git/FETCH_HEAD` because the execution sandbox grants read-only access to `.git`. At inspection time the worktree was clean and `master` was one local commit ahead of `origin/master`.
- Per the caller's instruction, no commit or push was performed. No config file was modified.
