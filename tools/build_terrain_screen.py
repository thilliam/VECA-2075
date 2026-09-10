#!/usr/bin/env python3
"""Build VECA EXP-002 terrain/buildability screening products.

Authoritative source:
  Geoscience Australia SRTM-derived 1-second DEM, mirrored by Digital Earth Australia.

The pipeline deliberately preserves continuous elevation and slope rasters separately
from the coarser map/display classification. It is a regional structural screen, not
parcel-scale geotechnical or engineering feasibility analysis.
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
from rasterio.warp import transform_bounds

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUT = ROOT / "experiments" / "EXP-002-habitat-resource-screening" / "data" / "terrain"
MAP_OUT = ROOT / "maps" / "poc-006" / "data"

# Geoscience Australia product ga_srtm_dem1sv1_0, DEA public mirror.
DEM_URL = "https://dea-public-data.s3-ap-southeast-2.amazonaws.com/projects/elevation/ga_srtm_dem1sv1_0/dems1sv1_0.tif"

# Full mainland extent required to cover QLD/NSW/ACT/VIC. Exact state clipping is a
# later presentation/summary concern; ocean/source nodata is excluded analytically.
BBOX_WGS84 = (137.8, -39.25, 154.1, -9.9)
TARGET_CRS = "EPSG:3577"  # GDA94 / Australian Albers; metre-based gradients.
DEFAULT_RESOLUTION_M = 250
DEFAULT_MAP_CELL_M = 2000
NODATA = -9999.0

BANDS = [
    ("very_low_gradient", 0.0, 3.0),
    ("low_gradient", 3.0, 8.0),
    ("moderate_gradient", 8.0, 15.0),
    ("steep", 15.0, 25.0),
    ("very_steep", 25.0, float("inf")),
]

SANITY_POINTS = {
    # Intentionally broad ranges: these checks catch projection/unit/source failures,
    # not local DEM error or urban micro-topography.
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
    p.add_argument("--dem-url", default=DEM_URL)
    p.add_argument("--skip-map", action="store_true")
    return p.parse_args()


def target_grid(src, resolution_m: int):
    left, bottom, right, top = transform_bounds("EPSG:4326", TARGET_CRS, *BBOX_WGS84, densify_pts=21)
    width = math.ceil((right - left) / resolution_m)
    height = math.ceil((top - bottom) / resolution_m)
    transform = from_origin(left, top, resolution_m, resolution_m)
    return width, height, transform


def read_dem(url: str, resolution_m: int):
    with rasterio.Env(GDAL_HTTP_MULTIRANGE="YES", GDAL_DISABLE_READDIR_ON_OPEN="EMPTY_DIR"):
        with rasterio.open(url) as src:
            width, height, transform = target_grid(src, resolution_m)
            with WarpedVRT(
                src,
                crs=TARGET_CRS,
                transform=transform,
                width=width,
                height=height,
                resampling=Resampling.bilinear,
                nodata=NODATA,
            ) as vrt:
                dem = vrt.read(1, masked=True).astype("float32")
    return dem, transform


def slope_degrees(dem: np.ma.MaskedArray, resolution_m: int) -> np.ma.MaskedArray:
    data = dem.filled(np.nan).astype("float64")
    dz_dy, dz_dx = np.gradient(data, resolution_m, resolution_m)
    slope = np.degrees(np.arctan(np.hypot(dz_dx, dz_dy))).astype("float32")
    mask = np.ma.getmaskarray(dem) | ~np.isfinite(slope)
    return np.ma.array(slope, mask=mask)


def band_name(value: float) -> str:
    for name, lo, hi in BANDS:
        if lo <= value < hi:
            return name
    return "unknown"


def write_raster(path: Path, arr: np.ma.MaskedArray, transform, units: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    profile = {
        "driver": "GTiff",
        "height": arr.shape[0],
        "width": arr.shape[1],
        "count": 1,
        "dtype": "float32",
        "crs": TARGET_CRS,
        "transform": transform,
        "nodata": NODATA,
        "compress": "deflate",
        "tiled": True,
        "blockxsize": 512,
        "blockysize": 512,
    }
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(arr.filled(NODATA).astype("float32"), 1)
        dst.update_tags(units=units, source=DEM_URL)


def sample_points(dem_path: Path):
    results = {}
    failures = []
    with rasterio.open(dem_path) as ds:
        from rasterio.warp import transform
        for name, spec in SANITY_POINTS.items():
            xs, ys = transform("EPSG:4326", ds.crs, [spec["lon"]], [spec["lat"]])
            val = float(next(ds.sample([(xs[0], ys[0])]))[0])
            ok = spec["elev_min"] <= val <= spec["elev_max"]
            results[name] = {"elevation_m": round(val, 1), "expected_range_m": [spec["elev_min"], spec["elev_max"]], "pass": ok}
            if not ok:
                failures.append(name)
    return results, failures


def aggregate_map_grid(dem, slope, transform, map_cell_m: int, resolution_m: int):
    factor = max(1, round(map_cell_m / resolution_m))
    h = (dem.shape[0] // factor) * factor
    w = (dem.shape[1] // factor) * factor
    d = dem[:h, :w].filled(np.nan).reshape(h // factor, factor, w // factor, factor)
    s = slope[:h, :w].filled(np.nan).reshape(h // factor, factor, w // factor, factor)
    elev_mean = np.nanmean(d, axis=(1, 3))
    slope_median = np.nanmedian(s, axis=(1, 3))
    slope_p90 = np.nanpercentile(s, 90, axis=(1, 3))
    steep_share = np.nanmean(s >= 15.0, axis=(1, 3))
    valid_share = np.mean(np.isfinite(d), axis=(1, 3))
    return factor, elev_mean, slope_median, slope_p90, steep_share, valid_share


def map_geojson(path: Path, transform, factor, resolution_m, metrics):
    elev_mean, slope_median, slope_p90, steep_share, valid_share = metrics
    features = []
    cell = factor * resolution_m
    # Decimated analytical grid: retain cells with >=50% valid terrain. Geometry is
    # exact to the derived grid, not to parcel/buildability boundaries.
    for row in range(elev_mean.shape[0]):
        y_top = transform.f - row * cell
        y_bottom = y_top - cell
        for col in range(elev_mean.shape[1]):
            if valid_share[row, col] < 0.5 or not np.isfinite(slope_p90[row, col]):
                continue
            x_left = transform.c + col * cell
            x_right = x_left + cell
            p90 = float(slope_p90[row, col])
            features.append({
                "type": "Feature",
                "geometry": {"type": "Polygon", "coordinates": [[[x_left,y_bottom],[x_right,y_bottom],[x_right,y_top],[x_left,y_top],[x_left,y_bottom]]]},
                "properties": {
                    "elevation_mean_m": round(float(elev_mean[row,col]),1),
                    "slope_median_deg": round(float(slope_median[row,col]),2),
                    "slope_p90_deg": round(p90,2),
                    "steep_share_ge15": round(float(steep_share[row,col]),3),
                    "terrain_band": band_name(p90),
                    "analysis_resolution_m": resolution_m,
                    "map_cell_m": cell,
                    "geometry_quality": "derived_regular_grid",
                },
            })
    fc = {"type": "FeatureCollection", "name": "terrain_buildability_v1", "crs": {"type":"name","properties":{"name":"EPSG:3577"}}, "features": features}
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(fc, separators=(",", ":")), encoding="utf-8")
    return len(features)


def main():
    args = parse_args()
    if args.map_cell_m % args.resolution_m:
        raise SystemExit("--map-cell-m must be an integer multiple of --resolution-m")

    args.out.mkdir(parents=True, exist_ok=True)
    print(f"Reading authoritative DEM at {args.resolution_m} m analytical resolution")
    dem, transform = read_dem(args.dem_url, args.resolution_m)
    slope = slope_degrees(dem, args.resolution_m)

    dem_path = args.out / f"elevation_{args.resolution_m}m.tif"
    slope_path = args.out / f"slope_degrees_{args.resolution_m}m.tif"
    write_raster(dem_path, dem, transform, "metres")
    write_raster(slope_path, slope, transform, "degrees")

    sanity, failures = sample_points(dem_path)
    summary = {
        "source": args.dem_url,
        "source_product": "Geoscience Australia SRTM-derived 1 Second DEM / ga_srtm_dem1sv1_0",
        "source_nominal_resolution": "1 arc-second (~30 m)",
        "analysis_crs": TARGET_CRS,
        "analysis_resolution_m": args.resolution_m,
        "map_cell_m": args.map_cell_m,
        "terrain_band_basis": "P90 slope within map cell",
        "bands_degrees": [{"name": n, "min": lo, "max": None if math.isinf(hi) else hi} for n,lo,hi in BANDS],
        "sanity_points": sanity,
        "valid_elevation_pixels": int(dem.count()),
        "valid_slope_pixels": int(slope.count()),
        "elevation_min_m": round(float(dem.min()),1),
        "elevation_max_m": round(float(dem.max()),1),
        "slope_p50_deg": round(float(np.ma.median(slope)),2),
        "slope_p95_deg": round(float(np.nanpercentile(slope.filled(np.nan),95)),2),
    }

    if not args.skip_map:
        factor, em, sm, sp90, ss, vs = aggregate_map_grid(dem, slope, transform, args.map_cell_m, args.resolution_m)
        count = map_geojson(MAP_OUT / "terrain_buildability.geojson", transform, factor, args.resolution_m, (em,sm,sp90,ss,vs))
        summary["map_features"] = count

    (args.out / "terrain_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    if failures:
        raise SystemExit("Terrain sanity checks failed: " + ", ".join(failures))
    print("Terrain sanity checks passed")


if __name__ == "__main__":
    main()
