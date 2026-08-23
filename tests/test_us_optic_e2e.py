import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_new_intake import build_blueprint, normalize_intake
from scripts.ivk_us_optic_e2e import (
    RUN_ID,
    VC_ID,
    UsOpticE2EError,
    emit_artifacts,
    source_documents,
    validate_packets,
    write_batches,
)


class UsOpticE2ETests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = json.loads(
            (ROOT / "runs/IVK-20260823-US-OPTIC-E2E-001/source_plan.json").read_text(encoding="utf-8")
        )
        cls.intake = json.loads(
            (ROOT / "examples/us_optic_e2e_intake.json").read_text(encoding="utf-8")
        )
        cls.graph = json.loads(
            (ROOT / "artifacts/kernel_v01/us_optic_e2e_existing_graph.json").read_text(encoding="utf-8")
        )

    def test_intake_matches_order_seeds_and_svb_frame(self):
        normalized = normalize_intake(self.intake)
        self.assertEqual(
            ["NVDA", "COHR", "LITE", "CRDO"],
            [item["canonical_id"] for item in normalized["validated_seeds"]],
        )
        self.assertEqual("sponsor_valuechain_bottleneck", normalized["frame_ref"]["id"])
        self.assertEqual("us_optic", normalized["identity"]["name"])
        blueprint = build_blueprint(self.intake, self.graph, observed_at="2026-08-23T00:00:00Z")
        self.assertEqual(4, len(blueprint["unresolved_seeds"]))
        self.assertFalse(blueprint["epistemic_policy"]["auto_confirm"])

    def test_packets_pass_quality_gates(self):
        packets = emit_artifacts(self.plan, ROOT / "runs" / RUN_ID)
        validate_packets(packets)
        ke = packets["ke"]
        self.assertEqual(VC_ID, ke["value_chain"]["id"])
        self.assertEqual("us_optic", ke["value_chain"]["nickname"])
        self.assertEqual(12, len(source_documents()))
        self.assertEqual(3, len(ke["assertions"]))
        self.assertTrue(all(a["review_status"] == "pending" for a in ke["assertions"]))
        self.assertTrue(all(a["counter_evidence"] for a in ke["assertions"]))
        self.assertEqual(0, packets["review"]["confirmed_assertions"])
        self.assertEqual({"strengthen", "weaken", "reject"}, {item["decision"] for item in ke["link_expansion"]})
        self.assertEqual(18, packets["quality"]["us_optic_total"])
        self.assertEqual(23, packets["quality"]["sti_total"])
        dumped = json.dumps(ke).lower()
        self.assertNotIn("power semiconductor", dumped)
        self.assertNotIn("company:vrt", dumped)

    def test_write_batches_are_merge_only_and_skip_sti_labels(self):
        packets = emit_artifacts(self.plan, ROOT / "runs" / RUN_ID)
        batches = write_batches(packets["write_manifest"])
        joined = "\n".join(item["query"] for item in batches)
        self.assertIn("MERGE (vc:ValueChain {id:$id})", joined)
        self.assertNotIn("CREATE (", joined.replace("MERGE", ""))
        self.assertNotIn("DETACH DELETE", joined)
        self.assertNotIn("FinancialPeriod", joined)
        self.assertNotIn("InventorySnapshot", joined)
        self.assertNotIn("SegmentResult", joined)
        self.assertTrue(all("MERGE" in item["query"] for item in batches))

    def test_negative_auto_accept_is_rejected(self):
        packets = emit_artifacts(self.plan, ROOT / "runs" / RUN_ID)
        packets["ke"]["assertions"][0]["review_status"] = "accepted"
        with self.assertRaisesRegex(UsOpticE2EError, "auto-accepted"):
            validate_packets(packets)


if __name__ == "__main__":
    unittest.main()
