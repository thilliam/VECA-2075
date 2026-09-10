#!/usr/bin/env python3
"""POC-008 land/corridor evidence builder.

Authoritative geometry is kept for analysis. Browser geometry is a separate,
narrow, simplified derivative. Route scoring is segment-first: each POC-007
segment queries local evidence through a spatial index, so large multipart land
polygons are never intersected against the entire Sydney-Melbourne route.
"""
from __future__ import annotations

import argparse
import json
import os
import time
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely import intersection, make_valid
from shapely.errors import GEOSException
from shapely.geometry import shape
from shapely.ops import clip_by_rect, unary_union

from land_corridor_rules import classify_abs_meshblock, classify_nsw_tenure

ROOT = Path(__file__).resolve().parents[1]
POC007 = ROOT / "maps" / "poc-007" / "data" / "hst_terrain_segments.geojson"
OUT = ROOT / "maps" / "poc-008" / "data"
CRS = "EPSG:3577"
WGS84 = "EPSG:4326"
DEFAULT_NSW_TENURE = ROOT / "research" / "source" / "land" / "nswlandtenure_dec2024_v2_seed.gdb"
DEFAULT_ABS_MB = ROOT / "research" / "source" / "land" / "MB_2021_AUST_SHP_GDA2020"
NSW_TENURE_LAYER = "NSW_LandTenure_DPI2024_v02"
START_TIME = time.perf_counter()


def log(message: str):
    print(f"[{time.perf_counter()-START_TIME:8.1f}s] {message}", flush=True)


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--nsw-tenure", type=Path, default=DEFAULT_NSW_TENURE)
    p.add_argument("--nsw-layer", default=NSW_TENURE_LAYER)
    p.add_argument("--vic-property", type=Path)
    p.add_argument("--vic-crown", type=Path)
    p.add_argument("--abs-meshblocks", type=Path, default=DEFAULT_ABS_MB)
    p.add_argument("--path", type=Path, default=POC007)
    p.add_argument("--buffer-km", type=float, default=50.0,
                   help="Analytical QA extraction buffer; not a routing constraint")
    p.add_argument("--browser-buffer-km", type=float, default=10.0,
                   help="Display-only browser corridor")
    p.add_argument("--browser-simplify-m", type=float, default=40.0)
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--inspect", type=Path)
    p.add_argument("--safe-polygons", action="store_true")
    return p.parse_args()


def inspect_vector(path: Path):
    print(f"Source: {path}")
    layers = pyogrio.list_layers(path)
    print("Layers:")
    for name, geom in layers:
        print(f"  {name} ({geom})")
    for name, _ in layers[:8]:
        g = gpd.read_file(path, layer=name, rows=3)
        print(f"\n{name}: {list(g.columns)}")
        if len(g):
            print(g.drop(columns="geometry", errors="ignore").head(2).to_string(index=False))


def pick_column(columns, candidates):
    lookup = {str(c).lower(): c for c in columns}
    for c in candidates:
        if c.lower() in lookup:
            return lookup[c.lower()]
    for original in columns:
        low = str(original).lower()
        if any(c.lower() in low for c in candidates):
            return original
    return None


def pick_layer(path: Path, hint: str | None, contains: tuple[str, ...]):
    if hint:
        return hint
    names = [str(x[0]) for x in pyogrio.list_layers(path)]
    for n in names:
        if any(x in n.lower() for x in contains):
            return n
    return names[0] if names else None


