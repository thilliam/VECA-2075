#!/usr/bin/env python3
"""Build XYZ PNG terrain tiles from accepted 250 m EXP-002 rasters.

Keeps 10 km GeoJSON as the overview/click-summary layer while exposing the
continuous 250 m elevation/slope surface at closer zooms without creating
hundreds of thousands of polygons.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path

import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.windows import from_bounds
from rasterio.vrt import WarpedVRT

ROOT = Path(__file__).resolve().parents[1]
TERRAIN_DIR = ROOT / "experiments" / "EXP-002-habitat-resource-screening" / "data" / "terrain"
OUT = ROOT / "maps" / "poc-006" / "data" / "tiles"
BBOX = (137.8, -39.25, 154.1, -9.9)
WEB_MERCATOR = "EPSG:3857"
R = 6378137.0
WORLD = 2 * math.pi * R
HALF = WORLD / 2

SLOPE_STOPS = [(0,"#f1f8e9"),(3,"#dcedc8"),(8,"#fff9c4"),(15,"#ffcc80"),(25,"#ef9a9a"),(40,"#b71c1c")]
ELEV_STOPS = [(0,"#f7f7f7"),(250,"#d9e6b8"),(750,"#b39b72"),(1500,"#8d6e63"),(2200,"#5d4037")]
BAND_COLOURS = [(0,3,"#e8f5e9"),(3,8,"#c8e6c9"),(8,15,"#fff59d"),(15,25,"#ffb74d"),(25,1e9,"#e57373")]


def hexrgb(h):
    h=h.lstrip('#'); return np.array([int(h[i:i+2],16) for i in (0,2,4)],dtype=float)


def colour_ramp(values, stops):
    out=np.zeros(values.shape+(4,),dtype=np.uint8)
    valid=np.isfinite(values)
    if not np.any(valid): return out
    v=values[valid]
    rgb=np.empty((v.size,3),dtype=float)
    for i,(lo,c0) in enumerate(stops):
        hi,c1 = stops[min(i+1,len(stops)-1)]
        m=(v>=lo) & ((v<hi) if i<len(stops)-1 else True)
        if not np.any(m): continue
        a=hexrgb(c0); b=hexrgb(c1)
        t=np.zeros(np.count_nonzero(m)) if hi==lo else np.clip((v[m]-lo)/(hi-lo),0,1)
        rgb[m]=a+(b-a)*t[:,None]
    out[valid,:3]=np.clip(rgb,0,255).astype(np.uint8)
    out[valid,3]=210
    return out


def colour_bands(values):
    out=np.zeros(values.shape+(4,),dtype=np.uint8)
    valid=np.isfinite(values)
    for lo,hi,c in BAND_COLOURS:
        m=valid & (values>=lo) & (values<hi)
        out[m,:3]=hexrgb(c).astype(np.uint8); out[m,3]=210
    return out


def lonlat_to_tile(lon,lat,z):
    n=2**z
    x=int((lon+180.0)/360.0*n)
    lat=max(min(lat,85.05112878),-85.05112878)
    y=int((1-math.asinh(math.tan(math.radians(lat)))/math.pi)/2*n)
    return x,y


def tile_bounds_3857(x,y,z):
    n=2**z; size=WORLD/n
    left=-HALF+x*size; right=left+size
    top=HALF-y*size; bottom=top-size
    return left,bottom,right,top


def read_tile(vrt,x,y,z):
    bounds=tile_bounds_3857(x,y,z)
    window=from_bounds(*bounds,transform=vrt.transform)
    a=vrt.read(1,window=window,out_shape=(256,256),masked=True,boundless=True,resampling=Resampling.bilinear)
    return a.filled(np.nan).astype("float32")


def save_png(path,rgba):
    path.parent.mkdir(parents=True,exist_ok=True)
    Image.fromarray(rgba,"RGBA").save(path,optimize=True)


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--min-zoom",type=int,default=6)
    p.add_argument("--max-zoom",type=int,default=9)
    p.add_argument("--terrain-dir",type=Path,default=TERRAIN_DIR)
    p.add_argument("--out",type=Path,default=OUT)
    args=p.parse_args()
    elev=args.terrain_dir/"elevation_250m.tif"; slope=args.terrain_dir/"slope_degrees_250m.tif"
    for path in (elev,slope):
        if not path.exists(): raise SystemExit(f"Missing {path}; run python tools/build_terrain_screen.py first")

    with rasterio.open(elev) as eds, rasterio.open(slope) as sds, \
         WarpedVRT(eds,crs=WEB_MERCATOR,resampling=Resampling.bilinear) as evrt, \
         WarpedVRT(sds,crs=WEB_MERCATOR,resampling=Resampling.bilinear) as svrt:
        total=0
        for z in range(args.min_zoom,args.max_zoom+1):
            x0,y1=lonlat_to_tile(BBOX[0],BBOX[1],z); x1,y0=lonlat_to_tile(BBOX[2],BBOX[3],z)
            count=(x1-x0+1)*(y1-y0+1); done=0
            print(f"Zoom {z}: {count:,} candidate tiles")
            for x in range(x0,x1+1):
                for y in range(y0,y1+1):
                    s=read_tile(svrt,x,y,z); e=read_tile(evrt,x,y,z)
                    if not np.isfinite(s).any() and not np.isfinite(e).any(): continue
                    save_png(args.out/"bands"/str(z)/str(x)/f"{y}.png",colour_bands(s))
                    save_png(args.out/"slope"/str(z)/str(x)/f"{y}.png",colour_ramp(s,SLOPE_STOPS))
                    save_png(args.out/"elevation"/str(z)/str(x)/f"{y}.png",colour_ramp(e,ELEV_STOPS))
                    done+=1; total+=1
            print(f"  wrote {done:,} land/intersecting tiles per mode")
    print(f"Terrain tile build complete: {total:,} spatial tiles x 3 modes -> {args.out}")

if __name__=="__main__": main()
