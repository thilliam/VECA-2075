# POC-002 — Real East Coast Spatial Foundation

POC-002 replaces the embedded demonstration geometry used by POC-001 with generated map derivatives built from the existing VECA corpus.

## What is real in this POC

- **Rail:** `data/derived/transport/ga_rail_east.geojson` (Geoscience Australia foundation rail extraction). POC-002 keeps operational railway geometry, removes siding/tramline noise where classified, and simplifies coordinates for browser display.
- **Roads:** `data/derived/transport/ga_major_roads_east.geojson` (existing east-coast major-road extraction), simplified for browser display.
- **Regional population/planning:** `domains/government-intent/data/derived/regional_growth_baselines_seed.csv`, spatially joined through `maps/spatial_registry.csv`.
- **Health / anchor assets:** `domains/government-intent/data/derived/anchor_assets_seed.csv`, spatially joined through the registry.
- **Universities / TAFE:** `domains/government-intent/data/derived/education_assets_seed.csv`, spatially joined through the registry.

Transport geometry remains derived from the authoritative source layer rather than hand-drawn map lines. Point locations in `maps/spatial_registry.csv` currently include a mixture of representative regional centroids and POC-verified approximate asset points; `geometry_quality` makes that distinction explicit.

## Build and run

From the repository root:

```bash
python tools/build_map_poc002.py
python -m http.server 8000
```

On Windows, `py` can be used instead of `python`.

Open:

```text
http://localhost:8000/maps/poc-002/
```

The build produces ignored derivatives under `maps/poc-002/data/`:

- `rail.geojson`
- `roads.geojson`
- `population.geojson`
- `infrastructure.geojson`
- `education.geojson`
- `manifest.json`
- `spatial-gaps.json`

## Why there is a build step

The committed foundation files are roughly tens of megabytes each and contain much more geometry/property detail than the browser needs. POC-002 proves a reproducible **source → normalized map derivative → browser** path without committing a second copy of those large datasets.

This is an intermediate architecture. Once the interaction/data model is stable, the transport layers should move to vector-tile/PMTiles/PostGIS delivery so the browser receives only the current viewport and zoom detail.

## Spatial entity contract introduced here

Mapped corpus objects now have a common minimum set:

- `entity_id`
- `name`
- `domain`
- geometry
- `geometry_quality`
- `status`
- `valid_from`
- jurisdiction/source fields where available
- original corpus attributes, including `veca_interpretation` and source URL where present

The spatial registry is deliberately separate from the UI. Missing geometry is reported by the builder in `spatial-gaps.json`; it should be fixed in the corpus/registry rather than hard-coded in JavaScript.

## Current limitation: population geometry

The regional-plan population layer is **not yet a population-density surface**. It places real plan baseline/forecast values at representative regional points. The repo's ABS population work remains authoritative evidence, but a useful dense population layer needs spatial geometry (SA2 boundaries or a processed population grid) and is the next population-specific map task.

## POC-002 acceptance tests

1. Real operational rail displays across the east-coast extraction envelope.
2. Major roads can be toggled independently and appear only from their semantic zoom threshold.
3. Browser data is generated from corpus files, not embedded feature definitions.
4. Health and education objects retain stable corpus IDs and evidence fields.
5. Clicking a transport segment reports source classification/status where present.
6. Clicking an asset exposes its corpus interpretation/source.
7. Missing spatial registry entries are reported automatically.
8. Large generated derivatives are not committed to Git.
