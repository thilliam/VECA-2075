#!/usr/bin/env python3
"""Independent reconciliation for VECA's direct authoritative imports.

This intentionally does NOT call the existing extraction functions. It independently
queries authoritative services and compares source identity sets against saved outputs.

Sources:
- ABS SA2 Regional Population 2025 FeatureServer vs XLSX-derived population CSV.
- GA National Roads FeatureServer vs saved east strategic-highway GeoJSON.
- GA Foundation Rail MapServer vs saved east rail GeoJSON.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "assurance" / "manifests"
RESULT = ROOT / "assurance" / "direct_import_reconciliation.json"
TIMEOUT = 120
ENVELOPE = {"xmin": 140.9, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
TARGET_STATES = {"QLD", "NSW", "ACT", "VIC"}

ABS_QUERY = "https://geo.abs.gov.au/arcgis/rest/services/Hosted/SA2_Regional_Population_2025/FeatureServer/3/query"
ROAD_QUERY = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0/query"
RAIL_QUERY = "https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1/query"


def get_json(url: str, params: dict) -> dict:
    r = requests.get(url, params=params, timeout=TIMEOUT)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ArcGIS error: {data['error']}")
    return data


def batches(values: list[int], size: int = 500) -> Iterable[list[int]]:
    for i in range(0, len(values), size):
        yield values[i:i + size]


def geojson_ids(path: Path) -> set[int]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    ids: list[int] = []
    for feature in data.get("features", []):
        p = feature.get("properties", {})
        value = p.get("OBJECTID") if p.get("OBJECTID") is not None else p.get("objectid")
        if value is None:
            value = p.get("FID") if p.get("FID") is not None else p.get("fid")
        if value is None:
            raise RuntimeError(f"Missing object ID in {path}")
        ids.append(int(value))
    if len(ids) != len(set(ids)):
        raise RuntimeError(f"Duplicate IDs in {path}")
    return set(ids)


def abs_reconcile() -> dict:
    # Independent source inventory comes from ABS's hosted feature layer, while the
    # existing VECA CSV was built from the separate published XLSX cubes.
    data = get_json(ABS_QUERY, {
        "where": "state_code_2021 IN ('1','2','3','8')",
        "outFields": "sa2_code_2021,state_code_2021,erp_2025",
        "returnGeometry": "false",
        "resultRecordCount": 5000,
        "f": "json",
    })
    features = data.get("features", [])
    source = {}
    for f in features:
        a = f.get("attributes", {})
        code = str(a.get("sa2_code_2021") or "").strip()
        if code:
            source[code] = a.get("erp_2025")
    if not source:
        raise RuntimeError("ABS independent service inventory empty")

    derived = {}
    with (ROOT / "data/derived/population_sa2_east.csv").open(newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            derived[row["sa2_code"].strip()] = int(float(row["erp_2025"])) if row["erp_2025"] else None

    missing = sorted(set(source) - set(derived))
    extra = sorted(set(derived) - set(source))
    value_mismatch = sorted(code for code in set(source) & set(derived)
                            if source[code] is not None and derived[code] is not None and int(source[code]) != int(derived[code]))
    passed = not missing and not extra and not value_mismatch
    return {
        "source_id": "POP-ABS-SA2-ERP-2001-2025",
        "source_inventory_count": len(source),
        "derived_count": len(derived),
        "missing_codes": missing,
        "extra_codes": extra,
        "erp_2025_value_mismatches": value_mismatch,
        "passed": passed,
        "inventory_evidence": "ABS SA2 Regional Population 2025 FeatureServer layer 3; state_code_2021 in 1,2,3,8",
    }


def source_ids_with_attrs(url: str, where: str, fields: str) -> list[dict]:
    ids_data = get_json(url, {
        "where": where,
        "geometry": json.dumps(ENVELOPE, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 7844,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
        "f": "json",
    })
    ids = [int(x) for x in ids_data.get("objectIds", [])]
    attrs: list[dict] = []
    for group in batches(ids):
        data = get_json(url, {
            "objectIds": ",".join(map(str, group)),
            "outFields": fields,
            "returnGeometry": "false",
            "f": "json",
        })
        attrs.extend(f.get("attributes", {}) for f in data.get("features", []))
    return attrs


def road_reconcile() -> dict:
    attrs = source_ids_with_attrs(
        ROAD_QUERY,
        "hierarchy = 'National or State Highway'",
        "OBJECTID,status,state,hierarchy",
    )
    expected = {
        int(a["OBJECTID"]) for a in attrs
        if str(a.get("status") or "").strip().lower() == "operational"
        and str(a.get("state") or "").strip().upper() in TARGET_STATES
    }
    derived = geojson_ids(ROOT / "data/derived/transport/ga_major_roads_east.geojson")
    missing, extra = sorted(expected - derived), sorted(derived - expected)
    return {
        "source_id": "TRANSPORT-GA-EAST-MAJOR-ROADS",
        "source_inventory_count": len(expected),
        "derived_count": len(derived),
        "missing_objectids": missing,
        "extra_objectids": extra,
        "passed": not missing and not extra,
        "inventory_evidence": "GA National Roads service; one whole-envelope returnIdsOnly query, then independent operational/state filtering",
    }


def rail_reconcile() -> dict:
    attrs = source_ids_with_attrs(RAIL_QUERY, "1=1", "OBJECTID,SOURCE_JURISDICTION")
    expected = {
        int(a["OBJECTID"]) for a in attrs
        if str(a.get("SOURCE_JURISDICTION") or "").strip().upper() != "SA"
    }
    derived = geojson_ids(ROOT / "data/derived/transport/ga_rail_east.geojson")
    missing, extra = sorted(expected - derived), sorted(derived - expected)
    return {
        "source_id": "TRANSPORT-GA-EAST-RAIL",
        "source_inventory_count": len(expected),
        "derived_count": len(derived),
        "missing_objectids": missing,
        "extra_objectids": extra,
        "passed": not missing and not extra,
        "inventory_evidence": "GA Foundation Rail Railway_Lines service; one whole-envelope returnIdsOnly query, independent SA-jurisdiction filtering",
    }


def write_manifest(result: dict, dataset: str, map_required: bool, field_check: str) -> None:
    count = result["source_inventory_count"]
    manifest = {
        "schema_version": 1,
        "source_id": result["source_id"],
        "map_required": map_required,
        "inventory": {
            "mode": "entity_count",
            "expected_count": count,
            "count_basis": "official_index" if result["source_id"].startswith("POP-") else "gis_feature_count",
            "evidence_locator": result["inventory_evidence"],
            "independent_from_extraction": True,
            "notes": "Generated by independent reconciliation script; does not call the production extractor.",
        },
        "disposition": {
            "mapped": count if map_required and result["passed"] else 0,
            "dataset_only": count if (not map_required and result["passed"]) else 0,
            "excluded": 0,
            "duplicate": 0,
            "unresolved": 0 if result["passed"] else len(result.get("missing_codes", result.get("missing_objectids", []))) + len(result.get("extra_codes", result.get("extra_objectids", []))),
        },
        "verification": {
            "state": "passed" if result["passed"] else "failed",
            "checks": [{
                "field": field_check,
                "method": "Compare the complete independent authoritative identity set with the saved derived identity set; also compare 2025 ERP values for ABS.",
                "evidence_locator": result["inventory_evidence"],
                "result": f"source={result['source_inventory_count']}; derived={result['derived_count']}; passed={result['passed']}",
            }],
        },
        "dataset_paths": [dataset],
        "map_layers": [],
        "notes": "Machine-generated direct-import assurance manifest.",
    }
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    (MANIFESTS / f"{result['source_id']}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    results = [abs_reconcile(), road_reconcile(), rail_reconcile()]
    write_manifest(results[0], "data/derived/population_sa2_east.csv", False, "SA2 identity + erp_2025")
    write_manifest(results[1], "data/derived/transport/ga_major_roads_east.geojson", True, "road OBJECTID identity")
    write_manifest(results[2], "data/derived/transport/ga_rail_east.geojson", True, "rail OBJECTID identity")
    RESULT.write_text(json.dumps({"schema_version": 1, "results": results}, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(r["source_id"], r["source_inventory_count"], r["derived_count"], "PASS" if r["passed"] else "FAIL")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
