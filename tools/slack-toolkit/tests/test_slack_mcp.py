import ast
import json
import pathlib
import sys
import unittest
from unittest.mock import patch

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import patch_grok_config as P
import slack_mcp_server as S


class _FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        return json.dumps(self._payload).encode("utf-8")


class SlackMcpTests(unittest.TestCase):
    def test_source_compiles(self):
        source = (ROOT / "slack_mcp_server.py").read_text(encoding="utf-8")
        ast.parse(source)

    def test_missing_token(self):
        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "", "OPENACP_SLACK_BOT_TOKEN": ""}, clear=False):
            result = S.slack_auth_test()
        self.assertFalse(result["ok"])
        self.assertIn("token missing", result["error"])

    def test_auth_test_and_read(self):
        payloads = [
            {
                "ok": True,
                "url": "https://example.slack.com/",
                "team": "VSURF",
                "team_id": "T123",
                "user": "bot",
                "user_id": "U123",
                "bot_id": "B123",
            },
            {
                "ok": True,
                "messages": [{"ts": "1.0", "user": "U9", "text": "hello", "reply_count": 0}],
                "has_more": False,
                "response_metadata": {"next_cursor": ""},
            },
        ]

        def fake_urlopen(req, timeout=20):
            return _FakeResponse(payloads.pop(0))

        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-test", "OPENACP_SLACK_BOT_TOKEN": ""}, clear=False):
            with patch("urllib.request.urlopen", side_effect=fake_urlopen):
                auth = S.slack_auth_test()
                hist = S.slack_read_channel("C0BQQ8ZBCL8", limit=5)
        self.assertTrue(auth["ok"])
        self.assertEqual(auth["team_id"], "T123")
        self.assertTrue(hist["ok"])
        self.assertEqual(hist["count"], 1)
        self.assertEqual(hist["messages"][0]["text"], "hello")

    def test_search_filters_by_name(self):
        page = {
            "ok": True,
            "channels": [
                {"id": "C1", "name": "random", "topic": {"value": ""}, "purpose": {"value": ""}},
                {"id": "C0BQQ8ZBCL8", "name": "vsurf-code-reports", "topic": {"value": "code"}, "purpose": {"value": ""}},
            ],
            "response_metadata": {"next_cursor": ""},
        }
        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-test"}, clear=False):
            with patch("urllib.request.urlopen", return_value=_FakeResponse(page)):
                result = S.slack_search_channels("code-reports")
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["channels"][0]["id"], "C0BQQ8ZBCL8")


class PatchGrokConfigTests(unittest.TestCase):
    def test_appends_block_without_writing_token_value(self):
        out = P.patch_config_text(
            "[cli]\ninstaller = \"npm\"\n",
            python_exe=r"C:\Python314\python.exe",
            server_py=r"C:\lab\vsurf_capital\common\tools\slack-toolkit\slack_mcp_server.py",
        )
        self.assertIn("[mcp_servers.slack]", out)
        self.assertIn("${OPENACP_SLACK_BOT_TOKEN}", out)
        self.assertNotIn("xoxb-", out)
        self.assertNotIn("xapp-", out)

    def test_replaces_old_autoai_path(self):
        old = (
            "[mcp_servers.slack]\n"
            "command = 'C:\\Python314\\python.exe'\n"
            "args = ['C:\\autoai\\slack-toolkit\\slack_mcp_server.py']\n"
            "enabled = true\n"
            "\n"
            "[mcp_servers.slack.env]\n"
            "SLACK_BOT_TOKEN = \"${OPENACP_SLACK_BOT_TOKEN}\"\n"
        )
        out = P.patch_config_text(
            old,
            python_exe=r"C:\Python314\python.exe",
            server_py=r"C:\lab\vsurf_capital\common\tools\slack-toolkit\slack_mcp_server.py",
        )
        self.assertNotIn(r"C:\autoai\slack-toolkit", out)
        self.assertEqual(out.count("[mcp_servers.slack]"), 1)


if __name__ == "__main__":
    unittest.main()
