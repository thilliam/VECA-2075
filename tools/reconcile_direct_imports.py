#!/usr/bin/env python3
"""Independent reconciliation for VECA's direct authoritative imports.

This intentionally does NOT call the existing extraction functions. It independently
queries authoritative services and compares source identity sets against saved outputs.
"""
from __future__ import annotations

import csv
import json
import time
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[1]
MANIFESTS = ROOT / "assurance" / "manifests"
RESULT = ROOT / "assurance" / "direct_import_reconciliation.json"
DATASET_REGISTER = ROOT / "assurance" / "dataset_register.json"
TIMEOUT = 90
ENVELOPE = {"xmin": 140.9, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}

ABS_QUERY = "https://geo.abs.gov.au/arcgis/rest/services/Hosted/SA2_Regional_Population_2025/FeatureServer/3/query"
ROAD_QUERY = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0/query"
RAIL_QUERY = "https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1/query"


def get_json(url: str, params: dict) -> dict:
    last: Exception | None = None
    for attempt in range(1, 4):
        try:
            r = requests.get(url, params=params, timeout=TIMEOUT)
            r.raise_for_status()
            data = r.json()
            if "error" in data:
                raise RuntimeError(f"ArcGIS error: {data['error']}")
            return data
        except (requests.RequestException, RuntimeError, ValueError) as exc:
            last = exc
            if attempt < 3:
                time.sleep(2 * attempt)
    raise RuntimeError(f"Source query failed after retries: {last}")


def assurance_tiles() -> list[dict[str, float]]:
    """Independent 3x4-degree tiling; deliberately not the production extractor tiling."""
    tiles = []
    y = ENVELOPE["ymin"]
    while y < ENVELOPE["ymax"]:
        x = ENVELOPE["xmin"]
        while x < ENVELOPE["xmax"]:
            tiles.append({"xmin": x, "ymin": y, "xmax": min(x + 3.0, ENVELOPE["xmax"]), "ymax": min(y + 4.0, ENVELOPE["ymax"])})
            x += 3.0
        y += 4.0
    return tiles


def tiled_ids(url: str, where: str) -> set[int]:
    ids: set[int] = set()
    for tile in assurance_tiles():
        data = get_json(url, {
            "where": where,
            "geometry": json.dumps(tile, separators=(",", ":")),
            "geometryType": "esriGeometryEnvelope",
            "inSR": 7844,
            "spatialRel": "esriSpatialRelIntersects",
            "returnIdsOnly": "true",
            "f": "json",
        })
        ids.update(int(x) for x in data.get("objectIds", []))
    return ids


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
    data = get_json(ABS_QUERY, {
        "where": "state_code_2021 IN ('1','2','3','8')",
        "outFields": "sa2_code_2021,state_code_2021,erp_2025",
        "returnGeometry": "false",
        "resultRecordCount": 5000,
        "f": "json",
    })
    source = {}
    for f in data.get("features", []):
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
    mismatch = sorted(code for code in set(source) & set(derived)
                      if source[code] is not None and derived[code] is not None and int(source[code]) != int(derived[code]))
    return {
        "source_id": "POP-ABS-SA2-ERP-2001-2025",
        "dataset": "data/derived/population_sa2_east.csv",
        "source_inventory_count": len(source), "derived_count": len(derived),
        "missing_codes": missing, "extra_codes": extra, "erp_2025_value_mismatches": mismatch,
        "passed": not missing and not extra and not mismatch,
        "inventory_evidence": "ABS SA2 Regional Population 2025 FeatureServer layer 3; state_code_2021 in 1,2,3,8",
    }


def road_reconcile() -> dict:
    expected = tiled_ids(
        ROAD_QUERY,
        "hierarchy = 'National or State Highway' AND status = 'Operational' AND state IN ('QLD','NSW','ACT','VIC')"
    )
    derived = geojson_ids(ROOT / "data/derived/transport/ga_major_roads_east.geojson")
    missing, extra = sorted(expected - derived), sorted(derived - expected)
    return {
        "source_id": "TRANSPORT-GA-EAST-MAJOR-ROADS",
        "dataset": "data/derived/transport/ga_major_roads_east.geojson",
        "source_inventory_count": len(expected), "derived_count": len(derived),
        "missing_objectids": missing, "extra_objectids": extra, "passed": not missing and not extra,
        "inventory_evidence": "GA National Roads service; independent 3x4-degree returnIdsOnly inventory with operational/highway/target-state source filtering",
    }


