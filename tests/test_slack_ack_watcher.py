import importlib.util
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "slack_ack_watcher.py"
SPEC = importlib.util.spec_from_file_location("slack_ack_watcher", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class MessageFilterTests(unittest.TestCase):
    def test_accepts_human_message(self):
        self.assertTrue(MODULE.is_human_message({"user": "U1", "text": "PING"}, "UBOT"))

    def test_rejects_bot_and_system_messages(self):
        self.assertFalse(MODULE.is_human_message({"user": "UBOT", "text": "x"}, "UBOT"))
        self.assertFalse(MODULE.is_human_message({"user": "U1", "subtype": "channel_join", "text": "x"}, "UBOT"))


class FetchNewMessagesPaginationTests(unittest.TestCase):
    def test_paginates_until_has_more_false(self):
        pages = [
            {"messages": [{"ts": "1.0", "text": "a"}], "has_more": True, "response_metadata": {"next_cursor": "CUR1"}},
            {"messages": [{"ts": "2.0", "text": "b"}], "has_more": False, "response_metadata": {"next_cursor": ""}},
        ]
        with patch.object(MODULE, "api", side_effect=pages) as mock_api:
            result = MODULE.fetch_new_messages("tok", "C1", 0.5)
        self.assertEqual([m["ts"] for m in result], ["1.0", "2.0"])
        first_call, second_call = mock_api.call_args_list
        self.assertEqual(first_call.args[2]["oldest"], "0.5")
        self.assertNotIn("cursor", first_call.args[2])
        self.assertEqual(second_call.args[2]["cursor"], "CUR1")

    def test_stops_without_cursor_even_if_has_more_true(self):
        pages = [{"messages": [{"ts": "1.0"}], "has_more": True, "response_metadata": {}}]
        with patch.object(MODULE, "api", side_effect=pages):
            result = MODULE.fetch_new_messages("tok", "C1", 0.0)
        self.assertEqual(len(result), 1)


class ProcessMessageDurabilityTests(unittest.TestCase):
    def test_writes_inbox_before_acking(self):
        calls = []
        with patch.object(MODULE.order_inbox, "write_pending", side_effect=lambda r: calls.append("write") or Path("x")), \
             patch.object(MODULE, "api", side_effect=lambda *a: calls.append("ack")):
            MODULE.process_message({"user": "U1", "text": "hi", "ts": "1.0"}, "tok", "UBOT", "codex-pc2", "C1")
        self.assertEqual(calls, ["write", "ack"])

    def test_does_not_ack_when_write_fails(self):
        with patch.object(MODULE.order_inbox, "write_pending", side_effect=OSError("disk full")), \
             patch.object(MODULE, "api") as mock_api:
            with self.assertRaises(OSError):
                MODULE.process_message({"user": "U1", "text": "hi", "ts": "1.0"}, "tok", "UBOT", "codex-pc2", "C1")
        mock_api.assert_not_called()

    def test_skips_non_human_messages_without_writing(self):
        with patch.object(MODULE.order_inbox, "write_pending") as mock_write, patch.object(MODULE, "api") as mock_api:
            MODULE.process_message({"user": "UBOT", "text": "hi", "ts": "1.0"}, "tok", "UBOT", "codex-pc2", "C1")
        mock_write.assert_not_called()
        mock_api.assert_not_called()

    def test_approved_write_happens_before_ack_and_uses_approval_ts_for_id(self):
        calls = []
        message = {"user": "U1", "text": "approve", "ts": "2.0", "thread_ts": "1.0"}
        with patch.object(MODULE.order_inbox, "write_pending", side_effect=lambda r: calls.append(("write", r)) or Path("x")), \
             patch.object(MODULE, "api", side_effect=lambda *a: calls.append(("ack", a))):
            tid = MODULE.enqueue_approved(message, "[EXECUTE ORDER 7]", "tok", "codex-pc2", "C1")
        self.assertEqual(tid, "C1-2.0")
        self.assertEqual(calls[0][0], "write")
        self.assertEqual(calls[0][1]["ts"], "1.0")
        self.assertEqual(calls[0][1]["approval"], "explicit")
        self.assertEqual(calls[1][0], "ack")


if __name__ == "__main__":
    unittest.main()
