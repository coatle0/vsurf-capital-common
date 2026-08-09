import importlib.util
import unittest
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
