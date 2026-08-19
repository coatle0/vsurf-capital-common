"""Safe Slack MCP smoke test: auth.test + skill latest-1. Never posts."""
import json
import os
import sys
import time

sys.path.insert(0, os.path.dirname(__file__))
from slack_mcp_server import slack_auth_test, slack_read_channel, slack_search_channels

print("=" * 60)
print("Slack MCP smoke — auth.test + skill latest-1")
print("=" * 60)

auth = slack_auth_test()
print(json.dumps({k: v for k, v in auth.items() if k != "ok"}, ensure_ascii=False, indent=2))
if not auth.get("ok"):
    print("[FAIL] slack_auth_test")
    sys.exit(1)
print("[OK] slack_auth_test")

known = slack_search_channels("vsurf-skill", limit=1)
if not known.get("ok") or (known.get("channels") or [{}])[0].get("id") != "C0BR8722F6C":
    print(f"[FAIL] known-channel short-circuit: {known}")
    sys.exit(1)
print("[OK] known-channel short-circuit id=C0BR8722F6C")

started = time.perf_counter()
first = slack_read_channel("C0BR8722F6C", limit=1)
first_ms = (time.perf_counter() - started) * 1000
if not first.get("ok"):
    print(f"[FAIL] slack_read_channel: {first.get('error')}")
    sys.exit(1)
msg = (first.get("messages") or [{}])[0]
print(f"[OK] latest ts={msg.get('ts')} count={first.get('count')} first_ms={first_ms:.0f}")

started = time.perf_counter()
second = slack_read_channel("C0BR8722F6C", limit=1)
second_ms = (time.perf_counter() - started) * 1000
if not second.get("ok"):
    print(f"[FAIL] slack_read_channel second: {second.get('error')}")
    sys.exit(1)
print(f"[OK] keep-alive second_ms={second_ms:.0f} ts={((second.get('messages') or [{}])[0]).get('ts')}")
