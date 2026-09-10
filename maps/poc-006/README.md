# POC-006 — Terrain Survival Screen

POC-006 is the first Stage-2 map increment. It adds terrain/buildability evidence without converting terrain into a settlement score.

## Inputs and analytical truth

Preferred v1 source: local Geoscience Australia SRTM-derived 3-second DEM (~90 m), stored outside Git under `research/source/terrain/3secSRTM_DEM/`.

`tools/build_terrain_screen.py` creates:

- continuous elevation at the configured analytical resolution (default 250 m);
- continuous slope in degrees at the same analytical resolution;
- a 10 km overview grid carrying mean elevation, median slope, P90 slope, share of analytical pixels >=15 degrees and a descriptive terrain band.

The GeoTIFF elevation/slope surfaces are the analytical products. The 10 km GeoJSON is only an overview/click-summary representation.

## Multiscale map delivery

`tools/build_terrain_tiles.py` reads the accepted 250 m GeoTIFFs and creates ignored local XYZ PNG tile pyramids for:

- descriptive slope bands;
- continuous slope;
- elevation.

POC-006 displays the 10 km vector summary at east-coast scale and switches to the tiled 250 m-derived surface from zoom 6 onward. The default tile pyramid ends at zoom 9, where Web Mercator pixels are roughly 300 m at the equator and therefore close to the analytical resolution; further browser zoom can overzoom those tiles without claiming additional source precision.

## Build

After the local GA 3-second source is present:

```bash
python -m pip install -r tools/requirements-terrain.txt
python tools/build_terrain_screen.py
python tools/build_terrain_tiles.py
```

The terrain screen build does not require POC-004 to succeed. Reference layers inherited from earlier POCs are optional context rather than a terrain-build dependency.

Run:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/maps/poc-006/`.

## Interpretation guardrails

A low-gradient terrain cell is not automatically developable. Flood, protected land, agriculture, native title/ILUA, water, climate/fire, soils/geology, existing urbanisation, ownership and servicing remain separate evidence layers.

A steep cell is not automatically excluded. It indicates likely higher terrain/civil complexity and requires later local investigation if a region survives the broad screen.

## Known v1 limitations

- The source is a national ~90 m DEM resampled to a 250 m regional analytical surface; it is not parcel-scale terrain.
- The study-area processing extent is a mainland bounding extent covering QLD/NSW/ACT/VIC. Ocean/nodata is excluded; exact state-border summary clipping can be added later.
- 10 km cell statistics remain useful for regional comparison and click details; the closer raster view shows the underlying spatial pattern rather than inventing finer vector summaries.
- Higher-resolution ELVIS/LiDAR should be reserved for shortlisted regions where local engineering questions justify it.
