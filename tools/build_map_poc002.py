#!/usr/bin/env python3
"""Build browser-ready POC-002 derivatives from the existing VECA corpus.

Inputs remain authoritative corpus assets. Outputs are map derivatives only.
No network access is required.
"""
from __future__ import annotations

import csv
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "maps" / "poc-002" / "data"
RAIL = ROOT / "data" / "derived" / "transport" / "ga_rail_east.geojson"
ROADS = ROOT / "data" / "derived" / "transport" / "ga_major_roads_east.geojson"
REGIONS = ROOT / "domains" / "government-intent" / "data" / "derived" / "regional_growth_baselines_seed.csv"
ANCHORS = ROOT / "domains" / "government-intent" / "data" / "derived" / "anchor_assets_seed.csv"
EDUCATION = ROOT / "domains" / "government-intent" / "data" / "derived" / "education_assets_seed.csv"
REGISTRY = ROOT / "maps" / "spatial_registry.csv"


def scalar(v):
    return isinstance(v, (str, int, float, bool)) or v is None


def prop(props: dict, *names: str, default=""):
    low = {str(k).lower(): v for k, v in props.items()}
    for name in names:
        if name.lower() in low and low[name.lower()] not in (None, ""):
            return low[name.lower()]
    return default


def perpendicular_distance(p, a, b):
    if a == b:
        return math.hypot(p[0]-a[0], p[1]-a[1])
    x, y = p; x1, y1 = a; x2, y2 = b
    t = ((x-x1)*(x2-x1)+(y-y1)*(y2-y1))/((x2-x1)**2+(y2-y1)**2)
    t = max(0.0, min(1.0, t))
    return math.hypot(x-(x1+t*(x2-x1)), y-(y1+t*(y2-y1)))


def simplify_line(coords, tolerance):
    if len(coords) <= 2:
        return coords
    a, b = coords[0], coords[-1]
    idx, max_d = 0, 0.0
    for i in range(1, len(coords)-1):
        d = perpendicular_distance(coords[i], a, b)
        if d > max_d:
            idx, max_d = i, d
    if max_d > tolerance:
        left = simplify_line(coords[:idx+1], tolerance)
        right = simplify_line(coords[idx:], tolerance)
        return left[:-1] + right
    return [a, b]


def geometry_length_degree(geom):
    def line_len(line):
        return sum(math.hypot(b[0]-a[0], b[1]-a[1]) for a, b in zip(line, line[1:]))
    if geom.get("type") == "LineString":
        return line_len(geom.get("coordinates", []))
    if geom.get("type") == "MultiLineString":
        return sum(line_len(x) for x in geom.get("coordinates", []))
    return 0.0


def simplify_geometry(geom, tolerance):
    kind = geom.get("type")
    if kind == "LineString":
        return {"type": kind, "coordinates": simplify_line(geom.get("coordinates", []), tolerance)}
    if kind == "MultiLineString":
        return {"type": kind, "coordinates": [simplify_line(x, tolerance) for x in geom.get("coordinates", []) if len(x) >= 2]}
    return geom


def rail_is_operational(props):
    status = str(prop(props, "operational_status", "oper_status", "status", default="")).lower()
    subtype = str(prop(props, "featuresubtype", "feature_subtype", "subtype", default=""))
    if subtype in {"90016", "90017"}:  # sidings / tramlines
        return False
    if not status:
        return True
    return any(word in status for word in ("operational", "capable of operation", "open", "active"))


