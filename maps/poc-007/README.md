# POC-007 — Terrain-only Sydney–Melbourne HST path

POC-007 is a lever-learning experiment. Its purpose is to render one plausible passenger-HST path from Sydney CBD to Melbourne CBD using only the accepted EXP-002 elevation and slope surfaces, then expose what a future alignment optimizer needs to model explicitly.

It is **not** a preferred VECA corridor, a cost estimate, or an engineering design.

## Inputs

Generated locally by EXP-002:

- `experiments/EXP-002-habitat-resource-screening/data/terrain/elevation_250m.tif`
- `experiments/EXP-002-habitat-resource-screening/data/terrain/slope_degrees_250m.tif`

The underlying source is the accepted local Geoscience Australia SRTM-derived 3-second DEM.

No settlement, land-use, hydrology, geology, protected-land, ownership, existing-corridor or economic evidence enters the route solver in v1. Existing VECA layers are available on the map only as visual context.

## v1 algorithm

1. Reproject the accepted elevation/slope surfaces into a Sydney–Melbourne search window.
2. Downsample to a default 2 km search grid.
3. Run raster A* from Sydney CBD to Melbourne CBD.
4. Movement resistance combines distance, terrain-following grade and local terrain slope.
5. Lightly smooth the raster centreline to remove obvious stair-step artefacts.
6. Resample the resulting alignment at 1 km intervals against the accepted 250 m surfaces.
7. Build an indicative vertical rail profile, smoothed over terrain and constrained to a default 3.5% maximum grade envelope.
8. Compare indicative rail elevation with ground elevation and classify each interval heuristically.
9. Merge adjacent intervals with the same construction mode into clickable map segments.

This deliberately separates **horizontal path search** from **vertical structure inference**. Later versions should solve these jointly.

## Construction-mode thresholds

These are exposed POC levers, not engineering standards:

- tunnel: indicative rail profile 20 m or more below ground;
- cutting: 3–20 m below ground;
- at grade: within about ±3 m of ground;
- embankment: 3–12 m above ground;
- bridge / elevated: 12 m or more above ground.

The classifications indicate the type of intervention the simple profile appears to require. They do not establish constructability.

## Build

From the repository root, after EXP-002 terrain has been built:

```bash
python -m pip install -r tools/requirements-terrain.txt
python tools/build_hst_terrain_path.py
python -m http.server 8000
```

Open:

`http://localhost:8000/maps/poc-007/`

Generated, gitignored outputs:

- `maps/poc-007/data/hst_terrain_segments.geojson`
- `maps/poc-007/data/hst_terrain_summary.json`

POC-007 reuses the POC-006 terrain tiles for the optional terrain backdrop. If those are missing, run `python tools/build_terrain_tiles.py`.

## What to inspect

The first run is intended to answer questions such as:

- Does a distance+slope least-cost path produce a believable broad Sydney–Melbourne corridor?
- Where does the simple 3.5% vertical profile require tunnels, cuttings, embankments and viaducts?
- Does the horizontal route zig-zag enough that minimum curve radius must become an early hard constraint?
- Are the structure thresholds too eager or too reluctant?
- How strongly do the route and structure shares change when grade, slope resistance or smoothing parameters change?

Those sensitivities are more important than declaring the v1 route "best".

## Known missing levers

- horizontal minimum curve radius / transition curves;
- explicit vertical-curve constraints and sustained-grade envelopes;
- bridge span/height and tunnel portal/length logic;
- cut/fill cross-sections and earthworks balancing;
- rivers/floodplains and geology;
- protected land / settlement / land ownership;
- existing corridor reuse;
- stations and network-access objectives;
- construction and operating cost functions;
- alternative-path generation rather than one winner.

Future alignment work should move toward a constrained 3D search/optimization problem rather than progressively adding arbitrary raster penalties.
