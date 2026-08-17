"""Patch ~/.grok/config.toml Slack MCP block. Never writes token values."""
from __future__ import annotations

import argparse
from pathlib import Path

ENV_REF = "${OPENACP_SLACK_BOT_TOKEN}"


def slack_block(python_exe: str, server_py: str) -> str:
    py = python_exe.replace("'", "''")
    server = server_py.replace("'", "''")
    return (
        "[mcp_servers.slack]\n"
        f"command = '{py}'\n"
        f"args = ['{server}']\n"
        "enabled = true\n"
        "startup_timeout_sec = 30\n"
        "\n"
        "[mcp_servers.slack.env]\n"
        f'SLACK_BOT_TOKEN = "{ENV_REF}"\n'
    )


def _is_slack_header(line: str) -> bool:
    stripped = line.strip()
    return stripped == "[mcp_servers.slack]" or stripped.startswith("[mcp_servers.slack.")


def drop_slack_sections(text: str) -> str:
    lines = text.splitlines()
    kept: list[str] = []
    skipping = False
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            skipping = _is_slack_header(line)
        if not skipping:
            kept.append(line)
    cleaned = "\n".join(kept).rstrip()
    return cleaned + ("\n\n" if cleaned else "")


def patch_config_text(text: str, python_exe: str, server_py: str) -> str:
    body = drop_slack_sections(text)
    return body + slack_block(python_exe, server_py)


def patch_config_file(config_path: Path, python_exe: str, server_py: str) -> Path:
    original = config_path.read_text(encoding="utf-8") if config_path.exists() else ""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(
        patch_config_text(original, python_exe, server_py),
        encoding="utf-8",
        newline="\n",
    )
    return config_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True)
    parser.add_argument("--python", required=True)
    parser.add_argument("--server", required=True)
    args = parser.parse_args()
    path = patch_config_file(Path(args.config), args.python, args.server)
    print(f"patched {path}")
    print(f"server {args.server}")
    print(f"token_ref {ENV_REF}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