def normalise_line_features(src: Path, domain: str, tolerance: float, min_length: float, operational_only=False):
    data = json.loads(src.read_text(encoding="utf-8"))
    out = []
    for i, f in enumerate(data.get("features", [])):
        geom = f.get("geometry") or {}
        if geom.get("type") not in {"LineString", "MultiLineString"}:
            continue
        props = f.get("properties") or {}
        if operational_only and not rail_is_operational(props):
            continue
        if geometry_length_degree(geom) < min_length:
            continue
        name = prop(props, "name", "feature_name", "road_name", "route_name", "railway_name", default=f"{domain.title()} segment")
        source_status = prop(props, "operational_status", "oper_status", "status", default="")
        source_class = prop(props, "road_class", "hierarchy", "class", "featuretype", "featuresubtype", default="")
        retained = {str(k): v for k, v in props.items() if scalar(v) and str(k).lower() in {
            "owner","gauge","track_gauge","operational_status","oper_status","status","road_class","hierarchy","class","featuretype","featuresubtype","source_jurisdiction","jurisdiction","length_km"
        }}
        retained.update({
            "entity_id": f"{domain.upper()}-{i}", "name": str(name), "domain": domain,
            "status": "existing", "valid_from": 2026, "source_status": str(source_status),
            "source_class": str(source_class), "geometry_quality": "authoritative_source_simplified",
            "source_dataset": src.name,
        })
        out.append({"type":"Feature", "geometry": simplify_geometry(geom, tolerance), "properties": retained})
    return {"type":"FeatureCollection", "features": out}


def read_csv(path):
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def registry():
    return {r["entity_id"]: r for r in read_csv(REGISTRY)}


def status_normalise(raw):
    s = (raw or "").lower()
    if any(x in s for x in ("under_construction", "committed", "recently_completed")):
        return "committed" if "recently_completed" not in s else "existing"
    if any(x in s for x in ("planned", "future", "proposed")):
        return "planned"
    return "existing"


def point_feature(row, reg, domain):
    r = reg.get(row.get("asset_id") or row.get("region_id"))
    if not r:
        return None
    entity_id = row.get("asset_id") or row.get("region_id")
    name = row.get("asset_name") or row.get("region") or entity_id
    props = dict(row)
    props.update({
        "entity_id": entity_id, "name": name, "domain": domain,
        "geometry_quality": r["geometry_quality"], "geometry_note": r["geometry_note"],
    })
    if domain == "population":
        props["status"] = "planned"
        props["valid_from"] = 2026
        props["horizon"] = row.get("plan_horizon") or ""
    else:
        props["status"] = status_normalise(row.get("status"))
        props["valid_from"] = 2026
    return {"type":"Feature", "geometry":{"type":"Point","coordinates":[float(r["longitude"]),float(r["latitude"])]}, "properties":props}


def write_geojson(name, data):
    path = OUT / name
    path.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    mb = path.stat().st_size / 1_000_000
    print(f"{name}: {len(data.get('features', [])):,} features, {mb:.1f} MB")
    return {"file": name, "features": len(data.get("features", [])), "size_mb": round(mb, 2)}


def main():
    for required in (RAIL, ROADS, REGIONS, ANCHORS, EDUCATION, REGISTRY):
        if not required.exists():
            raise FileNotFoundError(required)
    OUT.mkdir(parents=True, exist_ok=True)

    manifest = {}
    manifest["rail"] = write_geojson("rail.geojson", normalise_line_features(RAIL, "rail", tolerance=0.002, min_length=0.003, operational_only=True))
    manifest["roads"] = write_geojson("roads.geojson", normalise_line_features(ROADS, "roads", tolerance=0.004, min_length=0.015))

    reg = registry()
    population = [f for row in read_csv(REGIONS) if (f := point_feature(row, reg, "population"))]
    anchors = [f for row in read_csv(ANCHORS) if (f := point_feature(row, reg, "infrastructure"))]
    education = [f for row in read_csv(EDUCATION) if (f := point_feature(row, reg, "education"))]
    manifest["population"] = write_geojson("population.geojson", {"type":"FeatureCollection","features":population})
    manifest["infrastructure"] = write_geojson("infrastructure.geojson", {"type":"FeatureCollection","features":anchors})
    manifest["education"] = write_geojson("education.geojson", {"type":"FeatureCollection","features":education})

    mapped_ids = set(reg)
    corpus_ids = {r.get("asset_id") for r in read_csv(ANCHORS)+read_csv(EDUCATION)} | {r.get("region_id") for r in read_csv(REGIONS)}
    missing = sorted(x for x in corpus_ids if x and x not in mapped_ids)
    (OUT / "spatial-gaps.json").write_text(json.dumps({"missing_geometry_ids":missing}, indent=2), encoding="utf-8")
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Spatial registry gaps: {len(missing)} entities -> maps/poc-002/data/spatial-gaps.json")


if __name__ == "__main__":
    main()
