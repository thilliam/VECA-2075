# EXP-002 Terrain / Buildability Screen v1

**Status:** implementation in progress  
**Stage:** EXP-002 physical survival / habitat-resource screen  
**Purpose:** establish a reproducible, evidence-first terrain constraint layer before climate, land, water and hazard layers are combined.

## Research question

Which parts of the QLD/NSW/ACT/VIC study area are structurally easy, moderate or difficult from a broad terrain-gradient perspective?

This is **not** a parcel-scale engineering feasibility study and it is **not** a settlement score.

## Authoritative source

Primary elevation source family:

- **Publisher:** Geoscience Australia
- **Product:** SRTM-derived 1 Second Digital Elevation Models Version 1.0 (`ga_srtm_dem1sv1_0` in Digital Earth Australia)
- **Nominal source resolution:** 1 arc-second, approximately 30 m
- **Units:** metres
- **Licence:** Creative Commons Attribution 4.0
- **Access:** Geoscience Australia / Digital Earth Australia public data services
- **Persistent identifier:** GA 72759

The GA/DEA product contains DEM, smoothed DEM (DEM-S) and hydrologically enforced DEM (DEM-H) surfaces. v1 uses the DEA-hosted elevation GeoTIFF path documented in DEA examples. The exact source asset used by the build is recorded in `terrain_summary.json`.

Why this source: it provides nationally consistent ground-surface topography across the entire VECA study area and is published by the national authoritative mapping agency. Higher-resolution LiDAR/ELVIS data can later refine shortlisted regions, but using mixed local resolutions at the broad-screen stage would create inconsistent regional comparisons.

## Resolution strategy

Three resolution levels are deliberately separated:

1. **Source truth:** ~30 m GA SRTM-derived elevation.
2. **Analytical surface:** default 250 m in Australian Albers (`EPSG:3577`). Continuous elevation and slope are retained as GeoTIFFs.
3. **Map/summary surface:** default 2 km regular grid for browser inspection and broad regional statistics.

The 2 km map grid is a view of the continuous analytical surface. It is not the analytical authority.

The default 250 m surface is intended to capture regional terrain morphology without pretending that a continental-scale screen can answer subdivision, foundation, cut/fill, landslip or road-gradient engineering questions. Resolution is configurable so sensitivity can be tested.

## Derived slope

Slope is derived in a metre-based projected CRS:

`rise/run -> atan -> degrees`

Using Australian Albers avoids the latitude-dependent error that would result from calculating slope directly in geographic degrees.

Continuous slope in degrees is retained separately from elevation.

## Descriptive terrain/buildability bands

v1 uses the **P90 slope within each 2 km map cell** to produce a descriptive terrain-gradient class:

| P90 slope | Class | Meaning in v1 |
|---|---|---|
| 0–<3° | very low gradient | Broadly flat terrain signal |
| 3–<8° | low gradient | Generally gentle terrain signal |
| 8–<15° | moderate gradient | Increasing terrain/civil complexity signal |
| 15–<25° | steep | Material terrain constraint signal |
| >=25° | very steep | Strong terrain constraint signal |

These are **transparent analytical/display bands, not universal engineering cutoffs**. Continuous values remain available underneath and threshold sensitivity should be tested before any later candidate comparison.

Why P90 rather than only mean slope: a cell containing a flat valley floor plus steep surrounding slopes should not look equivalent to uniformly flat country. The map derivative also carries median slope and the share of analytical pixels >=15°.

## What terrain does not tell us

A flat cell is not automatically developable. Separate Stage-2 evidence must still address:

- floodplain and drainage;
- protected/environmentally sensitive land;
- agricultural value;
- native title / ILUA context;
- water availability and augmentation;
- future climate and fire risk;
- soil/geology/geotechnical conditions;
- existing urbanisation and land ownership;
- infrastructure/service accessibility.

Likewise, steep terrain is a cost/constraint signal, not an automatic exclusion. Existing cities and transport corridors demonstrate that difficult terrain can be engineered where system value justifies it.

## Sanity checks

The build contains broad elevation range checks at known terrain contexts including Brisbane, Sydney, Melbourne, Wagga Wagga, Katoomba and Mount Kosciuszko. These are designed to catch projection, unit, source-selection and gross sampling failures.

A successful pipeline must also satisfy:

- elevation maximum is physically plausible for mainland eastern Australia;
- slope is bounded to 0–90 degrees;
- low-gradient inland plains visibly differ from Great Dividing Range / alpine terrain;
- coastal urban regions do not become universally mountainous due to projection errors;
- nodata/ocean cells are excluded rather than classified as flat land.

## Outputs

`tools/build_terrain_screen.py` produces:

- `elevation_<resolution>m.tif` — continuous analytical elevation;
- `slope_degrees_<resolution>m.tif` — continuous analytical slope;
- `terrain_summary.json` — provenance, parameters, sanity checks and summary statistics;
- `maps/poc-006/data/terrain_buildability.geojson` — coarse browser/summary grid.

Large generated rasters and map derivatives are not intended to become hand-maintained repository truth.

## Build

```bash
python -m pip install -r tools/requirements-terrain.txt
python tools/build_terrain_screen.py
```

Optional sensitivity example:

```bash
python tools/build_terrain_screen.py --resolution-m 500 --map-cell-m 4000
```

## Next after v1

1. Run and inspect v1 across the full study area.
2. Compare at least one alternate analytical resolution to identify scale-sensitive areas.
3. Add terrain to POC-006.
4. Add structural land constraints and then climate/hazard layers as separate evidence families.
5. Use higher-resolution ELVIS/LiDAR only when Stage 3 produces a deliberately small candidate set requiring local refinement.
