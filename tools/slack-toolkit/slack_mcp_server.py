"""Slack MCP server for Grok / local stdio clients.

Uses the workspace bot token. Token resolution order:
  process SLACK_BOT_TOKEN -> process OPENACP_SLACK_BOT_TOKEN
  -> HKCU\\Environment SLACK_BOT_TOKEN -> HKCU\\Environment OPENACP_SLACK_BOT_TOKEN

Unexpanded Grok placeholders such as ${OPENACP_SLACK_BOT_TOKEN} are ignored.
Never prints token values.

Latency: reuse one HTTPS connection, cache the resolved token, resolve known
channel names locally, and default history reads to 3 messages (limit=1 for a
latest-message check).
"""
from __future__ import annotations

import http.client
import json
import os
import pathlib
import ssl
import sys
import threading
import urllib.error
import urllib.parse
import urllib.request

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("slack")

DEFAULT_TYPES = "public_channel,private_channel"
DEFAULT_HISTORY_LIMIT = 3
MAX_LIMIT = 200
_LAB_ROOT = pathlib.Path(r"C:\lab").resolve()
_API_HOST = "slack.com"
_API_TIMEOUT = 20
_MAX_READ_FILE_BYTES = 512 * 1024
_TEXT_FILETYPES = {"text", "markdown", "plain", "python", "javascript", "json", "yaml"}
_TOKEN_NAMES = ("SLACK_BOT_TOKEN", "OPENACP_SLACK_BOT_TOKEN")
_KNOWN_CHANNEL_ROWS = (
    {"id": "C0BR8722F6C", "name": "vsurf-skill"},
    {"id": "C0BSX931CPJ", "name": "vsurf-code-reports"},
    {"id": "C0BS4RXHV25", "name": "vsurf-agent-control"},
)
KNOWN_CHANNELS: dict[str, dict] = {}
for _row in _KNOWN_CHANNEL_ROWS:
    KNOWN_CHANNELS[_row["name"]] = _row
    KNOWN_CHANNELS[_row["id"].lower()] = _row

_cached_token = ""
_http_conn: http.client.HTTPSConnection | None = None
_http_lock = threading.Lock()


def _usable_token(value: str | None) -> str:
    text = (value or "").strip()
    if not text:
        return ""
    if text.startswith("${") and text.endswith("}"):
        return ""
    return text


def _user_env(name: str) -> str:
    if sys.platform != "win32":
        return ""
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, "Environment") as key:
            value, _reg_type = winreg.QueryValueEx(key, name)
    except OSError:
        return ""
    if not isinstance(value, str):
        value = "" if value is None else str(value)
    return _usable_token(value)


def _reset_runtime_state() -> None:
    global _cached_token, _http_conn
    with _http_lock:
        if _http_conn is not None:
            try:
                _http_conn.close()
            except Exception:
                pass
        _http_conn = None
        _cached_token = ""


def _token() -> str:
    global _cached_token
    if _cached_token:
        return _cached_token
    for name in _TOKEN_NAMES:
        token = _usable_token(os.environ.get(name))
        if token:
            _cached_token = token
            return token
    for name in _TOKEN_NAMES:
        token = _user_env(name)
        if token:
            _cached_token = token
            return token
    raise RuntimeError(
        "Slack token missing: set User env OPENACP_SLACK_BOT_TOKEN "
        "(unexpanded ${VAR} in Grok config is ignored)"
    )


def _close_http_conn_locked() -> None:
    global _http_conn
    if _http_conn is None:
        return
    try:
        _http_conn.close()
    except Exception:
        pass
    _http_conn = None


def _http_post(path: str, body: bytes, headers: dict[str, str]) -> bytes:
    global _http_conn
    last_exc: Exception | None = None
    for _attempt in range(2):
        with _http_lock:
            try:
                if _http_conn is None:
                    _http_conn = http.client.HTTPSConnection(
                        _API_HOST, timeout=_API_TIMEOUT
                    )
                _http_conn.request("POST", path, body=body, headers=headers)
                response = _http_conn.getresponse()
                payload = response.read()
                status = response.status
            except (http.client.HTTPException, OSError, ssl.SSLError) as exc:
                last_exc = exc
                _close_http_conn_locked()
                continue
            if status < 200 or status >= 300:
                detail = payload.decode("utf-8", errors="replace")[:300]
                raise RuntimeError(f"Slack HTTP {status} on {path}: {detail}")
            return payload
    raise RuntimeError(
        f"Slack HTTP failed on {path}: {type(last_exc).__name__}"
    ) from last_exc


