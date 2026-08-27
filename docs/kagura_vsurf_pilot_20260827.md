# Kagura → VSURF Slack Chatbot Pilot

Date: 2026-08-27 KST  
PC: codex-pc2  
Decision: **FAIL-CLOSED — do not connect to the production Slack app/channel**

## Objective

Evaluate Kagura as the conversational Slack frontend while retaining the existing VSURF durable inbox, Order consumer, Git finalization, and Slack result path as the only mutation backend.

## Fixed upstream

- Repository: `https://github.com/Innei/Kagura.git`
- Local pilot path: `C:\lab\vendor\kagura`
- Pinned commit: `a9f39cce17bd5670296970af68fbfb13f589732e`
- Upstream commit date: `2026-08-13T20:42:44+08:00`
- Node: `v24.14.1`
- pnpm through Corepack: `11.0.0`

The production VSURF listener and consumer were not stopped or modified.

## Verification results

### Passed

- Dependency installation with frozen lockfile
- Full TypeScript typecheck
- Review web application production build
- Kagura application production build
- `better-sqlite3` native installation on Windows
- Required environment, Node version, and `C:\lab` repository root checks in `kagura doctor`

### Failed

1. Memory CLI tests: 3 failures out of 4 tests.
   - `new URL(..., import.meta.url).pathname` becomes `C:\C:\lab\...` on Windows.
2. Kagura application tests: 16 failures out of 482 tests; 466 passed.
   - POSIX-only test commands: `rm`, `mkdir -p`.
   - tilde expansion does not handle Windows paths correctly.
   - worktree and workspace-context tests fail or time out on Windows.
   - CRLF expectation mismatch.
   - image-path assertion assumes `/tmp/...` rather than a Windows path.
3. `kagura doctor`: provider `codex-cli` failed because it checks for a literal `codex` executable.
   - This PC exposes `codex.cmd`/`codex.ps1` and the VSURF dispatcher intentionally invokes `node + codex.js` directly.
   - Kagura hardcodes `spawn('codex', ...)` and has no verified Windows command override in the inspected commit.
4. Kagura's Codex adapter sets `approval_policy="never"` and invokes the agent directly in a resolved workspace.
   - Connecting it unchanged would bypass the VSURF Order approval, clean-tree, exactly-once, and Git finalization boundary.

## Live Slack gate

No live Kagura Socket Mode connection was started.

- There is no pilot-specific Slack app/token set.
- Reusing the production App Token would create two Socket Mode consumers for the same app. Events could be distributed to either Kagura or the existing VSURF listener.
- The production `VSURF-Slack-Bolt-PC2` and `VSURF-OrderConsumer-PC2` tasks remained running.

## Required remediation before a live pilot

1. Add a configurable Codex launch command and use `node <codex.js>` on Windows.
2. Replace URL pathname conversion with `fileURLToPath`.
3. Make home, worktree, temporary-file, shell, and line-ending handling platform-aware.
4. Run the full suite on Windows and require zero runtime-contract failures.
5. Add a VSURF provider/adapter:
   - conversational turns are read-only;
   - proposed changes produce a structured Order draft;
   - explicit Slack approval submits to the existing durable inbox;
   - Kagura never writes the target repository directly.
6. Create a separate Slack pilot app and channel.
7. Pass live tests for thread continuation, restart recovery, duplicate event delivery, approval, Order handoff, completion reply, and cancellation.

## Conclusion

Kagura remains the closest reusable frontend, but the inspected version is not production-ready on this Windows PC2 and must not replace or share the current Slack Socket Mode connection. The correct next choice is either a bounded Windows compatibility fork plus the VSURF adapter, or the smaller native Conversation Router on top of the already-proven Python listener/consumer.
