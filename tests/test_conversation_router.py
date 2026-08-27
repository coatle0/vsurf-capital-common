import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "conversation_router.py"
SPEC = importlib.util.spec_from_file_location("conversation_router", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.store = MODULE.ConversationStore(Path(self.temp.name) / "router.sqlite3")
        self.posts = []
        self.enqueue = Mock(return_value="C1-2.0")

    def tearDown(self):
        self.temp.cleanup()

    def event(self, text, ts="1.0", thread_ts=None):
        event = {"channel": "C1", "ts": ts, "user": "U1", "text": text}
        if thread_ts:
            event["thread_ts"] = thread_ts
        return event

    def route(self, event):
        return MODULE.route_event(event, self.store, self.posts.append, self.enqueue)

    def test_direct_execute_is_proposed_not_enqueued(self):
        self.route(self.event("[EXECUTE ORDER 7]\nexecutor: codex"))
        self.assertEqual(self.store.get("C1", "1.0")["state"], "PROPOSED")
        self.enqueue.assert_not_called()

    def test_approve_queues_exactly_once(self):
        self.route(self.event("run [EXECUTE ORDER 7]\nexecutor: codex"))
        self.route(self.event("approve", ts="2.0", thread_ts="1.0"))
        self.route(self.event("approve", ts="3.0", thread_ts="1.0"))
        self.enqueue.assert_called_once()
        self.assertEqual(self.store.get("C1", "1.0")["state"], "QUEUED")

    def test_enqueue_failure_restores_proposed(self):
        self.route(self.event("run [EXECUTE ORDER 7]"))
        self.enqueue.side_effect = OSError("disk full")
        with patch.object(MODULE.order_inbox, "task_exists", return_value=False), self.assertRaises(OSError):
            self.route(self.event("approve", ts="2.0", thread_ts="1.0"))
        self.assertEqual(self.store.get("C1", "1.0")["state"], "PROPOSED")

    def test_ack_failure_after_durable_write_stays_queued(self):
        self.route(self.event("run [EXECUTE ORDER 7]"))
        self.enqueue.side_effect = OSError("Slack ACK failed")
        with patch.object(MODULE.order_inbox, "task_exists", return_value=True), self.assertRaises(OSError):
            self.route(self.event("approve", ts="2.0", thread_ts="1.0"))
        self.assertEqual(self.store.get("C1", "1.0")["state"], "QUEUED")
        self.route(self.event("approve", ts="3.0", thread_ts="1.0"))
        self.assertEqual(self.enqueue.call_count, 1)

    def test_cancel_never_enqueues(self):
        self.route(self.event("run [EXECUTE ORDER 7]"))
        self.route(self.event("cancel", ts="2.0", thread_ts="1.0"))
        self.assertEqual(self.store.get("C1", "1.0")["state"], "CANCELLED")
        self.enqueue.assert_not_called()

    def test_ambiguous_mutation_is_fail_closed(self):
        self.route(self.event("재시도해줘"))
        self.enqueue.assert_not_called()
        self.assertIn("UNCLASSIFIED", self.posts[-1])

    def test_run_requires_full_order_payload(self):
        self.route(self.event("run fix it"))
        self.enqueue.assert_not_called()
        self.assertIn("rejected", self.posts[-1])

    def test_slack_connector_signature_is_removed_before_command_classification(self):
        self.route(self.event("help *다음을 사용하여 보냄* ChatGPT"))
        self.assertIn("Commands:", self.posts[-1])
        self.enqueue.assert_not_called()

    def test_result_reads_outbox_without_execution(self):
        self.route(self.event("run [EXECUTE ORDER 7]"))
        self.route(self.event("approve", ts="2.0", thread_ts="1.0"))
        with patch.object(MODULE.order_inbox, "load_outbox", return_value={"status": "COMPLETED"}):
            self.route(self.event("result", ts="3.0", thread_ts="1.0"))
        self.assertIn("COMPLETED", self.posts[-1])


if __name__ == "__main__":
    unittest.main()
