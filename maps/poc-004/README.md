# POC-004 — Energy & Capital Geography

POC-004 integrates the map work through POC-003 with the next inherited/planned-system evidence families.

## Adds

- AEMO 2026 ISP transmission-project anchors.
- NSW declared and Victorian proposed REZ anchors.
- major recent/committed infrastructure-project anchors.
- intermodal freight nodes.
- restored health/regional-anchor assets.
- restored university/TAFE assets.
- the full POC-003 population lenses, settlements, satellite and land-use context.
- the POC-002 rail and road foundations.

## Spatial honesty

Transmission projects and REZs do **not** yet have authoritative line/polygon geometry in the VECA corpus. POC-004 therefore uses explicit representative anchors from `spatial_overrides.csv`. Click a feature to see `geometry_quality` and its spatial note.

Do not interpret a representative point as the project alignment, REZ boundary, local connection capacity, or land availability.

The next energy geometry task is to replace these anchors with authoritative project alignments / zone polygons where publishable source services exist.

## Build

From the repo root:

```bash
python tools/build_map_poc004.py
```

The builder calls/reuses POC-003, which in turn reuses POC-002 transport derivatives where present.

Generated files are intentionally ignored by Git:

- `maps/poc-004/data/transmission_projects.geojson`
- `maps/poc-004/data/energy_zones.geojson`
- `maps/poc-004/data/capital_projects.geojson`
- `maps/poc-004/data/freight_intermodal.geojson`
- `maps/poc-004/data/spatial-gaps.json`
- `maps/poc-004/data/manifest.json`

## Run

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/maps/poc-004/
```

## Current architecture lesson

POC-004 is the first map increment where the browser can juxtapose human geography, physical context, transport, social infrastructure, energy, freight and capital intent. It is still a POC serving several large GeoJSON files directly.

Roads alone are ~46 MB in the current derivative. Production-scale work should move large networks and spatial surfaces to tiled delivery while retaining the corpus/assurance records as authority.

## Next high-value additions

1. authoritative transmission alignments and REZ polygons;
2. DNSP substations / capacity / forecast constraints as those P0 assurance sources are ingested;
3. airports once the planned BITRE import is materialised and reconciled;
4. government land / growth-area geometry;
5. water-system assets and transfer/augmentation geography;
6. terrain/slope, protected land, flood, bushfire and future-climate surfaces for the Stage-2 survival screen.
