#!/usr/bin/env python3
"""POC-007: terrain-only Sydney–Melbourne passenger-HST candidate path.

This is a lever-learning model, not an engineering alignment. It searches a
coarse raster derived from accepted EXP-002 elevation/slope surfaces, then
samples the 250 m analytical rasters along the candidate horizontal alignment,
builds a grade-constrained indicative rail profile, infers construction mode
from design-vs-ground offset, and writes clickable GeoJSON segments.
"""
from __future__ import annotations

import argparse
import heapq
import json
import math
from pathlib import Path

import numpy as np
import rasterio
from rasterio.enums import Resampling
from rasterio.transform import from_origin
from rasterio.vrt import WarpedVRT
from rasterio.warp import transform, transform_bounds

ROOT = Path(__file__).resolve().parents[1]
TERRAIN_DIR = ROOT / "experiments" / "EXP-002-habitat-resource-screening" / "data" / "terrain"
OUT_DIR = ROOT / "maps" / "poc-007" / "data"
CRS = "EPSG:3577"
WGS84 = "EPSG:4326"
NODATA = -9999.0

SYDNEY = (151.2093, -33.8688)
MELBOURNE = (144.9631, -37.8136)
SEARCH_BBOX_WGS84 = (143.4, -38.35, 151.55, -33.35)

# Exposed v1 levers. These are heuristic POC parameters, not engineering truth.
DEFAULT_SEARCH_RESOLUTION_M = 2000
DEFAULT_PROFILE_STEP_M = 1000
MAX_GRADE = 0.035
DISTANCE_WEIGHT = 1.0
GROUND_GRADE_WEIGHT = 3.0
SIDE_SLOPE_WEIGHT = 0.65
SMOOTHING_WINDOW_KM = 12.0
PATH_SMOOTH_PASSES = 2

# Construction-mode inference from indicative rail elevation minus ground.
CUTTING_THRESHOLD_M = -3.0
TUNNEL_THRESHOLD_M = -20.0
EMBANKMENT_THRESHOLD_M = 3.0
BRIDGE_THRESHOLD_M = 12.0

NEIGHBOURS = [
    (-1, 0, 1.0), (1, 0, 1.0), (0, -1, 1.0), (0, 1, 1.0),
    (-1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)),
    (1, -1, math.sqrt(2)), (1, 1, math.sqrt(2)),
]


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--terrain-dir", type=Path, default=TERRAIN_DIR)
    p.add_argument("--out", type=Path, default=OUT_DIR)
    p.add_argument("--search-resolution-m", type=int, default=DEFAULT_SEARCH_RESOLUTION_M)
    p.add_argument("--profile-step-m", type=int, default=DEFAULT_PROFILE_STEP_M)
    p.add_argument("--max-grade", type=float, default=MAX_GRADE)
    p.add_argument("--ground-grade-weight", type=float, default=GROUND_GRADE_WEIGHT)
    p.add_argument("--side-slope-weight", type=float, default=SIDE_SLOPE_WEIGHT)
    p.add_argument("--smoothing-window-km", type=float, default=SMOOTHING_WINDOW_KM)
    return p.parse_args()


def search_grid(resolution_m):
    left, bottom, right, top = transform_bounds(WGS84, CRS, *SEARCH_BBOX_WGS84, densify_pts=21)
    width = math.ceil((right-left)/resolution_m)
    height = math.ceil((top-bottom)/resolution_m)
    return width, height, from_origin(left, top, resolution_m, resolution_m)


def read_search_surface(path, resolution_m, tx, width, height, resampling):
    with rasterio.open(path) as src:
        with WarpedVRT(src, crs=CRS, transform=tx, width=width, height=height,
                       nodata=NODATA, resampling=resampling) as vrt:
            return vrt.read(1, masked=True).filled(np.nan).astype("float32")


def xy_to_rc(x, y, tx, shape):
    col = int((x - tx.c) / tx.a)
    row = int((tx.f - y) / -tx.e)
    row = max(0, min(shape[0]-1, row)); col = max(0, min(shape[1]-1, col))
    return row, col


def rc_to_xy(row, col, tx):
    return tx.c + (col + 0.5)*tx.a, tx.f + (row + 0.5)*tx.e


def endpoint_rc(lonlat, tx, shape):
    xs, ys = transform(WGS84, CRS, [lonlat[0]], [lonlat[1]])
    return xy_to_rc(xs[0], ys[0], tx, shape)


