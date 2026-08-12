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

    def test_parse_request_threads_task_id_and_raw_message(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            (project / ".git").mkdir()
            order = dispatcher.ORDERS_DIR / "996_test.md"
            order.write_text("# test", encoding="utf-8")
            self.addCleanup(order.unlink, missing_ok=True)
            message = (
                "[EXECUTE ORDER 996]\nexecutor: claude\n"
                f"order: {order}\nproject: {project}\n"
            )
            with patch.object(dispatcher, "executor_prefix", return_value=[r"C:\bin\claude.exe"]):
                request = dispatcher.parse_request(message, task_id="C1-1.0")
            self.assertEqual(request.task_id, "C1-1.0")
            self.assertEqual(request.raw_message, message)

    def test_parse_request_without_task_id_defaults_to_none_but_keeps_message(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            (project / ".git").mkdir()
            order = dispatcher.ORDERS_DIR / "995_test.md"
            order.write_text("# test", encoding="utf-8")
            self.addCleanup(order.unlink, missing_ok=True)
            message = (
                "[EXECUTE ORDER 995]\nexecutor: claude\n"
                f"order: {order}\nproject: {project}\n"
            )
            with patch.object(dispatcher, "executor_prefix", return_value=[r"C:\bin\claude.exe"]):
                request = dispatcher.parse_request(message)
            self.assertIsNone(request.task_id)
            self.assertEqual(request.raw_message, message)

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

    def test_codex_command_uses_isolated_safe_config(self):
        request = dispatcher.DispatchRequest(
            order_id="003",
            executor="codex",
            order_path=str(dispatcher.ORDERS_DIR / "003_test.md"),
            project_path=str(dispatcher.COMMON_ROOT),
        )
        with patch.object(dispatcher, "executor_prefix", return_value=["node", "codex.js"]):
            command = dispatcher.executor_command(request, Path("summary.txt"))
        self.assertIn("--ignore-user-config", command)
        self.assertIn("workspace-write", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
        # approval_policy="never" would silently re-enable the exact
        # unattended-approval behavior --ignore-user-config exists to
        # strip from ~/.codex/config.toml's own dangerous global setting
        # (sandbox_mode = "danger-full-access", approval_policy = "never").
        # A prior commit (aac815c) added this flag AND a test asserting
        # its presence; both are wrong per this Order's own "no dangerous
        # bypass" rule -- fixed 2026-08-12 (work order task 3 audit).
        command_str = " ".join(command)
        self.assertNotIn("approval_policy", command_str)


class BuildPromptTests(unittest.TestCase):
    def test_omits_raw_section_when_no_raw_message(self):
        request = dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y",
        )
        prompt = dispatcher.build_prompt(request)
        self.assertNotIn("SLACK MESSAGE BEGIN", prompt)
        self.assertNotIn("task_id: None", prompt)

    def test_includes_task_id_and_verbatim_raw_message(self):
        # Korean content + a trailing Slack signature glued onto the same
        # line as "--- END ---", exactly the shape seen in ORDER 100's
        # real Slack message (work order 2026-08-12 task 3).
        raw = (
            "[EXECUTE ORDER 101]\nexecutor: claude\nproject: C:\\lab\\vsurf_capital\\common\n\n"
            "--- ORDER BODY ---\n번호: 101\n제목: loop_proof\n목적: 루프 검증\n"
            "--- END --- *다음을 사용하여 보냄* Claude"
        )
        request = dispatcher.DispatchRequest(
            order_id="101", executor="claude", order_path="x", project_path="y",
            task_id="C1-123.456", raw_message=raw,
        )
        prompt = dispatcher.build_prompt(request)
        self.assertIn("Slack task_id: C1-123.456", prompt)
        self.assertIn("--- SLACK MESSAGE BEGIN ---", prompt)
        self.assertIn("--- SLACK MESSAGE END ---", prompt)
        # Verbatim: no trimming/normalizing/summarizing of the raw text.
        self.assertIn(raw, prompt)

    def test_existing_fields_unchanged_when_raw_message_present(self):
        request = dispatcher.DispatchRequest(
            order_id="003", executor="claude",
            order_path=r"C:\lab\vsurf_capital\common\orders\003_x.md",
            project_path=r"C:\lab\vsurf_capital\common",
            task_id="C1-1.0", raw_message="[EXECUTE ORDER 003]\nexecutor: claude\n",
        )
        prompt = dispatcher.build_prompt(request)
        self.assertIn("Execute VSURF Order 003.", prompt)
        self.assertIn(r"Canonical Order: C:\lab\vsurf_capital\common\orders\003_x.md", prompt)
        self.assertIn("Do not commit or push", prompt)


if __name__ == "__main__":
    unittest.main()
