#!/usr/bin/env python3
"""Extract strategic highways/arterials for the VECA east-corridor base layer.

Source: Geoscience Australia hosted National Roads by Geoscape FeatureServer.
The source is monthly-updated national road-centreline data. To avoid turning EXP-001 into
a multi-million-feature street map, this extractor intentionally retains only operational
NATIONAL OR STATE HIGHWAY and ARTERIAL ROAD features within a broad Brisbane–Melbourne envelope.

Outputs:
- data/derived/transport/ga_major_roads_east.geojson
- data/derived/transport/ga_major_roads_east_summary.csv
- research/transport/road_foundation_validation.md
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import requests

BASE = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0"
QUERY = BASE + "/query"
ENVELOPE = {"xmin": 138.5, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
# Service values use title case. Keep SQL minimal; status is filtered again in Python.
WHERE = "hierarchy IN ('National or State Highway','Arterial Road')"
ID_BATCH = 400
FIELDS = ",".join([
    "road_id", "national_route", "state_route", "full_street_name", "feature_type",
    "hierarchy", "subtype", "ground_relationship", "lane_count", "one_way", "status",
    "surface", "trafficability", "travel_direction", "speed", "state", "source", "OBJECTID"
])
OUT = Path("data/derived/transport/ga_major_roads_east.geojson")
SUMMARY = Path("data/derived/transport/ga_major_roads_east_summary.csv")
VALIDATION = Path("research/transport/road_foundation_validation.md")


def get_ids() -> list[int]:
    params = {
        "where": WHERE,
        "geometry": json.dumps(ENVELOPE, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 7844,
        "spatialRel": "esriSpatialRelIntersects",
        "returnIdsOnly": "true",
        "f": "json",
    }
    r = requests.get(QUERY, params=params, timeout=180)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"ID query failed: {data['error']}")
    return sorted(int(x) for x in data.get("objectIds", []))


def get_features(ids: list[int]) -> list[dict]:
    params = {
        "objectIds": ",".join(map(str, ids)),
        "outFields": FIELDS,
        "returnGeometry": "true",
        "outSR": 7844,
        "f": "geojson",
    }
    r = requests.get(QUERY, params=params, timeout=180)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(f"Feature query failed: {data['error']}")
    return data.get("features", [])


def main() -> None:
    ids = get_ids()
    if not ids:
        raise RuntimeError("No strategic road IDs returned; check source values/service")
    print(f"Strategic road IDs in envelope before status filter: {len(ids):,}")

    features: list[dict] = []
    for start in range(0, len(ids), ID_BATCH):
        batch_ids = ids[start:start + ID_BATCH]
        batch = get_features(batch_ids)
        features.extend(batch)
        print(f"batch {start:,}-{start + len(batch_ids):,}: {len(batch)} features; total {len(features):,}")

    # Operational status is deliberately applied client-side because status vocabularies can
    # be finicky in ArcGIS SQL and geometry retrieval is already constrained to major roads.
    features = [
        f for f in features
        if str(f.get("properties", {}).get("status") or "").strip().lower() == "operational"
    ]
    if not features:
        raise RuntimeError("Major-road query returned records but none with operational status")

    returned_ids = [str(f.get("properties", {}).get("OBJECTID")) for f in features]
    if len(returned_ids) != len(set(returned_ids)):
        raise RuntimeError("Duplicate road OBJECTIDs returned")

    collection = {
        "type": "FeatureCollection",
        "name": "VECA east strategic road foundation",
        "source": BASE,
        "source_crs": "EPSG:7844 GDA2020",
        "filter": WHERE + "; client-side status=Operational",
        "extraction_envelope": ENVELOPE,
        "extraction_note": "Broad EXP-001 extraction convenience; not a future VECA corridor boundary.",
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")

    hierarchy, states, surface, named_routes = Counter(), Counter(), Counter(), Counter()
    for f in features:
        p = f.get("properties", {})
        hierarchy[str(p.get("hierarchy") or "UNKNOWN")] += 1
        states[str(p.get("state") or "UNKNOWN")] += 1
        surface[str(p.get("surface") or "UNKNOWN")] += 1
        nr = p.get("national_route") or p.get("state_route")
        if nr:
            named_routes[str(nr)] += 1

    with SUMMARY.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["dimension", "value", "feature_count"])
        for label, counter in [("hierarchy", hierarchy), ("state", states), ("surface", surface)]:
            for k, v in sorted(counter.items()):
                w.writerow([label, k, v])
        for k, v in named_routes.most_common(50):
            w.writerow(["route_number_top50", k, v])

    VALIDATION.write_text(
        "# Strategic road foundation extraction validation\n\n"
        "Source: Geoscience Australia-hosted National Roads by Geoscape.\n\n"
        f"Extracted **{len(features):,} operational highway/arterial line features** intersecting the broad EXP-001 envelope.\n\n"
        f"The initial spatial/hierarchy query returned {len(ids):,} object IDs before client-side operational-status filtering.\n\n"
        "## Scope decision\n\n"
        "This layer intentionally excludes sub-arterial, collector and local streets. EXP-001 needs the inherited inter-regional/major urban network first; local access can be added when evaluating specific places.\n\n"
        "## Important limitations\n\n"
        "- Geometry is not traffic volume, capacity or strategic freight importance.\n"
        "- Road importance must be enriched with NFDH harmonised traffic counts/heavy-vehicle share and state data.\n"
        "- The broad extraction envelope is not a future settlement or transport corridor.\n"
        "- Route segments rather than whole named corridors are the source unit, so feature counts are not road-length or capacity measures.\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(features):,} operational features")


if __name__ == "__main__":
    main()
