import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ivk.kernel import KernelError, block_for_graph, initialize_run, plan_run, resume_run


class IVKKernelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.runs = self.root / "runs"
        self.input = self.root / "input.json"
        self.graph = self.root / "graph.json"
        self.input.write_text(json.dumps({
            "contract_version": "ivk-intake-1.0",
            "operation": "new",
            "target_vc": None,
            "name": "Test Optical Ecosystem",
            "seed": ["LITE", "COHR"],
            "frame": "matrix",
            "thesis": "Test optical demand and bottlenecks.",
            "questions": ["Where is the bottleneck?"],
            "scope": ["value_chain"],
            "known_links": [],
            "limitations": [],
            "references": [],
            "options": {"periods": 5, "auto_expand": True, "write_policy": "approval_required"},
        }), encoding="utf-8")
        self.graph.write_text(json.dumps([
            {"seed": "LITE", "company": None, "value_chain": [], "assertions": []},
            {"seed": "COHR", "company": None, "value_chain": [], "assertions": []},
        ]), encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_init_plan_and_idempotent_resume(self):
        manifest = initialize_run(self.input, self.runs, "RUN-TEST-001")
        self.assertEqual("VALIDATED", manifest["status"])
        planned = plan_run(
            self.runs, "RUN-TEST-001", graph_results=self.graph,
            registry_path=ROOT / "registry/ivk_factory_packs.json",
            sector="optical_communications", regions=["us"],
        )
        self.assertEqual("PLANNED", planned["status"])
        self.assertEqual("plan", planned["last_completed_stage"])
        run_root = self.runs / "RUN-TEST-001"
        for name in ("manifest.json", "intake.json", "normalized.json", "existing_graph.json", "blueprint.json", "source_plan.json"):
            self.assertTrue((run_root / name).exists(), name)
        resumed = resume_run(self.runs, "RUN-TEST-001")
        self.assertEqual(planned, resumed)

    def test_missing_graph_blocks_and_resume_uses_saved_pack_selection(self):
        initialize_run(self.input, self.runs, "RUN-TEST-002")
        blocked = block_for_graph(
            self.runs, "RUN-TEST-002", sector="optical_communications",
            regions=["us"], registry=ROOT / "registry/ivk_factory_packs.json",
        )
        self.assertEqual("BLOCKED", blocked["status"])
        self.assertEqual("MISSING_GRAPH_RESULTS", blocked["blockers"][0]["reason_code"])
        resumed = resume_run(self.runs, "RUN-TEST-002", graph_results=self.graph)
        self.assertEqual("PLANNED", resumed["status"])

    def test_refuses_duplicate_run_id(self):
        initialize_run(self.input, self.runs, "RUN-TEST-003")
        with self.assertRaisesRegex(KernelError, "already exists"):
            initialize_run(self.input, self.runs, "RUN-TEST-003")


if __name__ == "__main__":
    unittest.main()