def rail_reconcile() -> dict:
    expected = tiled_ids(RAIL_QUERY, "SOURCE_JURISDICTION <> 'SA' OR SOURCE_JURISDICTION IS NULL")
    derived = geojson_ids(ROOT / "data/derived/transport/ga_rail_east.geojson")
    missing, extra = sorted(expected - derived), sorted(derived - expected)
    return {
        "source_id": "TRANSPORT-GA-EAST-RAIL",
        "dataset": "data/derived/transport/ga_rail_east.geojson",
        "source_inventory_count": len(expected), "derived_count": len(derived),
        "missing_objectids": missing, "extra_objectids": extra, "passed": not missing and not extra,
        "inventory_evidence": "GA Foundation Rail Railway_Lines service; independent 3x4-degree returnIdsOnly inventory excluding explicit SA source-jurisdiction rows",
    }


def write_manifest(result: dict, map_required: bool, field_check: str) -> None:
    count = result["source_inventory_count"]
    unresolved = len(result.get("missing_codes", result.get("missing_objectids", []))) + len(result.get("extra_codes", result.get("extra_objectids", [])))
    manifest = {
        "schema_version": 1,
        "source_id": result["source_id"],
        "map_required": map_required,
        "inventory": {
            "mode": "entity_count", "expected_count": count,
            "count_basis": "official_index" if result["source_id"].startswith("POP-") else "gis_feature_count",
            "evidence_locator": result["inventory_evidence"], "independent_from_extraction": True,
            "notes": "Generated by independent reconciliation script; does not call the production extractor."
        },
        "disposition": {
            "mapped": count if map_required and result["passed"] else 0,
            "dataset_only": count if (not map_required and result["passed"]) else 0,
            "excluded": 0, "duplicate": 0, "unresolved": 0 if result["passed"] else unresolved,
        },
        "verification": {
            "state": "passed" if result["passed"] else "failed",
            "checks": [{"field": field_check,
                        "method": "Compare complete independent authoritative identity set with saved derived identity set; ABS also compares every 2025 ERP value.",
                        "evidence_locator": result["inventory_evidence"],
                        "result": f"source={result['source_inventory_count']}; derived={result['derived_count']}; passed={result['passed']}"}],
        },
        "dataset_paths": [result["dataset"]], "map_layers": [],
        "notes": "Machine-generated direct-import assurance manifest."
    }
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    (MANIFESTS / f"{result['source_id']}.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def update_dataset_register(results: list[dict]) -> None:
    reg = json.loads(DATASET_REGISTER.read_text(encoding="utf-8"))
    by_path = {x["path"]: x for x in reg["datasets"]}
    for result in results:
        item = by_path[result["dataset"]]
        if result["passed"]:
            item["assurance_state"] = "reconciled"
            item["blocker"] = "Independent identity inventory reconciled with zero missing/extra entities; broader attribute/geometry field verification can continue separately."
            item["independent_expected_count"] = result["source_inventory_count"]
        else:
            item["assurance_state"] = "inventory_required"
            item["blocker"] = "Independent identity reconciliation failed; inspect assurance/direct_import_reconciliation.json for exact missing/extra identities."
    DATASET_REGISTER.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    results = [abs_reconcile(), road_reconcile(), rail_reconcile()]
    write_manifest(results[0], False, "SA2 identity + erp_2025")
    write_manifest(results[1], True, "road OBJECTID identity")
    write_manifest(results[2], True, "rail OBJECTID identity")
    update_dataset_register(results)
    RESULT.write_text(json.dumps({"schema_version": 1, "results": results}, indent=2) + "\n", encoding="utf-8")
    for r in results:
        print(r["source_id"], r["source_inventory_count"], r["derived_count"], "PASS" if r["passed"] else "FAIL")
    return 0 if all(r["passed"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