def astar(elev, slope, tx, start, goal, resolution_m, ground_grade_weight, side_slope_weight):
    """Raster A* with non-negative distance, terrain-grade and side-slope penalties."""
    h, w = elev.shape
    if not np.isfinite(elev[start]) or not np.isfinite(elev[goal]):
        raise RuntimeError("Start or goal falls on terrain NoData")

    gscore = np.full((h,w), np.inf, dtype="float64")
    parent = np.full((h,w,2), -1, dtype="int32")
    closed = np.zeros((h,w), dtype=bool)
    gscore[start] = 0.0

    def heuristic(r,c):
        return math.hypot(r-goal[0], c-goal[1]) * resolution_m * DISTANCE_WEIGHT

    queue = [(heuristic(*start), 0.0, start[0], start[1])]
    visited = 0
    while queue:
        _, g, r, c = heapq.heappop(queue)
        if closed[r,c]: continue
        closed[r,c] = True; visited += 1
        if (r,c) == goal:
            break
        z0 = float(elev[r,c])
        for dr,dc,mult in NEIGHBOURS:
            nr,nc = r+dr,c+dc
            if nr<0 or nr>=h or nc<0 or nc>=w or closed[nr,nc] or not np.isfinite(elev[nr,nc]):
                continue
            dist = resolution_m*mult
            grade = abs(float(elev[nr,nc])-z0)/dist
            local_slope = np.nanmean([slope[r,c], slope[nr,nc]])
            if not np.isfinite(local_slope): local_slope = 0.0
            grade_ratio = grade / MAX_GRADE
            slope_ratio = local_slope / 10.0
            step = dist * (DISTANCE_WEIGHT + ground_grade_weight*grade_ratio*grade_ratio + side_slope_weight*slope_ratio*slope_ratio)
            ng = g + step
            if ng < gscore[nr,nc]:
                gscore[nr,nc] = ng
                parent[nr,nc] = (r,c)
                heapq.heappush(queue,(ng+heuristic(nr,nc),ng,nr,nc))

    if not closed[goal]:
        raise RuntimeError(f"No path found after visiting {visited:,} cells")
    path=[]; cur=goal
    while cur != start:
        path.append(cur)
        pr,pc = parent[cur]
        if pr < 0: raise RuntimeError("Broken A* parent chain")
        cur=(int(pr),int(pc))
    path.append(start); path.reverse()
    print(f"A*: visited {visited:,} cells; raw path {len(path):,} nodes")
    return path, float(gscore[goal])


def smooth_xy(points, passes=PATH_SMOOTH_PASSES):
    pts=np.asarray(points,dtype="float64")
    for _ in range(passes):
        q=pts.copy()
        q[1:-1] = (pts[:-2] + 2*pts[1:-1] + pts[2:]) / 4.0
        pts=q
    return pts


def resample_polyline(points, step_m):
    pts=np.asarray(points,dtype="float64")
    seg=np.hypot(np.diff(pts[:,0]),np.diff(pts[:,1]))
    chain=np.concatenate(([0.0],np.cumsum(seg)))
    samples=np.arange(0,chain[-1],step_m,dtype="float64")
    if samples.size==0 or samples[-1] < chain[-1]: samples=np.append(samples,chain[-1])
    x=np.interp(samples,chain,pts[:,0]); y=np.interp(samples,chain,pts[:,1])
    return np.column_stack((x,y)),samples


def sample_raster(path, xy):
    with rasterio.open(path) as ds:
        vals=np.array([v[0] for v in ds.sample([tuple(p) for p in xy])],dtype="float64")
        if ds.nodata is not None: vals[vals==ds.nodata]=np.nan
    return vals


def moving_average(values, window):
    if window <= 1: return values.copy()
    if window % 2 == 0: window += 1
    pad=window//2
    v=np.pad(values,(pad,pad),mode="edge")
    return np.convolve(v,np.ones(window)/window,mode="valid")


def enforce_grade(profile, chainage, max_grade, start_elev, end_elev, iterations=12):
    """Project an indicative profile onto a simple max-grade envelope."""
    z=profile.astype("float64").copy(); z[0]=start_elev; z[-1]=end_elev
    for _ in range(iterations):
        z[0]=start_elev
        for i in range(1,len(z)):
            lim=max_grade*(chainage[i]-chainage[i-1])
            z[i]=min(max(z[i],z[i-1]-lim),z[i-1]+lim)
        z[-1]=end_elev
        for i in range(len(z)-2,-1,-1):
            lim=max_grade*(chainage[i+1]-chainage[i])
            z[i]=min(max(z[i],z[i+1]-lim),z[i+1]+lim)
        z[0]=start_elev; z[-1]=end_elev
    return z


