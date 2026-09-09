import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "assurance" / "dataset_register.json"
CONTRACTS = ROOT / "assurance" / "curated_dataset_contracts.json"


class DatasetRegisterTests(unittest.TestCase):
    def test_current_register_shape_and_counts(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        self.assertEqual(data["schema_version"], 1)
        datasets = data["datasets"]
        self.assertEqual(len(datasets), 28)
        self.assertEqual(len({d["path"] for d in datasets}), 28)
        imported = [d for d in datasets if d["role"] == "imported_dataset"]
        support = [d for d in datasets if d["role"] == "support_output"]
        self.assertEqual(len(imported), 25)
        self.assertEqual(len(support), 3)

    def test_curated_migration_is_complete(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        imported = [d for d in data["datasets"] if d["role"] == "imported_dataset"]
        states = {}
        for d in imported:
            states[d["assurance_state"]] = states.get(d["assurance_state"], 0) + 1
        self.assertEqual(states.get("provenance_reconciled"), 19)
        self.assertEqual(states.get("legacy_deprecated"), 2)
        self.assertEqual(states.get("source_decomposition_required", 0), 0)
        self.assertEqual(states.get("verified", 0), 0)

        contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))["contracts"]
        self.assertEqual(len(contracts), 21)
        self.assertEqual(sum(1 for c in contracts if c.get("canonical") is True), 19)
        self.assertEqual(sum(1 for c in contracts if c.get("canonical") is False), 2)

    def test_four_exhaustive_imports_are_never_silently_downgraded(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        imported = [d for d in data["datasets"] if d["role"] == "imported_dataset"]
        exhaustive = [d for d in imported if d["assurance_state"] in {"reconciled", "verified", "inventory_required"}]
        self.assertEqual(len(exhaustive), 4)
        self.assertEqual(
            {d["path"] for d in exhaustive},
            {
                "data/derived/population_sa2_east.csv",
                "data/derived/transport/ga_major_roads_east.geojson",
                "data/derived/transport/ga_rail_east.geojson",
                "domains/energy/data/derived/transmission_projects_seed.csv",
            },
        )
        aemo = next(d for d in exhaustive if d["path"].endswith("transmission_projects_seed.csv"))
        self.assertIn(aemo["assurance_state"], {"reconciled", "verified"})

    def test_unresolved_or_legacy_imports_explain_their_status(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
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
