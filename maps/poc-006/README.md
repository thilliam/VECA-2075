# POC-006 — Terrain Survival Screen

POC-006 is the first Stage-2 map increment. It adds terrain/buildability evidence over the inherited-system map without converting terrain into a settlement score.

## Inputs and analytical truth

Source family: Geoscience Australia SRTM-derived 1-second elevation (`ga_srtm_dem1sv1_0`), accessed through Digital Earth Australia.

`tools/build_terrain_screen.py` creates:

- continuous elevation at the configured analytical resolution (default 250 m);
- continuous slope in degrees at the same analytical resolution;
- a coarse browser grid (default 10 km) carrying mean elevation, median slope, P90 slope, share of analytical pixels >=15 degrees and a descriptive terrain band.

The GeoTIFF elevation/slope surfaces are the analytical products. The 10 km GeoJSON is only a map/summary representation.

## Terrain modes

The POC can display the same map cells as:

- descriptive P90 slope bands;
- continuous P90 slope;
- continuous mean elevation.

The bands are transparent display classes, not engineering cutoffs.

## Build

```bash
python -m pip install -r tools/requirements-terrain.txt
python tools/build_map_poc004.py
python tools/build_terrain_screen.py
```

Run:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/maps/poc-006/`.

## Interpretation guardrails

A low-gradient terrain cell is not automatically developable. Flood, protected land, agriculture, native title/ILUA, water, climate/fire, soils/geology, existing urbanisation, ownership and servicing remain separate evidence layers.

A steep cell is not automatically excluded. It indicates likely higher terrain/civil complexity and requires later local investigation if a region survives the broad screen.

## Known v1 limitations

- The continental product is intentionally resampled for broad regional analysis; it is not parcel-scale terrain.
- v1 uses the DEA-hosted smoothed DEM-S asset from the GA 1-second product family for slope derivation.
- The study-area processing extent is a mainland bounding extent covering QLD/NSW/ACT/VIC. Ocean/nodata is excluded; exact state-border summary clipping can be added if needed for jurisdiction statistics.
- Browser delivery uses a coarse regular grid rather than raster/vector tiles. Production serving remains a later concern.
- Higher-resolution ELVIS/LiDAR should be reserved for shortlisted regions where local engineering questions justify it.
