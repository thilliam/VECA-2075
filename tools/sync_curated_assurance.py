#!/usr/bin/env python3
"""Apply curated-dataset assurance contracts to the dataset register.

A curated set can become provenance_reconciled when:
- it has an explicit scope/selection contract;
- every included row has structural provenance that resolves to a registered source;
- it does not claim to be an exhaustive universe.
Legacy snapshots become legacy_deprecated and are explicitly non-canonical.
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ROOT / "assurance" / "dataset_register.json"
CONTRACTS = ROOT / "assurance" / "curated_dataset_contracts.json"
AUDIT = ROOT / "assurance" / "current_dataset_audit.json"


def main() -> int:
    registry = json.loads(DATASETS.read_text(encoding="utf-8"))
    contracts_data = json.loads(CONTRACTS.read_text(encoding="utf-8"))
    audit_data = json.loads(AUDIT.read_text(encoding="utf-8"))
    contracts = {x["path"]: x for x in contracts_data["contracts"]}
    audits = {x["path"]: x for x in audit_data["datasets"]}
    errors = []
    changed = []

    curated_paths = {x["path"] for x in audit_data["datasets"] if x.get("dataset_kind") == "curated_synthesis"}
    if curated_paths != set(contracts):
        for p in sorted(curated_paths - set(contracts)):
            errors.append(f"missing curated contract: {p}")
        for p in sorted(set(contracts) - curated_paths):
            errors.append(f"contract is not a current curated dataset: {p}")

    for item in registry["datasets"]:
        path = item["path"]
        if path not in contracts:
            continue
        contract = contracts[path]
        audit = audits.get(path, {})
        if contract.get("canonical") is False:
            target = "legacy_deprecated"
            item["blocker"] = "Legacy snapshot retained for history only; canonical domains/government-intent datasets supersede it. Do not use as a new map/data input."
        else:
            if not audit.get("structural_provenance_pass"):
                errors.append(f"{path}: cannot reconcile; structural provenance audit failed")
                continue
            target = "provenance_reconciled"
            item["blocker"] = None
        if item.get("assurance_state") != target:
            changed.append(f"{path}: {item.get('assurance_state')} -> {target}")
            item["assurance_state"] = target
        item["selection_claim"] = contract["selection_claim"]
        item["selection_policy"] = contract["selection_policy"]
        item["completeness_test"] = contract["completeness_test"]
        item["canonical"] = bool(contract.get("canonical", True))

    if errors:
        print("Curated assurance sync: FAIL")
        for e in errors:
            print("-", e)
        return 1

    registry["updated"] = "2026-09-09"
    DATASETS.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    print(f"Curated assurance sync: PASS; {len(changed)} state changes")
    for line in changed:
        print("-", line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