def load_route_segments(path: Path):
    log(f"Reading POC-007 route segments: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for i, f in enumerate(raw.get("features", []), 1):
        if not f.get("geometry"):
            continue
        props = dict(f.get("properties") or {})
        props.setdefault("segment_id", i)
        props["geometry"] = shape(f["geometry"])
        rows.append(props)
    if not rows:
        raise SystemExit(f"No path geometry in {path}; run POC-007 builder first")
    segments = gpd.GeoDataFrame(rows, geometry="geometry", crs=WGS84).to_crs(CRS)
    route = unary_union(segments.geometry.tolist())
    log(f"Loaded {len(segments):,} POC-007 segments; route length {route.length/1000:,.1f} km")
    return segments, route


def _empty_gdf(columns):
    data = {c: pd.Series(dtype="object") for c in columns if c != "geometry"}
    return gpd.GeoDataFrame(data, geometry=gpd.GeoSeries([], crs=CRS), crs=CRS)


def read_clip(path: Path, clip_geom, layer=None, columns=None, fast_polygons=False):
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {path}")
    log(f"Inspecting source metadata: {path}" + (f" :: {layer}" if layer else ""))
    info = pyogrio.read_info(path, layer=layer)
    source_crs = info.get("crs")
    if not source_crs:
        raise ValueError(f"Source has no CRS: {path}")
    log(f"Source CRS: {source_crs}; source features reported: {info.get('features','unknown')}")
    clip_src = gpd.GeoSeries([clip_geom], crs=CRS).to_crs(source_crs).iloc[0]
    bbox = clip_src.bounds
    log("Source-native bbox: " + ", ".join(f"{v:.2f}" for v in bbox))
    log("Reading bbox candidates" + (f"; requested attributes: {', '.join(columns)}" if columns else ""))
    old = os.environ.get("OGR_ORGANIZE_POLYGONS")
    if fast_polygons:
        os.environ["OGR_ORGANIZE_POLYGONS"] = "SKIP"
        log("Fast polygon mode: OGR_ORGANIZE_POLYGONS=SKIP")
    t = time.perf_counter()
    try:
        g = gpd.read_file(path, layer=layer, bbox=bbox, columns=columns, engine="pyogrio")
    finally:
        if fast_polygons:
            if old is None:
                os.environ.pop("OGR_ORGANIZE_POLYGONS", None)
            else:
                os.environ["OGR_ORGANIZE_POLYGONS"] = old
    log(f"BBox read complete: {len(g):,} candidate features in {time.perf_counter()-t:,.1f}s")
    if g.empty:
        return _empty_gdf([*(columns or []), "geometry"])
    if g.crs is None:
        raise ValueError(f"Source has no CRS after read: {path}")
    t = time.perf_counter()
    log(f"Reprojecting {len(g):,} candidates to {CRS}")
    g = g.to_crs(CRS)
    log(f"Reprojection complete in {time.perf_counter()-t:,.1f}s")
    g = g[g.geometry.notna() & ~g.geometry.is_empty]
    t = time.perf_counter()
    log(f"Applying exact analytical corridor intersection to {len(g):,} valid geometries")
    out = g[g.intersects(clip_geom)].copy()
    log(f"Exact clip complete: {len(out):,} retained in {time.perf_counter()-t:,.1f}s")
    return out


def rule_props(rule):
    return {"factor_class": rule.factor_class, "rule_role": rule.role,
            "rule_weight": rule.weight, "rule_rationale": rule.rationale}


def normalize_nsw(path: Path, clip_geom, layer_hint=None, safe_polygons=False):
    layer = pick_layer(path, layer_hint, ("tenure",))
    log(f"NSW tenure layer: {layer}")
    g = read_clip(path, clip_geom, layer, columns=["TenureClass"],
                  fast_polygons=not safe_polygons)
    if g.empty:
        return _empty_gdf(["source_id","jurisdiction","source_class","source_type",
                           "factor_class","rule_role","rule_weight","rule_rationale","geometry"])
    class_col = pick_column(g.columns, ("TenureClass","tenure_class","tenure class","ten_class"))
    if not class_col:
        raise ValueError(f"Could not identify NSW tenure class field. Columns: {list(g.columns)}")
    log(f"Normalizing {len(g):,} NSW tenure features using {class_col}")
    rows = []
    for _, r in g.iterrows():
        tc = None if pd.isna(r[class_col]) else str(r[class_col])
        rule = classify_nsw_tenure(tc, None)
        rows.append({"source_id":"NSW-LAND-TENURE-2024","jurisdiction":"NSW",
                     "source_class":tc,"source_type":None,**rule_props(rule),"geometry":r.geometry})
    out = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS)
    log(f"NSW normalization complete: {len(out):,} features")
    return out


def normalize_abs(path: Path, clip_geom):
    requested = ["MB_CODE21","MB_CAT21","STE_NAME21","SA2_NAME21"]
    g = read_clip(path, clip_geom, columns=requested)
    if g.empty:
        return _empty_gdf(["source_id","jurisdiction","source_class","source_type",
                           "state_name","sa2_name","source_feature_id","factor_class",
                           "rule_role","rule_weight","rule_rationale","geometry"])
    cat = pick_column(g.columns, ("MB_CAT21","mesh block category","mb_cat"))
    code = pick_column(g.columns, ("MB_CODE21","mb_code"))
    state_name = pick_column(g.columns, ("STE_NAME21","state name"))
    sa2_name = pick_column(g.columns, ("SA2_NAME21","sa2 name"))
    if not cat:
        raise ValueError(f"Could not identify ABS MB_CAT21 field. Columns: {list(g.columns)}")
    keep = {"residential","commercial","industrial","transport","education","hospital/medical","parkland"}
    log(f"Filtering {len(g):,} ABS Mesh Blocks to urban/developed categories")
    rows = []
    for _, r in g.iterrows():
        value = "" if pd.isna(r[cat]) else str(r[cat])
        if value.strip().lower() not in keep:
            continue
        rule = classify_abs_meshblock(value)
        rows.append({"source_id":"ABS-MESH-BLOCK-2021","jurisdiction":"AU",
                     "source_class":value,"source_type":None,
                     "state_name":None if not state_name or pd.isna(r[state_name]) else str(r[state_name]),
                     "sa2_name":None if not sa2_name or pd.isna(r[sa2_name]) else str(r[sa2_name]),
                     "source_feature_id":None if not code or pd.isna(r[code]) else str(r[code]),
                     **rule_props(rule),"geometry":r.geometry})
    out = gpd.GeoDataFrame(rows, geometry="geometry", crs=CRS) if rows else _empty_gdf(["geometry"])
    log(f"ABS normalization complete: {len(out):,} retained urban/developed features")
    return out


