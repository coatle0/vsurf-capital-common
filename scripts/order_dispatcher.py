"""VSURF Git-backed Order dispatcher.

This is deliberately a thin, local execution layer. Slack/OpenACP supplies the
message; this program validates it, resolves the canonical Git Order, prevents
duplicate execution, invokes the requested agent, and records a machine-readable
result. Tokens are never read or logged here.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Sequence


COMMON_ROOT = Path(r"C:\lab\vsurf_capital\common")
MCP_REGISTRY_PATH = COMMON_ROOT / "mcp_registry.json"
ORDERS_DIR = COMMON_ROOT / "orders"
RUNTIME_DIR = COMMON_ROOT / ".runtime"
LOG_DIR = COMMON_ROOT / "logs" / "dispatcher"
ALLOWED_ROOT = Path(r"C:\lab")
EXECUTE_RE = re.compile(r"(?im)^\[?EXECUTE\s+ORDER\s+(\d{3})\]?\s*$")
FIELD_RE = re.compile(r"(?im)^(executor|order|project)\s*:\s*(.+?)\s*$")
SLACK_SIGNATURE_RE = re.compile(
    r"\s*\*다음을 사용하여 보냄\*\s*"
    r"(?:Claude|ChatGPT|Codex|<@[A-Z0-9]+>)?\s*$",
    re.IGNORECASE,
)


class DispatchError(RuntimeError):
    """Expected, user-facing dispatch rejection."""


@dataclass(frozen=True)
class DispatchRequest:
    order_id: str
    executor: str
    order_path: str
    project_path: str
    # Both optional and additive -- callers that only have a message
    # string (no inbox context, e.g. manual --message-file runs) get the
    # exact prior behavior with these left at their default of None.
    task_id: str | None = None
    raw_message: str | None = None


@dataclass
class DispatchResult:
    order_id: str
    executor: str
    status: str
    project_path: str
    order_path: str
    started_at: str
    finished_at: str | None = None
    exit_code: int | None = None
    commit: str | None = None
    summary_file: str | None = None
    error: str | None = None


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def canonical(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def is_within(path: Path, root: Path) -> bool:
    try:
        canonical(path).relative_to(canonical(root))
        return True
    except ValueError:
        return False


def clean_field_value(value: str) -> str:
    """Remove a known Slack client attribution glued to a field value.

    Slack can append the attribution to the final line without inserting a
    newline. Keep the raw message untouched and normalize only parsed control
    fields so paths and executor names remain valid.
    """
    return SLACK_SIGNATURE_RE.sub("", value).strip()


def parse_request(message: str, task_id: str | None = None) -> DispatchRequest:
    match = EXECUTE_RE.search(message)
    if not match:
        raise DispatchError("Expected '[EXECUTE ORDER NNN]' on its own line.")
    order_id = match.group(1)
    fields = {
        key.lower(): clean_field_value(value)
        for key, value in FIELD_RE.findall(message)
    }
    executor = fields.get("executor", "").lower()
    if executor not in {"codex", "claude", "available"}:
        raise DispatchError("executor must be codex, claude, or available.")

    candidates = sorted(ORDERS_DIR.glob(f"{order_id}_*.md"))
    if len(candidates) != 1:
        raise DispatchError(
            f"Order {order_id} must resolve to exactly one file; found {len(candidates)}."
        )
    canonical_order = canonical(candidates[0])
    supplied_order = fields.get("order")
    if supplied_order:
        supplied = Path(supplied_order)
        if not supplied.is_absolute():
            supplied = COMMON_ROOT / supplied
        if canonical(supplied) != canonical_order:
            raise DispatchError("Supplied order path does not match the canonical Order file.")

    project_raw = fields.get("project")
    if not project_raw:
        raise DispatchError("project is required and must be an absolute path under C:\\lab.")
    project = Path(project_raw)
    if not project.is_absolute() or not is_within(project, ALLOWED_ROOT):
        raise DispatchError("project must be an absolute path under C:\\lab.")
    project = canonical(project)
    if not project.is_dir():
        raise DispatchError(f"Project directory does not exist: {project}")
    if not (project / ".git").exists():
        raise DispatchError(f"Project is not a Git repository: {project}")

    if executor == "available":
        executor = "codex" if executor_prefix("codex") else "claude"
    if executor_prefix(executor) is None:
        raise DispatchError(f"Executor CLI is not installed: {executor}")

    return DispatchRequest(
        order_id, executor, str(canonical_order), str(project),
        task_id=task_id, raw_message=message,
    )


def run(command: Sequence[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=str(cwd),
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        timeout=timeout,
        check=False,
    )


def git(project: Path, *args: str, timeout: int = 120) -> str:
    result = run(["git", *args], project, timeout=timeout)
    if result.returncode:
        detail = (result.stderr or result.stdout).strip()
        raise DispatchError(f"git {' '.join(args)} failed: {detail}")
    return result.stdout.strip()


def commit_pending_registration(project: Path, order_id: str, order_path: str) -> None:
    """Stage+commit a single freshly-registered order file, if that is the
    only reason the tree is dirty.

    ORDER 100 intake (order_inbox_consumer.py) writes orders/NNN_*.md
    directly to disk without any Git operations -- git add/commit stays the
    dispatcher's exclusive job (2026-08-12 redesign). But that leaves the
    file untracked, and ensure_clean_and_current()'s unconditional
    clean-tree check then rejects the very dispatch the registration exists
    to feed (orders 103/104 both failed this way; recovered manually in
    2fa4549/de8e2d8). This closes that gap without loosening the clean-tree
    check itself: it only ever stages/commits the exact order_path file, and
    only when that file is the sole untracked entry for that path -- any
    other dirty state in the tree is left for ensure_clean_and_current() to
    reject as before.
    """
    try:
        rel = str(Path(order_path).relative_to(project))
    except ValueError:
        return
    rel = rel.replace("\\", "/")
    status = git(project, "status", "--porcelain=v1", "--", rel)
    if status == f"?? {rel}":
        git(project, "add", "--", rel)
        git(project, "commit", "-m", f"Register ORDER {order_id} (auto, intake)")


def ensure_clean_and_current(project: Path, pull: bool) -> str:
    if git(project, "status", "--porcelain=v1"):
        raise DispatchError("Project working tree is not clean; refusing automated execution.")
    before = git(project, "rev-parse", "HEAD")
    if pull:
        git(project, "pull", "--ff-only", timeout=180)
    if git(project, "status", "--porcelain=v1"):
        raise DispatchError("Project became dirty after pull; refusing automated execution.")
    return before


def build_prompt(request: DispatchRequest) -> str:
    raw_section = ""
    if request.raw_message is not None:
        # Verbatim -- no summarizing/normalizing/trimming (work order
        # 2026-08-12 task 3). Orders whose real instructions live only in
        # the Slack message body (no pre-committed canonical text) used to
        # force the executor to go dig through .runtime/inbox/ itself to
        # recover this; that search was the main cost of ORDER 100's 6m29s
        # turnaround. Slack sometimes appends a trailing signature line
        # (e.g. "*다음을 사용하여 보냄* Claude") directly onto the same line
        # as the message's own last line -- called out explicitly since a
        # naive "last line is END" parse would misfire on it.
        raw_section = f"""
