#!/usr/bin/env python3
"""Build VECA EXP-002 terrain/buildability screening products.

Preferred source: local Geoscience Australia SRTM-derived 3-second DEM (~90 m)
stored outside Git. The pipeline preserves continuous elevation and slope as the
analytical truth; the browser classification is a deliberately coarser view.
"""
from __future__ import annotations

import argparse
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
DEFAULT_OUT = ROOT / "experiments" / "EXP-002-habitat-resource-screening" / "data" / "terrain"
MAP_OUT = ROOT / "maps" / "poc-006" / "data"
DEFAULT_LOCAL_DEM = ROOT / "research" / "source" / "terrain" / "3secSRTM_DEM" / "DEM_ESRI_GRID_16bit_Integer" / "dem3s_int"
BBOX_WGS84 = (137.8, -39.25, 154.1, -9.9)
TARGET_CRS = "EPSG:3577"
DEFAULT_RESOLUTION_M = 250
DEFAULT_MAP_CELL_M = 10000
NODATA = -9999.0

BANDS = [
    ("very_low_gradient", 0.0, 3.0),
    ("low_gradient", 3.0, 8.0),
    ("moderate_gradient", 8.0, 15.0),
    ("steep", 15.0, 25.0),
    ("very_steep", 25.0, float("inf")),
]

SANITY_POINTS = {
    "Brisbane_CBD": {"lon": 153.026, "lat": -27.4705, "elev_min": -20, "elev_max": 150},
    "Sydney_CBD": {"lon": 151.2093, "lat": -33.8688, "elev_min": -20, "elev_max": 180},
    "Melbourne_CBD": {"lon": 144.9631, "lat": -37.8136, "elev_min": -20, "elev_max": 180},
    "Wagga_Wagga": {"lon": 147.369, "lat": -35.108, "elev_min": 100, "elev_max": 350},
    "Katoomba": {"lon": 150.311, "lat": -33.712, "elev_min": 700, "elev_max": 1250},
    "Mount_Kosciuszko": {"lon": 148.2635, "lat": -36.4558, "elev_min": 1800, "elev_max": 2400},
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser()
    p.add_argument("--resolution-m", type=int, default=DEFAULT_RESOLUTION_M)
    p.add_argument("--map-cell-m", type=int, default=DEFAULT_MAP_CELL_M)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--dem-path", type=Path, default=DEFAULT_LOCAL_DEM,
                   help="Local GA 3-second DEM dataset path (AIG directory or GDAL-readable raster)")
    p.add_argument("--skip-map", action="store_true")
    return p.parse_args()


def target_grid(resolution_m: int):
    left, bottom, right, top = transform_bounds("EPSG:4326", TARGET_CRS, *BBOX_WGS84, densify_pts=21)
    width = math.ceil((right - left) / resolution_m)
    height = math.ceil((top - bottom) / resolution_m)
    return width, height, from_origin(left, top, resolution_m, resolution_m)


def read_dem(path: Path, resolution_m: int):
    if not path.exists():
        raise SystemExit(f"Local DEM not found: {path}")
    with rasterio.open(path) as src:
        print(f"Opened source: driver={src.driver} size={src.width}x{src.height} crs={src.crs} nodata={src.nodata}")
        width, height, tx = target_grid(resolution_m)
        print(f"Target grid: {width}x{height} at {resolution_m} m in {TARGET_CRS}")
        with WarpedVRT(src, crs=TARGET_CRS, transform=tx, width=width, height=height,
                       resampling=Resampling.bilinear, nodata=NODATA) as vrt:
            print("Reading/reprojecting DEM...")
            dem = vrt.read(1, masked=True).astype("float32")
    print(f"DEM read complete: {dem.count():,} valid cells")
    return dem, tx


def slope_degrees(dem: np.ma.MaskedArray, resolution_m: int) -> np.ma.MaskedArray:
    print("Calculating slope...")
    data = dem.filled(np.nan).astype("float64")
    dz_dy, dz_dx = np.gradient(data, resolution_m, resolution_m)
    slope = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy))).astype("float32")
    out = np.ma.array(slope, mask=np.ma.getmaskarray(dem) | ~np.isfinite(slope))
    print(f"Slope complete: {out.count():,} valid cells")
    return out


def band_name(value: float) -> str:
    return next((name for name, lo, hi in BANDS if lo <= value < hi), "unknown")


def write_raster(path: Path, arr: np.ma.MaskedArray, tx, units: str, source_ref: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {"driver":"GTiff","height":arr.shape[0],"width":arr.shape[1],"count":1,
               "dtype":"float32","crs":TARGET_CRS,"transform":tx,"nodata":NODATA,
               "compress":"deflate","tiled":True,"blockxsize":512,"blockysize":512}
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr.filled(NODATA).astype("float32"), 1)
        dst.update_tags(units=units, source=source_ref, analysis_role="continuous")
    print(f"Wrote {path}")


def sample_points(dem_path: Path):
    results, failures = {}, []
    with rasterio.open(dem_path) as ds:
        for name, spec in SANITY_POINTS.items():
            xs, ys = transform("EPSG:4326", ds.crs, [spec["lon"]], [spec["lat"]])
            val = float(next(ds.sample([(xs[0], ys[0])]))[0])
            ok = spec["elev_min"] <= val <= spec["elev_max"]
            results[name] = {"elevation_m":round(val,1),"expected_range_m":[spec["elev_min"],spec["elev_max"]],"pass":ok}
            if not ok: failures.append(name)
    return results, failures


