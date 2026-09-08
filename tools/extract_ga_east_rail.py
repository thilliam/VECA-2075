#!/usr/bin/env python3
"""Extract the VECA east-corridor rail foundation layer from Geoscience Australia.

Source: Foundation Rail Infrastructure / Railway_Lines (ArcGIS MapServer layer 1).
The extraction uses a transparent broad bounding envelope covering the Brisbane–Melbourne
study system. It does not imply a future VECA corridor or settlement boundary.

Outputs:
- data/derived/transport/ga_rail_east.geojson
- data/derived/transport/ga_rail_east_summary.csv
- research/transport/rail_foundation_validation.md
"""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

import requests

LAYER = "https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1/query"
# Broad EXP-001 extraction envelope, GDA2020 / EPSG:7844 decimal degrees.
# Includes SEQ, eastern/inland NSW, ACT and Victoria. This is an extraction convenience,
# not a settlement or future-network boundary.
ENVELOPE = {"xmin": 138.5, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
PAGE = 1500
OUT = Path("data/derived/transport/ga_rail_east.geojson")
SUMMARY = Path("data/derived/transport/ga_rail_east_summary.csv")
VALIDATION = Path("research/transport/rail_foundation_validation.md")
SOURCE_URL = "https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1"


def request_page(offset: int) -> dict:
    params = {
        "where": "1=1",
        "geometry": json.dumps(ENVELOPE, separators=(",", ":")),
        "geometryType": "esriGeometryEnvelope",
        "inSR": 7844,
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "*",
        "returnGeometry": "true",
        "outSR": 7844,
        "resultOffset": offset,
        "resultRecordCount": PAGE,
        "f": "geojson",
    }
    r = requests.get(LAYER, params=params, timeout=120)
    r.raise_for_status()
    data = r.json()
    if "error" in data:
        raise RuntimeError(data["error"])
    return data


def pick(props: dict, candidates: list[str]) -> str:
    lookup = {str(k).lower(): v for k, v in props.items()}
    for name in candidates:
        if name.lower() in lookup and lookup[name.lower()] not in (None, ""):
            return str(lookup[name.lower()])
    return "UNKNOWN"


def main() -> None:
    features = []
    offset = 0
    while True:
        data = request_page(offset)
        batch = data.get("features", [])
        features.extend(batch)
        if len(batch) < PAGE:
            break
        offset += len(batch)
        if offset > 100_000:
            raise RuntimeError("Pagination safety limit exceeded")

    if not features:
        raise RuntimeError("No rail features returned")

    # ArcGIS can return the same feature only once for an envelope query; retain service IDs
    # and explicitly fail if a stable id is duplicated when one is present.
    ids = []
    for f in features:
        p = f.get("properties", {})
        oid = p.get("OBJECTID") or p.get("objectid") or p.get("FID") or p.get("fid")
        if oid is not None:
            ids.append(str(oid))
    if ids and len(ids) != len(set(ids)):
        raise RuntimeError("Duplicate service object IDs returned")

    collection = {
        "type": "FeatureCollection",
        "name": "VECA east-corridor Geoscience Australia Foundation Rail Infrastructure",
        "source": SOURCE_URL,
        "source_crs": "EPSG:7844 GDA2020",
        "extraction_envelope": ENVELOPE,
        "extraction_note": "Envelope is an EXP-001 data-extraction convenience, not a future VECA route or study-area decision.",
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")

    status = Counter()
    feature_type = Counter()
    for f in features:
        p = f.get("properties", {})
        status[pick(p, ["OPER_STATUS", "OPERATIONAL_STATUS", "STATUS", "operationalstatus"])] += 1
        feature_type[pick(p, ["FEATURETYPE", "FEATURE_TYPE", "TYPE", "CLASS"])] += 1

    with SUMMARY.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["dimension", "value", "feature_count"])
        for k, v in sorted(status.items()):
            w.writerow(["operational_status", k, v])
        for k, v in sorted(feature_type.items()):
            w.writerow(["feature_type", k, v])

    VALIDATION.write_text(
        "# Rail foundation extraction validation\n\n"
        f"Source: Geoscience Australia Foundation Rail Infrastructure, Railway_Lines layer.\n\n"
        f"Extracted **{len(features):,} line features** intersecting the broad EXP-001 envelope "
        f"{ENVELOPE}.\n\n"
        "The source is a national aggregation of publicly available rail data and includes railway, "
        "siding and tram/light-rail line features grouped by operational status.\n\n"
        "## Important limitations\n\n"
        "- This is foundation geometry, not a statement of service frequency, capacity, gauge, ownership or freight importance.\n"
        "- The extraction envelope is deliberately broad and is not a VECA preferred corridor.\n"
        "- Usage/intensity must be layered separately from BITRE/NFDH/state/operator evidence.\n"
        "- Historical/disused/proposed records must remain distinguishable from operational lines.\n\n"
        "See `data/derived/transport/ga_rail_east_summary.csv` for service-attribute counts.\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(features):,} features")


if __name__ == "__main__":
    main()
