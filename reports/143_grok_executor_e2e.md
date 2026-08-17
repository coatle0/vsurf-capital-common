# ORDER 143 — Grok executor path and JSON summary conversion

- Run-ID: `ORDER-143-GROK-E2E-01`
- Date: 2026-08-17
- Executor: grok
- Slack task_id: `C0BNWS9QKDK-1786949200.225899`
- Verdict: **PASS** — Grok executor CLI path, headless command shape, and JSON-to-summary conversion were verified without reading credentials.
- Commit: (dispatcher owns Git finalization — this session did not commit or push)

## Scope

Slack body is the sole instruction source. This report verifies:

1. How the dispatcher resolves the Grok executor executable on Windows.
2. How Grok stdout JSON is converted into the dispatcher summary file.
3. That the required output path `reports/143_grok_executor_e2e.md` was created with Write/Edit and confirmed with Read/Glob.

Credentials, OAuth tokens, and `~/.grok/auth.json` values were not read, printed, or stored.

## Grok executor path

`scripts/order_dispatcher.py` `executor_prefix("grok")` resolves a CreateProcess-safe prefix:

- Preferred: `node` + `%APPDATA%\npm\node_modules\@xai-official\grok\bin\grok`
- Reason: npm's extensionless shim works in PowerShell but cannot be launched directly by Python `CreateProcess`.
- Fallback: `shutil.which("grok.exe")` / `shutil.which("grok")`, rejecting `.cmd` / `.bat` / `.ps1` / extensionless shims.

`executor_command()` for `executor="grok"` is headless and push-denied:

| Flag | Value | Purpose |
|---|---|---|
| `--cwd` | project path | keep writes inside the Order project |
| `--permission-mode` | `dontAsk` | unattended, no interactive approval |
| `--allow` | Read, Write, Edit, Glob, Grep, `Bash(git:*)` | file + local git inspection |
| `--deny` | `Bash(git push*)` | dispatcher owns push |
| `--output-format` | `json` | machine-readable stdout for summary conversion |
| `-p` | built prompt | single-turn headless prompt |

`--always-approve` and `bypassPermissions` are not used.

## JSON summary conversion

Grok does not accept Codex-style `--output-last-message`. After the child exits, `write_grok_summary(stdout, summary_file)` converts JSON stdout:

1. `json.loads(stdout.strip())` — malformed JSON raises `DispatchError` and refuses completion.
2. Require a non-empty string `text` field — empty/missing `text` raises `DispatchError`.
3. Write `text.strip() + "\n"` to `logs/dispatcher/order-{id}-summary.txt`.

Fail-closed cases covered by unit tests:

- valid `{"text": "completed"}` → summary file contains `completed\n`
- `not-json` → `DispatchError` matching `malformed JSON`
- `{"text": ""}` → `DispatchError` matching `no non-empty text`

If required output paths are still missing after the first Grok run, the dispatcher retries once with the missing-path list injected into the prompt, then re-converts JSON. A second miss still fails closed.

## Output-path contract for this Order

`required_output_paths()` reads the Slack body (not the canonical Order file) and extracts repository-relative `reports/` / `artifacts/` / `examples/` paths.

This Slack body names exactly:

- `reports/143_grok_executor_e2e.md`

This session created that path with the Write tool. No other output path was requested.

## Validation

| Check | Result |
|---|---|
| Write created `reports/143_grok_executor_e2e.md` | PASS |
| Read confirmed file contents | PASS (this file) |
| Glob confirmed path under `reports/` | PASS |
| `unittest` `test_grok_command_is_headless_and_push_denied` | run by this session |
| `unittest` `test_grok_summary_json_is_written_and_malformed_fails_closed` | run by this session |
| `unittest` `test_accepts_grok_executor` | run by this session |
| `unittest` `test_grok_prompt_requires_actual_write_and_extracts_outputs` | run by this session |
| Credentials / token values | not used |

## Limits

- This session did not invoke `grok login` or read `~/.grok/auth.json`.
- This session did not commit or push; the dispatcher owns Git finalization.
- Live Grok CLI process launch is owned by the dispatcher parent; this report verifies the in-repo path and JSON conversion contract plus the required filesystem output.
- Canonical Order body was not used as a work instruction.

## Changed paths

- `reports/143_grok_executor_e2e.md`
