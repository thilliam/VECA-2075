#!/usr/bin/env python3
"""Extract operational national/state highways for VECA's east-corridor base layer.

Source: Geoscience Australia hosted National Roads by Geoscape FeatureServer.
EXP-001 deliberately starts with national/state highways only. South Australia is excluded
from the base model. The service is queried in small geographic tiles and features are
finally filtered to QLD/NSW/ACT/VIC.
"""
from __future__ import annotations

import csv
import json
import time
from collections import Counter
from pathlib import Path

import requests

BASE = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0"
QUERY = BASE + "/query"
ENVELOPE = {"xmin": 140.9, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
WHERE = "hierarchy = 'National or State Highway'"
TARGET_STATES = {"QLD", "NSW", "ACT", "VIC"}
ID_BATCH = 200
FIELDS = ",".join([
    "road_id", "national_route", "state_route", "full_street_name", "feature_type",
    "hierarchy", "subtype", "ground_relationship", "lane_count", "one_way", "status",
    "surface", "trafficability", "travel_direction", "speed", "state", "source", "OBJECTID"
])
OUT = Path("data/derived/transport/ga_major_roads_east.geojson")
SUMMARY = Path("data/derived/transport/ga_major_roads_east_summary.csv")
VALIDATION = Path("research/transport/road_foundation_validation.md")


def make_tiles() -> list[dict[str, float]]:
    tiles = []
    y = ENVELOPE["ymin"]
    while y < ENVELOPE["ymax"]:
        x = ENVELOPE["xmin"]
        while x < ENVELOPE["xmax"]:
            tiles.append({"xmin": x, "ymin": y, "xmax": min(x + 4.0, ENVELOPE["xmax"]), "ymax": min(y + 3.0, ENVELOPE["ymax"])})
            x += 4.0
        y += 3.0
    return tiles


def get_tile_ids(tile: dict[str, float]) -> list[int]:
    params = {
        "where": WHERE, "geometry": json.dumps(tile, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope", "inSR": 7844,
        "spatialRel": "esriSpatialRelIntersects", "returnIdsOnly": "true", "f": "json",
    }
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            r = requests.get(QUERY, params=params, timeout=120); r.raise_for_status(); data = r.json()
            if "error" in data: raise RuntimeError(data["error"])
            return [int(x) for x in data.get("objectIds", [])]
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
            if attempt < 3: time.sleep(5 * attempt)
    raise RuntimeError(f"Tile ID query failed for {tile}: {last_error}")


def get_features(ids: list[int]) -> list[dict]:
    form = {"objectIds": ",".join(map(str, ids)), "outFields": FIELDS, "returnGeometry": "true", "outSR": "7844", "f": "geojson"}
    last_error: Exception | None = None
    for attempt in range(1, 4):
        try:
            r = requests.post(QUERY, data=form, timeout=180); r.raise_for_status(); data = r.json()
            if "error" in data: raise RuntimeError(data["error"])
            return data.get("features", [])
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
            if attempt < 3: time.sleep(5 * attempt)
    raise RuntimeError(f"Feature batch failed after retries: {last_error}")


def main() -> None:
    ids_set: set[int] = set(); tiles = make_tiles()
    for i, tile in enumerate(tiles, start=1):
        tile_ids = get_tile_ids(tile); before = len(ids_set); ids_set.update(tile_ids)
        print(f"tile {i}/{len(tiles)}: {len(tile_ids):,} ids; +{len(ids_set)-before:,} unique")
    ids = sorted(ids_set)
    if not ids: raise RuntimeError("No highway IDs returned")
    if len(ids) > 100_000: raise RuntimeError(f"Strategic highway extraction unexpectedly large: {len(ids):,}")

    fetched: list[dict] = []
    for start in range(0, len(ids), ID_BATCH):
        batch_ids = ids[start:start + ID_BATCH]; fetched.extend(get_features(batch_ids))
        print(f"batch {start:,}: total {len(fetched):,}")

    pre_filter = len(fetched)
    features = []
    excluded_states = Counter()
    for f in fetched:
        p = f.get("properties", {})
        status = str(p.get("status") or "").strip().lower()
        state = str(p.get("state") or "").strip().upper()
        if status != "operational":
            continue
        if state not in TARGET_STATES:
            excluded_states[state or "UNKNOWN"] += 1
            continue
        features.append(f)
    if not features: raise RuntimeError("No in-scope operational highways returned")

    returned_ids = [str(f.get("properties", {}).get("OBJECTID")) for f in features]
    if len(returned_ids) != len(set(returned_ids)): raise RuntimeError("Duplicate road OBJECTIDs returned")

    collection = {
        "type": "FeatureCollection", "name": "VECA east national/state highway foundation",
        "source": BASE, "source_crs": "EPSG:7844 GDA2020", "filter": WHERE + "; operational; states=QLD/NSW/ACT/VIC",
        "extraction_envelope": ENVELOPE, "tile_count": len(tiles), "pre_scope_filter_feature_count": pre_filter,
        "excluded_state_feature_counts": dict(excluded_states),
        "extraction_note": "EXP-001 extraction controls only; not a future VECA corridor boundary.", "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True); VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")

    states, surface, named_routes = Counter(), Counter(), Counter()
    for f in features:
        p = f.get("properties", {}); states[str(p.get("state") or "UNKNOWN")] += 1; surface[str(p.get("surface") or "UNKNOWN")] += 1
        nr = p.get("national_route") or p.get("state_route")
        if nr: named_routes[str(nr)] += 1
    with SUMMARY.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp); w.writerow(["dimension", "value", "feature_count"])
        for label, counter in [("state", states), ("surface", surface)]:
            for k, v in sorted(counter.items()): w.writerow([label, k, v])
        for k, v in named_routes.most_common(75): w.writerow(["route_number_top75", k, v])

    VALIDATION.write_text(
        "# Strategic road foundation extraction validation\n\n"
        "Source: Geoscience Australia-hosted National Roads by Geoscape.\n\n"
        f"Extracted **{len(features):,} operational National or State Highway line features** for QLD, NSW, ACT and VIC within the broad EXP-001 envelope.\n\n"
        f"The tiled query returned {len(ids):,} unique object IDs; {pre_filter:,} features were fetched before operational/state filtering. Explicitly out-of-scope state counts excluded: {dict(excluded_states)}.\n\n"
        "## Scope decision\n\nThe first base layer excludes arterials and South Australia. Earlier QA showed highway+arterial selection was too granular and a wider rectangular envelope leaked SA data. Both are now controlled at extraction time.\n\n"
        "## Important limitations\n\n- Geometry is not traffic volume, capacity or freight importance.\n- Road importance must be enriched with NFDH traffic counts/heavy-vehicle share and state data.\n- Source units are road segments, so feature counts are not road-length or capacity measures.\n",
        encoding="utf-8")
    print(f"Wrote {len(features):,} in-scope operational highway features; excluded {dict(excluded_states)}")


if __name__ == "__main__": main()