def _local_intersection_length(segment, geom):
    """Fast path first; repair only a tiny local fragment after GEOS failure."""
    try:
        return float(intersection(segment, geom).length), False, False
    except GEOSException:
        minx, miny, maxx, maxy = segment.bounds
        pad = 2.0
        local = clip_by_rect(geom, minx-pad, miny-pad, maxx+pad, maxy+pad)
        if local.is_empty:
            return 0.0, False, True
        try:
            return float(intersection(segment, local, grid_size=0.01).length), False, True
        except GEOSException:
            local = make_valid(local)
            return float(intersection(segment, local, grid_size=0.01).length), True, True


def score_route_segments(segments: gpd.GeoDataFrame, datasets):
    records = []
    per_segment = {}
    stats = {}
    for name, g in datasets.items():
        if g is None or g.empty:
            continue
        t = time.perf_counter()
        log(f"Building spatial index for {name} ({len(g):,} analytical features)")
        sindex = g.sindex
        candidate_pairs = 0
        repaired = 0
        fallback = 0
        hit_pairs = 0
        for n, (_, segrow) in enumerate(segments.iterrows(), 1):
            seg = segrow.geometry
            sid = int(segrow.get("segment_id", n))
            candidates = list(sindex.query(seg, predicate=None))
            candidate_pairs += len(candidates)
            for pos in candidates:
                r = g.iloc[int(pos)]
                length, was_repaired, used_fallback = _local_intersection_length(seg, r.geometry)
                repaired += int(was_repaired)
                fallback += int(used_fallback)
                if length <= 0:
                    continue
                hit_pairs += 1
                rec = {"segment_id":sid,"dataset":name,
                       "factor_class":r.get("factor_class"),"rule_role":r.get("rule_role"),
                       "rule_weight":float(r.get("rule_weight",0)),
                       "intersection_length_m":round(length,1),
                       "source_class":r.get("source_class"),"source_type":r.get("source_type"),
                       "state_name":r.get("state_name"),"sa2_name":r.get("sa2_name")}
                records.append(rec)
                ps = per_segment.setdefault(str(sid), {"segment_id":sid,"observations":[],
                                                        "intersection_length_m":0.0,
                                                        "diagnostic_weighted_length":0.0})
                ps["observations"].append(rec)
                ps["intersection_length_m"] += length
                ps["diagnostic_weighted_length"] += length * rec["rule_weight"]
            if n % 50 == 0 or n == len(segments):
                log(f"{name}: scored {n}/{len(segments)} route segments; {candidate_pairs:,} bbox candidates; {hit_pairs:,} exact hits")
        stats[name] = {"candidate_pairs":candidate_pairs,"exact_hits":hit_pairs,
                       "local_repair_count":repaired,"fallback_count":fallback,
                       "elapsed_s":round(time.perf_counter()-t,1)}
        log(f"{name} complete: {candidate_pairs:,} bbox candidates -> {hit_pairs:,} exact hits; local repairs {repaired}; fallbacks {fallback}; {stats[name]['elapsed_s']:.1f}s")

    by = {}
    for x in records:
        key = x["factor_class"]
        v = by.setdefault(key,{"factor_class":key,"intersection_length_m":0.0,
                               "crossed_features":0,"rule_role":x["rule_role"]})
        v["intersection_length_m"] += x["intersection_length_m"]
        v["crossed_features"] += 1
    for v in by.values():
        v["intersection_length_km"] = round(v.pop("intersection_length_m")/1000,2)
    for v in per_segment.values():
        v["intersection_length_m"] = round(v["intersection_length_m"],1)
        v["diagnostic_weighted_length"] = round(v["diagnostic_weighted_length"],1)
    return records, sorted(by.values(), key=lambda x:-x["intersection_length_km"]), per_segment, stats


