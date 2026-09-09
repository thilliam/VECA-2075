import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "assurance" / "dataset_register.json"


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

    def test_current_assurance_states_are_honest(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        imported = [d for d in data["datasets"] if d["role"] == "imported_dataset"]
        states = {}
        for d in imported:
            states[d["assurance_state"]] = states.get(d["assurance_state"], 0) + 1
        self.assertEqual(states.get("reconciled"), 1)
        self.assertEqual(states.get("inventory_required"), 3)
        self.assertEqual(states.get("source_decomposition_required"), 21)
        self.assertEqual(states.get("verified", 0), 0)

    def test_every_unfinished_import_has_blocker(self):
        data = json.loads(REGISTER.read_text(encoding="utf-8"))
        for d in data["datasets"]:
            if d["role"] != "imported_dataset":
                continue
            if d["assurance_state"] in {"reconciled", "verified"}:
                continue
            self.assertTrue(d.get("blocker"), d["path"])


if __name__ == "__main__":
    unittest.main()
