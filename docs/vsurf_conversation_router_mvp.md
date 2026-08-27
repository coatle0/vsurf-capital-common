# VSURF Conversation Router MVP

## Purpose

Provide a Slack thread-based mobile conversation layer without introducing a
new agent runtime or bypassing the existing durable Order pipeline.

The Router is deliberately not an executor. It can read local state, persist a
proposal, or enqueue an explicitly approved proposal. Only the existing
`order_inbox_consumer.py` may reach `order_dispatcher.py`.

## Trust boundary

```text
Slack message
  -> Conversation Router
       -> read-only status/result reply, or
       -> PROPOSED state
            -> explicit approve
                 -> durable inbox
                      -> existing consumer/dispatcher/Git proof
```

- A raw `[EXECUTE ORDER NNN]` message is **PROPOSED**, not executed.
- `run` and `continue` require a complete `[EXECUTE ORDER NNN]` payload.
- `approve` must be sent in the same Slack thread.
- `cancel` transitions a proposal to `CANCELLED` without queueing it.
- Unknown or ambiguous text is `UNCLASSIFIED` and causes no action.
- The approval event timestamp is the inbox idempotency key.
- The original thread timestamp is retained for ACK and terminal replies.

## Commands

| Command | Effect |
|---|---|
| `help` | Show the supported command set |
| `status` | Return `IDLE`, `PROPOSED`, `CANCELLED`, `APPROVING`, or `QUEUED` |
| `run <full Order>` | Store a proposal; never execute immediately |
| `continue <full Order>` | Store a follow-up proposal; never execute immediately |
| `approve` | Atomically reserve and enqueue the current proposal |
| `cancel` | Discard the current proposal |
| `result` | Read the existing durable outbox for the approved task |

## State and files

- Router state: `.runtime/conversation_router.sqlite3` (SQLite WAL)
- Durable execution queue: `.runtime/inbox/pending/*.json`
- Execution result: `.runtime/inbox/outbox/*.json`
- Router: `scripts/conversation_router.py`
- Slack integration: `scripts/slack_bolt_listener.py`
- Approved enqueue boundary: `scripts/slack_ack_watcher.py::enqueue_approved`

## Verification

```powershell
python -m py_compile scripts\conversation_router.py scripts\slack_ack_watcher.py scripts\slack_bolt_listener.py
python -m unittest tests.test_conversation_router tests.test_slack_ack_watcher tests.test_slack_bolt_listener -v
```

The tests prove direct Order text does not enqueue, duplicate approval queues
once, ambiguous requests fail closed, cancel does not enqueue, failed durable
writes restore `PROPOSED`, and write-before-ACK remains intact.

## Deferred reliability sprint

This MVP does not claim production-grade fault tolerance. Before promotion,
add fault-injection coverage for process termination between `APPROVING` and
queue completion, Slack duplicate/redelivery across restart, concurrent PC
ownership, cancellation races, and terminal result reconciliation.