def _http_get_authorized(url: str) -> bytes:
    if not (url or "").startswith("https://"):
        raise ValueError("download url must be https")
    req = urllib.request.Request(
        url,
        method="GET",
        headers={"Authorization": f"Bearer {_token()}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as response:
            status = response.status
            payload = response.read()
    except urllib.error.HTTPError as exc:
        exc.read()
        raise RuntimeError(f"Slack file download HTTP {exc.code}") from exc
    if status < 200 or status >= 300:
        raise RuntimeError(f"Slack file download HTTP {status}")
    return payload


def _http_upload_bytes(url: str, data: bytes) -> None:
    if not (url or "").startswith("https://"):
        raise ValueError("upload url must be https")
    req = urllib.request.Request(
        url,
        data=data,
        method="POST",
        headers={
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(data)),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=_API_TIMEOUT) as response:
            status = response.status
            response.read()
    except urllib.error.HTTPError as exc:
        exc.read()
        raise RuntimeError(f"Slack file binary upload HTTP {exc.code}") from exc
    if status < 200 or status >= 300:
        raise RuntimeError(f"Slack file binary upload HTTP {status}")


def slack_api(method: str, payload: dict | None = None) -> dict:
    body: dict[str, str] = {}
    for key, value in (payload or {}).items():
        if value is None or value == "":
            continue
        if isinstance(value, bool):
            body[key] = "true" if value else "false"
        else:
            body[key] = str(value)
    raw = _http_post(
        f"/api/{method}",
        urllib.parse.urlencode(body).encode("utf-8"),
        {
            "Authorization": f"Bearer {_token()}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Connection": "keep-alive",
        },
    )
    try:
        result = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Slack {method} returned non-JSON") from exc
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


def _lookup_known_channel(channel: str) -> dict | None:
    key = (channel or "").strip().lstrip("#").lower()
    if not key:
        return None
    return KNOWN_CHANNELS.get(key)


def _resolve_channel(channel: str) -> str:
    known = _lookup_known_channel(channel)
    if known:
        return known["id"]
    return (channel or "").strip()


def _md_filename(title: str, filename: str) -> str:
    raw = (filename or title or "note").strip()
    raw = raw.replace("\\", "_").replace("/", "_").replace(":", "_")
    if not raw:
        raw = "note"
    if not raw.lower().endswith(".md"):
        raw += ".md"
    return raw


def _read_md_path(path: str) -> tuple[str, str]:
    resolved = pathlib.Path(path).expanduser().resolve()
    if resolved.suffix.lower() != ".md":
        raise ValueError("path must end with .md")
    try:
        resolved.relative_to(_LAB_ROOT)
    except ValueError as exc:
        raise ValueError("markdown path must be under C:\\lab") from exc
    if not resolved.is_file():
        raise ValueError("markdown file not found")
    return resolved.read_text(encoding="utf-8"), resolved.name


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


def _public_file(item: dict) -> dict:
    return {
        "id": item.get("id"),
        "name": item.get("name") or "",
        "title": item.get("title") or "",
        "mimetype": item.get("mimetype") or "",
        "filetype": item.get("filetype") or "",
        "size": item.get("size"),
    }


def _is_text_file(name: str, mimetype: str, filetype: str) -> bool:
    lower = (name or "").lower()
    mime = (mimetype or "").lower()
    kind = (filetype or "").lower()
    if lower.endswith((".md", ".txt", ".markdown", ".json", ".yaml", ".yml", ".py", ".toml")):
        return True
    if mime.startswith("text/"):
        return True
    return kind in _TEXT_FILETYPES


def _public_message(item: dict) -> dict:
    files = [_public_file(entry) for entry in (item.get("files") or []) if entry.get("id")]
    return {
        "ts": item.get("ts"),
        "thread_ts": item.get("thread_ts"),
        "user": item.get("user"),
        "bot_id": item.get("bot_id"),
        "text": item.get("text") or "",
        "reply_count": item.get("reply_count"),
        "subtype": item.get("subtype"),
        "files": files,
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
    known = _lookup_known_channel(needle)
    if known:
        return {
            "channels": [_public_channel(known)],
            "count": 1,
            "query": query,
        }
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
    resolved = _resolve_channel(channel)
    if not resolved:
        raise ValueError("channel is required")
    result = slack_api(
        "conversations.history",
        {
            "channel": resolved,
            "limit": _clamp_limit(limit),
            "oldest": oldest,
            "latest": latest,
            "cursor": cursor,
        },
    )
    messages = [_public_message(item) for item in result.get("messages") or []]
    return {
        "channel": resolved,
        "messages": messages,
        "count": len(messages),
        "has_more": bool(result.get("has_more")),
        "next_cursor": ((result.get("response_metadata") or {}).get("next_cursor") or ""),
    }


def _read_thread_body(channel: str, thread_ts: str, limit: int = 50) -> dict:
    resolved = _resolve_channel(channel)
    if not resolved or not (thread_ts or "").strip():
        raise ValueError("channel and thread_ts are required")
    result = slack_api(
        "conversations.replies",
        {
            "channel": resolved,
            "ts": thread_ts.strip(),
            "limit": _clamp_limit(limit, 50),
        },
    )
    messages = [_public_message(item) for item in result.get("messages") or []]
    return {
        "channel": resolved,
        "thread_ts": thread_ts.strip(),
        "messages": messages,
        "count": len(messages),
        "has_more": bool(result.get("has_more")),
    }


def _send_message_body(channel: str, text: str, thread_ts: str = "") -> dict:
    resolved = _resolve_channel(channel)
    if not resolved:
        raise ValueError("channel is required")
    if not (text or "").strip():
        raise ValueError("text is required")
    result = slack_api(
        "chat.postMessage",
        {
            "channel": resolved,
            "text": text,
            "thread_ts": thread_ts,
        },
    )
    return {
        "channel": result.get("channel") or resolved,
        "ts": result.get("ts"),
        "text": ((result.get("message") or {}).get("text") or text),
    }


def _post_markdown_body(
    channel: str,
    title: str = "",
    markdown: str = "",
    path: str = "",
    filename: str = "",
    initial_comment: str = "",
) -> dict:
    resolved = _resolve_channel(channel)
    if not resolved:
        raise ValueError("channel is required")
    source_name = ""
    text = markdown
    if (path or "").strip():
        text, source_name = _read_md_path(path)
    if not (text or "").strip():
        raise ValueError("markdown or path is required")
    fname = _md_filename(title, filename or source_name)
    heading = (title or "").strip() or pathlib.Path(fname).stem
    payload = text.encode("utf-8")
    ticket = slack_api(
        "files.getUploadURLExternal",
        {"filename": fname, "length": str(len(payload))},
    )
    upload_url = ticket.get("upload_url") or ""
    file_id = ticket.get("file_id") or ""
    if not upload_url or not file_id:
        raise RuntimeError("Slack upload URL missing")
    _http_upload_bytes(upload_url, payload)
    done = slack_api(
        "files.completeUploadExternal",
        {
            "files": json.dumps([{"id": file_id, "title": heading}]),
            "channel_id": resolved,
            "initial_comment": initial_comment,
        },
    )
    uploaded = ((done.get("files") or [{}])[0]) if isinstance(done.get("files"), list) else {}
    return {
        "channel": resolved,
        "file_id": uploaded.get("id") or file_id,
        "filename": uploaded.get("name") or fname,
        "title": uploaded.get("title") or heading,
        "permalink": uploaded.get("permalink") or "",
    }


def _read_file_body(file_id: str, save_path: str = "") -> dict:
    fid = (file_id or "").strip()
    if not fid:
        raise ValueError("file_id is required")
    info = slack_api("files.info", {"file": fid})
    item = info.get("file") or {}
    name = item.get("name") or ""
    mime = item.get("mimetype") or ""
    kind = item.get("filetype") or ""
    if not _is_text_file(name, mime, kind):
        raise ValueError("only text/markdown files can be read")
    url = item.get("url_private_download") or item.get("url_private") or ""
    if not url:
        raise RuntimeError("Slack file url missing")
    raw = _http_get_authorized(url)
    if len(raw) > _MAX_READ_FILE_BYTES:
        raise ValueError(f"file exceeds {_MAX_READ_FILE_BYTES} bytes")
    text = raw.decode("utf-8")
    saved = ""
    dest = (save_path or "").strip()
    if dest:
        resolved = pathlib.Path(dest).expanduser().resolve()
        try:
            resolved.relative_to(_LAB_ROOT)
        except ValueError as exc:
            raise ValueError("save_path must be under C:\\lab") from exc
        resolved.parent.mkdir(parents=True, exist_ok=True)
        resolved.write_text(text, encoding="utf-8")
        saved = str(resolved)
    return {
        "file_id": item.get("id") or fid,
        "filename": name,
        "title": item.get("title") or "",
        "mimetype": mime,
        "bytes": len(raw),
        "text": text,
        "saved": saved,
    }


def _add_reaction_body(channel: str, timestamp: str, name: str) -> dict:
    resolved = _resolve_channel(channel)
    if not resolved or not (timestamp or "").strip() or not (name or "").strip():
        raise ValueError("channel, timestamp, and name are required")
    slack_api(
        "reactions.add",
        {
            "channel": resolved,
            "timestamp": timestamp.strip(),
            "name": name.strip().strip(":"),
        },
    )
    return {
        "channel": resolved,
        "timestamp": timestamp.strip(),
        "name": name.strip().strip(":"),
    }


def _conversation_info_body(channel: str) -> dict:
    resolved = _resolve_channel(channel)
    if not resolved:
        raise ValueError("channel is required")
    result = slack_api("conversations.info", {"channel": resolved})
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
    """Find channels by name. Known IDs: #vsurf-skill=C0BR8722F6C, #vsurf-code-reports=C0BSX931CPJ, #vsurf-agent-control=C0BS4RXHV25. Those names resolve locally; prefer slack_read_channel with the ID."""
    return _wrap(_search_channels_body, query, limit)


@mcp.tool()
def slack_read_channel(
    channel: str,
    limit: int = DEFAULT_HISTORY_LIMIT,
    oldest: str = "",
    latest: str = "",
    cursor: str = "",
) -> dict:
    """Read recent Slack messages. Use C0BR8722F6C (#vsurf-skill), C0BSX931CPJ (#vsurf-code-reports), or C0BS4RXHV25 (#vsurf-agent-control); those names also resolve. Default limit=3. Pass limit=1 for a latest-message check. Returns caption text plus attached file ids, not file bodies. Do not search channels first."""
    return _wrap(_read_channel_body, channel, limit, oldest, latest, cursor)


@mcp.tool()
def slack_read_file(file_id: str, save_path: str = "") -> dict:
    """Read a Slack file body in memory. Pass file_id from slack_read_channel.files. Default does not write disk. save_path is optional and must be under C:\\lab. Text/markdown only."""
    return _wrap(_read_file_body, file_id, save_path)


@mcp.tool()
def slack_read_thread(channel: str, thread_ts: str, limit: int = 50) -> dict:
    """Read a Slack thread. channel is a channel ID; thread_ts is the parent message ts."""
    return _wrap(_read_thread_body, channel, thread_ts, limit)


@mcp.tool()
def slack_send_message(channel: str, text: str, thread_ts: str = "") -> dict:
    """Short one-line ACK only. Prompts, reports, and any document text must use slack_post_markdown."""
    return _wrap(_send_message_body, channel, text, thread_ts)


@mcp.tool()
def slack_post_markdown(
    channel: str,
    title: str = "",
    markdown: str = "",
    path: str = "",
    filename: str = "",
    initial_comment: str = "",
) -> dict:
    """Post Slack text as a Markdown file. Pass path to a C:\\lab .md file, or markdown body. Do not dump documents via slack_send_message."""
    return _wrap(
        _post_markdown_body,
        channel,
        title,
        markdown,
        path,
        filename,
        initial_comment,
    )


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
