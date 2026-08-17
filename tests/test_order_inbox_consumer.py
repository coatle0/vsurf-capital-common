import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

MODULE_PATH = Path(__file__).parents[1] / "scripts" / "order_inbox_consumer.py"
SPEC = importlib.util.spec_from_file_location("order_inbox_consumer", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)

order_dispatcher = MODULE.order_dispatcher
order_inbox = MODULE.order_inbox
DispatchResult = order_dispatcher.DispatchResult
DispatchError = order_dispatcher.DispatchError


class _WithDirs(unittest.TestCase):
    """Isolates order_inbox's four state directories and order_dispatcher's
    RUNTIME_DIR (used for the last-result correlation check) per test."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        root = Path(self._tmp.name)
        senders_path = root / "order_senders.json"
        # Default fixture authorizes write_pending()'s default user "U1" so
        # existing dispatch-path tests don't need to know about the
        # allowlist. Sender-whitelist tests below override this directly.
        senders_path.write_text(
            json.dumps({"allowed_senders": [{"user_id": "U1", "label": "test"}]}), encoding="utf-8"
        )
        patches = {
            (order_inbox, "PENDING_DIR"): root / "pending",
            (order_inbox, "CLAIMED_DIR"): root / "claimed",
            (order_inbox, "OUTBOX_DIR"): root / "outbox",
            (order_inbox, "PROCESSED_DIR"): root / "processed",
            (order_dispatcher, "RUNTIME_DIR"): root / "dispatcher-runtime",
            (MODULE, "CONSUMER_LOCK_PATH"): root / "consumer.lock",
            (MODULE, "SENDERS_PATH"): senders_path,
        }
        self._patches = []
        for (target, attr), value in patches.items():
            p = patch.object(target, attr, value)
            p.start()
            self.addCleanup(p.stop)
            self._patches.append(p)
        self.addCleanup(self._tmp.cleanup)

    def write_pending(self, **overrides) -> Path:
        record = {
            "task_id": "C1-1.0",
            "channel": "C1",
            "ts": "1.0",
            "text": "hello there",
            "user": "U1",
            "received_at": "2026-08-09T00:00:00+00:00",
        }
        record.update(overrides)
        return order_inbox.write_pending(record)

    def completed_result(self, **overrides) -> DispatchResult:
        base = dict(
            order_id="003",
            executor="claude",
            status="COMPLETED",
            project_path=r"C:\lab\vsurf_capital\common",
            order_path=r"C:\lab\vsurf_capital\common\orders\003_x.md",
            started_at="t0",
            finished_at="2026-08-09T00:05:00+00:00",
            commit="a" * 40,
        )
        base.update(overrides)
        return DispatchResult(**base)


class NonOrderAndInvalidOrderTests(_WithDirs):
    def test_non_order_message_gets_note_reply_not_silent_ignore(self):
        path = self.write_pending(text="just chatting")
        with patch.object(MODULE, "reply") as mock_reply, patch.object(order_dispatcher, "dispatch") as mock_dispatch:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_not_called()
        mock_reply.assert_called_once()
        self.assertIn("NOTE", mock_reply.call_args.args[3])
        self.assertIn("EXECUTE ORDER", mock_reply.call_args.args[3])
        processed = order_inbox.list_pending()
        self.assertEqual(processed, [])  # moved out of pending/

    def test_invalid_order_is_rejected_without_dispatch(self):
        path = self.write_pending(text="[EXECUTE ORDER 999]\nexecutor: claude\n")
        with patch.object(order_dispatcher, "parse_request", side_effect=DispatchError("bad order")), \
             patch.object(order_dispatcher, "dispatch") as mock_dispatch, \
             patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_not_called()
        self.assertIn("REJECTED", mock_reply.call_args.args[3])
        self.assertIn("bad order", mock_reply.call_args.args[3])
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "REJECTED")


class SenderAllowlistTests(_WithDirs):
    def test_load_allowed_senders_reads_configured_ids(self):
        self.assertEqual(MODULE.load_allowed_senders(), {"U1"})

    def test_missing_allowlist_file_yields_empty_set(self):
        with patch.object(MODULE, "SENDERS_PATH", Path(self._tmp.name) / "does-not-exist.json"):
            self.assertEqual(MODULE.load_allowed_senders(), set())

    def test_unauthorized_sender_rejected_before_dispatch(self):
        path = self.write_pending(user="U_EVIL", text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        with patch.object(order_dispatcher, "parse_request") as mock_parse, \
             patch.object(order_dispatcher, "dispatch") as mock_dispatch, \
             patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_parse.assert_not_called()
        mock_dispatch.assert_not_called()
        reply_text = mock_reply.call_args.args[3]
        self.assertIn("REJECTED", reply_text)
        self.assertIn("sender not allowed", reply_text)
        processed = order_inbox.PROCESSED_DIR / path.name
        self.assertTrue(processed.is_file())
        self.assertEqual(order_inbox.load(processed)["result"]["status"], "REJECTED")
        self.assertEqual(order_inbox.load(processed)["result"]["sender"], "U_EVIL")

    def test_authorized_sender_reaches_dispatch(self):
        path = self.write_pending(user="U1", text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        fake_request = order_dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y"
        )
        with patch.object(order_dispatcher, "parse_request", return_value=fake_request) as mock_parse, \
             patch.object(order_dispatcher, "dispatch", return_value=self.completed_result()), \
             patch.object(MODULE, "reply"):
            MODULE.process_pending(path, "tok")
        mock_parse.assert_called_once()

    def test_empty_allowlist_fails_closed_even_for_normally_authorized_sender(self):
        senders_path = Path(self._tmp.name) / "order_senders.json"
        senders_path.write_text(json.dumps({"allowed_senders": []}), encoding="utf-8")
        path = self.write_pending(user="U1", text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        with patch.object(order_dispatcher, "dispatch") as mock_dispatch, patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_not_called()
        self.assertIn("allowlist is empty or unreadable", mock_reply.call_args.args[3])


class IntakeRegistrationTests(_WithDirs):
    """orders/100_order_intake.md's registration step, now done by
    process_pending() itself instead of by the LLM executor."""

    def setUp(self):
        super().setUp()
        self._orders_tmp = tempfile.TemporaryDirectory()
        self._orders_patch = patch.object(order_dispatcher, "ORDERS_DIR", Path(self._orders_tmp.name))
        self._orders_patch.start()
        self.addCleanup(self._orders_patch.stop)
        self.addCleanup(self._orders_tmp.cleanup)

    INTAKE_TEXT = (
        "[EXECUTE ORDER 100]\nexecutor: claude\nproject: C:\\lab\\vsurf_capital\\common\n\n"
        "--- ORDER BODY ---\n번호: 103\n제목: speed_check_v2\n목적: 테스트\n"
        "작업:\n1. 아무것도 안 함\nDoD: N/A\n"
        "--- END --- *다음을 사용하여 보냄* Claude"
    )

    def test_parse_intake_body_extracts_number_title_body_verbatim(self):
        parsed = MODULE.parse_intake_body(self.INTAKE_TEXT)
        self.assertEqual(parsed["number"], "103")
        self.assertEqual(parsed["title"], "speed_check_v2")
        self.assertIn("목적: 테스트", parsed["body"])
        # Trailing Slack signature (after --- END ---) must not leak into body.
        self.assertNotIn("다음을 사용하여 보냄", parsed["body"])

    def test_parse_intake_body_rejects_missing_markers(self):
        with self.assertRaises(DispatchError):
            MODULE.parse_intake_body("[EXECUTE ORDER 100]\nexecutor: claude\nno markers here\n")

    def test_parse_intake_body_rejects_order_number_100(self):
        text = self.INTAKE_TEXT.replace("번호: 103", "번호: 100")
        with self.assertRaises(DispatchError):
            MODULE.parse_intake_body(text)

    def test_register_new_order_file_writes_verbatim_body_with_header(self):
        path = MODULE.register_new_order_file("103", "speed_check_v2", "번호: 103\n제목: speed_check_v2\n목적: 테스트", "claude")
        content = path.read_text(encoding="utf-8")
        self.assertIn("발신: COO (via ORDER 100 intake)", content)
        self.assertIn("수신: claude", content)
        self.assertIn("목적: 테스트", content)
        self.assertEqual(path.name, "103_speed_check_v2.md")

    def test_register_new_order_file_rejects_existing_number(self):
        (Path(self._orders_tmp.name) / "103_already_here.md").write_text("x", encoding="utf-8")
        with self.assertRaises(DispatchError):
            MODULE.register_new_order_file("103", "speed_check_v2", "body", "claude")

    def test_process_pending_registers_then_dispatches_with_intake_body_preserved(self):
        path = self.write_pending(text=self.INTAKE_TEXT)
        fake_request = order_dispatcher.DispatchRequest(
            order_id="103", executor="claude", order_path="x", project_path="y"
        )
        with patch.object(order_dispatcher, "parse_request", return_value=fake_request) as mock_parse, \
             patch.object(order_dispatcher, "dispatch", return_value=self.completed_result(order_id="103")), \
             patch.object(MODULE, "reply"):
            MODULE.process_pending(path, "tok")
        # parse_request must receive the control header plus the original
        # Slack intake body; the canonical file is not the instruction source.
        called_text = mock_parse.call_args.args[0]
        self.assertIn("[EXECUTE ORDER 103]", called_text)
        self.assertIn("ORDER BODY", called_text)
        self.assertIn("목적: 테스트", called_text)
        registered = list(Path(self._orders_tmp.name).glob("103_*.md"))
        self.assertEqual(len(registered), 1)

    def test_process_pending_trims_glued_signature_from_intake_project(self):
        text = self.INTAKE_TEXT.replace(
            "project: C:\\lab\\vsurf_capital\\common\n",
            "project: C:\\lab\\vsurf_capital\\common *다음을 사용하여 보냄* <@U0BP56ZV2NT>\n",
        )
        path = self.write_pending(text=text)
        fake_request = order_dispatcher.DispatchRequest(
            order_id="103", executor="claude", order_path="x", project_path="y"
        )
        with patch.object(order_dispatcher, "parse_request", return_value=fake_request) as mock_parse, \
             patch.object(order_dispatcher, "dispatch", return_value=self.completed_result(order_id="103")), \
             patch.object(MODULE, "reply"):
            MODULE.process_pending(path, "tok")
        called_text = mock_parse.call_args.args[0]
        self.assertIn("project: C:\\lab\\vsurf_capital\\common\n", called_text)
        self.assertNotIn("다음을 사용하여 보냄", called_text)

    def test_process_pending_rejects_duplicate_order_number_without_dispatch(self):
        (Path(self._orders_tmp.name) / "103_taken.md").write_text("x", encoding="utf-8")
        path = self.write_pending(text=self.INTAKE_TEXT)
        with patch.object(order_dispatcher, "dispatch") as mock_dispatch, patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_not_called()
        self.assertIn("REJECTED", mock_reply.call_args.args[3])
        self.assertIn("already exists", mock_reply.call_args.args[3])

    def test_process_pending_non_intake_order_number_unaffected(self):
        # order_id != 100 must skip registration entirely and behave exactly
        # as before (regression check).
        path = self.write_pending(text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        with patch.object(order_dispatcher, "parse_request", side_effect=DispatchError("bad")), \
             patch.object(MODULE, "register_new_order_file") as mock_register, \
             patch.object(MODULE, "reply"):
            MODULE.process_pending(path, "tok")
        mock_register.assert_not_called()


class HappyPathTests(_WithDirs):
    def test_fresh_valid_order_dispatches_once_and_replies_with_commit(self):
        path = self.write_pending(text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        result = self.completed_result()
        with patch.object(order_dispatcher, "parse_request", return_value=order_dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y")), \
             patch.object(order_dispatcher, "dispatch", return_value=result) as mock_dispatch, \
             patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_called_once()
        reply_text = mock_reply.call_args.args[3]
        self.assertIn("COMPLETED", reply_text)
        self.assertIn("order 003", reply_text)
        self.assertIn("a" * 12, reply_text)
        self.assertEqual(order_inbox.list_claimed(), [])
        outbox = order_inbox.load_outbox("C1-1.0")
        self.assertEqual(outbox["status"], "COMPLETED")
        self.assertTrue(outbox["replied"])

    def test_reboot_recovers_leftover_pending_end_to_end(self):
        # Simulate: a message was durably written before a reboot and never
        # got past pending/. A fresh run_once() must process it normally.
        self.write_pending(text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        result = self.completed_result()
        with patch.object(order_dispatcher, "parse_request", return_value=order_dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y")), \
             patch.object(order_dispatcher, "dispatch", return_value=result), \
             patch.object(MODULE, "reply"):
            MODULE.run_once("tok")
        self.assertEqual(order_inbox.list_pending(), [])
        self.assertEqual(order_inbox.list_claimed(), [])
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "COMPLETED")


class DuplicateDeliveryTests(_WithDirs):
    def test_duplicate_pending_after_already_completed_does_not_redispatch(self):
        order_inbox.write_outbox("C1-1.0", {"status": "COMPLETED", "order_id": "003", "replied": True})
        path = self.write_pending(text="[EXECUTE ORDER 003]\nexecutor: claude\n")
        with patch.object(order_dispatcher, "dispatch") as mock_dispatch, patch.object(MODULE, "reply") as mock_reply:
            MODULE.process_pending(path, "tok")
        mock_dispatch.assert_not_called()
        mock_reply.assert_not_called()
        self.assertEqual(order_inbox.list_pending(), [])


class CrashRecoveryTests(_WithDirs):
    def test_crash_between_dispatch_return_and_outbox_write_adopts_prior_result(self):
        """Fault injection: dispatch() completed for real (its own result file
        is on disk, proving the lock was cleanly released) but the consumer
        died before recording that in outbox/. Recovery must NOT call
        dispatch() again."""
        record = {
            "task_id": "C1-1.0", "channel": "C1", "ts": "1.0",
            "text": (
                "[EXECUTE ORDER 003]\nexecutor: claude\n"
                r"order: C:\lab\vsurf_capital\common\orders\003_slack_order_pipeline_smoke.md" "\n"
                r"project: C:\lab\vsurf_capital\common" "\n"
            ),
            "user": "U1",
            "received_at": "2026-08-09T00:00:00+00:00", "claimed_at": "2026-08-09T00:01:00+00:00",
        }
        claimed_path = order_inbox.CLAIMED_DIR / "C1-1.0.json"
        claimed_path.parent.mkdir(parents=True, exist_ok=True)
        claimed_path.write_text(json.dumps(record), encoding="utf-8")
        order_inbox.write_outbox("C1-1.0", {"status": "DISPATCHING", "order_id": "003", "replied": False})

        prior = self.completed_result(finished_at="2026-08-09T00:02:00+00:00")  # after claimed_at
        order_dispatcher.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        (order_dispatcher.RUNTIME_DIR / "order-003-last.json").write_text(
            json.dumps(dataclasses_asdict(prior)), encoding="utf-8"
        )

        request = order_dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y"
        )
        with patch.object(order_dispatcher, "parse_request", return_value=request), \
             patch.object(order_dispatcher, "dispatch") as mock_dispatch, \
             patch.object(MODULE, "reply") as mock_reply:
            MODULE.handle_claimed(claimed_path, "tok")

        mock_dispatch.assert_not_called()
        self.assertIn("COMPLETED", mock_reply.call_args.args[3])
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "COMPLETED")
        self.assertEqual(order_inbox.list_claimed(), [])

    def test_stale_dispatching_outbox_with_no_prior_result_redispatches_once(self):
        """Fault injection: outbox shows DISPATCHING but no order_dispatcher
        result exists yet (crash happened before or during the real dispatch
        call) -- this is safe to retry because order_dispatcher's own
        OrderLock makes a genuinely-in-flight or truly-completed dispatch
        either fail fast or be a no-op double-check, never a silent
        duplicate."""
        record = {
            "task_id": "C1-1.0", "channel": "C1", "ts": "1.0",
            "text": "[EXECUTE ORDER 003]\nexecutor: claude\n", "user": "U1",
            "received_at": "2026-08-09T00:00:00+00:00", "claimed_at": "2026-08-09T00:01:00+00:00",
        }
        claimed_path = order_inbox.CLAIMED_DIR / "C1-1.0.json"
        claimed_path.parent.mkdir(parents=True, exist_ok=True)
        claimed_path.write_text(json.dumps(record), encoding="utf-8")
        order_inbox.write_outbox("C1-1.0", {"status": "DISPATCHING", "order_id": "003", "replied": False})

        result = self.completed_result()
        with patch.object(order_dispatcher, "parse_request", return_value=order_dispatcher.DispatchRequest(
            order_id="003", executor="claude", order_path="x", project_path="y")), \
             patch.object(order_dispatcher, "dispatch", return_value=result) as mock_dispatch, \
             patch.object(MODULE, "reply"):
            MODULE.handle_claimed(claimed_path, "tok")

        mock_dispatch.assert_called_once()
        self.assertEqual(order_inbox.load_outbox("C1-1.0")["status"], "COMPLETED")

    def test_reply_failure_after_result_saved_leaves_claimed_for_retry_then_succeeds(self):
        """Fault injection: result saved, then Slack reply fails. Retry must
        not call dispatch() again and must eventually archive."""
        record = {
            "task_id": "C1-1.0", "channel": "C1", "ts": "1.0",
            "text": "[EXECUTE ORDER 003]\nexecutor: claude\n", "user": "U1",
            "received_at": "2026-08-09T00:00:00+00:00", "claimed_at": "2026-08-09T00:01:00+00:00",
        }
        claimed_path = order_inbox.CLAIMED_DIR / "C1-1.0.json"
        claimed_path.parent.mkdir(parents=True, exist_ok=True)
        claimed_path.write_text(json.dumps(record), encoding="utf-8")
        order_inbox.write_outbox("C1-1.0", {
            "status": "COMPLETED", "order_id": "003", "commit": "a" * 40, "replied": False,
        })

        with patch.object(order_dispatcher, "dispatch") as mock_dispatch, \
             patch.object(MODULE, "reply", side_effect=RuntimeError("slack down")):
            with self.assertRaises(RuntimeError):
                MODULE.handle_claimed(claimed_path, "tok")
        mock_dispatch.assert_not_called()
        self.assertFalse(order_inbox.load_outbox("C1-1.0")["replied"])
        self.assertTrue(claimed_path.exists())  # not archived -- retry will pick it up

        with patch.object(order_dispatcher, "dispatch") as mock_dispatch2, patch.object(MODULE, "reply") as mock_reply2:
            MODULE.handle_claimed(claimed_path, "tok")
        mock_dispatch2.assert_not_called()  # status was already terminal
        mock_reply2.assert_called_once()
        self.assertTrue(order_inbox.load_outbox("C1-1.0")["replied"])
        self.assertFalse(claimed_path.exists())


class ConsumerLockTests(_WithDirs):
    def test_current_pid_is_alive_without_terminating_process(self):
        self.assertTrue(MODULE.ConsumerLock._pid_is_alive(os.getpid()))

    def test_second_lock_acquire_raises_while_first_held(self):
        with MODULE.ConsumerLock():
            with self.assertRaises(RuntimeError):
                with MODULE.ConsumerLock():
                    pass

    def test_lock_is_released_and_reacquirable_after_clean_exit(self):
        with MODULE.ConsumerLock():
            pass
        with MODULE.ConsumerLock():
            pass  # must not raise

    def test_dead_owner_is_quarantined_and_new_lock_acquired(self):
        MODULE.CONSUMER_LOCK_PATH.write_text(
            "pid=999999 started=2026-08-15T12:47:30+09:00", encoding="utf-8"
        )
        with patch.object(MODULE.ConsumerLock, "_pid_is_alive", return_value=False):
            with MODULE.ConsumerLock():
                self.assertIn(f"pid={os.getpid()}", MODULE.CONSUMER_LOCK_PATH.read_text())
                stale = list((MODULE.CONSUMER_LOCK_PATH.parent / "stale").iterdir())
                self.assertEqual(1, len(stale))
                self.assertIn("pid=999999", stale[0].read_text(encoding="utf-8"))
        self.assertFalse(MODULE.CONSUMER_LOCK_PATH.exists())

    def test_malformed_lock_fails_closed_and_is_preserved(self):
        MODULE.CONSUMER_LOCK_PATH.write_text("partial", encoding="utf-8")
        with self.assertRaisesRegex(RuntimeError, "Malformed consumer lock"):
            with MODULE.ConsumerLock():
                pass
        self.assertEqual("partial", MODULE.CONSUMER_LOCK_PATH.read_text(encoding="utf-8"))

    def test_concurrent_stale_recovery_keeps_singleton(self):
        MODULE.CONSUMER_LOCK_PATH.write_text(
            "pid=999998 started=2026-08-15T12:47:30+09:00", encoding="utf-8"
        )
        first = MODULE.ConsumerLock()
        second = MODULE.ConsumerLock()
        with patch.object(MODULE.ConsumerLock, "_pid_is_alive", side_effect=lambda pid: pid == os.getpid()):
            with first:
                with self.assertRaises(RuntimeError):
                    second.__enter__()
        stale = list((MODULE.CONSUMER_LOCK_PATH.parent / "stale").iterdir())
        self.assertEqual(1, len(stale))

    def test_recovery_is_reentrant_after_clean_exit(self):
        MODULE.CONSUMER_LOCK_PATH.write_text(
            "pid=999997 started=2026-08-15T12:47:30+09:00", encoding="utf-8"
        )
        with patch.object(MODULE.ConsumerLock, "_pid_is_alive", return_value=False):
            with MODULE.ConsumerLock():
                pass
        with MODULE.ConsumerLock():
            pass


class ThreadReplyTests(_WithDirs):
    def test_reply_targets_original_message_via_thread_ts(self):
        with patch.object(MODULE, "api") as mock_api:
            MODULE.reply("tok", "C1", "1699999999.000100", "hello")
        method, token, payload = mock_api.call_args.args
        self.assertEqual(method, "chat.postMessage")
        self.assertEqual(payload["thread_ts"], "1699999999.000100")
        self.assertEqual(payload["channel"], "C1")


def dataclasses_asdict(result: DispatchResult) -> dict:
    import dataclasses
    return dataclasses.asdict(result)


if __name__ == "__main__":
    unittest.main()
