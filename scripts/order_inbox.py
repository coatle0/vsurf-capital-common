"""Durable local inbox for Slack-originated messages.

State machine (each transition is a single atomic filesystem operation):

    pending/<task_id>.json      -- written by the ingress watcher; ACK only
                                    follows a successful write here.
      | claim() = os.rename (fails with FileNotFoundError for a second
      |           claimant -- this IS the single-owner guarantee)
      v
    claimed/<task_id>.json
      | write_outbox() as often as needed while resolving the outcome
      v
    outbox/<task_id>.json       -- durable result, independent of whether the
                                    Slack reply has been sent yet (see the
                                    "replied" flag consumers set once the
                                    reply call returns).
      | archive() = os.replace, only after the outcome is terminal and the
      |             reply has been attempted
      v
    processed/<task_id>.json

A crash at any point leaves the record in exactly one of these directories;
order_inbox_consumer.py's recovery sweep resumes from wherever it was left
without ever calling order_dispatcher.dispatch() a second time for real work
that already completed (see order_inbox_consumer.resolve_outcome).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

COMMON_ROOT = Path(r"C:\lab\vsurf_capital\common")
INBOX_DIR = COMMON_ROOT / ".runtime" / "inbox"
PENDING_DIR = INBOX_DIR / "pending"
CLAIMED_DIR = INBOX_DIR / "claimed"
OUTBOX_DIR = INBOX_DIR / "outbox"
PROCESSED_DIR = INBOX_DIR / "processed"

_UNSAFE_CHARS = re.compile(r"[^A-Za-z0-9_.\-]")


def task_id(channel: str, ts: str) -> str:
    return _UNSAFE_CHARS.sub("_", f"{channel}-{ts}")


def _atomic_write(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    temp.replace(path)


def load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


# --- pending -----------------------------------------------------------

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


def mark_processed(path: Path, result: dict[str, Any]) -> Path:
    """Move a pending/ record straight to processed/ (for messages that never
    needed the claim/outbox machinery, e.g. non-Order chat)."""
    record = load(path)
    record["result"] = result
    dest = PROCESSED_DIR / path.name
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    _atomic_write(dest, record)
    path.unlink(missing_ok=True)
    return dest


# --- claimed -------------------------------------------------------------

def claim(path: Path) -> Path | None:
    """Atomically move pending/<name> -> claimed/<name>. Returns None if
    another process already claimed it first (source vanished)."""
    CLAIMED_DIR.mkdir(parents=True, exist_ok=True)
    dest = CLAIMED_DIR / path.name
    try:
        path.rename(dest)
    except FileNotFoundError:
        return None
    return dest


def list_claimed() -> list[Path]:
    if not CLAIMED_DIR.is_dir():
        return []
    return sorted(CLAIMED_DIR.glob("*.json"), key=lambda p: p.name)


def archive(claimed_path: Path) -> Path:
    """Move claimed/<name> -> processed/<name>. Only call once the outcome
    is terminal (not DISPATCHING) and a reply attempt has been made."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED_DIR / claimed_path.name
    claimed_path.replace(dest)
    return dest


# --- outbox ----------------------------------------------------------------

def write_outbox(tid: str, record: dict[str, Any]) -> Path:
    """Durably record (or overwrite) the outcome for a task_id, independent
    of whether the Slack reply has been sent."""
    path = OUTBOX_DIR / f"{tid}.json"
    _atomic_write(path, record)
    return path


def load_outbox(tid: str) -> dict[str, Any] | None:
    path = OUTBOX_DIR / f"{tid}.json"
    if not path.is_file():
        return None
    return load(path)


def task_exists(tid: str) -> bool:
    """Return whether a durable record for *tid* exists in any lifecycle state."""
    filename = f"{tid}.json"
    return any((directory / filename).is_file() for directory in (
        PENDING_DIR, CLAIMED_DIR, OUTBOX_DIR, PROCESSED_DIR
    ))
