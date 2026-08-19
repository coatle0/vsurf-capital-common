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


class SlackMcpTests(unittest.TestCase):
    def setUp(self):
        S._reset_runtime_state()

    def tearDown(self):
        S._reset_runtime_state()

    def test_source_compiles(self):
        source = (ROOT / "slack_mcp_server.py").read_text(encoding="utf-8")
        ast.parse(source)

    def test_missing_token(self):
        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "", "OPENACP_SLACK_BOT_TOKEN": ""}, clear=False):
            with patch.object(S, "_user_env", return_value=""):
                result = S.slack_auth_test()
        self.assertFalse(result["ok"])
        self.assertIn("token missing", result["error"])

    def test_unexpanded_placeholder_is_ignored(self):
        self.assertEqual(S._usable_token("${OPENACP_SLACK_BOT_TOKEN}"), "")
        self.assertEqual(S._usable_token("${OPENACP_SLACK_BOT_TOKEN:-}"), "")
        self.assertEqual(S._usable_token("xoxb-test"), "xoxb-test")

    def test_placeholder_process_env_falls_back_to_user_env(self):
        with patch.dict(
            "os.environ",
            {
                "SLACK_BOT_TOKEN": "${OPENACP_SLACK_BOT_TOKEN}",
                "OPENACP_SLACK_BOT_TOKEN": "",
            },
            clear=False,
        ):
            with patch.object(
                S,
                "_user_env",
                side_effect=lambda name: "xoxb-from-user" if name == "OPENACP_SLACK_BOT_TOKEN" else "",
            ):
                self.assertEqual(S._token(), "xoxb-from-user")

    def test_process_env_wins_over_user_env(self):
        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-process"}, clear=False):
            with patch.object(S, "_user_env", return_value="xoxb-from-user"):
                self.assertEqual(S._token(), "xoxb-process")

    def test_token_is_cached_after_first_resolve(self):
        with patch.dict(
            "os.environ",
            {"SLACK_BOT_TOKEN": "", "OPENACP_SLACK_BOT_TOKEN": ""},
            clear=False,
        ):
            with patch.object(S, "_user_env", side_effect=lambda name: "xoxb-from-user" if name == "OPENACP_SLACK_BOT_TOKEN" else "") as mock_user:
                first = S._token()
                second = S._token()
        self.assertEqual(first, "xoxb-from-user")
        self.assertEqual(second, "xoxb-from-user")
        self.assertEqual(mock_user.call_count, 2)

    def test_resolve_known_channel_names(self):
        self.assertEqual(S._resolve_channel("#vsurf-skill"), "C0BR8722F6C")
        self.assertEqual(S._resolve_channel("vsurf-code-reports"), "C0BQQ8ZBCL8")
        self.assertEqual(S._resolve_channel("C0BR8722F6C"), "C0BR8722F6C")

    def test_search_known_channel_skips_network(self):
        with patch.object(S, "_http_post", side_effect=AssertionError("network should not be called")):
            result = S.slack_search_channels("#vsurf-skill")
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["channels"][0]["id"], "C0BR8722F6C")

    def test_read_default_limit_is_three_and_resolves_alias(self):
        seen: dict[str, str] = {}

        def fake_http_post(path, body, headers):
            seen["path"] = path
            seen["body"] = body.decode("utf-8")
            return json.dumps({"ok": True, "messages": [], "has_more": False}).encode("utf-8")

        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-test"}, clear=False):
            with patch.object(S, "_http_post", side_effect=fake_http_post):
                result = S.slack_read_channel("vsurf-skill")
        self.assertTrue(result["ok"])
        self.assertEqual(result["channel"], "C0BR8722F6C")
        self.assertEqual(seen["path"], "/api/conversations.history")
        self.assertIn("limit=3", seen["body"])
        self.assertIn("channel=C0BR8722F6C", seen["body"])

    def test_http_post_retries_once_and_reuses_connection(self):
        requests: list[str] = []
        constructed = {"n": 0}
        state = {"fails_left": 1}

        class _FakeConn:
            def request(self, method, path, body=None, headers=None):
                if state["fails_left"]:
                    state["fails_left"] -= 1
                    raise ConnectionResetError("reset")
                requests.append(path)

            def getresponse(self):
                class _Resp:
                    status = 200

                    def read(self):
                        return b'{"ok":true}'

                return _Resp()

            def close(self):
                return None

        def factory(*args, **kwargs):
            constructed["n"] += 1
            return _FakeConn()

        with patch.object(S.http.client, "HTTPSConnection", side_effect=factory):
            first = S._http_post("/api/auth.test", b"", {"Connection": "keep-alive"})
            second = S._http_post("/api/conversations.history", b"limit=1", {"Connection": "keep-alive"})
        self.assertEqual(json.loads(first.decode("utf-8"))["ok"], True)
        self.assertEqual(json.loads(second.decode("utf-8"))["ok"], True)
        self.assertEqual(requests, ["/api/auth.test", "/api/conversations.history"])
        self.assertEqual(constructed["n"], 2)

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

        def fake_http_post(path, body, headers):
            return json.dumps(payloads.pop(0)).encode("utf-8")

        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-test", "OPENACP_SLACK_BOT_TOKEN": ""}, clear=False):
            with patch.object(S, "_http_post", side_effect=fake_http_post):
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
                {"id": "C9ELSE", "name": "other-code-reports", "topic": {"value": "code"}, "purpose": {"value": ""}},
            ],
            "response_metadata": {"next_cursor": ""},
        }

        def fake_http_post(path, body, headers):
            return json.dumps(page).encode("utf-8")

        with patch.dict("os.environ", {"SLACK_BOT_TOKEN": "xoxb-test"}, clear=False):
            with patch.object(S, "_http_post", side_effect=fake_http_post):
                result = S.slack_search_channels("other-code-reports")
        self.assertTrue(result["ok"])
        self.assertEqual(result["count"], 1)
        self.assertEqual(result["channels"][0]["id"], "C9ELSE")


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
