import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ivk_factory import EvidenceStore, FactoryValidationError, PackRegistry, TokenLedger, build_source_plan


class IVKFactoryPhaseATests(unittest.TestCase):
    def setUp(self):
        self.registry = PackRegistry(ROOT / "registry/ivk_factory_packs.json")
        self.blueprint = json.loads((ROOT / "artifacts/140_ai_optical_cpo_blueprint.json").read_text(encoding="utf-8"))

    def test_pack_registry_composes_frame_sector_region(self):
        selection = self.registry.select(frame="Sponsor→Value Chain→Bottleneck", sector="CPO", regions=["USA"])
        self.assertEqual("sponsor_valuechain_bottleneck@1.0.0", selection.manifest()["frame"])
        self.assertEqual(["us@1.0.0"], selection.manifest()["regions"])

    def test_unknown_sector_uses_explicit_bootstrap_pack(self):
        selection = self.registry.select(
            frame="Sponsor→Value Chain→Bottleneck", sector="biotech", regions=["us"]
        )
        self.assertEqual("bootstrap", selection.sector["pack_mode"])
        self.assertEqual("biotech", selection.sector["requested_selector"])
        self.assertEqual("bootstrap_biotech@0.0.0", selection.manifest()["sector"])
        plan = build_source_plan(self.blueprint, selection)
        self.assertEqual("bootstrap", plan["pack_policy"]["mode"])
        self.assertFalse(plan["pack_policy"]["reusable_sector_pack"])

    def test_source_plan_is_complete_and_retains_unresolved_seeds(self):
        selection = self.registry.select(frame=self.blueprint["normalized"]["primary_frame"], sector="semiconductor_optical", regions=["us"])
        plan = build_source_plan(self.blueprint, selection)
        entity_tasks = [item for item in plan["tasks"] if item["task_type"] == "entity_resolution"]
        self.assertEqual({"NVDA", "COHR", "LITE", "CRDO"}, {item["seed"] for item in entity_tasks})
        self.assertFalse(plan["evidence_policy"]["auto_confirm"])
        self.assertEqual(50000, plan["token_budgets"]["evidence_extraction"])
        self.assertIn("earnings_call", plan["tasks"][0]["source_adapters"])

    def test_evidence_store_deduplicates_and_reuses_extraction(self):
        with tempfile.TemporaryDirectory() as tmp:
            with EvidenceStore(Path(tmp) / "evidence.db") as store:
                first, created = store.put_document(company_id="NVDA", source_type="10-Q", source_url="https://example.test/a", content="same")
                second, created_again = store.put_document(company_id="NVDA", source_type="10-Q", source_url="https://example.test/b", content="same")
                self.assertEqual(first, second)
                self.assertTrue(created)
                self.assertFalse(created_again)
                self.assertEqual(2, store.db.execute("SELECT count(*) FROM source_occurrences").fetchone()[0])
                section, section_created = store.put_section(first, "relevant section", heading="Optical")
                self.assertTrue(section_created)
                digest = store.db.execute("SELECT content_hash FROM sections WHERE section_id=?", (section,)).fetchone()[0]
                store.cache_extraction(digest, "extractor@1", {"facts": 2})
                self.assertEqual({"facts": 2}, store.get_extraction(digest, "extractor@1"))

    def test_token_ledger_enforces_budget_and_validates_counts(self):
        with tempfile.TemporaryDirectory() as tmp:
            with TokenLedger(Path(tmp) / "tokens.db") as ledger:
                ledger.record(run_id="r1", value_chain_id="vc1", stage="synthesis", model="small", input_tokens=900, cached_input_tokens=500, output_tokens=200, facts_accepted=3)
                self.assertEqual(1100, ledger.budget_status("r1", {"synthesis": 1000})["stages"]["synthesis"]["used"])
                self.assertTrue(ledger.budget_status("r1", {"synthesis": 1000})["exceeded"])
                self.assertEqual(3, ledger.totals("r1")["facts_accepted"])
                with self.assertRaises(FactoryValidationError):
                    ledger.record(run_id="r1", value_chain_id="vc1", stage="bad", model="small", input_tokens=1, cached_input_tokens=2)


if __name__ == "__main__":
    unittest.main()
