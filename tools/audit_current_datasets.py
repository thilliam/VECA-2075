#!/usr/bin/env python3
"""Audit every current VECA derived dataset for structural assurance.

This does not replace independent source reconciliation. It answers a different question:
for every file currently able to feed analysis/map work, what kind of dataset is it, how
many rows/features does it contain, and can every curated row be traced to a source?

Outputs:
  assurance/current_dataset_audit.json
  assurance/current_dataset_audit.md
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
REGISTER = ROOT / "assurance" / "dataset_register.json"
OUT_JSON = ROOT / "assurance" / "current_dataset_audit.json"
OUT_MD = ROOT / "assurance" / "current_dataset_audit.md"


def load_source_ids() -> set[str]:
    ids: set[str] = set()
    for path in ROOT.rglob("source_register.csv"):
        try:
            with path.open(newline="", encoding="utf-8-sig") as f:
                for row in csv.DictReader(f):
                    value = (row.get("source_id") or "").strip()
                    if value:
                        ids.add(value)
        except (OSError, UnicodeDecodeError, csv.Error):
            pass
    return ids


def valid_url(value: str) -> bool:
    if not value:
        return False
    try:
        p = urlparse(value)
        return p.scheme in {"http", "https"} and bool(p.netloc)
    except ValueError:
        return False


def csv_audit(path: Path, source_ids: set[str]) -> dict:
    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = reader.fieldnames or []

    provenance_fields = [x for x in ("source_id", "source_url", "url") if x in fields]
    missing_provenance: list[int] = []
    unresolved_source_ids: set[str] = set()
    invalid_urls: set[str] = set()

    for i, row in enumerate(rows, start=2):
        values = [(row.get(field) or "").strip() for field in provenance_fields]
        if provenance_fields and not any(values):
            missing_provenance.append(i)
        sid = (row.get("source_id") or "").strip()
        if sid and sid not in source_ids:
            unresolved_source_ids.add(sid)
        for field in ("source_url", "url"):
            value = (row.get(field) or "").strip()
            if value and not valid_url(value):
                invalid_urls.add(value)

    return {
        "record_count": len(rows),
        "columns": fields,
        "provenance_fields": provenance_fields,
        "rows_missing_provenance": missing_provenance,
        "unresolved_source_ids": sorted(unresolved_source_ids),
        "invalid_source_urls": sorted(invalid_urls),
        "structural_provenance_pass": bool(provenance_fields) and not missing_provenance and not unresolved_source_ids and not invalid_urls,
    }


def geojson_audit(path: Path) -> dict:
    # Current GA files are large but safely below typical Actions memory limits.
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    features = data.get("features") if isinstance(data, dict) else None
    if not isinstance(features, list):
        raise ValueError("GeoJSON must contain a FeatureCollection features array")
    ids = []
    for feature in features:
        props = feature.get("properties", {}) if isinstance(feature, dict) else {}
        oid = props.get("OBJECTID") or props.get("objectid") or props.get("FID") or props.get("fid")
        if oid is not None:
            ids.append(str(oid))
    return {
        "record_count": len(features),
        "object_id_count": len(ids),
        "unique_object_id_count": len(set(ids)),
        "duplicate_object_ids": len(ids) - len(set(ids)),
        "structural_provenance_pass": bool(data.get("source")) and (not ids or len(ids) == len(set(ids))),
    }


def main() -> int:
    reg = json.loads(REGISTER.read_text(encoding="utf-8"))
    source_ids = load_source_ids()
    results = []
    errors = []

    for item in reg["datasets"]:
        path = ROOT / item["path"]
        role = item["role"]
        if role == "support_output":
            kind = "support_output"
        elif item["assurance_state"] in {"inventory_required", "reconciled", "verified"}:
            kind = "exhaustive_import"
        else:
            kind = "curated_synthesis"

        audit = {}
        try:
            if path.suffix.lower() == ".csv":
                audit = csv_audit(path, source_ids)
            elif path.suffix.lower() in {".geojson", ".json"}:
                audit = geojson_audit(path)
            else:
                audit = {"record_count": None, "structural_provenance_pass": False, "note": "unsupported audit format"}
        except Exception as exc:  # audit should report, not silently skip
            audit = {"record_count": None, "structural_provenance_pass": False, "error": str(exc)}
            errors.append(f"{item['path']}: {exc}")

        results.append({
            "path": item["path"],
            "domain": item["domain"],
            "role": role,
            "dataset_kind": kind,
            "assurance_state": item["assurance_state"],
            "map_relevance": item["map_relevance"],
            "blocker": item.get("blocker"),
            **audit,
        })

    counts = Counter(r["dataset_kind"] for r in results)
    provenance_fail = [r for r in results if r["dataset_kind"] == "curated_synthesis" and not r.get("structural_provenance_pass")]
    report = {
        "schema_version": 1,
        "dataset_count": len(results),
        "kind_counts": dict(counts),
        "curated_structural_provenance_failures": len(provenance_fail),
        "datasets": results,
    }
    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# Current dataset assurance audit",
        "",
        "> Generated by `tools/audit_current_datasets.py`. Structural provenance is not the same as source completeness or factual verification.",
        "",
        f"- Derived files: **{len(results)}**",
        f"- Exhaustive imports: **{counts['exhaustive_import']}**",
        f"- Curated syntheses: **{counts['curated_synthesis']}**",
        f"- Support outputs: **{counts['support_output']}**",
        f"- Curated sets failing structural provenance: **{len(provenance_fail)}**",
        "",
        "| Dataset | Kind | Records | Structural provenance | Current assurance |",
        "|---|---|---:|---|---|",
    ]
    for r in results:
        name = r["path"]
        count = "" if r.get("record_count") is None else f"{r['record_count']:,}"
        structural = "PASS" if r.get("structural_provenance_pass") else "FAIL/N/A"
        lines.append(f"| `{name}` | {r['dataset_kind']} | {count} | {structural} | {r['assurance_state']} |")
    lines += ["", "## Structural provenance failures", ""]
    if not provenance_fail:
        lines.append("_None._")
    else:
        for r in provenance_fail:
            details = []
            if r.get("rows_missing_provenance"):
                details.append(f"missing provenance at CSV rows {r['rows_missing_provenance']}")
            if r.get("unresolved_source_ids"):
                details.append(f"unknown source IDs {r['unresolved_source_ids']}")
            if r.get("invalid_source_urls"):
                details.append("invalid source URLs")
            if not r.get("provenance_fields"):
                details.append("no recognised provenance column")
            lines.append(f"- `{r['path']}` — {'; '.join(details) or 'structural audit failed'}")
    lines += ["", "## Interpretation", "",
              "- `exhaustive_import` must ultimately prove an independent expected inventory and exact reconciliation.",
              "- `curated_synthesis` may intentionally select evidence. It must prove every included row is sourced and declare its selection scope; it must not claim to be an exhaustive universe unless separately inventoried.",
              "- `support_output` inherits assurance from its upstream dataset.", ""]
    OUT_MD.write_text("\n".join(lines), encoding="utf-8")

    if errors:
        print("Audit completed with read/parse errors:")
        for e in errors:
            print("-", e)
        return 1
    print(f"Audited {len(results)} derived files; curated structural provenance failures={len(provenance_fail)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
