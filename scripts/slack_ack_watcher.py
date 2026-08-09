"""Durable Slack ingress: persist every human message to the local inbox
before acknowledging it. ACK means "safely queued on disk", not "seen".

order_inbox_consumer.py is the slower worker that actually consumes the
queue and executes Orders; this script's only job is fast, lossless intake.
"""

from __future__ import annotations

import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import order_inbox
from slack_api import api

CHANNEL_ID = os.environ.get("VSURF_SLACK_CHANNEL_ID", "C0BNWS9QKDK")
POLL_SECONDS = float(os.environ.get("VSURF_SLACK_ACK_POLL_SECONDS", "2"))
STATE_PATH = Path(os.environ.get("VSURF_SLACK_ACK_STATE", r"C:\lab\.openacp\slack_ack_state.json"))
LOG_PATH = Path(r"C:\lab\vsurf_capital\common\logs\slack_ack_watcher.log")

logger = logging.getLogger("slack_ack_watcher")


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def is_human_message(message: dict, bot_user_id: str) -> bool:
    return bool(
        message.get("user")
        and message.get("user") != bot_user_id
        and not message.get("bot_id")
        and not message.get("subtype")
        and message.get("text", "").strip()
    )


def fetch_new_messages(token: str, channel: str, since_ts: float) -> list[dict]:
    """Fetch every message strictly after since_ts, paginating past Slack's
    per-call limit so a catch-up after downtime never silently drops history."""
    collected: list[dict] = []
    cursor: str | None = None
    while True:
        payload = {"channel": channel, "oldest": str(since_ts), "limit": "200"}
        if cursor:
            payload["cursor"] = cursor
        page = api("conversations.history", token, payload)
        collected.extend(page.get("messages", []))
        cursor = (page.get("response_metadata") or {}).get("next_cursor") or None
        if not cursor or not page.get("has_more"):
            break
    return sorted(collected, key=lambda item: float(item["ts"]))


def load_cursor() -> float:
    try:
        return float(json.loads(STATE_PATH.read_text(encoding="utf-8"))["last_ts"])
    except (FileNotFoundError, KeyError, ValueError, TypeError, json.JSONDecodeError):
        return time.time()


def save_cursor(ts: float) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    temp = STATE_PATH.with_suffix(".tmp")
    temp.write_text(json.dumps({"last_ts": ts}), encoding="utf-8")
    temp.replace(STATE_PATH)


def process_message(message: dict, token: str, bot_user_id: str, pc_id: str, channel: str) -> None:
    ts = message["ts"]
    if not is_human_message(message, bot_user_id):
        return
    tid = order_inbox.task_id(channel, ts)
    record = {
        "task_id": tid,
        "channel": channel,
        "ts": ts,
        "user": message.get("user"),
        "text": message.get("text", ""),
        "received_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "pc_id": pc_id,
    }
    # Durable write MUST succeed before we ACK. If this raises, the caller
    # must not advance the cursor, so the message is retried next poll.
    order_inbox.write_pending(record)
    api(
        "chat.postMessage",
        token,
        {
            "channel": channel,
            "thread_ts": ts,
            "text": f"ACK [{pc_id}] RECEIVED task={tid}",
        },
    )


def run() -> None:
    configure_logging()
    token = os.environ.get("OPENACP_SLACK_BOT_TOKEN")
    bot_user_id = os.environ.get("VSURF_SLACK_BOT_USER_ID", "U0BPUB9ES8G")
    pc_id = os.environ.get("CODEX_PC_ID", "unknown-pc")
    if not token:
        raise RuntimeError("OPENACP_SLACK_BOT_TOKEN is not configured")
    if "VSURF_SLACK_CHANNEL_ID" not in os.environ:
        logger.warning("VSURF_SLACK_CHANNEL_ID not set; falling back to hardcoded default %s", CHANNEL_ID)
    if "VSURF_SLACK_BOT_USER_ID" not in os.environ:
        logger.warning("VSURF_SLACK_BOT_USER_ID not set; falling back to hardcoded default %s", bot_user_id)

    cursor = load_cursor()
    while True:
        try:
            for message in fetch_new_messages(token, CHANNEL_ID, cursor):
                ts = float(message["ts"])
                if ts <= cursor:
                    continue
                process_message(message, token, bot_user_id, pc_id, CHANNEL_ID)
                cursor = ts
                save_cursor(cursor)
        except Exception:
            logger.exception("slack_ack_watcher poll iteration failed")
            time.sleep(max(POLL_SECONDS, 5))
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
