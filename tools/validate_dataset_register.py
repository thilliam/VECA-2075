#!/usr/bin/env python3
"""Validate that every current VECA derived dataset is registered for assurance.

This complements source-level manifests. It prevents a newly-created CSV/GeoJSON from
quietly feeding the map without appearing in the assurance queue.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "assurance" / "dataset_register.json"
VALID_STATES = {"reconciled", "verified", "inventory_required", "source_decomposition_required", "support_output", "stale"}
VALID_ROLES = {"imported_dataset", "support_output"}


def discover() -> set[str]:
    out: set[str] = set()
    roots = [ROOT / "data" / "derived"]
    domains = ROOT / "domains"
    if domains.exists():
        for p in domains.iterdir():
            candidate = p / "data" / "derived"
            if candidate.exists():
                roots.append(candidate)
    for base in roots:
        if not base.exists():
            continue
        for p in base.rglob("*"):
            if p.is_file() and p.name != ".gitkeep":
                out.add(p.relative_to(ROOT).as_posix())
    return out


def main() -> int:
    errors: list[str] = []
    data = json.loads(REGISTER.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("datasets"), list):
        print("dataset register schema invalid", file=sys.stderr)
        return 1

    registered: dict[str, dict] = {}
    for i, item in enumerate(data["datasets"]):
        where = f"dataset_register datasets[{i}]"
        if not isinstance(item, dict):
            errors.append(f"{where}: must be object")
            continue
        path = item.get("path")
        if not isinstance(path, str) or not path:
            errors.append(f"{where}: path required")
            continue
        if path in registered:
            errors.append(f"{where}: duplicate path {path}")
        registered[path] = item
        if item.get("role") not in VALID_ROLES:
            errors.append(f"{where}: invalid role {item.get('role')!r}")
        if item.get("assurance_state") not in VALID_STATES:
            errors.append(f"{where}: invalid assurance_state {item.get('assurance_state')!r}")
        if not isinstance(item.get("domain"), str) or not item.get("domain"):
            errors.append(f"{where}: domain required")
        if not isinstance(item.get("map_relevance"), bool):
            errors.append(f"{where}: map_relevance must be boolean")
        if item.get("role") == "imported_dataset" and item.get("assurance_state") not in {"reconciled", "verified"}:
            blocker = item.get("blocker")
            if not isinstance(blocker, str) or not blocker.strip():
                errors.append(f"{where}: incomplete imported dataset requires blocker")

    actual = discover()
    reg_paths = set(registered)
    for path in sorted(actual - reg_paths):
        errors.append(f"unregistered derived file: {path}")
    for path in sorted(reg_paths - actual):
        errors.append(f"registered dataset missing from repository: {path}")

    imported = [v for v in registered.values() if v.get("role") == "imported_dataset"]
    states: dict[str, int] = {}
    for item in imported:
        s = item["assurance_state"]
        states[s] = states.get(s, 0) + 1

    if errors:
        print(f"VECA dataset assurance: FAIL ({len(errors)} issue(s))", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1

    print(f"VECA dataset assurance: PASS ({len(registered)} derived files; {len(imported)} imported datasets)")
    print("Imported assurance states: " + ", ".join(f"{k}={v}" for k, v in sorted(states.items())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
