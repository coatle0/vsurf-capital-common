import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_new_intake import IntakeValidationError, build_blueprint, normalize_intake, validate_intake


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

    def test_mixed_market_normalizes_us_kr_jp_tw(self):
        raw = dict(self.raw)
        raw["market"] = "mixed"
        raw["seed"] = ["NVDA", "FORM", "KR:131290", "JP:6855", "TW:6515"]
        seeds = normalize_intake(raw)["validated_seeds"]
        self.assertEqual(
            ["NVDA", "FORM", "KRX:131290", "TSE:6855", "TWSE:6515"],
            [seed["canonical_id"] for seed in seeds],
        )
        self.assertEqual("A131290", seeds[2]["provider_ids"]["tikr"])

    def test_mixed_market_rejects_unprefixed_numeric_seed(self):
        raw = dict(self.raw)
        raw["seed"] = ["131290"]
        with self.assertRaisesRegex(IntakeValidationError, "requires KR:, JP:, or TW:"):
            normalize_intake(raw)

    def test_single_market_applies_once_to_all_numeric_seeds(self):
        raw = dict(self.raw)
        raw["market"] = "jp"
        raw["seed"] = ["6855", "6871"]
        seeds = normalize_intake(raw)["validated_seeds"]
        self.assertEqual(["TSE:6855", "TSE:6871"], [seed["canonical_id"] for seed in seeds])

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

    def test_legacy_input_upgrades_to_v1_new(self):
        canonical = validate_intake(self.raw)
        self.assertEqual("ivk-intake-1.0", canonical["contract_version"])
        self.assertEqual("new", canonical["operation"])
        self.assertIsNone(canonical["target_vc"])

    def test_add_requires_target_vc(self):
        raw = {
            "contract_version": "ivk-intake-1.0", "operation": "add",
            "target_vc": None, "name": None, "seed": ["MPI"], "frame": "matrix",
            "thesis": "Add MPI", "questions": [], "scope": [], "known_links": [],
            "limitations": [], "references": [],
            "options": {"write_policy": "approval_required"},
        }
        with self.assertRaisesRegex(IntakeValidationError, "target_vc"):
            validate_intake(raw)

    def test_add_and_expand_normalize_target_vc(self):
        for operation in ("add", "expand"):
            raw = {
                "contract_version": "ivk-intake-1.0", "operation": operation,
                "target_vc": "vc:sti-ecosystem", "name": None, "seed": ["MPI"],
                "frame": "matrix", "thesis": "Extend STI", "questions": [],
                "scope": ["value_chain"], "known_links": [], "limitations": [],
                "references": [], "options": {"write_policy": "approval_required"},
            }
            normalized = normalize_intake(raw)
            self.assertEqual(operation, normalized["operation"])
            self.assertEqual("vc:sti-ecosystem", normalized["target_vc"])
            self.assertEqual("MPI", normalized["validated_seeds"][0]["canonical_id"])

    def test_update_allows_empty_seed_and_null_frame(self):
        raw = {
            "contract_version": "ivk-intake-1.0", "operation": "update",
            "target_vc": "vc:sti-ecosystem", "name": None, "seed": [], "frame": None,
            "thesis": "Refresh time series", "questions": [], "scope": ["financials"],
            "known_links": [], "limitations": [], "references": [],
            "options": {"periods": 5, "write_policy": "approval_required"},
        }
        normalized = normalize_intake(raw)
        self.assertEqual("update", normalized["operation"])
        self.assertEqual("vc:sti-ecosystem", normalized["target_vc"])
        self.assertEqual([], normalized["validated_seeds"])


if __name__ == "__main__":
    unittest.main()
