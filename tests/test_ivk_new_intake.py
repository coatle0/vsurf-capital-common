import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_new_intake import IntakeValidationError, build_blueprint, normalize_intake


class IVKNewIntakeTests(unittest.TestCase):
    def setUp(self):
        self.raw = json.loads((ROOT / "examples/140_ai_optical_cpo_intake.json").read_text(encoding="utf-8"))
        self.graph = json.loads((ROOT / "examples/140_ai_optical_cpo_graph.json").read_text(encoding="utf-8"))

    def test_e2e_blueprint_is_complete_and_review_gated(self):
        result = build_blueprint(self.raw, self.graph, observed_at="2026-08-16T00:00:00Z")
        self.assertEqual(["NVDA", "COHR", "LITE", "CRDO"], [s["canonical_id"] for s in result["normalized"]["validated_seeds"]])
        self.assertEqual("neo4j-official.read_cypher", result["existing_graph"]["read_path"])
        self.assertEqual(4, len(result["unresolved_seeds"]))
        self.assertFalse(result["epistemic_policy"]["auto_confirm"])
        self.assertEqual("pending", result["review_status"])
        self.assertEqual({"drivers", "bottlenecks", "beneficiaries"}, set(result["candidate_slots"]))

    def test_missing_required_field(self):
        raw = dict(self.raw); raw.pop("thesis")
        with self.assertRaisesRegex(IntakeValidationError, "missing required"):
            normalize_intake(raw)

    def test_duplicate_seed_after_normalization(self):
        raw = dict(self.raw); raw["seed"] = ["nvda", " NVDA "]
        with self.assertRaisesRegex(IntakeValidationError, "duplicate seed"):
            normalize_intake(raw)

    def test_empty_seed(self):
        raw = dict(self.raw); raw["seed"] = []
        with self.assertRaisesRegex(IntakeValidationError, "at least one"):
            normalize_intake(raw)

    def test_malformed_type(self):
        raw = dict(self.raw); raw["questions"] = "not-an-array"
        with self.assertRaisesRegex(IntakeValidationError, "must be an array"):
            normalize_intake(raw)

    def test_frame_nickname_resolves_to_versioned_frame(self):
        raw = dict(self.raw); raw["frame"] = "svb"
        normalized = normalize_intake(raw)
        self.assertEqual("Sponsor→Value Chain→Bottleneck", normalized["primary_frame"])
        self.assertEqual("sponsor_valuechain_bottleneck", normalized["frame_ref"]["id"])
        self.assertEqual("svb", normalized["frame_ref"]["nickname"])

    def test_matrix_is_a_frame_kind(self):
        raw = dict(self.raw); raw["frame"] = "matrix"
        normalized = normalize_intake(raw)
        self.assertEqual("Matrix", normalized["primary_frame"])
        self.assertEqual("matrix", normalized["frame_ref"]["id"])

    def test_stream_is_upstream_midstream_downstream_frame(self):
        raw = dict(self.raw); raw["frame"] = "stream"
        normalized = normalize_intake(raw)
        self.assertEqual("Upstream→Midstream→Downstream", normalized["primary_frame"])
        self.assertEqual("upstream_midstream_downstream", normalized["frame_ref"]["id"])


if __name__ == "__main__":
    unittest.main()