def write_browser_geojson(gdf: gpd.GeoDataFrame, path: Path, display_clip, simplify_m: float):
    path.parent.mkdir(parents=True, exist_ok=True)
    if gdf.empty:
        path.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
        log(f"Wrote {path}: 0 features")
        return 0
    t = time.perf_counter()
    idx = list(gdf.sindex.query(display_clip, predicate=None))
    out = gdf.iloc[idx].copy() if idx else gdf.iloc[0:0].copy()
    log(f"Browser bbox retained {len(out):,}/{len(gdf):,} analytical features in {time.perf_counter()-t:,.1f}s")
    if out.empty:
        path.write_text('{"type":"FeatureCollection","features":[]}', encoding="utf-8")
        return 0
    t = time.perf_counter()
    log(f"Fast display simplification: {len(out):,} geometries at {simplify_m:g} m")
    out["geometry"] = out.geometry.simplify(simplify_m, preserve_topology=False)
    out = out[out.geometry.notna() & ~out.geometry.is_empty]
    log(f"Display simplification complete in {time.perf_counter()-t:,.1f}s")
    t = time.perf_counter()
    out = out.to_crs(WGS84)
    out.to_file(path, driver="GeoJSON")
    log(f"Wrote {path}: {len(out):,} features in {time.perf_counter()-t:,.1f}s")
    return len(out)


def main():
    args = parse_args()
    if args.inspect:
        inspect_vector(args.inspect)
        return
    if not args.path.exists():
        raise SystemExit(f"Missing {args.path}; run python tools/build_hst_terrain_path.py first")

    segments, route = load_route_segments(args.path)
    analysis_clip = route.buffer(args.buffer_km*1000)
    display_clip = route.buffer(args.browser_buffer_km*1000)
    log(f"Analytical QA corridor {args.buffer_km:g} km; browser corridor {args.browser_buffer_km:g} km")
    args.out.mkdir(parents=True, exist_ok=True)
    datasets = {}

    if args.nsw_tenure:
        log(f"Normalizing NSW land tenure from {args.nsw_tenure}")
        datasets["nsw_tenure"] = normalize_nsw(args.nsw_tenure, analysis_clip,
                                                 args.nsw_layer, args.safe_polygons)
    if args.abs_meshblocks:
        log(f"Normalizing ABS Mesh Blocks from {args.abs_meshblocks}")
        datasets["abs_meshblocks"] = normalize_abs(args.abs_meshblocks, analysis_clip)

    detailed, summary, per_segment, scoring_stats = score_route_segments(segments, datasets)

    browser_counts = {}
    if "nsw_tenure" in datasets:
        browser_counts["nsw_tenure"] = write_browser_geojson(
            datasets["nsw_tenure"], args.out/"land_tenure_nsw.geojson",
            display_clip, args.browser_simplify_m)
    if "abs_meshblocks" in datasets:
        browser_counts["abs_meshblocks"] = write_browser_geojson(
            datasets["abs_meshblocks"], args.out/"urban_meshblocks.geojson",
            display_clip, args.browser_simplify_m)

    (args.out/"poc007_segment_land_summary.json").write_text(
        json.dumps({"segments":per_segment,"records":detailed}, indent=2), encoding="utf-8")

    pending = [str(p) for p in (args.vic_property,args.vic_crown) if p]
    result = {
        "status":"partial" if len(datasets)<2 or pending else "initial_evidence_built",
        "analysis_buffer_km":args.buffer_km,
        "browser_buffer_km":args.browser_buffer_km,
        "qa_buffer_is_routing_constraint":False,
        "datasets_built":list(datasets),
        "browser_feature_counts":browser_counts,
        "victoria_schema_pending":pending,
        "poc007_path_intersections":summary,
        "intersection_records":len(detailed),
        "segment_scoring_stats":scoring_stats,
        "source_schemas":{
            "nsw":{"layer":NSW_TENURE_LAYER,"class_field":"TenureClass"},
            "abs":{"layer":"MB_2021_AUST_GDA2020","category_field":"MB_CAT21",
                   "state_field":"STE_NAME21","sa2_field":"SA2_NAME21"}},
        "fast_polygon_mode":not args.safe_polygons,
        "intersection_method":"segment_spatial_index_local_geometry"
    }
    (args.out/"land_corridor_summary.json").write_text(json.dumps(result,indent=2), encoding="utf-8")
    log("POC-008 build complete")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
