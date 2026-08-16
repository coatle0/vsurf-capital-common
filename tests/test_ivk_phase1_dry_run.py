import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_phase1_dry_run import DryRunValidationError, build_outputs


class Phase1DryRunTests(unittest.TestCase):
    def setUp(self):
        self.plan = json.loads((ROOT / "artifacts/141_ai_data_center_power_source_plan.json").read_text(encoding="utf-8"))
        self.collection = json.loads((ROOT / "artifacts/141_power_semiconductor_source_collection.json").read_text(encoding="utf-8"))

    def test_full_minimal_contract_path(self):
        out = build_outputs(self.plan, self.collection)
        self.assertEqual(5, len(out["evidence"]["documents"]))
        self.assertEqual([], out["evidence"]["coverage"]["unresolved_seeds"])
        self.assertFalse(out["evidence"]["auto_confirm"])
        self.assertEqual([], out["ke"]["assertions"])
        self.assertEqual("candidate_identity_only", out["ke"]["governance"]["write_scope"])
        self.assertTrue(out["review"]["quality_gates"]["all_nodes_have_provenance"])

    def test_missing_provenance_rejects(self):
        self.collection["documents"][0]["source_ref"] = ""
        with self.assertRaisesRegex(DryRunValidationError, "provenance"):
            build_outputs(self.plan, self.collection)


if __name__ == "__main__":
    unittest.main()
