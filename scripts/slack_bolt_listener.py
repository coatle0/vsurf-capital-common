"""Real-time Slack ingress via Socket Mode.

Replaces the REST-polling watcher's role as OpenACP is removed from the
critical path (Windows daemon unsupported upstream, /health and /adapters
404 while the CLI reports the daemon offline, libuv assertions, stale
"active" sessions, Slack adapter bugs that needed node_modules patches).
slack-bolt is Slack's own SDK, not a replacement product -- it only owns
the "receive Slack events" job OpenACP used to do.

Reuses slack_ack_watcher.py's message handling and durability guarantees
unchanged -- only the delivery mechanism changes, from REST polling to a
push-based WebSocket:

  * process_message() / order_inbox.write_pending() -- write-before-ACK,
    unchanged.
  * fetch_new_messages() -- still used once at startup for a bounded
    catch-up pass, because Socket Mode does not redeliver events sent
    while this process was offline.

The narrow gap between "catch-up finishes" and "Socket Mode connects" is
not specially handled: write_pending() is idempotent per task_id, and
order_inbox_consumer's outbox-based duplicate detection already makes a
message arriving via both paths safe.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import slack_ack_watcher as ingress  # noqa: E402  (after sys.path.insert)
import conversation_router  # noqa: E402
from slack_api import api  # noqa: E402
from slack_bolt import App  # noqa: E402
from slack_bolt.adapter.socket_mode import SocketModeHandler  # noqa: E402

LOG_PATH = Path(r"C:\lab\vsurf_capital\common\logs\slack_bolt_listener.log")
logger = logging.getLogger("slack_bolt_listener")


def configure_logging() -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    handler = logging.FileHandler(LOG_PATH, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class Cursor:
    """Mutable holder so the live-event callback can advance the shared
    cursor without nonlocal, and so tests can inspect the current value."""

    def __init__(self, value: float):
        self.value = value

    def advance(self, ts: float) -> None:
        if ts > self.value:
            self.value = ts
            ingress.save_cursor(ts)


def route_human_event(event: dict, token: str, bot_user_id: str, pc_id: str, channel: str) -> None:
    if not ingress.is_human_message(event, bot_user_id):
        return
    root_ts = event.get("thread_ts") or event["ts"]
    conversation_router.route_event(
        event,
        conversation_router.ConversationStore(),
        lambda text: api("chat.postMessage", token, {"channel": channel, "thread_ts": root_ts, "text": text}),
        lambda approval_event, proposal: ingress.enqueue_approved(
            approval_event, proposal, token, pc_id, channel
        ),
    )


def catch_up(token: str, channel: str, bot_user_id: str, pc_id: str, cursor: Cursor) -> None:
    for message in ingress.fetch_new_messages(token, channel, cursor.value):
        ts = float(message["ts"])
        if ts <= cursor.value:
            continue
        route_human_event(message, token, bot_user_id, pc_id, channel)
        cursor.advance(ts)


def handle_live_event(event: dict, token: str, bot_user_id: str, pc_id: str, channel: str, cursor: Cursor) -> None:
    if event.get("channel") != channel:
        return
    ts = float(event["ts"])
    if ts <= cursor.value:
        return
    route_human_event(event, token, bot_user_id, pc_id, channel)
    cursor.advance(ts)


def run() -> None:
    configure_logging()
    pc_id = os.environ.get("CODEX_PC_ID", "unknown-pc")
    if pc_id != "codex-pc2":
        raise RuntimeError(f"slack_bolt_listener is restricted to codex-pc2; current CODEX_PC_ID='{pc_id}'.")
    token = os.environ.get("OPENACP_SLACK_BOT_TOKEN")
    app_token = os.environ.get("OPENACP_SLACK_APP_TOKEN")
    if not token:
        raise RuntimeError("OPENACP_SLACK_BOT_TOKEN is not configured")
    if not app_token:
        raise RuntimeError("OPENACP_SLACK_APP_TOKEN is not configured")
    bot_user_id = os.environ.get("VSURF_SLACK_BOT_USER_ID", "U0BPUB9ES8G")
    channel = ingress.CHANNEL_ID

    cursor = Cursor(ingress.load_cursor())
    logger.info("starting bounded catch-up from cursor=%s", cursor.value)
    catch_up(token, channel, bot_user_id, pc_id, cursor)

    app = App(token=token)

    @app.event("message")
    def _on_message(event: dict) -> None:
        try:
            handle_live_event(event, token, bot_user_id, pc_id, channel, cursor)
        except Exception:
            logger.exception("failed to handle live event ts=%s", event.get("ts"))

    logger.info("catch-up done, starting Socket Mode handler")
    SocketModeHandler(app, app_token).start()


if __name__ == "__main__":
    run()
