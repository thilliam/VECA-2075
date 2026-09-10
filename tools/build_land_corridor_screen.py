#!/usr/bin/env python3
"""POC-008: normalize land/urban evidence around the POC-007 HST candidate.

The initial extraction window is a QA/browser window around the existing path,
NOT a routing constraint. The normalized factor schema and rules are intended to
be reusable by future corridor and alignment solvers over wider search areas.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import geopandas as gpd
import pandas as pd
import pyogrio
from shapely.geometry import shape
from shapely.ops import unary_union

from land_corridor_rules import classify_abs_meshblock, classify_nsw_tenure

ROOT = Path(__file__).resolve().parents[1]
POC007 = ROOT / "maps" / "poc-007" / "data" / "hst_terrain_segments.geojson"
OUT = ROOT / "maps" / "poc-008" / "data"
CRS = "EPSG:3577"
WGS84 = "EPSG:4326"
DEFAULT_NSW_TENURE = ROOT / "research" / "source" / "land" / "nswlandtenure_dec2024_v2_seed.gdb"
DEFAULT_ABS_MB = ROOT / "research" / "source" / "land" / "MB_2021_AUST_SHP_GDA2020"
NSW_TENURE_LAYER = "NSW_LandTenure_DPI2024_v02"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--nsw-tenure", type=Path, default=DEFAULT_NSW_TENURE,
                   help="NSW Land Tenure source; defaults to inspected local GDB")
    p.add_argument("--nsw-layer", default=NSW_TENURE_LAYER,
                   help="NSW tenure layer; defaults to inspected 2024 layer")
    p.add_argument("--vic-property", type=Path, help="Vicmap Property source (optional in first pass)")
    p.add_argument("--vic-crown", type=Path, help="Vicmap Crown Land Tenure source (optional in first pass)")
    p.add_argument("--abs-meshblocks", type=Path, default=DEFAULT_ABS_MB,
                   help="ABS 2021 Mesh Blocks source; defaults to inspected local dataset")
    p.add_argument("--path", type=Path, default=POC007)
    p.add_argument("--buffer-km", type=float, default=50.0,
                   help="Browser/QA extraction buffer around POC-007; not a route-search constraint")
    p.add_argument("--out", type=Path, default=OUT)
    p.add_argument("--inspect", type=Path, help="Print layers/columns for a vector source and exit")
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
        if len(g): print(g.drop(columns="geometry", errors="ignore").head(2).to_string(index=False))


def pick_column(columns, candidates):
    lookup = {str(c).lower(): c for c in columns}
    for c in candidates:
        if c.lower() in lookup: return lookup[c.lower()]
    for original in columns:
        low = str(original).lower()
        if any(c.lower() in low for c in candidates): return original
    return None


def pick_layer(path: Path, hint: str | None, contains: tuple[str, ...]):
    if hint: return hint
    names = [str(x[0]) for x in pyogrio.list_layers(path)]
    for n in names:
        low=n.lower()
        if any(x in low for x in contains): return n
    return names[0] if names else None


def path_buffer(path: Path, buffer_km: float):
    raw=json.loads(path.read_text(encoding="utf-8"))
    geoms=[shape(f["geometry"]) for f in raw.get("features",[]) if f.get("geometry")]
    if not geoms: raise SystemExit(f"No path geometry in {path}; run POC-007 builder first")
    route=gpd.GeoSeries([unary_union(geoms)],crs=WGS84).to_crs(CRS).iloc[0]
    return route, route.buffer(buffer_km*1000)


def read_clip(path: Path, clip_geom, layer=None):
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {path}")
    # bbox first for efficient drivers, exact intersection after reprojection.
    clip_wgs=gpd.GeoSeries([clip_geom],crs=CRS).to_crs(WGS84).iloc[0]
    g=gpd.read_file(path,layer=layer,bbox=clip_wgs.bounds)
    if g.crs is None: raise ValueError(f"Source has no CRS: {path}")
    g=g.to_crs(CRS)
    g=g[g.geometry.notna() & ~g.geometry.is_empty]
    return g[g.intersects(clip_geom)].copy()


def rule_props(rule):
    return {"factor_class":rule.factor_class,"rule_role":rule.role,
            "rule_weight":rule.weight,"rule_rationale":rule.rationale}


def normalize_nsw(path: Path, clip_geom, layer_hint=None):
    layer=pick_layer(path,layer_hint,("tenure",))
    g=read_clip(path,clip_geom,layer)
    # Inspected 2024 schema pins TenureClass; fallback aliases kept for resilience.
    class_col=pick_column(g.columns,("TenureClass","tenure_class","tenure class","ten_class"))
    type_col=pick_column(g.columns,("tenure_type","tenuretype","tenure type","ten_type"))
    if not class_col:
        raise ValueError(f"Could not identify NSW tenure class field. Columns: {list(g.columns)}; use --inspect first")
    rows=[]
    for _,r in g.iterrows():
        tc=None if pd.isna(r[class_col]) else str(r[class_col])
        tt=None if not type_col or pd.isna(r[type_col]) else str(r[type_col])
        rule=classify_nsw_tenure(tc,tt)
        rows.append({"source_id":"NSW-LAND-TENURE-2024","jurisdiction":"NSW",
                     "source_class":tc,"source_type":tt,**rule_props(rule),"geometry":r.geometry})
    return gpd.GeoDataFrame(rows,crs=CRS)


def normalize_abs(path: Path, clip_geom):
    g=read_clip(path,clip_geom)
    # Inspected ABS schema pins these Edition 3 field names.
    cat=pick_column(g.columns,("MB_CAT21","mesh block category","mb_cat"))
    code=pick_column(g.columns,("MB_CODE21","mesh block code","mb_code"))
    state_name=pick_column(g.columns,("STE_NAME21","state name"))
    sa2_name=pick_column(g.columns,("SA2_NAME21","sa2 name"))
    if not cat: raise ValueError(f"Could not identify ABS MB_CAT21 field. Columns: {list(g.columns)}")
    rows=[]
    keep={"residential","commercial","industrial","transport","education","hospital/medical","parkland"}
    for _,r in g.iterrows():
        value="" if pd.isna(r[cat]) else str(r[cat])
        if value.strip().lower() not in keep: continue
        rule=classify_abs_meshblock(value)
        rows.append({"source_id":"ABS-MESH-BLOCK-2021","jurisdiction":"AU",
                     "source_class":value,"source_type":None,
                     "state_name":None if not state_name or pd.isna(r[state_name]) else str(r[state_name]),
                     "sa2_name":None if not sa2_name or pd.isna(r[sa2_name]) else str(r[sa2_name]),
                     "source_feature_id":None if not code or pd.isna(r[code]) else str(r[code]),
                     **rule_props(rule),"geometry":r.geometry})
    return gpd.GeoDataFrame(rows,crs=CRS)


def write_geojson(gdf: gpd.GeoDataFrame, path: Path, simplify_m: float=15.0):
    path.parent.mkdir(parents=True,exist_ok=True)
    out=gdf.copy()
    if len(out):
        out["geometry"]=out.geometry.simplify(simplify_m,preserve_topology=True)
        out=out.to_crs(WGS84)
    out.to_file(path,driver="GeoJSON")
    print(f"Wrote {path}: {len(out):,} features")


def route_intersections(route, datasets):
    records=[]
    for name,g in datasets.items():
        if g is None or g.empty: continue
        hits=g[g.intersects(route)].copy()
        for _,r in hits.iterrows():
            length=float(route.intersection(r.geometry).length)
            if length <= 0: continue
            records.append({"dataset":name,"factor_class":r.factor_class,"rule_role":r.rule_role,
                            "rule_weight":float(r.rule_weight),"intersection_length_m":round(length,1),
                            "source_class":r.source_class,"source_type":r.source_type,
                            "state_name":r.get("state_name"),"sa2_name":r.get("sa2_name")})
    by={}
    for x in records:
        key=x["factor_class"]
        by.setdefault(key,{"factor_class":key,"intersection_length_m":0.0,"crossed_features":0,"rule_role":x["rule_role"]})
        by[key]["intersection_length_m"]+=x["intersection_length_m"]
        by[key]["crossed_features"]+=1
    for v in by.values(): v["intersection_length_km"]=round(v.pop("intersection_length_m")/1000,2)
    return records,sorted(by.values(),key=lambda x:-x["intersection_length_km"])


def main():
    args=parse_args()
    if args.inspect:
        inspect_vector(args.inspect); return
    if not args.path.exists(): raise SystemExit(f"Missing {args.path}; run python tools/build_hst_terrain_path.py first")
    route,clip=path_buffer(args.path,args.buffer_km)
    args.out.mkdir(parents=True,exist_ok=True)
    datasets={}

    if args.nsw_tenure:
        print(f"Normalizing NSW land tenure from {args.nsw_tenure}...")
        datasets["nsw_tenure"]=normalize_nsw(args.nsw_tenure,clip,args.nsw_layer)
        write_geojson(datasets["nsw_tenure"],args.out/"land_tenure_nsw.geojson")
    if args.abs_meshblocks:
        print(f"Normalizing ABS urban/developed Mesh Blocks from {args.abs_meshblocks}...")
        datasets["abs_meshblocks"]=normalize_abs(args.abs_meshblocks,clip)
        write_geojson(datasets["abs_meshblocks"],args.out/"urban_meshblocks.geojson")

    # Victoria sources are pinned in the manifest; first local run should use --inspect
    # to lock their exact layer/field schema before normalization is added rather than
    # guessing semantic fields from metadata alone.
    pending=[]
    if args.vic_property: pending.append(str(args.vic_property))
    if args.vic_crown: pending.append(str(args.vic_crown))
    if pending:
        print("Victoria source supplied but v1 normalizer intentionally not guessing fields yet.")
        print("Run --inspect on each source and pin the observed layer/column schema next.")

    detailed,summary=route_intersections(route,datasets)
    result={"status":"partial" if len(datasets)<2 or pending else "initial_evidence_built",
            "qa_buffer_km":args.buffer_km,"qa_buffer_is_routing_constraint":False,
            "datasets_built":list(datasets),"victoria_schema_pending":pending,
            "poc007_path_intersections":summary,"intersection_records":len(detailed),
            "source_schemas":{"nsw":{"layer":NSW_TENURE_LAYER,"class_field":"TenureClass"},
                              "abs":{"layer":"MB_2021_AUST_GDA2020","category_field":"MB_CAT21","state_field":"STE_NAME21","sa2_field":"SA2_NAME21"}}}
    (args.out/"land_corridor_summary.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))

if __name__=="__main__": main()
