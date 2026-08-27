import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "slack_bolt_listener.py"
SPEC = importlib.util.spec_from_file_location("slack_bolt_listener", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

ingress = MODULE.ingress


class CursorTests(unittest.TestCase):
    def test_advance_moves_forward_and_persists(self):
        cursor = MODULE.Cursor(1.0)
        with patch.object(ingress, "save_cursor") as mock_save:
            cursor.advance(2.0)
        self.assertEqual(cursor.value, 2.0)
        mock_save.assert_called_once_with(2.0)

    def test_advance_ignores_non_increasing_ts(self):
        cursor = MODULE.Cursor(5.0)
        with patch.object(ingress, "save_cursor") as mock_save:
            cursor.advance(5.0)
            cursor.advance(1.0)
        self.assertEqual(cursor.value, 5.0)
        mock_save.assert_not_called()


class ListenerLockTests(unittest.TestCase):
    def test_second_listener_is_rejected_and_lock_releases(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "listener.lock"
            with MODULE.ListenerLock(path):
                with self.assertRaises(RuntimeError):
                    with MODULE.ListenerLock(path):
                        pass
            with MODULE.ListenerLock(path):
                pass


class CatchUpTests(unittest.TestCase):
    def test_processes_only_messages_after_cursor_and_advances(self):
        messages = [{"ts": "1.0", "text": "old"}, {"ts": "2.0", "text": "new"}, {"ts": "3.0", "text": "newer"}]
        cursor = MODULE.Cursor(1.0)
        with patch.object(ingress, "fetch_new_messages", return_value=messages) as mock_fetch, \
             patch.object(MODULE, "route_human_event") as mock_process, \
             patch.object(ingress, "save_cursor"):
            MODULE.catch_up("tok", "C1", "UBOT", "codex-pc2", cursor)
        mock_fetch.assert_called_once_with("tok", "C1", 1.0)
        self.assertEqual(mock_process.call_count, 2)  # ts 2.0 and 3.0 only
        processed_ts = [call.args[0]["ts"] for call in mock_process.call_args_list]
        self.assertEqual(processed_ts, ["2.0", "3.0"])
        self.assertEqual(cursor.value, 3.0)

    def test_no_new_messages_leaves_cursor_untouched(self):
        cursor = MODULE.Cursor(5.0)
        with patch.object(ingress, "fetch_new_messages", return_value=[]), \
             patch.object(ingress, "process_message") as mock_process, \
             patch.object(ingress, "save_cursor") as mock_save:
            MODULE.catch_up("tok", "C1", "UBOT", "codex-pc2", cursor)
        mock_process.assert_not_called()
        mock_save.assert_not_called()
        self.assertEqual(cursor.value, 5.0)


class HandleLiveEventTests(unittest.TestCase):
    def test_ignores_events_from_other_channels(self):
        cursor = MODULE.Cursor(0.0)
        with patch.object(MODULE, "route_human_event") as mock_process:
            MODULE.handle_live_event({"channel": "OTHER", "ts": "1.0"}, "tok", "UBOT", "codex-pc2", "C1", cursor)
        mock_process.assert_not_called()
        self.assertEqual(cursor.value, 0.0)

    def test_ignores_stale_ts(self):
        cursor = MODULE.Cursor(10.0)
        with patch.object(MODULE, "route_human_event") as mock_process:
            MODULE.handle_live_event({"channel": "C1", "ts": "1.0"}, "tok", "UBOT", "codex-pc2", "C1", cursor)
        mock_process.assert_not_called()

    def test_processes_and_advances_for_new_event_in_channel(self):
        cursor = MODULE.Cursor(1.0)
        event = {"channel": "C1", "ts": "2.0", "user": "U1", "text": "[EXECUTE ORDER 003]"}
        with patch.object(MODULE, "route_human_event") as mock_process, patch.object(ingress, "save_cursor"):
            MODULE.handle_live_event(event, "tok", "UBOT", "codex-pc2", "C1", cursor)
        mock_process.assert_called_once_with(event, "tok", "UBOT", "codex-pc2", "C1")
        self.assertEqual(cursor.value, 2.0)


if __name__ == "__main__":
    unittest.main()