def aggregate_map_grid(dem, slope, map_cell_m: int, resolution_m: int):
    print("Aggregating 10 km map cells...")
    factor = map_cell_m // resolution_m
    h, w = (dem.shape[0] // factor) * factor, (dem.shape[1] // factor) * factor
    d = dem[:h,:w].filled(np.nan).reshape(h//factor,factor,w//factor,factor)
    s = slope[:h,:w].filled(np.nan).reshape(h//factor,factor,w//factor,factor)
    return factor, (
        np.nanmean(d, axis=(1,3)),
        np.nanmedian(s, axis=(1,3)),
        np.nanpercentile(s, 90, axis=(1,3)),
        np.nanmean(s >= 15.0, axis=(1,3)),
        np.mean(np.isfinite(d), axis=(1,3)),
    )


def map_geojson(path: Path, tx, factor: int, resolution_m: int, metrics):
    elev_mean, slope_median, slope_p90, steep_share, valid_share = metrics
    features, cell = [], factor * resolution_m
    for row in range(elev_mean.shape[0]):
        y_top, y_bottom = tx.f - row*cell, tx.f - (row+1)*cell
        for col in range(elev_mean.shape[1]):
            if valid_share[row,col] < 0.5 or not np.isfinite(slope_p90[row,col]): continue
            x_left, x_right = tx.c + col*cell, tx.c + (col+1)*cell
            xs = [x_left,x_right,x_right,x_left,x_left]
            ys = [y_bottom,y_bottom,y_top,y_top,y_bottom]
            lons, lats = transform(TARGET_CRS, "EPSG:4326", xs, ys)
            p90 = float(slope_p90[row,col])
            features.append({"type":"Feature","geometry":{"type":"Polygon","coordinates":[list(map(list,zip(lons,lats)))]},
                "properties":{"elevation_mean_m":round(float(elev_mean[row,col]),1),
                    "slope_median_deg":round(float(slope_median[row,col]),2),
                    "slope_p90_deg":round(p90,2),"steep_share_ge15":round(float(steep_share[row,col]),3),
                    "terrain_band":band_name(p90),"analysis_resolution_m":resolution_m,"map_cell_m":cell,
                    "geometry_quality":"derived_regular_grid","source_surface":"GA SRTM 3-second DEM"}})
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"type":"FeatureCollection","name":"terrain_buildability_v1","features":features},separators=(",",":")),encoding="utf-8")
    print(f"Wrote {path} with {len(features):,} cells")
    return len(features)


def main():
    args = parse_args()
    if args.map_cell_m % args.resolution_m:
        raise SystemExit("--map-cell-m must be an integer multiple of --resolution-m")
    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Reading local GA 3-second DEM -> {args.resolution_m} m continuous analysis surface")
    dem, tx = read_dem(args.dem_path, args.resolution_m)
    slope = slope_degrees(dem, args.resolution_m)
    if float(slope.min()) < 0 or float(slope.max()) > 90:
        raise SystemExit("Slope sanity bound failed: expected 0..90 degrees")

    source_ref = str(args.dem_path)
    dem_path = args.out / f"elevation_{args.resolution_m}m.tif"
    slope_path = args.out / f"slope_degrees_{args.resolution_m}m.tif"
    write_raster(dem_path, dem, tx, "metres", source_ref)
    write_raster(slope_path, slope, tx, "degrees", source_ref)
    sanity, failures = sample_points(dem_path)

    summary = {"source":source_ref,"source_product":"Geoscience Australia SRTM-derived 3 Second DEM",
        "source_nominal_resolution":"3 arc-second (~90 m)","analysis_crs":TARGET_CRS,
        "analysis_resolution_m":args.resolution_m,"map_cell_m":args.map_cell_m,"terrain_band_basis":"P90 slope within map cell",
        "bands_degrees":[{"name":n,"min":lo,"max":None if math.isinf(hi) else hi} for n,lo,hi in BANDS],
        "sanity_points":sanity,"valid_elevation_pixels":int(dem.count()),"valid_slope_pixels":int(slope.count()),
        "elevation_min_m":round(float(dem.min()),1),"elevation_max_m":round(float(dem.max()),1),
        "slope_p50_deg":round(float(np.ma.median(slope)),2),"slope_p95_deg":round(float(np.nanpercentile(slope.filled(np.nan),95)),2)}

    if not args.skip_map:
        factor, metrics = aggregate_map_grid(dem, slope, args.map_cell_m, args.resolution_m)
        summary["map_features"] = map_geojson(MAP_OUT/"terrain_buildability.geojson", tx, factor, args.resolution_m, metrics)
    (args.out/"terrain_summary.json").write_text(json.dumps(summary,indent=2),encoding="utf-8")
    print(json.dumps(summary,indent=2))
    if failures: raise SystemExit("Terrain sanity checks failed: " + ", ".join(failures))
    print("Terrain sanity checks passed")

if __name__ == "__main__": main()
