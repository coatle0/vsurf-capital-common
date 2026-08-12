"""The "slower worker" slack_ack_watcher.py's docstring refers to: consumes
the durable inbox and wires it to order_dispatcher.py, which previously had
no caller anywhere in this repo.

Exactly-once execution is the point of this module, not just delivery:

  * pending -> claimed is a single os.rename, so only one process can ever
    own a given task_id (order_inbox.claim).
  * A whole-process ConsumerLock additionally refuses to let a second
    instance of this script run at all.
  * Before calling order_dispatcher.dispatch() (the only thing in this repo
    with real side effects: git commit/push, running the executor), the
    outcome is looked up in outbox/. If a terminal outcome is already
    recorded, dispatch() is never called again. If the outbox shows
    DISPATCHING with no lock file and a newer order_dispatcher result
    exists for that order_id, that result is adopted instead of
    re-dispatching -- this is what makes a crash between "dispatch()
    returned" and "we recorded that" safe.
  * The Slack reply is attempted only after the outcome is durably
    recorded, and a "replied" flag is persisted right after a successful
    reply and before archiving, so a second crash after a successful
    reply can only retry the reply (a harmless duplicate notification),
    never re-run the order.
  * Every record gets a definitive outcome (IGNORED / DUPLICATE / REJECTED
    / COMPLETED / FAILED) archived to processed/ -- nothing is dropped
    silently.
"""

from __future__ import annotations

import dataclasses
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import order_dispatcher
import order_inbox
from slack_api import api

POLL_SECONDS = float(os.environ.get("VSURF_INBOX_POLL_SECONDS", "5"))
LOG_PATH = Path(r"C:\lab\vsurf_capital\common\logs\inbox_consumer\inbox_consumer.log")
CONSUMER_LOCK_PATH = order_inbox.INBOX_DIR / "consumer.lock"

# Not a secret -- Slack user IDs only, safe to commit and sync PC1/PC2.
# Adding an account is a CIO/COO decision, not something this module
# decides on its own (per the 2026-08-12 work order, task 2).
SENDERS_PATH = Path(r"C:\lab\vsurf_capital\common\order_senders.json")


def load_allowed_senders() -> set[str]:
    try:
        data = json.loads(SENDERS_PATH.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return set()
    return {entry["user_id"] for entry in data.get("allowed_senders", []) if entry.get("user_id")}

logger = logging.getLogger("order_inbox_consumer")


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class ConsumerLock:
    """Whole-process singleton guard (req: consumer 중복 프로세스 방지).

    Like order_dispatcher.OrderLock, a crash leaves the lock file behind on
    purpose: a stuck lock blocks automatic restarts until a human clears it,
    which is safer than silently allowing two consumers to run at once.
    """

    def __init__(self) -> None:
        self.path = CONSUMER_LOCK_PATH
        self.fd: int | None = None

    def __enter__(self) -> "ConsumerLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise RuntimeError(
                f"Another order_inbox_consumer instance already holds {self.path}; "
                "if it is not actually running, remove the lock file manually."
            ) from exc
        os.write(self.fd, f"pid={os.getpid()} started={order_dispatcher.now_iso()}".encode())
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


def reply(token: str, channel: str, thread_ts: str, text: str) -> None:
    # thread_ts ties the reply to the originating message via Slack's
    # standard chat.postMessage threading (Web API, documented, stable).
    api("chat.postMessage", token, {"channel": channel, "thread_ts": thread_ts, "text": text})


def last_dispatcher_result(order_id: str) -> dict[str, Any] | None:
    path = order_dispatcher.RUNTIME_DIR / f"order-{order_id}-last.json"
    if not path.is_file():
        return None
    try:
        return order_inbox.load(path)
    except (OSError, ValueError):
        return None


def format_reply(tid: str, outbox: dict[str, Any]) -> str:
    status = outbox.get("status")
    if status == "REJECTED":
        return f"REJECTED [{tid}]: {outbox.get('error')}"
    if status == "COMPLETED":
        commit = (outbox.get("commit") or "")[:12]
        return f"COMPLETED [{tid}] order {outbox.get('order_id')} commit {commit}"
    return f"FAILED [{tid}] order {outbox.get('order_id')}: {outbox.get('error')}"


