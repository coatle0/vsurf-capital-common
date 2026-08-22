"""Read-only MCP stdio smoke for neo4j-official. Never prints credentials."""
from __future__ import annotations

import json
import subprocess
import sys

PY = r"C:\lab\knowgraph\vendor\neo4j-mcp\.venv\Scripts\python.exe"
WRAP = r"C:\lab\knowgraph\investment_workbench\neo4j_mcp_wrapper.py"


def send(proc, obj) -> None:
    proc.stdin.write(json.dumps(obj, separators=(",", ":")) + "\n")
    proc.stdin.flush()


def recv(proc, label: str) -> dict:
    line = proc.stdout.readline()
    if not line:
        err = ""
        if proc.poll() is not None:
            err = proc.stderr.read() or ""
        raise RuntimeError(f"no stdout during {label}; rc={proc.poll()}; stderr_chars={len(err)}")
    return json.loads(line)


def main() -> int:
    proc = subprocess.Popen(
        [PY, WRAP],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    try:
        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2025-11-25",
                    "capabilities": {},
                    "clientInfo": {"name": "vsurf-smoke", "version": "1.0"},
                },
            },
        )
        init = recv(proc, "initialize")
        if "error" in init:
            print("initialize FAIL")
            print(init["error"])
            return 1
        result = init.get("result") or {}
        print("initialize PASS")
        print("serverInfo", result.get("serverInfo"))
        send(proc, {"jsonrpc": "2.0", "method": "notifications/initialized"})

        send(proc, {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
        listed = recv(proc, "tools/list")
        tools = ((listed.get("result") or {}).get("tools") or [])
        names = [t.get("name") for t in tools]
        print("tools", names)
        for want in ("get_schema", "get-schema", "read_cypher", "read-cypher", "write_cypher", "write-cypher"):
            print("exposed", want, want in names)

        read_name = next((n for n in names if n.replace("-", "_") == "read_cypher"), None)
        schema_name = next((n for n in names if n.replace("-", "_") == "get_schema"), None)
        if not read_name:
            print("read_cypher missing")
            return 1

        send(
            proc,
            {
                "jsonrpc": "2.0",
                "id": 3,
                "method": "tools/call",
                "params": {"name": read_name, "arguments": {"query": "RETURN 1 AS ok"}},
            },
        )
        smoke = recv(proc, "read_cypher")
        if "error" in smoke:
            print("smoke FAIL", smoke["error"])
            return 1
        body = json.dumps(smoke.get("result"), ensure_ascii=False)
        print("smoke PASS")
        print("smoke_body", body[:800])

        if schema_name:
            send(
                proc,
                {
                    "jsonrpc": "2.0",
                    "id": 4,
                    "method": "tools/call",
                    "params": {"name": schema_name, "arguments": {}},
                },
            )
            sch = recv(proc, "get_schema")
            if "error" in sch:
                print("schema FAIL", sch["error"])
            else:
                print("schema PASS")
                print("schema_body", json.dumps(sch.get("result"), ensure_ascii=False)[:400])
        return 0
    finally:
        proc.kill()


if __name__ == "__main__":
    sys.exit(main())
