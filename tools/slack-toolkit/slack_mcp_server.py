"""Slack MCP server for Grok / local stdio clients.

Uses the workspace bot token. Token resolution order:
  SLACK_BOT_TOKEN -> OPENACP_SLACK_BOT_TOKEN

Never prints token values.
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("slack")

DEFAULT_TYPES = "public_channel,private_channel"
DEFAULT_HISTORY_LIMIT = 20
MAX_LIMIT = 200


def _token() -> str:
    token = (
        os.environ.get("SLACK_BOT_TOKEN")
        or os.environ.get("OPENACP_SLACK_BOT_TOKEN")
        or ""
    ).strip()
    if not token:
        raise RuntimeError(
            "Slack token missing: set SLACK_BOT_TOKEN or OPENACP_SLACK_BOT_TOKEN"
        )
    return token


def slack_api(method: str, payload: dict | None = None) -> dict:
    body: dict[str, str] = {}
    for key, value in (payload or {}).items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            body[key] = "true" if value else "false"
        else:
            body[key] = str(value)
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=urllib.parse.urlencode(body).encode("utf-8"),
        headers={"Authorization": f"Bearer {_token()}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Slack HTTP {exc.code} on {method}: {detail}") from exc
    if not result.get("ok"):
        raise RuntimeError(f"Slack {method} failed: {result.get('error', 'unknown_error')}")
    return result


def _wrap(fn, *args, **kwargs):
    try:
        return {"ok": True, **fn(*args, **kwargs)}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


def _clamp_limit(limit: int, default: int = DEFAULT_HISTORY_LIMIT) -> int:
    try:
        value = int(limit)
    except (TypeError, ValueError):
        value = default
    return max(1, min(value, MAX_LIMIT))


def _public_channel(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "name": item.get("name"),
        "is_private": bool(item.get("is_private")),
        "is_im": bool(item.get("is_im")),
        "is_mpim": bool(item.get("is_mpim")),
        "is_archived": bool(item.get("is_archived")),
        "is_member": item.get("is_member"),
        "num_members": item.get("num_members"),
        "topic": ((item.get("topic") or {}).get("value") or ""),
        "purpose": ((item.get("purpose") or {}).get("value") or ""),
    }


def _public_message(item: dict) -> dict:
    return {
        "ts": item.get("ts"),
        "thread_ts": item.get("thread_ts"),
        "user": item.get("user"),
        "bot_id": item.get("bot_id"),
        "text": item.get("text") or "",
        "reply_count": item.get("reply_count"),
        "subtype": item.get("subtype"),
    }


def _auth_test_body() -> dict:
    result = slack_api("auth.test")
    return {
        "url": result.get("url"),
        "team": result.get("team"),
        "team_id": result.get("team_id"),
        "user": result.get("user"),
        "user_id": result.get("user_id"),
        "bot_id": result.get("bot_id"),
    }


def _list_conversations_body(
    types: str = DEFAULT_TYPES,
    limit: int = 100,
    cursor: str = "",
    exclude_archived: bool = True,
) -> dict:
    result = slack_api(
        "conversations.list",
        {
            "types": types or DEFAULT_TYPES,
            "limit": _clamp_limit(limit, 100),
            "cursor": cursor,
            "exclude_archived": exclude_archived,
        },
    )
    channels = [_public_channel(item) for item in result.get("channels") or []]
    return {
        "channels": channels,
        "count": len(channels),
        "next_cursor": ((result.get("response_metadata") or {}).get("next_cursor") or ""),
    }


def _search_channels_body(query: str, limit: int = 20) -> dict:
    needle = (query or "").strip().lower().lstrip("#")
    if not needle:
        raise ValueError("query is required")
    collected: list[dict] = []
    cursor = ""
    while len(collected) < _clamp_limit(limit) and True:
        page = _list_conversations_body(
            types=DEFAULT_TYPES,
            limit=200,
            cursor=cursor,
            exclude_archived=True,
        )
        for item in page["channels"]:
            hay = f"{item.get('name') or ''} {item.get('topic') or ''} {item.get('purpose') or ''}".lower()
            if needle in hay or needle == (item.get("id") or "").lower():
                collected.append(item)
                if len(collected) >= _clamp_limit(limit):
                    break
        cursor = page.get("next_cursor") or ""
        if not cursor:
            break
    return {"channels": collected, "count": len(collected), "query": query}


def _read_channel_body(
    channel: str,
    limit: int = DEFAULT_HISTORY_LIMIT,
    oldest: str = "",
    latest: str = "",
    cursor: str = "",
) -> dict:
    if not (channel or "").strip():
        raise ValueError("channel is required")
    result = slack_api(
        "conversations.history",
        {
            "channel": channel.strip(),
            "limit": _clamp_limit(limit),
            "oldest": oldest,
            "latest": latest,
            "cursor": cursor,
        },
    )
    messages = [_public_message(item) for item in result.get("messages") or []]
    return {
        "channel": channel.strip(),
        "messages": messages,
        "count": len(messages),
        "has_more": bool(result.get("has_more")),
        "next_cursor": ((result.get("response_metadata") or {}).get("next_cursor") or ""),
    }


def _read_thread_body(channel: str, thread_ts: str, limit: int = 50) -> dict:
    if not (channel or "").strip() or not (thread_ts or "").strip():
        raise ValueError("channel and thread_ts are required")
    result = slack_api(
        "conversations.replies",
        {
            "channel": channel.strip(),
            "ts": thread_ts.strip(),
            "limit": _clamp_limit(limit, 50),
        },
    )
    messages = [_public_message(item) for item in result.get("messages") or []]
    return {
        "channel": channel.strip(),
        "thread_ts": thread_ts.strip(),
        "messages": messages,
        "count": len(messages),
        "has_more": bool(result.get("has_more")),
    }


def _send_message_body(channel: str, text: str, thread_ts: str = "") -> dict:
    if not (channel or "").strip():
        raise ValueError("channel is required")
    if not (text or "").strip():
        raise ValueError("text is required")
    result = slack_api(
        "chat.postMessage",
        {
            "channel": channel.strip(),
            "text": text,
            "thread_ts": thread_ts,
        },
    )
    return {
        "channel": result.get("channel") or channel.strip(),
        "ts": result.get("ts"),
        "text": ((result.get("message") or {}).get("text") or text),
    }


def _add_reaction_body(channel: str, timestamp: str, name: str) -> dict:
    if not (channel or "").strip() or not (timestamp or "").strip() or not (name or "").strip():
        raise ValueError("channel, timestamp, and name are required")
    slack_api(
        "reactions.add",
        {
            "channel": channel.strip(),
            "timestamp": timestamp.strip(),
            "name": name.strip().strip(":"),
        },
    )
    return {"channel": channel.strip(), "timestamp": timestamp.strip(), "name": name.strip().strip(":")}


def _conversation_info_body(channel: str) -> dict:
    if not (channel or "").strip():
        raise ValueError("channel is required")
    result = slack_api("conversations.info", {"channel": channel.strip()})
    return {"channel": _public_channel(result.get("channel") or {})}


def _user_info_body(user: str) -> dict:
    if not (user or "").strip():
        raise ValueError("user is required")
    result = slack_api("users.info", {"user": user.strip()})
    profile = result.get("user") or {}
    return {
        "id": profile.get("id"),
        "name": profile.get("name"),
        "real_name": profile.get("real_name"),
        "is_bot": bool(profile.get("is_bot")),
        "deleted": bool(profile.get("deleted")),
        "tz": profile.get("tz"),
    }


@mcp.tool()
def slack_auth_test() -> dict:
    """Verify the Slack bot token and return workspace/bot identity (no secrets)."""
    return _wrap(_auth_test_body)


@mcp.tool()
def slack_list_conversations(
    types: str = DEFAULT_TYPES,
    limit: int = 100,
    cursor: str = "",
    exclude_archived: bool = True,
) -> dict:
    """List Slack conversations the bot can see. types e.g. public_channel,private_channel."""
    return _wrap(_list_conversations_body, types, limit, cursor, exclude_archived)


@mcp.tool()
def slack_search_channels(query: str, limit: int = 20) -> dict:
    """Find channels by name, topic, purpose, or channel ID. Example: vsurf-code-reports."""
    return _wrap(_search_channels_body, query, limit)


@mcp.tool()
def slack_read_channel(
    channel: str,
    limit: int = DEFAULT_HISTORY_LIMIT,
    oldest: str = "",
    latest: str = "",
    cursor: str = "",
) -> dict:
    """Read recent messages from a Slack channel. channel is a channel ID (e.g. C0BQQ8ZBCL8)."""
    return _wrap(_read_channel_body, channel, limit, oldest, latest, cursor)


@mcp.tool()
def slack_read_thread(channel: str, thread_ts: str, limit: int = 50) -> dict:
    """Read a Slack thread. channel is a channel ID; thread_ts is the parent message ts."""
    return _wrap(_read_thread_body, channel, thread_ts, limit)


@mcp.tool()
def slack_send_message(channel: str, text: str, thread_ts: str = "") -> dict:
    """Post a Slack message. Use thread_ts to reply in a thread."""
    return _wrap(_send_message_body, channel, text, thread_ts)


@mcp.tool()
def slack_add_reaction(channel: str, timestamp: str, name: str) -> dict:
    """Add an emoji reaction to a Slack message. name is the emoji shortcode without colons."""
    return _wrap(_add_reaction_body, channel, timestamp, name)


@mcp.tool()
def slack_conversation_info(channel: str) -> dict:
    """Get metadata for one Slack conversation/channel ID."""
    return _wrap(_conversation_info_body, channel)


@mcp.tool()
def slack_user_info(user: str) -> dict:
    """Get public Slack user profile fields for a user ID."""
    return _wrap(_user_info_body, user)


if __name__ == "__main__":
    mcp.run()
