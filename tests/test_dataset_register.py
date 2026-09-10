import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "assurance" / "dataset_register.json"
CONTRACTS = ROOT / "assurance" / "curated_dataset_contracts.json"


class DatasetRegisterTests(unittest.TestCase):
    def load(self):
        return json.loads(REGISTER.read_text(encoding="utf-8")), json.loads(CONTRACTS.read_text(encoding="utf-8"))

    def test_current_register_shape_and_uniqueness(self):
        data, _ = self.load()
        self.assertEqual(data["schema_version"], 1)
        datasets = data["datasets"]
        self.assertGreater(len(datasets), 0)
        paths = [d["path"] for d in datasets]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertTrue(any(d["role"] == "imported_dataset" for d in datasets))
        self.assertTrue(any(d["role"] == "support_output" for d in datasets))

    def test_curated_contracts_match_registered_dataset_semantics(self):
        data, contracts_data = self.load()
        by_path = {d["path"]: d for d in data["datasets"]}
        contracts = contracts_data["contracts"]
        contract_paths = [c["path"] for c in contracts]
        self.assertEqual(len(contract_paths), len(set(contract_paths)))
        self.assertGreater(len(contracts), 0)

        for c in contracts:
            self.assertIn(c["path"], by_path, c["path"])
            d = by_path[c["path"]]
            self.assertEqual(d["role"], "imported_dataset", c["path"])
            self.assertTrue(c.get("selection_claim"), c["path"])
            self.assertTrue(c.get("selection_policy"), c["path"])
            self.assertTrue(c.get("completeness_test"), c["path"])
            if c.get("canonical") is True:
                self.assertEqual(d["assurance_state"], "provenance_reconciled", c["path"])
                self.assertTrue(d.get("canonical", True), c["path"])
            else:
                self.assertEqual(d["assurance_state"], "legacy_deprecated", c["path"])
                self.assertFalse(d.get("canonical", True), c["path"])

    def test_exhaustive_imports_are_not_silently_downgraded_to_curated(self):
        data, contracts_data = self.load()
        imported = [d for d in data["datasets"] if d["role"] == "imported_dataset"]
        contract_paths = {c["path"] for c in contracts_data["contracts"]}
        exhaustive = [d for d in imported if d["assurance_state"] in {"reconciled", "verified", "inventory_required"}]
        self.assertGreater(len(exhaustive), 0)
        for d in exhaustive:
            self.assertNotIn(d["path"], contract_paths, d["path"])
            if d["assurance_state"] == "reconciled":
                # Reconciled exhaustive imports should carry source inventory evidence,
                # either explicit expected/observed counts or a source/manifest linkage.
                has_inventory = "independent_expected_count" in d or bool(d.get("source_ids")) or bool(d.get("manifest"))
                self.assertTrue(has_inventory, d["path"])

    def test_unresolved_or_legacy_imports_explain_their_status(self):
        data, _ = self.load()
        for d in data["datasets"]:
            if d["role"] != "imported_dataset":
                continue
            if d["assurance_state"] in {"inventory_required", "stale", "legacy_deprecated"}:
                self.assertTrue(d.get("blocker"), d["path"])
            if d["assurance_state"] == "legacy_deprecated":
                self.assertFalse(d.get("canonical", True), d["path"])
                self.assertFalse(d["map_relevance"], d["path"])


if __name__ == "__main__":
    unittest.main()