def build_design_profile(ground, chainage, max_grade, smoothing_window_km, step_m):
    window=max(3,int(round(smoothing_window_km*1000/step_m)))
    target=moving_average(ground,window)
    target[0]=ground[0]; target[-1]=ground[-1]
    return enforce_grade(target,chainage,max_grade,ground[0],ground[-1])


def construction_mode(clearance_m):
    if clearance_m <= TUNNEL_THRESHOLD_M: return "tunnel"
    if clearance_m < CUTTING_THRESHOLD_M: return "cutting"
    if clearance_m >= BRIDGE_THRESHOLD_M: return "bridge_or_elevated"
    if clearance_m > EMBANKMENT_THRESHOLD_M: return "embankment"
    return "at_grade"


def mode_reason(mode):
    return {
        "tunnel":f"Indicative rail profile >= {abs(TUNNEL_THRESHOLD_M):.0f} m below terrain",
        "cutting":f"Indicative rail profile {abs(CUTTING_THRESHOLD_M):.0f}–{abs(TUNNEL_THRESHOLD_M):.0f} m below terrain",
        "bridge_or_elevated":f"Indicative rail profile >= {BRIDGE_THRESHOLD_M:.0f} m above terrain",
        "embankment":f"Indicative rail profile {EMBANKMENT_THRESHOLD_M:.0f}–{BRIDGE_THRESHOLD_M:.0f} m above terrain",
        "at_grade":f"Indicative rail profile within about {EMBANKMENT_THRESHOLD_M:.0f} m of terrain",
    }[mode]


def percentile(a,q):
    a=np.asarray(a); a=a[np.isfinite(a)]
    return float(np.percentile(a,q)) if a.size else float("nan")


def write_segments(out_path, xy, chainage, ground, design, terrain_slope):
    clearance=design-ground
    modes=[construction_mode((clearance[i]+clearance[i+1])/2) for i in range(len(xy)-1)]
    # Merge consecutive one-km samples with the same inferred mode.
    ranges=[]; start=0
    for i in range(1,len(modes)+1):
        if i==len(modes) or modes[i]!=modes[start]:
            ranges.append((start,i,modes[start])); start=i

    features=[]; totals={m:0.0 for m in ["at_grade","embankment","cutting","bridge_or_elevated","tunnel"]}
    for sid,(a,b,mode) in enumerate(ranges,1):
        coords_xy=xy[a:b+1]
        lons,lats=transform(CRS,WGS84,coords_xy[:,0].tolist(),coords_xy[:,1].tolist())
        length_m=float(chainage[b]-chainage[a]); totals[mode]+=length_m
        ds=np.diff(chainage[a:b+1]); grades=np.diff(design[a:b+1])/ds*100.0 if len(ds) else np.array([0.0])
        gs=ground[a:b+1]; dz=clearance[a:b+1]; ts=terrain_slope[a:b+1]
        props={
            "segment_id":sid,"construction_mode":mode,"reason":mode_reason(mode),
            "chainage_start_km":round(float(chainage[a]/1000),2),"chainage_end_km":round(float(chainage[b]/1000),2),
            "length_km":round(length_m/1000,2),
            "ground_elev_min_m":round(float(np.nanmin(gs)),1),"ground_elev_mean_m":round(float(np.nanmean(gs)),1),"ground_elev_max_m":round(float(np.nanmax(gs)),1),
            "design_elev_start_m":round(float(design[a]),1),"design_elev_end_m":round(float(design[b]),1),
            "mean_clearance_m":round(float(np.nanmean(dz)),1),"min_clearance_m":round(float(np.nanmin(dz)),1),"max_clearance_m":round(float(np.nanmax(dz)),1),
            "mean_grade_pct":round(float((design[b]-design[a])/length_m*100.0),3) if length_m else 0.0,
            "max_abs_grade_pct":round(float(np.max(np.abs(grades))),3),
            "terrain_slope_mean_deg":round(float(np.nanmean(ts)),2),"terrain_slope_p90_deg":round(percentile(ts,90),2),
            "analysis_surface_m":250,"search_grid_m":DEFAULT_SEARCH_RESOLUTION_M,"status":"terrain_only_poc"
        }
        features.append({"type":"Feature","geometry":{"type":"LineString","coordinates":[[float(x),float(y)] for x,y in zip(lons,lats)]},"properties":props})
    out_path.parent.mkdir(parents=True,exist_ok=True)
    out_path.write_text(json.dumps({"type":"FeatureCollection","name":"poc007_hst_terrain_segments","features":features},separators=(",",":")),encoding="utf-8")
    return features,totals


