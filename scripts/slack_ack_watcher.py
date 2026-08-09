"""Post an immediate Slack ACK independently of the slower OpenACP worker."""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

CHANNEL_ID = os.environ.get("VSURF_SLACK_CHANNEL_ID", "C0BNWS9QKDK")
POLL_SECONDS = float(os.environ.get("VSURF_SLACK_ACK_POLL_SECONDS", "2"))
STATE_PATH = Path(os.environ.get("VSURF_SLACK_ACK_STATE", r"C:\lab\.openacp\slack_ack_state.json"))


def api(method: str, token: str, payload: dict[str, str]) -> dict:
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(f"Slack {method} failed: {result.get('error', 'unknown_error')}")
    return result


def is_human_message(message: dict, bot_user_id: str) -> bool:
    return bool(
        message.get("user")
        and message.get("user") != bot_user_id
        and not message.get("bot_id")
        and not message.get("subtype")
        and message.get("text", "").strip()
    )


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


def run() -> None:
    token = os.environ.get("OPENACP_SLACK_BOT_TOKEN")
    bot_user_id = os.environ.get("VSURF_SLACK_BOT_USER_ID", "U0BPUB9ES8G")
    pc_id = os.environ.get("CODEX_PC_ID", "unknown-pc")
    if not token:
        raise RuntimeError("OPENACP_SLACK_BOT_TOKEN is not configured")

    cursor = load_cursor()
    while True:
        try:
            history = api("conversations.history", token, {"channel": CHANNEL_ID, "limit": "25"})
            messages = sorted(history.get("messages", []), key=lambda item: float(item["ts"]))
            for message in messages:
                ts = float(message["ts"])
                if ts <= cursor:
                    continue
                if is_human_message(message, bot_user_id):
                    api(
                        "chat.postMessage",
                        token,
                        {
                            "channel": CHANNEL_ID,
                            "thread_ts": message["ts"],
                            "text": f"ACK [{pc_id}] — received; starting work.",
                        },
                    )
                cursor = max(cursor, ts)
                save_cursor(cursor)
        except Exception:
            # Keep the watcher alive across transient Slack/network failures.
            time.sleep(max(POLL_SECONDS, 5))
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    run()