def resolve_outcome(record: dict[str, Any], existing: dict[str, Any] | None) -> dict[str, Any]:
    """Determine (or adopt) the terminal outcome for a claimed record.
    Only path in this module that may call order_dispatcher.dispatch()."""
    tid = record["task_id"]
    text = record["text"]

    try:
        request = order_dispatcher.parse_request(text, task_id=tid)
    except order_dispatcher.DispatchError as exc:
        return {"status": "REJECTED", "error": str(exc), "replied": False}

    order_id = request.order_id
    claimed_at = record.get("claimed_at") or record.get("received_at", "")

    if existing is None:
        order_inbox.write_outbox(tid, {"status": "DISPATCHING", "order_id": order_id, "replied": False})

    prior = last_dispatcher_result(order_id)
    if prior is not None and (prior.get("finished_at") or "") >= claimed_at:
        # A previous attempt already ran order_dispatcher.dispatch() to
        # completion for this exact claim (its own lock/result file is the
        # proof) but this process crashed before recording that fact.
        # Adopt that result instead of dispatching again.
        result = dict(prior)
    else:
        result = dataclasses.asdict(order_dispatcher.dispatch(request, execute=True, pull=True, push=True))
    result["replied"] = False
    return result


def handle_claimed(claimed_path: Path, token: str) -> None:
    record = order_inbox.load(claimed_path)
    tid, channel, ts = record["task_id"], record["channel"], record["ts"]

    outbox = order_inbox.load_outbox(tid)
    if outbox is None or outbox.get("status") == "DISPATCHING":
        outbox = resolve_outcome(record, outbox)
        order_inbox.write_outbox(tid, outbox)

    if not outbox.get("replied"):
        reply(token, channel, ts, format_reply(tid, outbox))
        outbox["replied"] = True
        order_inbox.write_outbox(tid, outbox)

    order_inbox.archive(claimed_path)


def process_pending(path: Path, token: str) -> None:
    record = order_inbox.load(path)
    tid, text, channel, ts = record["task_id"], record["text"], record["channel"], record["ts"]
    sender = record.get("user")

    if not order_dispatcher.EXECUTE_RE.search(text):
        reply(
            token, channel, ts,
            f"NOTE [{tid}]: no [EXECUTE ORDER NNN] found — send an Order-formatted "
            "message (see AGENT_RULES.md) to trigger execution.",
        )
        order_inbox.mark_processed(path, {"status": "IGNORED", "reason": "not an EXECUTE ORDER message"})
        return

    allowed_senders = load_allowed_senders()
    if sender not in allowed_senders:
        # Fail closed: an empty/missing/corrupt allowlist rejects everyone
        # rather than silently letting every sender through. This check
        # runs before claim()/dispatch() -- an unauthorized attempt never
        # reaches order_dispatcher.py at all.
        reason = "sender not allowed" if allowed_senders else "sender allowlist is empty or unreadable"
        reply(token, channel, ts, f"REJECTED [{tid}]: {reason}")
        order_inbox.mark_processed(path, {"status": "REJECTED", "error": reason, "sender": sender})
        return

    existing = order_inbox.load_outbox(tid)
    if existing is not None and existing.get("status") not in (None, "DISPATCHING"):
        # Duplicate delivery of an already-completed task_id -- e.g. the
        # watcher retried after its own ACK failed even though the durable
        # write and full processing had already gone through earlier.
        order_inbox.mark_processed(path, {"status": "DUPLICATE", "original_status": existing.get("status")})
        return

    record["claimed_at"] = order_dispatcher.now_iso()
    order_inbox.write_pending(record)
    claimed_path = order_inbox.claim(path)
    if claimed_path is None:
        return  # another process claimed it first
    handle_claimed(claimed_path, token)


def run_once(token: str) -> None:
    # Recovery sweep first: anything left in claimed/ from a prior crashed run.
    for path in order_inbox.list_claimed():
        try:
            handle_claimed(path, token)
        except Exception:
            logger.exception("failed to recover claimed %s; left for retry", path.name)

    for path in order_inbox.list_pending():
        try:
            process_pending(path, token)
        except Exception:
            logger.exception("failed to process pending %s; left for retry", path.name)


def run() -> None:
    configure_logging()
    pc_id = os.environ.get("CODEX_PC_ID")
    if pc_id != "codex-pc2":
        raise RuntimeError(f"order_inbox_consumer is restricted to codex-pc2; current CODEX_PC_ID='{pc_id}'.")
    token = os.environ.get("OPENACP_SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("OPENACP_SLACK_BOT_TOKEN is not configured")

    with ConsumerLock():
        while True:
            run_once(token)
            time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
