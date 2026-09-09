# Maps

Spatial outputs live here. The map is an evidence-inspection surface over VECA entities; it is not the analytical model or source of truth.

## Current state

`poc-001/` is a working layered-map explorer. It already proves:
- MapLibre pan/zoom;
- grouped layer toggles;
- semantic zoom;
- time/status/scenario filtering;
- regional navigation;
- clickable feature evidence/interpretation panels.

The POC currently uses a small spatially enabled subset of the corpus, including hospital and tertiary-education/government-intent records. Coordinates in the POC are display-oriented unless explicitly documented as authoritative geometry.

Large authoritative Geoscience Australia road and rail extracts already exist under legacy `data/derived/transport/`. They are too large for normal whole-file browser loading.

## Next map increment

Do **not** rebuild the POC simply because a new research layer exists. Add map work when it improves evidence inspection.

The next architecture step should introduce tiled/viewport delivery (for example PostGIS/vector tiles and/or PMTiles) for large authoritative layers and later EXP-002 climate/terrain/land surfaces.

## Relationship to analysis

The intended progression is:

`authoritative evidence -> structured VECA entities/layers -> analytical joins/screens -> map views`

A future Regional Anchor Cluster layer, when explicitly resumed, would be a **derived analytical overlay** on top of the existing evidence layers. It must not replace or hide the component assets.

The first EXP-002 survival map should likewise preserve separate climate, water, hazard, terrain and land evidence rather than rendering one unexplained suitability colour.

See `poc-001/README.md` for run instructions and current architecture.