Slack task_id: {request.task_id}
Raw Slack message, verbatim and unmodified (Slack may append a trailing
signature directly onto the final line with no line break -- parse
defensively, don't assume the literal last line is clean):
--- SLACK MESSAGE BEGIN ---
{request.raw_message}
--- SLACK MESSAGE END ---
"""
    return f"""Execute VSURF Order {request.order_id}.

Canonical Order: {request.order_path}
Project root: {request.project_path}
Shared rules: {COMMON_ROOT / 'AGENT_RULES.md'}
{raw_section}
Requirements:
1. Read the canonical Order and shared rules completely before changing files.
2. Work only inside the project root and explicitly allowed shared paths.
3. Do not commit or push; the dispatcher owns Git finalization.
4. Run at least one relevant validation. Do not report unverified work as complete.
5. Do not expose credentials or token values in output, files, or logs.
6. End with a concise summary containing changed files, validations, and remaining limits.
"""


def executor_prefix(executor: str) -> list[str] | None:
    """Return a CreateProcess-safe CLI prefix on Windows.

    npm's extensionless shims work in PowerShell but cannot be launched directly
    by Python CreateProcess. Invoke the package entry point with Node instead.
    """
    if executor == "codex":
        appdata = Path(os.environ.get("APPDATA", ""))
        entry = appdata / "npm" / "node_modules" / "@openai" / "codex" / "bin" / "codex.js"
        node = shutil.which("node")
        if node and entry.is_file():
            return [node, str(entry)]
    executable = shutil.which(f"{executor}.exe") or shutil.which(executor)
    if executable and Path(executable).suffix.lower() not in {".cmd", ".bat", ".ps1", ""}:
        return [executable]
    return None


def toml_value(value: str) -> str:
    """Return a TOML-compatible quoted string for a Codex -c override."""
    return json.dumps(value, ensure_ascii=False)


def load_mcp_registry(path: Path = MCP_REGISTRY_PATH) -> dict:
    """Load the Git-tracked MCP registry and fail closed on invalid input."""
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise DispatchError(f"MCP registry could not be loaded: {path}: {exc}") from exc
    servers = payload.get("mcp_servers")
    if payload.get("version") != 1 or not isinstance(servers, dict):
        raise DispatchError("MCP registry must have version=1 and an mcp_servers object.")
    return payload


def _mcp_context() -> dict[str, str]:
    python = Path(sys.executable).resolve()
    autoai_root = os.environ.get("AUTOAI_ROOT") or str(Path(python.anchor) / "autoai")
    return {
        "PYTHON_EXECUTABLE": str(python),
        "AUTOAI_ROOT": autoai_root,
        "USER_HOME": str(Path.home()),
    }


def _resolve_registry_value(spec: object, context: dict[str, str], label: str) -> str:
    if isinstance(spec, str):
        return spec.format_map(context)
    if not isinstance(spec, dict):
        raise DispatchError(f"MCP registry {label} must be a string or object.")
    value = ""
    source = spec.get("env") or spec.get("source")
    if source:
        value = os.environ.get(str(source), "")
    if not value and spec.get("fallback_source"):
        value = os.environ.get(str(spec["fallback_source"]), "")
    if not value and spec.get("default") is not None:
        value = str(spec["default"]).format_map(context)
    if not value and spec.get("discover"):
        value = shutil.which(str(spec["discover"])) or ""
    if not value and spec.get("required"):
        raise DispatchError(f"MCP registry value is missing: {label}")
    if value and spec.get("must_exist"):
        path = Path(value)
        if not path.is_file():
            raise DispatchError(f"MCP registry file does not exist for {label}: {path}")
        value = str(path.resolve())
    return value


def resolve_mcp_config(name: str, registry: dict | None = None) -> dict[str, object]:
    """Resolve one declarative MCP entry using environment-first PC overrides."""
    registry = registry or load_mcp_registry()
    entry = registry["mcp_servers"].get(name)
    if not isinstance(entry, dict):
        raise DispatchError(f"MCP is not registered: {name}")
    if not entry.get("enabled", False):
        raise DispatchError(f"MCP is disabled: {name}")
    context = _mcp_context()
    command = _resolve_registry_value(entry.get("command"), context, f"{name}.command")
    args_raw = entry.get("args", [])
    if not isinstance(args_raw, list):
        raise DispatchError(f"MCP registry {name}.args must be an array.")
    args = [
        _resolve_registry_value(spec, context, f"{name}.args[{index}]")
        for index, spec in enumerate(args_raw)
    ]
    env_raw = entry.get("env", {})
    if not isinstance(env_raw, dict):
        raise DispatchError(f"MCP registry {name}.env must be an object.")
    resolved_env = {
        key: _resolve_registry_value(spec, context, f"{name}.env.{key}")
        for key, spec in env_raw.items()
    }
    return {
        "command": command,
        "args": args,
        "default_tools_approval_mode": entry.get(
            "default_tools_approval_mode", "approve"
        ),
        "env": resolved_env,
    }


def mcp_config_overrides(registry: dict | None = None) -> list[str]:
    """Generate Codex -c arguments for every enabled registry entry."""
    registry = registry or load_mcp_registry()
    output: list[str] = []
    for name, entry in registry["mcp_servers"].items():
        if not isinstance(entry, dict) or not entry.get("enabled", False):
            continue
        config = resolve_mcp_config(name, registry)
        output.extend(["-c", f"mcp_servers.{name}.command={toml_value(str(config['command']))}"])
        args = ",".join(toml_value(str(value)) for value in config["args"])
        output.extend(["-c", f"mcp_servers.{name}.args=[{args}]"])
        approval = toml_value(str(config["default_tools_approval_mode"]))
        output.extend(["-c", f"mcp_servers.{name}.default_tools_approval_mode={approval}"])
        for key, value in config["env"].items():
            output.extend(["-c", f"mcp_servers.{name}.env.{key}={toml_value(str(value))}"])
    return output


def executor_command(request: DispatchRequest, summary_file: Path) -> list[str]:
    prefix = executor_prefix(request.executor)
    if prefix is None:
        raise DispatchError(f"Executor CLI is not installed: {request.executor}")
    if request.executor == "codex":
        mcp_config = mcp_config_overrides()
        return [
            *prefix, "exec", "-C", request.project_path,
            "--ignore-user-config",
            # --ignore-user-config strips ~/.codex/config.toml entirely, which
            # is where this machine's [windows] sandbox = "elevated" lived --
            # without it, --sandbox workspace-write only sets sandbox_mode and
            # silently leaves Windows running read-only (order 107, FAILED:
            # "no Git change; completion not proven"). -c is the highest config
            # precedence layer (above the now-stripped user file), so restore
            # just the two keys needed instead of dropping --ignore-user-config
            # itself. Verified empirically 2026-08-13 (STEP 0-2, in this order,
            # against an isolated temp repo, before touching this file):
            # session header shows sandbox: workspace-write; writes inside
            # workdir/--add-dir succeed; writes outside them are still
            # rejected ("patch rejected: writing outside of the project") --
            # i.e. restoring these two keys does not reintroduce
            # danger-full-access, it only fixes the Windows backend + approval
            # gate that --ignore-user-config over-stripped.
            "-c", 'approval_policy="never"',
            "-c", 'windows.sandbox="elevated"',
            *mcp_config,
            "--add-dir", str(COMMON_ROOT),
            "--sandbox", "workspace-write",
            "--output-last-message", str(summary_file),
            build_prompt(request),
        ]
    return [*prefix, "-p", build_prompt(request)]


class OrderLock:
    def __init__(self, order_id: str):
        self.path = RUNTIME_DIR / f"order-{order_id}.lock"
        self.fd: int | None = None

    def __enter__(self) -> "OrderLock":
        RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        try:
            self.fd = os.open(self.path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise DispatchError("Order is already claimed or needs manual lock recovery.") from exc
        os.write(self.fd, f"pid={os.getpid()} started={now_iso()}".encode())
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self.fd is not None:
            os.close(self.fd)
        self.path.unlink(missing_ok=True)


def write_result(result: DispatchResult) -> Path:
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNTIME_DIR / f"order-{result.order_id}-last.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(asdict(result), ensure_ascii=False, indent=2), encoding="utf-8")
    temporary.replace(path)
    return path


def dispatch(request: DispatchRequest, execute: bool, pull: bool, push: bool) -> DispatchResult:
    result = DispatchResult(
        order_id=request.order_id,
        executor=request.executor,
        status="VALIDATED" if not execute else "RUNNING",
        project_path=request.project_path,
        order_path=request.order_path,
        started_at=now_iso(),
    )
    if not execute:
        result.finished_at = now_iso()
        write_result(result)
        return result

    project = Path(request.project_path)
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    summary_file = LOG_DIR / f"order-{request.order_id}-summary.txt"
    result.summary_file = str(summary_file)
    with OrderLock(request.order_id):
        try:
            commit_pending_registration(project, request.order_id, request.order_path)
            ensure_clean_and_current(project, pull=pull)
            completed = run(executor_command(request, summary_file), project, timeout=3600)
            result.exit_code = completed.returncode
            (LOG_DIR / f"order-{request.order_id}-stdout.log").write_text(
                completed.stdout, encoding="utf-8"
            )
            (LOG_DIR / f"order-{request.order_id}-stderr.log").write_text(
                completed.stderr, encoding="utf-8"
            )
            if completed.returncode:
                raise DispatchError(f"{request.executor} exited with code {completed.returncode}.")
            changes = git(project, "status", "--porcelain=v1")
            if changes:
                git(project, "add", "-A")
                git(project, "commit", "-m", f"Complete ORDER {request.order_id}")
                result.commit = git(project, "rev-parse", "HEAD")
                if push:
                    git(project, "push", timeout=180)
            else:
                raise DispatchError(
                    "Executor exited successfully but produced no Git change; completion not proven."
                )
            result.status = "COMPLETED"
        except (DispatchError, subprocess.TimeoutExpired, OSError) as exc:
            result.status = "FAILED"
            result.error = str(exc)
        finally:
            result.finished_at = now_iso()
            write_result(result)
    return result


def load_message(args: argparse.Namespace) -> str:
    if args.message:
        return args.message
    if args.message_file:
        return Path(args.message_file).read_text(encoding="utf-8")
    return sys.stdin.read()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group()
    source.add_argument("--message")
    source.add_argument("--message-file")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--no-pull", action="store_true")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args(argv)
    try:
        request = parse_request(load_message(args))
        result = dispatch(request, args.execute, not args.no_pull, not args.no_push)
    except DispatchError as exc:
        print(json.dumps({"status": "REJECTED", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(asdict(result), ensure_ascii=False, indent=2))
    return 0 if result.status in {"VALIDATED", "COMPLETED"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
