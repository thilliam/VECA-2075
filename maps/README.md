# Maps

Spatial outputs live here. `layers/` contains the canonical map-layer catalogue and small map-definition artefacts appropriate for Git.

## Interactive mapping lineage

- `poc-001/` — first runnable layered explorer: toggles, semantic zoom, time/status filtering, regional navigation and feature evidence panels.
- `poc-002/` — real east-coast spatial foundation: Geoscience Australia rail/major roads plus corpus-backed health, education and regional anchors; introduced reproducible map derivatives and spatial-gap reporting.
- `poc-003/` — population, settlements and landscape: ABS SA2 density/growth, ABS LGA population/growth, ranked settlements/functional centres, satellite and ABARES land use.
- `poc-004/` — energy and capital geography: AEMO transmission-project anchors, REZ anchors, major capital projects and intermodal freight, while restoring social infrastructure and retaining POC-003/002 layers.

The map is a view over VECA evidence entities. It is not the analytical model itself.

## Layer catalogue

`layers/catalogue.json` records the current mapped evidence families, source/assurance state, geometry quality and serving mode. New durable map layers should be registered there rather than existing only inside frontend code.

## Spatial serving boundary

Large authoritative source files should not be loaded wholesale into the browser in production. Current POCs deliberately prove the data and interaction model first. Roads alone are ~46 MB after POC simplification.

Target production boundary remains:

```text
VECA corpus + assurance
        |
        v
canonical spatial entities
        |
        +---- PostGIS / API ---- dynamic/queryable layers
        |
        +---- PMTiles ---------- large mostly-static layers
                  |
                  v
         viewport/vector tiles
                  |
                  v
              MapLibre
```

GeoJSON remains appropriate for small POC/diagnostic derivatives. Large roads, rail, population surfaces and future hazard/resource layers should move to tiled delivery.

## Geometry-quality rule

Every spatial representation must distinguish source truth from map convenience. Examples include:

- `authoritative_source_simplified`
- `representative_project_anchor`
- `representative_zone_anchor`
- `approximate_asset_point`
- `UCL_bounds_centre`

A representative project or zone point is not an alignment, boundary, local connection capacity or land-availability claim.
