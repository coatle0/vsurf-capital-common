import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "scripts" / "order_dispatcher.py"
SPEC = importlib.util.spec_from_file_location("order_dispatcher", SCRIPT)
dispatcher = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
sys.modules[SPEC.name] = dispatcher
SPEC.loader.exec_module(dispatcher)


class ParseRequestTests(unittest.TestCase):
    def test_accepts_canonical_order_and_project(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            (project / ".git").mkdir()
            order = dispatcher.ORDERS_DIR / "999_test.md"
            order.write_text("# test", encoding="utf-8")
            self.addCleanup(order.unlink, missing_ok=True)
            message = (
                "[EXECUTE ORDER 999]\n"
                "executor: codex\n"
                f"order: {order}\n"
                f"project: {project}\n"
            )
            with patch.object(dispatcher, "executor_prefix", return_value=[r"C:\bin\codex.exe"]):
                request = dispatcher.parse_request(message)
            self.assertEqual(request.order_id, "999")
            self.assertEqual(request.executor, "codex")

    def test_rejects_project_outside_lab(self):
        order = dispatcher.ORDERS_DIR / "998_test.md"
        order.write_text("# test", encoding="utf-8")
        self.addCleanup(order.unlink, missing_ok=True)
        message = (
            "[EXECUTE ORDER 998]\nexecutor: codex\n"
            f"order: {order}\nproject: C:\\Windows\n"
        )
        with self.assertRaises(dispatcher.DispatchError):
            dispatcher.parse_request(message)

    def test_rejects_duplicate_lock(self):
        lock = dispatcher.OrderLock("997")
        with lock:
            with self.assertRaises(dispatcher.DispatchError):
                with dispatcher.OrderLock("997"):
                    pass


if __name__ == "__main__":
    unittest.main()
