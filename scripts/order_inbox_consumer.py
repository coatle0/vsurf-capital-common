"""The "slower worker" slack_ack_watcher.py's docstring refers to: consumes
the durable inbox and wires it to order_dispatcher.py, which previously had
no caller anywhere in this repo.

Every pending record gets a definitive outcome (IGNORED / REJECTED / COMPLETED
/ FAILED) posted back to the originating Slack thread and archived to
processed/ before it is removed from pending/ — nothing is dropped silently.
"""

from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import order_dispatcher
import order_inbox
from slack_api import api

POLL_SECONDS = float(os.environ.get("VSURF_INBOX_POLL_SECONDS", "5"))
LOG_PATH = Path(r"C:\lab\vsurf_capital\common\logs\inbox_consumer\inbox_consumer.log")

logger = logging.getLogger("order_inbox_consumer")


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def reply(token: str, channel: str, thread_ts: str, text: str) -> None:
    api("chat.postMessage", token, {"channel": channel, "thread_ts": thread_ts, "text": text})


def process_one(path: Path, token: str) -> None:
    record = order_inbox.load(path)
    text = record["text"]
    tid = record["task_id"]
    channel = record["channel"]
    ts = record["ts"]

    if not order_dispatcher.EXECUTE_RE.search(text):
        order_inbox.mark_processed(path, {"status": "IGNORED", "reason": "not an EXECUTE ORDER message"})
        return

    try:
        request = order_dispatcher.parse_request(text)
    except order_dispatcher.DispatchError as exc:
        reply(token, channel, ts, f"REJECTED [{tid}]: {exc}")
        order_inbox.mark_processed(path, {"status": "REJECTED", "error": str(exc)})
        return

    result = order_dispatcher.dispatch(request, execute=True, pull=True, push=True)
    if result.status == "COMPLETED":
        commit = (result.commit or "")[:12]
        reply(token, channel, ts, f"COMPLETED [{tid}] order {result.order_id} commit {commit}")
    else:
        reply(token, channel, ts, f"FAILED [{tid}] order {result.order_id}: {result.error}")
    order_inbox.mark_processed(
        path,
        {
            "status": result.status,
            "order_id": result.order_id,
            "commit": result.commit,
            "error": result.error,
        },
    )


def run_once(token: str) -> None:
    for path in order_inbox.list_pending():
        try:
            process_one(path, token)
        except Exception:
            # Leave the file in pending/ so a transient failure (Slack API
            # outage, git contention) is retried on the next cycle instead
            # of the order being silently lost.
            logger.exception("failed to process %s; left in pending for retry", path.name)


def run() -> None:
    configure_logging()
    pc_id = os.environ.get("CODEX_PC_ID")
    if pc_id != "codex-pc2":
        raise RuntimeError(f"order_inbox_consumer is restricted to codex-pc2; current CODEX_PC_ID='{pc_id}'.")
    token = os.environ.get("OPENACP_SLACK_BOT_TOKEN")
    if not token:
        raise RuntimeError("OPENACP_SLACK_BOT_TOKEN is not configured")

    while True:
        run_once(token)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
