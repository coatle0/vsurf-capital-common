Run-ID: RUN-139-02

# Order 139 — IVK WinWay official MCP write closure

## Result

**PASS.** The headless approval failure was reproduced, diagnosed, corrected,
and verified through the actual `neo4j-official` MCP path. Both identical
`write_cypher` calls completed, and the three count snapshots stayed invariant.

## Root cause

The Dispatcher launched `codex exec` with `approval_policy="never"`. That mode
does not auto-approve a destructive/write MCP tool. It prevents interactive
approval; therefore a headless `write_cypher` PermissionRequest had no user UI
that could answer it and terminated as `user cancelled MCP tool call`.

The verified CLI path is `--approve-for-me`. It keeps the workspace-write
sandbox and routes PermissionRequest events through Codex automatic review.
The execution log recorded two `PermissionRequest Completed` events followed
by two successful `neo4j-official/write-cypher (completed)` events.

## Official MCP validation

| Snapshot | Nodes | Relationships | CausalAssertion | ASSERTED_FOR | Pilot IDs |
|---|---:|---:|---:|---:|---:|
| Baseline | 347 | 368 | 3 | 3 | 3 |
| After official write 1 | 347 | 368 | 3 | 3 | 3 |
| After identical official write 2 | 347 | 368 | 3 | 3 | 3 |

- Official `read_cypher`: completed for all three snapshots.
- Official `write_cypher` first call: completed.
- Official `write_cypher` identical second call: completed.
- `user cancelled MCP tool call`: absent in the successful run.
- Direct Bolt/Python fallback: not used.
- Idempotency: PASS; the second write produced no count delta.
- Worktree mutation by verification executor: none.

## Dispatcher correction

`scripts/order_dispatcher.py` now uses `--approve-for-me` for Codex unattended
execution and no longer combines `approval_policy="never"` with explicit
`--sandbox workspace-write`. The verified Windows backend override
`windows.sandbox="elevated"` and `--add-dir` boundary remain in place.

## Integrity status

The existing three assertions remain mapped to `company:winway`; prior direct
readback established exact type/evidence/status equivalence and integrity
counts of duplicate 0, orphan 0, missing source/evidence 0, wrong mapping 0,
and unsupported auto-confirm 0.

## Closure

Order 139 DoD is closed: official write 1, identical official write 2, and
idempotency verification all PASS. Follow-on IVK work may proceed.
