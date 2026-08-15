"""Launch the official Neo4j MCP with both read and write Cypher tools."""
from __future__ import annotations

import os
import runpy


def _load_user_env(name: str) -> str:
    value = os.environ.get(name, "")
    if value:
        return value
    try:
        import winreg

        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            return str(winreg.QueryValueEx(key, name)[0])
    except (FileNotFoundError, OSError):
        return ""


def main() -> None:
    password = _load_user_env("NEO4J_PASSWORD")
    if not password:
        raise SystemExit("NEO4J_PASSWORD is missing from process and HKCU\\Environment")
    os.environ.setdefault("NEO4J_URI", "bolt://127.0.0.1:7687")
    os.environ.setdefault("NEO4J_USERNAME", "neo4j")
    os.environ.setdefault("NEO4J_DATABASE", "neo4j")
    os.environ["NEO4J_READ_ONLY"] = "false"
    os.environ.setdefault("NEO4J_TELEMETRY", "false")
    os.environ["NEO4J_PASSWORD"] = password
    runpy.run_module("neo4j_mcp_server", run_name="__main__")


if __name__ == "__main__":
    main()
