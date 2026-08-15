import csv
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_v2 import CausalRecord, load_records, query


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


if __name__ == "__main__":
    unittest.main()
