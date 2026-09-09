#!/usr/bin/env python3
"""Apply one declared ingestion batch to VECA assurance registers.

The batch file may declare source-register entries, dataset-register entries and
curated-dataset contracts. Updates are idempotent by source_id/path. Existing
entries are only replaced when `replace_existing` is true on the batch, preventing
accidental silent overwrites.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REGISTER = ROOT / "assurance" / "source_register.json"
DATASET_REGISTER = ROOT / "assurance" / "dataset_register.json"
CURATED_CONTRACTS = ROOT / "assurance" / "curated_dataset_contracts.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def dump(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def merge(items: list[dict], additions: list[dict], key: str, replace: bool) -> tuple[list[dict], int, int]:
    positions = {item[key]: i for i, item in enumerate(items)}
    added = replaced = 0
    for addition in additions:
        value = addition[key]
        if value in positions:
            if items[positions[value]] == addition:
                continue
            if not replace:
                raise SystemExit(f"Refusing to overwrite existing {key}={value}; set replace_existing=true explicitly")
            items[positions[value]] = addition
            replaced += 1
        else:
            positions[value] = len(items)
            items.append(addition)
            added += 1
    return items, added, replaced


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("batch", type=Path)
    args = parser.parse_args()
    batch = load(args.batch)
    replace = bool(batch.get("replace_existing", False))

    sources = load(SOURCE_REGISTER)
    datasets = load(DATASET_REGISTER)
    contracts = load(CURATED_CONTRACTS)

    sources["sources"], sa, sr = merge(sources["sources"], batch.get("sources", []), "source_id", replace)
    datasets["datasets"], da, dr = merge(datasets["datasets"], batch.get("datasets", []), "path", replace)
    contracts["contracts"], ca, cr = merge(contracts["contracts"], batch.get("curated_contracts", []), "path", replace)

    updated = batch.get("updated")
    if updated:
        sources["updated"] = updated
        datasets["updated"] = updated
        contracts["updated"] = updated

    dump(SOURCE_REGISTER, sources)
    dump(DATASET_REGISTER, datasets)
    dump(CURATED_CONTRACTS, contracts)

    print(
        "assurance batch applied: "
        f"sources +{sa}/~{sr}; datasets +{da}/~{dr}; curated_contracts +{ca}/~{cr}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
