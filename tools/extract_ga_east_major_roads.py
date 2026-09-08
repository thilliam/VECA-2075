#!/usr/bin/env python3
"""Extract strategic highways/arterials for the VECA east-corridor base layer.

Source: Geoscience Australia hosted National Roads by Geoscape FeatureServer.
The source is monthly-updated national road-centreline data. To avoid turning EXP-001 into
a multi-million-feature street map, this extractor intentionally retains only hierarchy
classes NATIONAL OR STATE HIGHWAY and ARTERIAL ROAD within a broad Brisbane–Melbourne
envelope. Sub-arterials/local roads can be added later for local access analysis.

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

LAYER = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0/query"
ENVELOPE = {"xmin": 138.5, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
WHERE = "hierarchy IN ('NATIONAL OR STATE HIGHWAY','ARTERIAL ROAD') AND status = 'OPERATIONAL'"
PAGE = 1800
FIELDS = ",".join([
    "road_id", "national_route", "state_route", "full_street_name", "feature_type",
    "hierarchy", "subtype", "ground_relationship", "lane_count", "one_way", "status",
    "surface", "trafficability", "travel_direction", "speed", "state", "source", "OBJECTID"
])
OUT = Path("data/derived/transport/ga_major_roads_east.geojson")
SUMMARY = Path("data/derived/transport/ga_major_roads_east_summary.csv")
VALIDATION = Path("research/transport/road_foundation_validation.md")
SOURCE = "https://services-ap1.arcgis.com/ypkPEy1AmwPKGNNv/ArcGIS/rest/services/National_Roads/FeatureServer/0"


def page(offset: int) -> dict:
    params = {
        "where": WHERE,
        "geometry": json.dumps(ENVELOPE, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 7844,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": FIELDS,
        "returnGeometry": "true",
        "outSR": 7844,
        "resultOffset": offset,
        "resultRecordCount": PAGE,
        "orderByFields": "OBJECTID",
        "f": "geojson",
    }
    r = requests.get(LAYER, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def main() -> None:
    features = []
    offset = 0
    while True:
        batch = page(offset).get("features", [])
        features.extend(batch)
        print(f"offset={offset} batch={len(batch)} total={len(features)}")
        if len(batch) < PAGE:
            break
        offset += len(batch)
        if offset > 250_000:
            raise RuntimeError("Road extraction exceeded 250k-feature safety limit; tighten scope before committing")

    if not features:
        raise RuntimeError("No road features returned; check hierarchy/status values or source service")

    ids = [str(f.get("properties", {}).get("OBJECTID")) for f in features]
    if len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate road OBJECTIDs returned")

    collection = {
        "type": "FeatureCollection",
        "name": "VECA east strategic road foundation",
        "source": SOURCE,
        "source_crs": "EPSG:7844 GDA2020",
        "filter": WHERE,
        "extraction_envelope": ENVELOPE,
        "extraction_note": "Broad EXP-001 extraction convenience; not a future VECA corridor boundary.",
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")

    hierarchy = Counter()
    states = Counter()
    surface = Counter()
    named_routes = Counter()
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
        "## Scope decision\n\n"
        "This layer intentionally excludes sub-arterial, collector and local streets. EXP-001 needs the inherited inter-regional/major urban network first; local access can be added when evaluating specific places.\n\n"
        "## Important limitations\n\n"
        "- Geometry is not traffic volume, capacity or strategic freight importance.\n"
        "- Road importance must be enriched with NFDH harmonised traffic counts/heavy-vehicle share and state data.\n"
        "- The broad extraction envelope is not a future settlement or transport corridor.\n"
        "- Route segments rather than whole named corridors are the source unit, so feature counts are not road-length or capacity measures.\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(features):,} features")


if __name__ == "__main__":
    main()
