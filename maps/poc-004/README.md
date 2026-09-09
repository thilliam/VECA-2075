# POC-004 — Energy & Capital Geography

POC-004 integrates the map work through POC-003 with the next inherited/planned-system evidence families.

## Adds

- AEMO 2026 ISP transmission-project anchors.
- AEMO 2026 indicative REZ boundary GIS, parsed directly from the published KMZ when available.
- NSW declared and Victorian proposed REZ status anchors, kept separate from AEMO's indicative geometry.
- urban water-system anchors for SEQ, Sydney, Canberra-Queanbeyan, Melbourne/South-Central, Wagga, Albury and Goulburn.
- spatially meaningful government growth-land / planning-optionality anchors.
- major recent/committed infrastructure-project anchors.
- intermodal freight nodes.
- restored health/regional-anchor assets.
- restored university/TAFE assets.
- the full POC-003 population lenses, settlements, satellite and land-use context.
- the POC-002 rail and road foundations.

## Spatial honesty

AEMO's indicative REZ polygons are direct-source geometry and are labelled accordingly. State REZ anchors remain separate because state declaration/proposal status is a different fact from AEMO's indicative planning boundary.

Transmission projects, water systems, capital projects and planning-optionality records do **not** yet all have authoritative line/polygon geometry in the VECA corpus. POC-004 therefore uses explicit representative anchors. Click a feature to see `geometry_quality` and its spatial note.

Do not interpret a representative point as a project alignment, REZ legal boundary, water service area, local connection capacity, statutory planning boundary, parcel boundary or land-availability claim.

## Build

From the repo root:

```bash
python tools/build_map_poc004.py
```

The builder calls/reuses POC-003, which in turn reuses POC-002 transport derivatives where present. The first POC-004 run also downloads AEMO's small indicative-REZ KMZ into an ignored local cache; later runs reuse it. If the external GIS download fails, the build continues with an empty AEMO polygon layer and the state REZ anchors remain usable.

Generated files are intentionally ignored by Git, including:

- `maps/poc-004/data/transmission_projects.geojson`
- `maps/poc-004/data/energy_zones.geojson`
- `maps/poc-004/data/aemo_rez_boundaries.geojson`
- `maps/poc-004/data/water_systems.geojson`
- `maps/poc-004/data/planning_optionality.geojson`
- `maps/poc-004/data/capital_projects.geojson`
- `maps/poc-004/data/freight_intermodal.geojson`
- `maps/poc-004/data/spatial-gaps.json`
- `maps/poc-004/data/manifest.json`
- `maps/poc-004/data/cache/`

## Run

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/maps/poc-004/
```

## Current architecture lesson

POC-004 is the first map increment where the browser can juxtapose human geography, physical context, transport, social infrastructure, energy, water, freight, public/private capital and planning optionality. It is still a POC serving several large GeoJSON files directly.

Roads alone are ~46 MB in the current derivative. Production-scale work should move large networks and spatial surfaces to tiled delivery while retaining the corpus/assurance records as authority.

`maps/layers/catalogue.json` is now the durable inventory of mapped layers, assurance state, geometry quality and serving mode.

## Next high-value additions

1. authoritative transmission project alignments where publishable GIS exists;
2. DNSP substations / capacity / forecast constraints from Essential Energy, Ausgrid, Endeavour, Energex, Ergon and Victorian DNSPs;
3. airports once the planned BITRE import is materialised and reconciled;
4. statutory government land / growth-area polygons replacing representative anchors;
5. water-system asset/transfer/augmentation geometry;
6. terrain/slope, protected land, flood, bushfire and future-climate surfaces for the Stage-2 survival screen.