def main():
    args=parse_args()
    elev_path=args.terrain_dir/"elevation_250m.tif"; slope_path=args.terrain_dir/"slope_degrees_250m.tif"
    for p in (elev_path,slope_path):
        if not p.exists(): raise SystemExit(f"Missing {p}; run python tools/build_terrain_screen.py first")
    width,height,tx=search_grid(args.search_resolution_m)
    print(f"POC-007 search grid: {width}x{height} at {args.search_resolution_m:,} m")
    elev=read_search_surface(elev_path,args.search_resolution_m,tx,width,height,Resampling.bilinear)
    slope=read_search_surface(slope_path,args.search_resolution_m,tx,width,height,Resampling.average)
    start=endpoint_rc(SYDNEY,tx,elev.shape); goal=endpoint_rc(MELBOURNE,tx,elev.shape)
    print(f"A* Sydney {start} -> Melbourne {goal}")
    path,search_cost=astar(elev,slope,tx,start,goal,args.search_resolution_m,args.ground_grade_weight,args.side_slope_weight)
    xy=smooth_xy([rc_to_xy(r,c,tx) for r,c in path])
    # Preserve exact CBD endpoint coordinates rather than grid-cell centres.
    ex,ey=transform(WGS84,CRS,[SYDNEY[0],MELBOURNE[0]],[SYDNEY[1],MELBOURNE[1]])
    xy[0]=[ex[0],ey[0]]; xy[-1]=[ex[1],ey[1]]
    samples,chain=resample_polyline(xy,args.profile_step_m)
    ground=sample_raster(elev_path,samples); terrain_slope=sample_raster(slope_path,samples)
    if not np.isfinite(ground).all(): raise RuntimeError("Candidate alignment samples terrain NoData")
    design=build_design_profile(ground,chain,args.max_grade,args.smoothing_window_km,args.profile_step_m)
    grades=np.diff(design)/np.diff(chain)
    max_grade=float(np.max(np.abs(grades))) if grades.size else 0.0
    if max_grade > args.max_grade + 1e-6:
        raise RuntimeError(f"Grade envelope failed: {max_grade*100:.3f}% > {args.max_grade*100:.3f}%")

    args.out.mkdir(parents=True,exist_ok=True)
    features,totals=write_segments(args.out/"hst_terrain_segments.geojson",samples,chain,ground,design,terrain_slope)
    total_m=float(chain[-1])
    summary={
        "name":"POC-007 terrain-only Sydney–Melbourne HST candidate",
        "start":"Sydney CBD","end":"Melbourne CBD","path_length_km":round(total_m/1000,1),
        "straight_line_note":"Path length is projected alignment distance; no stations or corridor constraints are included.",
        "search_resolution_m":args.search_resolution_m,"profile_sample_m":args.profile_step_m,"analysis_surface_m":250,
        "max_grade_pct":round(args.max_grade*100,2),"actual_max_abs_profile_grade_pct":round(max_grade*100,3),
        "search_cost_units":round(search_cost,1),"segment_count":len(features),
        "construction_thresholds_m":{"tunnel_below_ground":TUNNEL_THRESHOLD_M,"cutting_below_ground":CUTTING_THRESHOLD_M,"embankment_above_ground":EMBANKMENT_THRESHOLD_M,"bridge_above_ground":BRIDGE_THRESHOLD_M},
        "construction_share_pct":{k:round(v/total_m*100,1) for k,v in totals.items()},
        "construction_length_km":{k:round(v/1000,1) for k,v in totals.items()},
        "parameters":{"ground_grade_weight":args.ground_grade_weight,"side_slope_weight":args.side_slope_weight,"smoothing_window_km":args.smoothing_window_km},
        "limitations":["Terrain only; not an engineering alignment or cost estimate.","Horizontal curvature is not yet enforced; raster path is lightly smoothed.","Construction modes are inferred from a heuristic vertical profile versus ground.","No hydrology, geology, land constraints, existing corridors, settlements or station objectives are included."]
    }
    (args.out/"hst_terrain_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    print(f"Wrote {args.out/'hst_terrain_segments.geojson'}")

if __name__=="__main__": main()
