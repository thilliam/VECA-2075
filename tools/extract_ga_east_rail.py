#!/usr/bin/env python3
"""Extract the VECA east-corridor rail foundation layer from Geoscience Australia.

Source: Foundation Rail Infrastructure / Railway_Lines (ArcGIS MapServer layer 1).
The extraction uses a transparent broad bounding envelope covering SEQ through Victoria.
South Australia is explicitly excluded from EXP-001's base scope.

Outputs the source-rich GeoJSON; `summarize_ga_rail.py` produces the QA summary.
"""
from __future__ import annotations

import json
from pathlib import Path

import requests

LAYER = "https://services.ga.gov.au/gis/rest/services/Foundation_Rail_Infrastructure/MapServer/1/query"
# Western edge just inside the SA/Victoria border (~141E) avoids most SA leakage while
# retaining western Victoria. Jurisdiction is also filtered defensively after retrieval.
ENVELOPE = {"xmin": 140.9, "ymin": -39.8, "xmax": 154.2, "ymax": -25.0}
PAGE = 1500
OUT = Path("data/derived/transport/ga_rail_east.geojson")
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


def source_jurisdiction(props: dict) -> str:
    lookup = {str(k).lower(): v for k, v in props.items()}
    value = lookup.get("source_jurisdiction") or lookup.get("sourcejurisdiction")
    return str(value or "").strip().upper()


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

    before_scope_filter = len(features)
    # ACT records may inherit NSW source jurisdiction in the national aggregation, so filter
    # only the explicitly out-of-scope SA source records rather than demanding four labels.
    features = [f for f in features if source_jurisdiction(f.get("properties", {})) != "SA"]

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
        "pre_scope_filter_feature_count": before_scope_filter,
        "scope_filter": "exclude source_jurisdiction=SA",
        "extraction_note": "Envelope/filter are EXP-001 extraction controls, not a future VECA route or settlement decision.",
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")
    print(f"Wrote {OUT} with {len(features):,} in-scope features ({before_scope_filter-len(features):,} SA features excluded)")


if __name__ == "__main__":
    main()
