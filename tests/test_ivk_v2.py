import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_v2 import CausalRecord, load_records, migration_dry_run, query


class IVKV2Tests(unittest.TestCase):
    def test_review_packet_is_33_rows_and_has_evidence(self):
        with (ROOT / "data/127_bu030_taxonomy_review.csv").open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(33, len(rows))
        self.assertTrue(all(r["source_evidence"] and r["recommended_decision"] for r in rows))
        self.assertEqual(1, sum(r["special_case"] == "megatouch_total" for r in rows))
        self.assertEqual(2, sum(r["special_case"].startswith("micro2nano_note") for r in rows))

    def test_prototypes_are_guarded_and_complete(self):
        records = load_records(ROOT / "data/127_causal_prototypes.json")
        self.assertEqual({"company:form", "company:tse", "company:winway"},
                         {r.company_id for r in records})
        self.assertEqual({"EarningsDriverLink", "Bottleneck", "BeneficiaryAssessment"},
                         {r.kind for r in records})
        self.assertTrue(all(r.source and r.evidence for r in records))
        self.assertFalse(any(r.review_status == "accepted" for r in records))
        self.assertEqual(len(records), len({r.id for r in records}))
        self.assertTrue(query(records, company_id="company:tse"))

    def test_inference_cannot_be_accepted(self):
        record = CausalRecord("x", "Bottleneck", "c", "p", "m", "up", "unknown",
                              "s", "e", .5, "none", "inference", "accepted")
        with self.assertRaises(ValueError):
            record.validate()

    def test_order_129_decision_packet_has_twelve_ready_rows(self):
        with (ROOT / "data/129_bu030_decision_packet.csv").open(encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
        self.assertEqual(12, len(rows))
        required = {"추천안", "대안", "채택_시_영향", "defer_시_영향", "근거", "confidence"}
        self.assertTrue(required.issubset(rows[0]))
        self.assertTrue(all(all(r[k] for k in required) for r in rows))
        self.assertEqual(2, sum(r["deterministic_eligible"] == "true" for r in rows))

    def test_migration_dry_run_and_rollback_guards(self):
        records = load_records(ROOT / "data/127_causal_prototypes.json")
        plan = migration_dry_run(records)
        self.assertEqual("dry-run", plan["mode"])
        self.assertEqual(9, plan["write_count"])
        self.assertEqual(9, len(plan["rollback"]))
        self.assertEqual(0, plan["duplicate_count"])
        self.assertEqual(0, plan["auto_confirm_count"])


if __name__ == "__main__":
    unittest.main()
