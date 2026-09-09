# VECA layered map POC-001

This POC proves the first interactive map surface for VECA-2075.

## What it proves

- MapLibre GL JS pan/zoom interaction.
- Grouped layer toggles.
- Semantic zoom: regional features appear before local assets.
- 2026–2075 time-horizon filtering.
- Existing / committed / planned / VECA-scenario filtering and distinct styling.
- Region jump controls for SEQ, Central Coast, New England, Canberra, Wagga/Albury and Gippsland.
- Clickable assets with a right-side evidence / interpretation panel.
- A layer catalogue separate from rendering code.

## What the data is

The hospital and tertiary-education records are a spatially enabled POC subset of the existing government-intent corpus, principally:

- `domains/government-intent/data/derived/anchor_assets_seed.csv`
- `domains/government-intent/data/derived/education_assets_seed.csv`

Coordinates are POC display coordinates and should not yet be treated as authoritative facility geometries.

The current-rail and VECA-HSR lines are intentionally simplified POC geometry. They prove line-layer behaviour, status styling and time filtering only. Production transport rendering should use the existing authoritative east-coast extracts already in the repository, including:

- `data/derived/transport/ga_rail_east.geojson`
- `data/derived/transport/ga_major_roads_east.geojson`

Those files are too large to push directly into the browser as the normal VECA serving model.

## Run locally

From the repository root:

```bash
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/maps/poc-001/
```

A small HTTP server is preferable to opening `index.html` directly because future POC layers will be loaded as separate resources.

## Current architecture

```text
VECA research / derived data
        |
        v
 small POC spatial feature pack
        |
        v
 MapLibre GL JS
   |         |
 layer UI   evidence panel
```

This is deliberately the smallest runnable slice. It does not establish the production serving architecture.

## Next architecture step

The next map increment should introduce a geospatial serving boundary instead of expanding `data.js` indefinitely:

```text
VECA corpus / ingest
        |
        v
 canonical spatial entities
        |
        +---- PostGIS -------- dynamic/queryable layers
        |
        +---- PMTiles -------- large mostly-static layers
                  |
                  v
         vector tiles / viewport
                  |
                  v
       MapLibre GL + deck.gl
```

Priority conversion candidates are the existing Geoscience Australia rail and major-road GeoJSONs. The browser should request only visible tiles, never the full 60–90 MB source files.

## Pinned design rule

A VECA asset is not a marker, and a transport corridor is not a polyline. They are VECA entities that may have geometry. Rendering is a view over those entities; provenance, status, time horizon and scenario class remain properties of the underlying entity/evidence model.
