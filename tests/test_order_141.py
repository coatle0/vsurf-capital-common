import copy
import json
import sys
import unittest
from pathlib import Path

import jsonschema

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_factory import FactoryValidationError, PackRegistry
from scripts.ivk_new_intake import IntakeValidationError, build_blueprint, normalize_intake


class Order141PhaseAE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = json.loads((ROOT / "examples/141_ai_data_center_power_intake.json").read_text(encoding="utf-8"))
        cls.graph = json.loads((ROOT / "examples/141_ai_data_center_power_graph.json").read_text(encoding="utf-8"))
        cls.observed_at = "2026-08-16T00:00:00Z"

    def test_intake_normalization_and_blueprint_are_deterministic(self):
        first = build_blueprint(self.raw, self.graph, observed_at=self.observed_at)
        second = build_blueprint(self.raw, self.graph, observed_at=self.observed_at)
        self.assertEqual(first, second)
        self.assertEqual(["VRT", "ETN", "VST", "ON", "WOLF"], [s["canonical_id"] for s in first["normalized"]["validated_seeds"]])
        self.assertEqual(self.raw["frame"], first["normalized"]["primary_frame"])
        self.assertEqual(self.raw["thesis"], first["normalized"]["thesis"])
        self.assertEqual(self.raw["questions"], first["normalized"]["questions"])
        self.assertEqual(set(self.raw["seed"]), {item["seed"] for item in first["unresolved_seeds"]})
        self.assertFalse(first["epistemic_policy"]["auto_confirm"])
        schema = json.loads((ROOT / "schemas/ivk_blueprint.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(schema).validate(first)

    def test_registry_rejects_missing_power_semiconductor_sector_pack(self):
        registry = PackRegistry(ROOT / "registry/ivk_factory_packs.json")
        with self.assertRaisesRegex(FactoryValidationError, "unknown sector pack: power semiconductor"):
            registry.select(frame=self.raw["frame"], sector="power semiconductor", regions=["us"])

    def test_negative_empty_seed_is_rejected(self):
        invalid = copy.deepcopy(self.raw)
        invalid["seed"] = []
        with self.assertRaisesRegex(IntakeValidationError, "at least one"):
            normalize_intake(invalid)

    def test_negative_malformed_field_type_is_rejected(self):
        invalid = copy.deepcopy(self.raw)
        invalid["questions"] = "not-an-array"
        with self.assertRaisesRegex(IntakeValidationError, "must be an array"):
            normalize_intake(invalid)


if __name__ == "__main__":
    unittest.main()
