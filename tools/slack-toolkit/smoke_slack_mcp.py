"""Safe Slack MCP smoke test: auth.test only. Never posts."""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from slack_mcp_server import slack_auth_test, slack_search_channels

print("=" * 60)
print("Slack MCP smoke — auth.test + channel search")
print("=" * 60)

auth = slack_auth_test()
print(json.dumps({k: v for k, v in auth.items() if k != "ok"}, ensure_ascii=False, indent=2))
if not auth.get("ok"):
    print("[FAIL] slack_auth_test")
    sys.exit(1)
print("[OK] slack_auth_test")

found = slack_search_channels("vsurf-code-reports", limit=5)
if not found.get("ok"):
    print(f"[FAIL] slack_search_channels: {found.get('error')}")
    sys.exit(1)
ids = [item.get("id") for item in found.get("channels") or []]
print(f"[OK] slack_search_channels count={found.get('count')} ids={ids}")
