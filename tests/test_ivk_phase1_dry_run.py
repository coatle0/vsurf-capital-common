import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_phase1_dry_run import DryRunValidationError, build_outputs


class Phase1DryRunTests(unittest.TestCase):
    def setUp(self):
        self.plan = {
            "contract_version": "ivk-source-plan-1.0",
            "value_chain": {
                "name": "US Optical Ecosystem", "slug": "us-optical-ecosystem",
                "operation": "new", "target_vc": None,
            },
            "tasks": [
                {"seed": "LITE", "task_type": "entity_resolution"},
                {"seed": "COHR", "task_type": "entity_resolution"},
                {"seed": None, "task_type": "question_evidence"},
            ],
        }
        self.collection = {
            "contract_version": "ivk-source-collection-0.1",
            "run_id": "TEST-US-OPTIC-001",
            "documents": [
                {
                    "evidence_id": "test-LITE", "ticker": "LITE", "company_id": "1",
                    "company_name": "Lumentum", "exchange": "NASDAQ",
                    "source_ref": "test.company_overview:LITE", "facts": ["Optical component supplier."],
                },
                {
                    "evidence_id": "test-COHR", "ticker": "COHR", "company_id": "2",
                    "company_name": "Coherent", "exchange": "NYSE",
                    "source_ref": "test.company_overview:COHR", "facts": ["Photonics supplier."],
                },
            ],
        }

    def test_full_minimal_contract_path(self):
        out = build_outputs(self.plan, self.collection)
        self.assertEqual(2, len(out["evidence"]["documents"]))
        self.assertEqual([], out["evidence"]["coverage"]["unresolved_seeds"])
        self.assertFalse(out["evidence"]["auto_confirm"])
        self.assertEqual([], out["ke"]["assertions"])
        self.assertEqual("candidate_identity_only", out["ke"]["governance"]["write_scope"])
        self.assertTrue(out["review"]["quality_gates"]["all_nodes_have_provenance"])
        self.assertEqual("vc:us-optical-ecosystem", out["ke"]["value_chain"]["id"])

    def test_missing_provenance_rejects(self):
        self.collection["documents"][0]["source_ref"] = ""
        with self.assertRaisesRegex(DryRunValidationError, "provenance"):
            build_outputs(self.plan, self.collection)


if __name__ == "__main__":
    unittest.main()
