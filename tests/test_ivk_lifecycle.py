import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ivk.kernel import initialize_run, plan_run
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


if __name__ == "__main__":
    unittest.main()
