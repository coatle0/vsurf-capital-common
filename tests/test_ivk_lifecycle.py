import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ivk.kernel import initialize_run, plan_run, read_json
from ivk.lifecycle import LifecycleError, collect_stage, ke_stage, validate_packets, write_batches


class IVKLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.runs = Path(self.temp.name) / "runs"
        self.intake = ROOT / "examples/ivk_lifecycle_fixture_intake.json"
        self.graph = ROOT / "examples/ivk_lifecycle_fixture_graph.json"
        self.docs = json.loads((ROOT / "examples/ivk_lifecycle_fixture_documents.json").read_text(encoding="utf-8"))
        self.structure = json.loads((ROOT / "examples/ivk_lifecycle_fixture_structure.json").read_text(encoding="utf-8"))

    def tearDown(self):
        self.temp.cleanup()

    def _plan(self):
        initialize_run(self.intake, self.runs, "RUN-FIXTURE-001")
        return plan_run(
            self.runs, "RUN-FIXTURE-001", graph_results=self.graph,
            registry_path=ROOT / "registry/ivk_factory_packs.json",
            sector="generic_test", regions=["us"],
        ), json.loads((self.runs / "RUN-FIXTURE-001/source_plan.json").read_text(encoding="utf-8"))

    def test_collect_ke_write_are_vc_neutral(self):
        _, plan = self._plan()
        collection = collect_stage(plan, self.docs["documents"], run_id="RUN-FIXTURE-001")
        packets = ke_stage(plan, collection, structure=self.structure)
        validate_packets(packets)
        self.assertEqual("vc:fixture_demo", packets["ke"]["value_chain"]["id"])
        self.assertEqual("candidate_pending_source", packets["ke"]["link_expansion"][0]["decision"])
        self.assertTrue(all(doc.get("publisher") for doc in packets["evidence"]["documents"]))
        batches = write_batches(packets["write_manifest"])
        joined = "\n".join(item["query"] for item in batches)
        self.assertIn("MERGE (vc:ValueChain {id:$id})", joined)
        self.assertIn("CANDIDATE_IN", joined)
        self.assertIn("c.security_id=row.security_id", joined)
        self.assertIn("c.name_local=coalesce(row.name_local,c.name_local)", joined)
        self.assertIn("c.country=coalesce(row.country,c.country)", joined)
        self.assertNotIn("us_optic", joined)
        self.assertNotIn("NVDA", joined)
        self.assertNotIn("DETACH DELETE", joined)
        self.assertNotIn("FinancialPeriod", joined)

    def test_missing_provenance_is_rejected(self):
        _, plan = self._plan()
        bad = json.loads(json.dumps(self.docs["documents"]))
        bad[0]["source_url"] = ""
        with self.assertRaisesRegex(LifecycleError, "missing field"):
            collect_stage(plan, bad, run_id="RUN-FIXTURE-001")

    def test_avgo_style_pending_source_is_allowed(self):
        _, plan = self._plan()
        collection = collect_stage(plan, self.docs["documents"], run_id="RUN-FIXTURE-001")
        packets = ke_stage(plan, collection, structure=self.structure)
        self.assertIn(packets["ke"]["link_expansion"][0]["decision"], {"candidate_pending_source"})

    def _cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-m", "ivk", *args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
        )

    def _fixture_to_batches(self) -> Path:
        self._plan()
        runs = str(self.runs)
        for args in (
            ["ingest-sources", "--run-id", "RUN-FIXTURE-001", "--runs-dir", runs,
             "--documents", str(ROOT / "examples/ivk_lifecycle_fixture_documents.json")],
            ["ke", "--run-id", "RUN-FIXTURE-001", "--runs-dir", runs,
             "--structure", str(ROOT / "examples/ivk_lifecycle_fixture_structure.json")],
            ["review", "--run-id", "RUN-FIXTURE-001", "--runs-dir", runs],
            ["emit-write-batches", "--run-id", "RUN-FIXTURE-001", "--runs-dir", runs],
        ):
            result = self._cli(*args)
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        return self.runs / "RUN-FIXTURE-001"

    def test_cli_fixture_stops_at_batch_ready(self):
        root = self._fixture_to_batches()
        manifest = read_json(root / "manifest.json")
        self.assertEqual("BATCH_READY", manifest["status"])
        self.assertNotEqual("WRITTEN", manifest["status"])
        self.assertNotEqual("VERIFIED", manifest["status"])
        verify = self._cli("verify", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs))
        self.assertNotEqual(0, verify.returncode)
        text = (verify.stdout + verify.stderr).lower()
        self.assertTrue("readback" in text or "write_confirmed" in text, text)
        self.assertEqual("BATCH_READY", read_json(root / "manifest.json")["status"])

    def test_write_without_receipt_is_not_written(self):
        root = self._fixture_to_batches()
        alias = self._cli("write", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs))
        self.assertEqual(0, alias.returncode, alias.stdout)
        self.assertEqual("BATCH_READY", read_json(root / "manifest.json")["status"])

    def test_confirm_write_and_verify_require_proof(self):
        root = self._fixture_to_batches()
        bad_receipt = root / "bad_receipt.json"
        bad_receipt.write_text(json.dumps({"contract_version": "nope", "run_id": "RUN-FIXTURE-001"}), encoding="utf-8")
        denied = self._cli(
            "confirm-write", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs),
            "--receipt", str(bad_receipt),
        )
        self.assertNotEqual(0, denied.returncode)
        self.assertEqual("BATCH_READY", read_json(root / "manifest.json")["status"])
        batches = read_json(root / "write_batches.json")
        receipt = {
            "contract_version": "ivk-write-receipt-0.1",
            "run_id": "RUN-FIXTURE-001",
            "executed_at": datetime.now(timezone.utc).isoformat(),
            "database": "neo4j",
            "identity": "bolt://fixture-dry-run",
            "batches": [{"name": item["name"], "ok": True, "result": []} for item in batches],
            "failed_batches": [],
        }
        receipt_path = root / "write_receipt.json"
        receipt_path.write_text(json.dumps(receipt), encoding="utf-8")
        confirmed = self._cli(
            "confirm-write", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs),
            "--receipt", str(receipt_path),
        )
        self.assertEqual(0, confirmed.returncode, confirmed.stdout)
        self.assertEqual("WRITE_CONFIRMED", read_json(root / "manifest.json")["status"])
        missing_rb = self._cli("verify", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs))
        self.assertNotEqual(0, missing_rb.returncode)
        fake_rb = root / "fake_readback.json"
        fake_rb.write_text(json.dumps({"ok": True}), encoding="utf-8")
        fake = self._cli(
            "verify", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs),
            "--readback", str(fake_rb),
        )
        self.assertNotEqual(0, fake.returncode)
        self.assertEqual("WRITE_CONFIRMED", read_json(root / "manifest.json")["status"])

    def test_stage_order_violation_rejected(self):
        initialize_run(self.intake, self.runs, "RUN-FIXTURE-001")
        result = self._cli("ke", "--run-id", "RUN-FIXTURE-001", "--runs-dir", str(self.runs))
        self.assertNotEqual(0, result.returncode)
        self.assertIn("rejected", (result.stdout + result.stderr).lower())

    def test_build_runs_deterministic_pipeline_to_batch_ready(self):
        result = self._cli(
            "build",
            "--input", str(self.intake),
            "--run-id", "RUN-BUILD-001",
            "--runs-dir", str(self.runs),
            "--graph-results", str(self.graph),
            "--documents", str(ROOT / "examples/ivk_lifecycle_fixture_documents.json"),
            "--structure", str(ROOT / "examples/ivk_lifecycle_fixture_structure.json"),
            "--sector", "generic_test",
            "--region", "us",
        )
        self.assertEqual(0, result.returncode, result.stderr + result.stdout)
        manifest = read_json(self.runs / "RUN-BUILD-001/manifest.json")
        self.assertEqual("BATCH_READY", manifest["status"])
        self.assertEqual("BATCH_READY", manifest["build_summary"]["terminal_status"])
        self.assertFalse(manifest["build_summary"]["live_write_proven"])
        self.assertTrue((self.runs / "RUN-BUILD-001/write_batches.json").exists())

    def test_build_rejects_readback_without_receipt(self):
        fake_readback = Path(self.temp.name) / "readback.json"
        fake_readback.write_text(json.dumps({"ok": True}), encoding="utf-8")
        result = self._cli(
            "build",
            "--input", str(self.intake),
            "--run-id", "RUN-BUILD-INVALID",
            "--runs-dir", str(self.runs),
            "--graph-results", str(self.graph),
            "--documents", str(ROOT / "examples/ivk_lifecycle_fixture_documents.json"),
            "--sector", "generic_test",
            "--region", "us",
            "--readback", str(fake_readback),
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("requires --receipt", result.stdout)

    def test_build_rejects_missing_neo4j_executor_before_write(self):
        result = self._cli(
            "build",
            "--input", str(self.intake),
            "--run-id", "RUN-BUILD-NO-EXECUTOR",
            "--runs-dir", str(self.runs),
            "--graph-results", str(self.graph),
            "--documents", str(ROOT / "examples/ivk_lifecycle_fixture_documents.json"),
            "--sector", "generic_test",
            "--region", "us",
            "--execute-neo4j",
            "--neo4j-python", str(Path(self.temp.name) / "missing-python.exe"),
        )
        self.assertNotEqual(0, result.returncode)
        self.assertIn("interpreter not found", result.stdout)
        manifest = read_json(self.runs / "RUN-BUILD-NO-EXECUTOR/manifest.json")
        self.assertEqual("BATCH_READY", manifest["status"])


if __name__ == "__main__":
    unittest.main()
