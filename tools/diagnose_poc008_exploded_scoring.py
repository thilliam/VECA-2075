#!/usr/bin/env python3
"""Diagnostic: test POC-008 scoring after exploding multipart evidence.

This reuses the current POC-008 reader/rules, but converts MultiPolygon evidence
into individual Polygon rows before route scoring. Broad multipart envelopes were
shown to create false bbox hits and pathological GEOS work for short route segments.

The route-level kilometre summary printed here is NON-EXCLUSIVE evidence overlap:
several evidence polygons/classes can cover the same route distance. Do not treat
those totals as a partition of the route. Segment-level evidence is the primary QA
output from this diagnostic.
"""
from __future__ import annotations

import time

import geopandas as gpd

import build_land_corridor_screen as poc


def explode_for_scoring(gdf: gpd.GeoDataFrame, name: str) -> gpd.GeoDataFrame:
    t = time.perf_counter()
    before = len(gdf)
    multi = int((gdf.geometry.geom_type == "MultiPolygon").sum())
    poc.log(f"{name}: exploding multipart evidence for scoring; {before:,} rows, {multi:,} MultiPolygons")
    out = gdf.explode(index_parts=False, ignore_index=True)
    out = out[out.geometry.notna() & ~out.geometry.is_empty].copy()
    types = out.geometry.geom_type.value_counts().to_dict()
    poc.log(
        f"{name}: explode complete: {before:,} -> {len(out):,} rows in "
        f"{time.perf_counter()-t:,.1f}s; geometry types {types}"
    )
    return out


def main():
    segments = poc.load_route_segments(poc.POC007)
    route = segments.geometry.union_all()
    analysis_clip = route.buffer(50_000)

    poc.log("Loading NSW tenure for exploded-scoring diagnostic")
    nsw = poc.normalize_nsw(
        poc.DEFAULT_NSW_TENURE,
        analysis_clip,
        poc.NSW_TENURE_LAYER,
        safe_polygons=False,
    )
    nsw = explode_for_scoring(nsw, "nsw_tenure")

    poc.log("Loading ABS Mesh Blocks for exploded-scoring diagnostic")
    abs_mb = poc.normalize_abs(poc.DEFAULT_ABS_MB, analysis_clip)
    abs_mb = explode_for_scoring(abs_mb, "abs_meshblocks")

    poc.log("Scoring exploded NSW + ABS polygon parts against POC-007 segments")
    detailed, summary, per_segment, stats = poc.score_route_segments(
        segments,
        {
            "nsw_tenure": nsw,
            "abs_meshblocks": abs_mb,
        },
    )

    print("\n=== DIAGNOSTIC RESULT ===")
    print(f"records: {len(detailed):,}")
    print(f"stats: {stats}")
    print("summary (NON-EXCLUSIVE evidence overlaps; km can sum above route length):")
    print(summary)
    print("\nsegment 313 evidence:")
    evidence = per_segment.get("313", [])
    if evidence:
        for row in evidence:
            print(row)
    else:
        print("  none")


if __name__ == "__main__":
    main()
