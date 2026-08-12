import importlib.util
import subprocess
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


class CommitPendingRegistrationTests(unittest.TestCase):
    """dispatcher.dispatch() calls this immediately before
    ensure_clean_and_current(). ORDER 100 intake registration
    (order_inbox_consumer.py) writes orders/NNN_*.md without any Git
    operation, which otherwise trips ensure_clean_and_current()'s
    unconditional clean-tree check on the very first dispatch -- orders 103
    and 104 both failed exactly this way and had to be recovered by hand
    (commits 2fa4549, de8e2d8). This closes the gap narrowly: only the exact
    order_path file is ever staged/committed.
    """

    def _init_repo(self, path: Path) -> None:
        subprocess.run(["git", "init", "-q"], cwd=path, check=True)
        subprocess.run(["git", "config", "user.email", "test@test.local"], cwd=path, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=path, check=True)
        (path / "seed.txt").write_text("seed", encoding="utf-8")
        subprocess.run(["git", "add", "-A"], cwd=path, check=True)
        subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=path, check=True)

    def test_commits_only_the_untracked_order_file(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            self._init_repo(project)
            order = project / "orders" / "200_test.md"
            order.parent.mkdir(parents=True, exist_ok=True)
            order.write_text("# body", encoding="utf-8")

            dispatcher.commit_pending_registration(project, "200", str(order))

            self.assertEqual(dispatcher.git(project, "status", "--porcelain=v1"), "")
            self.assertEqual(
                dispatcher.git(project, "log", "-1", "--format=%s"),
                "Register ORDER 200 (auto, intake)",
            )

    def test_leaves_unrelated_dirty_files_for_clean_check_to_reject(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            self._init_repo(project)
            order = project / "orders" / "201_test.md"
            order.parent.mkdir(parents=True, exist_ok=True)
            order.write_text("# body", encoding="utf-8")
            (project / "seed.txt").write_text("modified, unrelated to registration", encoding="utf-8")

            dispatcher.commit_pending_registration(project, "201", str(order))

            status = dispatcher.git(project, "status", "--porcelain=v1")
            self.assertNotIn("orders/201_test.md", status)  # committed
            self.assertIn("M seed.txt", status)  # left dirty, on purpose
            with self.assertRaises(dispatcher.DispatchError):
                dispatcher.ensure_clean_and_current(project, pull=False)

    def test_noop_when_order_file_already_tracked_and_clean(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            self._init_repo(project)
            order = project / "orders" / "202_test.md"
            order.parent.mkdir(parents=True, exist_ok=True)
            order.write_text("# body", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=project, check=True)
            subprocess.run(["git", "commit", "-q", "-m", "pre-existing"], cwd=project, check=True)
            before = dispatcher.git(project, "rev-parse", "HEAD")

            dispatcher.commit_pending_registration(project, "202", str(order))

            self.assertEqual(dispatcher.git(project, "rev-parse", "HEAD"), before)


if __name__ == "__main__":
    unittest.main()
