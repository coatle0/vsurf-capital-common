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


class _WithDirs(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        self.pending = root / "pending"
        self.claimed = root / "claimed"
        self.outbox = root / "outbox"
        self.processed = root / "processed"
        self._patches = [
            patch.object(order_inbox, "PENDING_DIR", self.pending),
            patch.object(order_inbox, "CLAIMED_DIR", self.claimed),
            patch.object(order_inbox, "OUTBOX_DIR", self.outbox),
            patch.object(order_inbox, "PROCESSED_DIR", self.processed),
        ]
        for p in self._patches:
            p.start()
            self.addCleanup(p.stop)
        self.addCleanup(self._tmp.cleanup)


class PendingRoundTripTests(_WithDirs):
    def test_write_list_load_and_mark_processed(self):
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
        self.assertEqual(order_inbox.list_pending(), [])


class ClaimTests(_WithDirs):
    def test_claim_moves_pending_to_claimed(self):
        path = order_inbox.write_pending({"task_id": "C1-1.0", "channel": "C1", "ts": "1.0", "text": "x"})
        claimed = order_inbox.claim(path)
        self.assertIsNotNone(claimed)
        self.assertFalse(path.exists())
        self.assertTrue(claimed.is_file())
        self.assertEqual(order_inbox.list_claimed(), [claimed])

    def test_second_claim_of_same_file_returns_none(self):
        path = order_inbox.write_pending({"task_id": "C1-1.0", "channel": "C1", "ts": "1.0", "text": "x"})
        first = order_inbox.claim(path)
        second = order_inbox.claim(path)  # same (now-vanished) source path
        self.assertIsNotNone(first)
        self.assertIsNone(second)

    def test_archive_moves_claimed_to_processed(self):
        path = order_inbox.write_pending({"task_id": "C1-1.0", "channel": "C1", "ts": "1.0", "text": "x"})
        claimed = order_inbox.claim(path)
        dest = order_inbox.archive(claimed)
        self.assertFalse(claimed.exists())
        self.assertTrue(dest.is_file())
        self.assertEqual(order_inbox.list_claimed(), [])


class OutboxTests(_WithDirs):
    def test_write_and_load_outbox_round_trip(self):
        self.assertIsNone(order_inbox.load_outbox("C1-1.0"))
        order_inbox.write_outbox("C1-1.0", {"status": "DISPATCHING"})
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "DISPATCHING")
        order_inbox.write_outbox("C1-1.0", {"status": "COMPLETED"})
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "COMPLETED")


if __name__ == "__main__":
    unittest.main()
