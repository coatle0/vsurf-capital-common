import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ivk.enrichment import EnrichmentValidationError, prepare_enrichment


class IVKEnrichmentTests(unittest.TestCase):
    def setUp(self):
        self.registry = ROOT / "registry/ivk_factory_packs.json"
        self.intake = json.loads((ROOT / "intakes/new/kr_후공정.json").read_text(encoding="utf-8"))
        self.qa = json.loads((ROOT / "examples/kr_backend_enrichment_qa.json").read_text(encoding="utf-8"))

    def test_matrix_contract_separates_universal_unique_and_gap(self):
        bundle = prepare_enrichment(self.intake, self.qa, registry_path=self.registry)
        contract = bundle["analysis_contract"]
        self.assertEqual("matrix", contract["primary_frame"]["id"])
        self.assertEqual(["upstream_midstream_downstream"], [x["id"] for x in contract["secondary_frames"]])
        self.assertEqual(3, len([q for q in contract["investor_questions"] if not q["id"].startswith("custom:")]))
        self.assertIn("five_quarter_financials", contract["universal_requirements"])
        self.assertIn("processes_technologies", contract["universal_requirements"])
        self.assertIn("order_backlog", contract["universal_requirements"])
        self.assertIn("comparison_axes", contract["unique_requirements"]["outputs"])
        self.assertTrue(contract["unique_requirements"]["must_reference_universal_fact_ids"])
        self.assertEqual("company_fact_layer_shared_across_value_chains", bundle["universal_plan"]["ownership"])
        self.assertEqual("planned_secondary", bundle["unique_plan"]["secondary_view_plans"][0]["status"])
        self.assertIn("stage_positions", bundle["unique_plan"]["secondary_view_plans"][0]["outputs"])
        self.assertTrue(all(gap["revalidate_unique"] for gap in bundle["evidence_gaps"]["gaps"]))

    def test_each_frame_defines_three_investor_questions_and_extensions(self):
        cases = [("matrix", "matrix"), ("stream", "upstream_midstream_downstream"), ("svb", "sponsor_valuechain_bottleneck")]
        for selector, expected in cases:
            raw = json.loads(json.dumps(self.intake))
            raw["frame"] = selector
            qa = json.loads(json.dumps(self.qa))
            qa["secondary_frames"] = []
            bundle = prepare_enrichment(raw, qa, registry_path=self.registry)
            frame = bundle["analysis_contract"]["primary_frame"]
            self.assertEqual(expected, frame["id"])
            self.assertEqual({"earning_mechanism", "state_transition", "evidence_gap"}, set(frame["investor_questions"]))
            self.assertTrue(frame["extension_points"])

    def test_primary_frame_cannot_repeat_as_secondary(self):
        qa = json.loads(json.dumps(self.qa))
        qa["secondary_frames"] = ["matrix"]
        with self.assertRaisesRegex(EnrichmentValidationError, "primary frame"):
            prepare_enrichment(self.intake, qa, registry_path=self.registry)

    def test_auto_confirm_cannot_be_enabled(self):
        qa = json.loads(json.dumps(self.qa))
        qa["completion_gates"]["allow_auto_confirm"] = True
        with self.assertRaisesRegex(EnrichmentValidationError, "auto_confirm"):
            prepare_enrichment(self.intake, qa, registry_path=self.registry)

    def test_cli_writes_four_machine_readable_artifacts(self):
        with tempfile.TemporaryDirectory() as temp:
            result = subprocess.run(
                [sys.executable, "-m", "ivk", "prepare-enrichment",
                 "--input", str(ROOT / "intakes/new/kr_후공정.json"),
                 "--qa", str(ROOT / "examples/kr_backend_enrichment_qa.json"),
                 "--output-dir", temp],
                cwd=ROOT, capture_output=True, text=True, encoding="utf-8",
            )
            self.assertEqual(0, result.returncode, result.stderr + result.stdout)
            output = json.loads(result.stdout)
            self.assertEqual("ENRICHMENT_PLANNED", output["status"])
            for filename in ("analysis_contract.json", "universal_plan.json", "unique_plan.json", "evidence_gaps.json"):
                self.assertTrue((Path(temp) / filename).is_file(), filename)


if __name__ == "__main__":
    unittest.main()
