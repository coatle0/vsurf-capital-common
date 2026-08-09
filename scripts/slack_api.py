"""Minimal Slack Web API caller shared by the ingress watcher and the inbox consumer."""

from __future__ import annotations

import json
import urllib.parse
import urllib.request


def api(method: str, token: str, payload: dict[str, str]) -> dict:
    data = urllib.parse.urlencode(payload).encode("utf-8")
    req = urllib.request.Request(
        f"https://slack.com/api/{method}",
        data=data,
        headers={"Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=20) as response:
        result = json.load(response)
    if not result.get("ok"):
        raise RuntimeError(f"Slack {method} failed: {result.get('error', 'unknown_error')}")
    return result
