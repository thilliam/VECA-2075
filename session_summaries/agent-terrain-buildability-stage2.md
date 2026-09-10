# Session Summary — Stage 2 Terrain / Buildability

## 1. Session identity and scope

Implemented the first EXP-002 Stage-2 structural survival-screen slice: authoritative elevation -> derived slope -> descriptive terrain/buildability bands -> sanity checks -> POC-006 map layer.

## 2. What I actually did

- Pinned Geoscience Australia / Digital Earth Australia `ga_srtm_dem1sv1_0` as the national authoritative elevation source family.
- Chose the documented DEM-S public GeoTIFF asset for regional slope derivation.
- Added `tools/build_terrain_screen.py` and terrain-specific dependencies.
- Preserved continuous elevation and continuous slope as separate analytical GeoTIFFs at configurable resolution (default 250 m).
- Added a separate 10 km browser/summary grid carrying mean elevation, median slope, P90 slope, >=15 degree share and descriptive terrain class.
- Added known-location elevation sanity checks and 0–90 degree slope bounds.
- Added synthetic slope/band/aggregation regression tests and terrain CI.
- Added POC-006 terrain map with band, P90-slope and mean-elevation display modes.
- Added source profile, methodology, acceptance note and map catalogue entry.

## 3. Important reasoning outcomes

- Source resolution, analytical resolution and browser/display resolution are different concepts and must remain explicit.
- Terrain bands are display/analytical descriptors, not engineering cutoffs.
- P90 slope is used in the coarse cell because mean slope alone hides cells with material steep terrain surrounding flatter areas.
- Flat terrain is not synonymous with developable land; flood, land/environment, water, climate, soils/geology and servicing remain independent layers.
- High-resolution ELVIS/LiDAR should be used later for shortlisted regions rather than mixing local resolutions into the broad national comparison.

## 4. Current repository status

Implementation is on `feature/exp002-terrain-buildability-001`. Full-source terrain data remains intentionally generated/ignored rather than committed. The data product should not be called accepted until `terrain_buildability_acceptance_v1.md` passes on a full run.

## 5. Incomplete work / backlog

- Run the full GA/DEA source build in a network-enabled local environment.
- Review `terrain_summary.json` sanity results and POC-006 visually.
- Optionally compare 250 m against a coarser sensitivity run.
- Add exact state-boundary clipping if jurisdiction-level terrain statistics become useful.
- Move to tiled raster/vector serving when survival-map raster families become large enough to justify it.

## 6. Potential overlaps or conflicts

Terrain should remain separate from upcoming protected/agricultural/native-title, flood/fire, climate and water-feasibility layers. Do not combine them into a score during Stage 2.

## 7. Canonical knowledge

Promote the analytical-vs-display-resolution distinction and the rule that descriptive terrain classes never replace continuous evidence.

## 8. Suggested reconciliation checks

- Confirm the PR is based on current reconciled main.
- Confirm terrain CI passes.
- Confirm full-source build uses the pinned GA/DEA source rather than a substitute.
- Confirm POC-006 renders WGS84 browser geometry and excludes nodata/ocean.

## 9. Compact handover

- Terrain is the first implemented Stage-2 screen.
- GA/DEA 1-second source family is pinned.
- Default analysis is continuous 250 m elevation + slope.
- Browser grid is 10 km and not analytical truth.
- Bands are based on P90 slope: <3, 3–8, 8–15, 15–25, >=25 degrees.
- Sanity checks cover major flat/urban, tableland and alpine contexts.
- Synthetic regression CI validates math without requiring the large DEM.
- Full-source run remains the final data acceptance gate.
- POC-006 is the terrain inspection surface.
- Next Stage-2 family should remain separate from terrain rather than collapsing into a score.
