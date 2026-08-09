"""Durable local inbox for Slack-originated messages.

Slack messages must be persisted to disk before they are acknowledged, so an
ACK means "safely queued", not merely "seen". Consumers (order_inbox_consumer.py)
read pending/, act on the record, then move it to processed/ so a restart never
reprocesses an already-handled message.
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(r"C:\lab\vsurf_capital\common")
INBOX_DIR = COMMON_ROOT / ".runtime" / "inbox"
PENDING_DIR = INBOX_DIR / "pending"
PROCESSED_DIR = INBOX_DIR / "processed"

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_.\-]")


def task_id(channel: str, ts: str) -> str:
    return _UNSAFE_CHARS.sub("_", f"{channel}-{ts}")


def _atomic_write(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def write_pending(record: dict[str, Any]) -> Path:
    """Atomically persist a Slack message record. Raises on failure (caller must not ACK)."""
    tid = record["task_id"]
    path = PENDING_DIR / f"{tid}.json"
    _atomic_write(path, record)
    return path


def list_pending() -> list[Path]:
    if not PENDING_DIR.is_dir():
        return []
    return sorted(PENDING_DIR.glob("*.json"), key=lambda p: p.name)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def mark_processed(path: Path, result: dict[str, Any]) -> Path:
    """Merge `result` into the record and move it out of pending/ atomically."""
    record = load(path)
    record["result"] = result
    dest = PROCESSED_DIR / path.name
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_write(dest, record)
    path.unlink(missing_ok=True)
    return dest
