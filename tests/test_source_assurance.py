import json
import tempfile
import unittest
from pathlib import Path

import tools.validate_source_assurance as assurance


REGISTER = {
    "schema_version": 1,
    "sources": [
        {
            "source_id": "TEST-SOURCE",
            "title": "Test source",
            "publisher": "Test publisher",
            "domain": "energy",
            "geography": "NSW",
            "source_type": "authoritative_reality",
            "status": "relevant",
            "priority": "P1",
            "map_relevance": True,
            "known_gaps": [],
        }
    ],
}


def manifest(expected=27, mapped=23, excluded=0, duplicate=0, unresolved=0, dataset_only=0):
    return {
        "schema_version": 1,
        "source_id": "TEST-SOURCE",
        "map_required": True,
        "inventory": {
            "mode": "entity_count",
            "expected_count": expected,
            "count_basis": "table_rows",
            "evidence_locator": "Report p. 7, site table",
            "independent_from_extraction": True,
        },
        "disposition": {
            "mapped": mapped,
            "dataset_only": dataset_only,
            "excluded": excluded,
            "duplicate": duplicate,
            "unresolved": unresolved,
        },
        "verification": {"state": "not_started", "checks": []},
    }


class SourceAssuranceTests(unittest.TestCase):
    def setUp(self):
        errors, self.register = assurance.validate_register(REGISTER)
        self.assertEqual([], errors)
        self.path = Path("assurance/manifests/test.json")

    def test_27_expected_23_accounted_fails(self):
        errors = assurance.validate_manifest(self.path, manifest(), self.register)
        self.assertTrue(any("expected 27, accounted 23" in e for e in errors), errors)

    def test_all_27_with_explicit_dispositions_passes_reconciliation(self):
        m = manifest(mapped=23, excluded=2, duplicate=1, unresolved=1)
        errors = assurance.validate_manifest(self.path, m, self.register)
        self.assertFalse(any("reconciliation FAIL" in e for e in errors), errors)

    def test_expected_inventory_must_be_independent(self):
        m = manifest(mapped=27)
        m["inventory"]["independent_from_extraction"] = False
        errors = assurance.validate_manifest(self.path, m, self.register)
        self.assertTrue(any("independent_from_extraction" in e for e in errors), errors)

    def test_map_required_rejects_dataset_only_disposition(self):
        m = manifest(mapped=26, dataset_only=1)
        errors = assurance.validate_manifest(self.path, m, self.register)
        self.assertTrue(any("map_required source has dataset_only" in e for e in errors), errors)

    def test_verification_pass_rejects_unresolved(self):
        m = manifest(mapped=26, unresolved=1)
        m["verification"] = {
            "state": "passed",
            "checks": [
                {
                    "field": "location",
                    "method": "direct comparison",
                    "evidence_locator": "Report p. 7",
                    "result": "checked"
                }
            ]
        }
        errors = assurance.validate_manifest(self.path, m, self.register)
        self.assertTrue(any("verification cannot pass" in e for e in errors), errors)

    def test_verification_requires_evidence_backed_checks(self):
        m = manifest(mapped=27)
        m["verification"] = {"state": "passed", "checks": []}
        errors = assurance.validate_manifest(self.path, m, self.register)
        self.assertTrue(any("verification.checks" in e for e in errors), errors)


if __name__ == "__main__":
    unittest.main()
