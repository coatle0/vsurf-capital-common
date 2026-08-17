import importlib.util
import json
import os
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

    def test_accepts_grok_executor(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            (project / ".git").mkdir()
            order = dispatcher.ORDERS_DIR / "993_test.md"
            order.write_text("# test", encoding="utf-8")
            self.addCleanup(order.unlink, missing_ok=True)
            message = (
                "[EXECUTE ORDER 993]\nexecutor: grok\n"
                f"order: {order}\nproject: {project}\n"
            )
            with patch.object(dispatcher, "executor_prefix", return_value=["node", "grok"]):
                request = dispatcher.parse_request(message)
            self.assertEqual(request.executor, "grok")

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

    def test_parse_request_trims_glued_slack_signature_from_project_only(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            project = Path(raw)
            (project / ".git").mkdir()
            order = dispatcher.ORDERS_DIR / "994_test.md"
            order.write_text("# test", encoding="utf-8")
            self.addCleanup(order.unlink, missing_ok=True)
            message = (
                "[EXECUTE ORDER 994]\nexecutor: codex\n"
                f"order: {order}\n"
                f"project: {project} *다음을 사용하여 보냄* Claude"
            )
            with patch.object(dispatcher, "executor_prefix", return_value=[r"C:\bin\codex.exe"]):
                request = dispatcher.parse_request(message)
            self.assertEqual(request.project_path, str(project.resolve()))
            self.assertEqual(request.raw_message, message)

    def test_clean_field_value_is_narrow(self):
        self.assertEqual(
            dispatcher.clean_field_value("codex *다음을 사용하여 보냄* Claude"),
            "codex",
        )
        self.assertEqual(
            dispatcher.clean_field_value(r"C:\lab\Claude\project"),
            r"C:\lab\Claude\project",
        )
        self.assertEqual(
            dispatcher.clean_field_value("project sent using Claude"),
            "project sent using Claude",
        )
        self.assertEqual(
            dispatcher.clean_field_value(
                r"C:\lab\vsurf_capital\common *다음을 사용하여 보냄* <@U0BP56ZV2NT>"
            ),
            r"C:\lab\vsurf_capital\common",
        )

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

    def test_codex_command_inherits_user_config_but_forces_safe_settings(self):
        request = dispatcher.DispatchRequest(
            order_id="003",
            executor="codex",
            order_path=str(dispatcher.ORDERS_DIR / "003_test.md"),
            project_path=str(dispatcher.COMMON_ROOT),
        )
        with patch.object(dispatcher, "executor_prefix", return_value=["node", "codex.js"]):
            command = dispatcher.executor_command(request, Path("summary.txt"))
        self.assertNotIn("--ignore-user-config", command)
        self.assertIn("--approve-for-me", command)
        self.assertNotIn("--dangerously-bypass-approvals-and-sandbox", command)
        # User config is inherited so MCP definitions remain available.
        # --approve-for-me supplies automatic review for PermissionRequest
        # events in headless execution; approval_policy="never" instead
        # cancelled Neo4j write tools because no interactive UI existed
        # (Order 139). windows.sandbox remains a highest-precedence override,
        # while --approve-for-me itself selects workspace-write.
        command_str = " ".join(command)
        self.assertNotIn('approval_policy="never"', command_str)
        self.assertIn('windows.sandbox="elevated"', command_str)
        self.assertNotIn("mcp_servers.tikr.command=", command_str)
        self.assertNotIn("mcp_servers.gs.command=", command_str)
        self.assertNotIn("danger-full-access", command_str)

    def test_grok_command_is_headless_and_push_denied(self):
        request = dispatcher.DispatchRequest(
            order_id="004", executor="grok", order_path="x", project_path=r"C:\lab\vsurf_capital\common"
        )
        with patch.object(dispatcher, "executor_prefix", return_value=["node", "grok"]):
            command = dispatcher.executor_command(request, Path("summary.txt"))
        self.assertIn("-p", command)
        self.assertIn("--permission-mode", command)
        self.assertIn("dontAsk", command)
        self.assertIn("--output-format", command)
        self.assertIn("json", command)
        self.assertIn("Bash(git push*)", command)
        self.assertNotIn("--always-approve", command)
        self.assertNotIn("bypassPermissions", command)

    def test_grok_summary_json_is_written_and_malformed_fails_closed(self):
        with tempfile.TemporaryDirectory(dir=r"C:\lab") as raw:
            summary = Path(raw) / "summary.txt"
            dispatcher.write_grok_summary(json.dumps({"text": "completed"}), summary)
            self.assertEqual("completed\n", summary.read_text(encoding="utf-8"))
            with self.assertRaisesRegex(dispatcher.DispatchError, "malformed JSON"):
                dispatcher.write_grok_summary("not-json", summary)
            with self.assertRaisesRegex(dispatcher.DispatchError, "no non-empty text"):
                dispatcher.write_grok_summary(json.dumps({"text": ""}), summary)

    def test_grok_prompt_requires_actual_write_and_extracts_outputs(self):
        request = dispatcher.DispatchRequest(
            order_id="143", executor="grok",
            order_path=str(dispatcher.ORDERS_DIR / "143_grok_executor_e2e.md"),
            project_path=str(dispatcher.COMMON_ROOT),
        )
        prompt = dispatcher.build_prompt(request, ["reports/143_grok_executor_e2e.md"])
        self.assertIn("actual filesystem changes", prompt)
        self.assertIn("Write/Edit", prompt)
        self.assertIn("reports/143_grok_executor_e2e.md", prompt)
        self.assertEqual(["reports/143_grok_executor_e2e.md"], dispatcher.required_output_paths(request))

    def test_slack_body_is_instruction_source_and_output_guard_source(self):
        body = (
            "[EXECUTE ORDER 143]\nexecutor: grok\n"
            "order: C:\\lab\\vsurf_capital\\common\\orders\\143_grok_executor_e2e.md\n"
            "project: C:\\lab\\vsurf_capital\\common\n"
            "작업: reports/slack_body_result.md 파일을 실제로 작성한다.\n"
        )
        request = dispatcher.DispatchRequest(
            order_id="143", executor="grok", order_path=str(dispatcher.ORDERS_DIR / "143_grok_executor_e2e.md"),
            project_path=str(dispatcher.COMMON_ROOT), raw_message=body,
        )
        prompt = dispatcher.build_prompt(request)
        self.assertIn("sole source of task instructions", prompt)
        self.assertIn("Do not read or execute task instructions from the canonical Order file", prompt)
        self.assertEqual(["reports/slack_body_result.md"], dispatcher.required_output_paths(request))

    def test_user_config_inventory_and_write_warning_are_value_free(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            config = root / "config.toml"
            config.write_text(
                '[mcp_servers.tikr]\ncommand="secret-command"\n'
                '[mcp_servers.github]\nurl="https://example.invalid"\n'
                '[mcp_servers.disabled]\nenabled=false\ncommand="x"\n',
                encoding="utf-8",
            )
            audit_log = root / "audit.log"
            with patch.object(dispatcher, "MCP_AUDIT_LOG", audit_log):
                loaded, write_capable = dispatcher.audit_user_config_mcps(config)
            self.assertEqual(loaded, ["github", "tikr"])
            self.assertEqual(write_capable, ["github"])
            text = audit_log.read_text(encoding="utf-8")
            self.assertIn("github, tikr", text)
            self.assertNotIn("secret-command", text)

    def test_registry_resolver_uses_environment_overrides_and_checks_files(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            python = root / "python.exe"
            server = root / "gs_mcp_server.py"
            rscript = root / "Rscript.exe"
            for path in (python, server, rscript):
                path.touch()
            env = {
                "GS_PYTHON": str(python),
                "GS_MCP_SERVER": str(server),
                "GS_RSCRIPT": str(rscript),
                "APPDATA": str(root / "roaming"),
                "LOCALAPPDATA": str(root / "local"),
                "USERPROFILE": str(root / "user"),
            }
            with patch.dict(os.environ, env, clear=True):
                actual = dispatcher.resolve_mcp_config("gs")
            self.assertEqual(actual["command"], str(python.resolve()))
            self.assertEqual(actual["args"], [str(server.resolve())])
            self.assertEqual(actual["env"]["R_USER"], env["USERPROFILE"])

    def test_registry_resolver_rejects_missing_server_script(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            python = root / "python.exe"
            rscript = root / "Rscript.exe"
            python.touch()
            rscript.touch()
            env = {
                "GS_PYTHON": str(python),
                "GS_MCP_SERVER": str(root / "missing.py"),
                "GS_RSCRIPT": str(rscript),
                "APPDATA": str(root / "roaming"),
                "LOCALAPPDATA": str(root / "local"),
                "USERPROFILE": str(root / "user"),
            }
            with patch.dict(os.environ, env, clear=True):
                with self.assertRaises(dispatcher.DispatchError):
                    dispatcher.resolve_mcp_config("gs")

    def test_registry_generates_enabled_servers_without_server_branches(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            executable = root / "python.exe"
            server = root / "demo.py"
            executable.touch()
            server.touch()
            registry = {
                "version": 1,
                "mcp_servers": {
                    "demo": {
                        "enabled": True,
                        "command": {"default": str(executable), "must_exist": True},
                        "args": [{"default": str(server), "must_exist": True}],
                        "default_tools_approval_mode": "approve",
                        "env": {"DEMO_HOME": {"default": str(root), "required": True}},
                    },
                    "off": {"enabled": False},
                },
            }
            overrides = " ".join(dispatcher.mcp_config_overrides(registry))
            self.assertIn("mcp_servers.demo.command=", overrides)
            self.assertIn("mcp_servers.demo.args=", overrides)
            self.assertIn("mcp_servers.demo.env.DEMO_HOME=", overrides)
            self.assertNotIn("mcp_servers.off", overrides)

    def test_registry_load_rejects_invalid_shape(self):
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "registry.json"
            path.write_text('{"version": 2}', encoding="utf-8")
            with self.assertRaises(dispatcher.DispatchError):
                dispatcher.load_mcp_registry(path)


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
