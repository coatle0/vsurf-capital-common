"""Fail-closed Slack conversation layer for the VSURF Order pipeline.

The router never executes work.  It may answer local state queries or turn a
validated, explicitly approved proposal into one durable inbox record.  The
existing consumer remains the only path to order_dispatcher and mutations.
"""

from __future__ import annotations

import json
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, NamedTuple

sys.path.insert(0, str(Path(__file__).resolve().parent))
import order_inbox
import order_dispatcher

DB_PATH = Path(r"C:\lab\vsurf_capital\common\.runtime\conversation_router.sqlite3")
MUTATION_PREFIXES = ("[execute order ", "run ", "continue ")
READ_COMMANDS = {"status", "result", "help"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def thread_key(event: dict) -> tuple[str, str]:
    return event["channel"], event.get("thread_ts") or event["ts"]


class RouteResult(NamedTuple):
    handled: bool
    action: str


class ConversationStore:
    def __init__(self, path: Path = DB_PATH):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(self._connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            db.execute(
                """CREATE TABLE IF NOT EXISTS threads (
                    channel TEXT NOT NULL,
                    thread_ts TEXT NOT NULL,
                    state TEXT NOT NULL,
                    proposal TEXT,
                    proposal_event_ts TEXT,
                    approved_task_id TEXT,
                    updated_at TEXT NOT NULL,
                    PRIMARY KEY(channel, thread_ts)
                )"""
            )
            db.commit()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        return db

    def get(self, channel: str, thread_ts: str) -> dict | None:
        with closing(self._connect()) as db:
            row = db.execute(
                "SELECT * FROM threads WHERE channel=? AND thread_ts=?", (channel, thread_ts)
            ).fetchone()
        return dict(row) if row else None

    def propose(self, channel: str, thread_ts: str, text: str, event_ts: str) -> None:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            db.execute(
                """INSERT INTO threads
                   (channel, thread_ts, state, proposal, proposal_event_ts, approved_task_id, updated_at)
                   VALUES (?, ?, 'PROPOSED', ?, ?, NULL, ?)
                   ON CONFLICT(channel, thread_ts) DO UPDATE SET
                     state='PROPOSED', proposal=excluded.proposal,
                     proposal_event_ts=excluded.proposal_event_ts,
                     approved_task_id=NULL, updated_at=excluded.updated_at""",
                (channel, thread_ts, text, event_ts, now_iso()),
            )
            db.commit()

    def transition(self, channel: str, thread_ts: str, expected: str, state: str, task_id: str | None = None) -> bool:
        with closing(self._connect()) as db:
            db.execute("BEGIN IMMEDIATE")
            cursor = db.execute(
                """UPDATE threads SET state=?, approved_task_id=?, updated_at=?
                   WHERE channel=? AND thread_ts=? AND state=?""",
                (state, task_id, now_iso(), channel, thread_ts, expected),
            )
            db.commit()
            return cursor.rowcount == 1


def _reply(post: Callable[[str], None], text: str) -> RouteResult:
    post(text)
    return RouteResult(True, "REPLIED")


def route_event(
    event: dict,
    store: ConversationStore,
    post: Callable[[str], None],
    enqueue: Callable[[dict, str], str],
) -> RouteResult:
    """Classify one human Slack event. Unknown/ambiguous text never executes."""
    text = order_dispatcher.clean_field_value(event.get("text", "").strip())
    lowered = text.casefold()
    channel, root_ts = thread_key(event)

    if lowered in READ_COMMANDS:
        if lowered == "help":
            return _reply(post, "Commands: status | run <full Order> | approve | cancel | result | continue <full Order>")
        row = store.get(channel, root_ts)
        if lowered == "status":
            state = row["state"] if row else "IDLE"
            return _reply(post, f"STATUS thread={root_ts} state={state}")
        if not row or not row.get("approved_task_id"):
            return _reply(post, "RESULT unavailable: this thread has no approved task.")
        outcome = order_inbox.load_outbox(row["approved_task_id"])
        if not outcome:
            return _reply(post, f"RESULT task={row['approved_task_id']} status=QUEUED_OR_RUNNING")
        return _reply(post, "RESULT " + json.dumps(outcome, ensure_ascii=False, sort_keys=True))

    if lowered == "cancel":
        if store.transition(channel, root_ts, "PROPOSED", "CANCELLED"):
            return _reply(post, "CANCELLED: proposal discarded; no Order was queued.")
        return _reply(post, "CANCEL ignored: no PROPOSED request in this thread.")

    if lowered == "approve":
        row = store.get(channel, root_ts)
        if not row or row["state"] != "PROPOSED":
            return _reply(post, "APPROVE rejected: no PROPOSED request in this thread.")
        task_id = order_inbox.task_id(channel, event["ts"])
        # Reserve approval atomically before queueing. A duplicate approve can
        # never enqueue twice. If enqueue fails, restore PROPOSED for retry.
        if not store.transition(channel, root_ts, "PROPOSED", "APPROVING", task_id):
            return _reply(post, "APPROVE rejected: proposal state changed; inspect status.")
        try:
            enqueue(event, row["proposal"])
        except Exception:
            # ACK/network failure can happen after the durable write. Never
            # reopen approval in that case or a second user message could
            # enqueue the same proposal under a new event timestamp.
            if order_inbox.task_exists(task_id):
                store.transition(channel, root_ts, "APPROVING", "QUEUED", task_id)
            else:
                store.transition(channel, root_ts, "APPROVING", "PROPOSED")
            raise
        store.transition(channel, root_ts, "APPROVING", "QUEUED", task_id)
        return RouteResult(True, "QUEUED")

    proposal: str | None = None
    if lowered.startswith("run "):
        proposal = text[4:].strip()
    elif lowered.startswith("continue "):
        proposal = text[9:].strip()
    elif lowered.startswith("[execute order "):
        proposal = text

    if proposal is not None:
        if not proposal.casefold().startswith("[execute order "):
            return _reply(post, "PROPOSAL rejected: run/continue must contain a full [EXECUTE ORDER NNN] payload.")
        store.propose(channel, root_ts, proposal, event["ts"])
        return _reply(post, "PROPOSED: no execution occurred. Reply `approve` in this thread to queue it, or `cancel`.")

    return _reply(post, "UNCLASSIFIED: no action taken. Use `help`; mutation-like requests require `run` and `approve`.")
