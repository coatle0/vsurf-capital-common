import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).parents[1] / "scripts" / "order_inbox.py"
SPEC = importlib.util.spec_from_file_location("order_inbox", SCRIPT)
order_inbox = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = order_inbox
SPEC.loader.exec_module(order_inbox)


class TaskIdTests(unittest.TestCase):
    def test_sanitizes_unsafe_characters(self):
        self.assertEqual(order_inbox.task_id("C0BNWS9QKDK", "1699999999.000100"), "C0BNWS9QKDK-1699999999.000100")
        self.assertNotIn("/", order_inbox.task_id("weird/chan", "1.2"))


class InboxRoundTripTests(unittest.TestCase):
    def test_write_list_load_and_mark_processed(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            pending = root / "pending"
            processed = root / "processed"
            with patch.object(order_inbox, "PENDING_DIR", pending), patch.object(
                order_inbox, "PROCESSED_DIR", processed
            ):
                record = {"task_id": "C1-1.0", "channel": "C1", "ts": "1.0", "text": "hello"}
                path = order_inbox.write_pending(record)
                self.assertTrue(path.is_file())
                self.assertEqual(order_inbox.list_pending(), [path])
                self.assertEqual(order_inbox.load(path)["text"], "hello")

                dest = order_inbox.mark_processed(path, {"status": "COMPLETED"})
                self.assertFalse(path.exists())
                self.assertTrue(dest.is_file())
                self.assertEqual(order_inbox.list_pending(), [])
                self.assertEqual(order_inbox.load(dest)["result"]["status"], "COMPLETED")

    def test_list_pending_empty_when_dir_missing(self):
        with tempfile.TemporaryDirectory() as raw:
            missing = Path(raw) / "does-not-exist"
            with patch.object(order_inbox, "PENDING_DIR", missing):
                self.assertEqual(order_inbox.list_pending(), [])


if __name__ == "__main__":
    unittest.main()
