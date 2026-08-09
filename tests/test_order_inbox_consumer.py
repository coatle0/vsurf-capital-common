import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "order_inbox_consumer.py"
SPEC = importlib.util.spec_from_file_location("order_inbox_consumer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

DispatchResult = MODULE.order_dispatcher.DispatchResult
DispatchError = MODULE.order_dispatcher.DispatchError


def write_record(root: Path, **overrides) -> Path:
    record = {
        "task_id": "C1-1.0",
        "channel": "C1",
        "ts": "1.0",
        "text": "hello there",
        "user": "U1",
    }
    record.update(overrides)
    path = root / f"{record['task_id']}.json"
    path.write_text(json.dumps(record), encoding="utf-8")
    return path


class ProcessOneTests(unittest.TestCase):
    def test_ignores_non_order_message(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_record(Path(raw), text="just chatting")
            with patch.object(MODULE, "reply") as mock_reply, patch.object(
                MODULE.order_inbox, "mark_processed"
            ) as mock_mark:
                MODULE.process_one(path, "tok")
            mock_reply.assert_not_called()
            mock_mark.assert_called_once()
            self.assertEqual(mock_mark.call_args.args[1]["status"], "IGNORED")

    def test_rejects_invalid_order_and_replies(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_record(Path(raw), text="[EXECUTE ORDER 999]\nexecutor: claude\n")
            with patch.object(MODULE.order_dispatcher, "parse_request", side_effect=DispatchError("bad order")), \
                 patch.object(MODULE, "reply") as mock_reply, \
                 patch.object(MODULE.order_inbox, "mark_processed") as mock_mark:
                MODULE.process_one(path, "tok")
            self.assertIn("REJECTED", mock_reply.call_args.args[3])
            self.assertIn("bad order", mock_reply.call_args.args[3])
            self.assertEqual(mock_mark.call_args.args[1]["status"], "REJECTED")

    def test_completed_dispatch_replies_with_commit(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_record(Path(raw), text="[EXECUTE ORDER 003]\nexecutor: claude\n")
            fake_request = object()
            fake_result = DispatchResult(
                order_id="003",
                executor="claude",
                status="COMPLETED",
                project_path=r"C:\lab\vsurf_capital\common",
                order_path=r"C:\lab\vsurf_capital\common\orders\003_x.md",
                started_at="t0",
                finished_at="t1",
                commit="a" * 40,
            )
            with patch.object(MODULE.order_dispatcher, "parse_request", return_value=fake_request), \
                 patch.object(MODULE.order_dispatcher, "dispatch", return_value=fake_result), \
                 patch.object(MODULE, "reply") as mock_reply, \
                 patch.object(MODULE.order_inbox, "mark_processed") as mock_mark:
                MODULE.process_one(path, "tok")
            reply_text = mock_reply.call_args.args[3]
            self.assertIn("COMPLETED", reply_text)
            self.assertIn("order 003", reply_text)
            self.assertIn("a" * 12, reply_text)
            self.assertEqual(mock_mark.call_args.args[1]["status"], "COMPLETED")

    def test_failed_dispatch_replies_with_error(self):
        with tempfile.TemporaryDirectory() as raw:
            path = write_record(Path(raw), text="[EXECUTE ORDER 003]\nexecutor: claude\n")
            fake_result = DispatchResult(
                order_id="003",
                executor="claude",
                status="FAILED",
                project_path=r"C:\lab\vsurf_capital\common",
                order_path=r"C:\lab\vsurf_capital\common\orders\003_x.md",
                started_at="t0",
                finished_at="t1",
                error="git push failed: rejected",
            )
            with patch.object(MODULE.order_dispatcher, "parse_request", return_value=object()), \
                 patch.object(MODULE.order_dispatcher, "dispatch", return_value=fake_result), \
                 patch.object(MODULE, "reply") as mock_reply, \
                 patch.object(MODULE.order_inbox, "mark_processed") as mock_mark:
                MODULE.process_one(path, "tok")
            reply_text = mock_reply.call_args.args[3]
            self.assertIn("FAILED", reply_text)
            self.assertIn("git push failed", reply_text)
            self.assertEqual(mock_mark.call_args.args[1]["status"], "FAILED")


if __name__ == "__main__":
    unittest.main()
