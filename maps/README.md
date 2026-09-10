# Maps

Spatial outputs live here. `layers/` contains the canonical map-layer catalogue and small map-definition artefacts appropriate for Git. The map is a view over VECA evidence entities; it is not the analytical model itself.

## Interactive mapping lineage

- `poc-001/` — first runnable layered explorer: toggles, semantic zoom, time/status filtering, regional navigation and feature evidence panels.
- `poc-002/` — real east-coast spatial foundation: Geoscience Australia rail/major roads plus corpus-backed health, education and regional anchors; introduced reproducible map derivatives and spatial-gap reporting.
- `poc-003/` — population, settlements and landscape: ABS SA2 density/growth, ABS LGA population/growth, ranked settlements/functional centres, satellite and ABARES land use.
- `poc-004/` — energy and capital geography: AEMO transmission/REZ, major capital, freight, water, planning optionality and restored social infrastructure over the earlier spatial/population foundations. The current builder includes the AEMO browser-download attempt, local KMZ cache fallback and robust KML parsing/diagnostics.
- `poc-005/` — systems capacity and digital: compute/data-centre campuses, digital backbone corridors, conventional-rail capacity/investment, port systems, DNSP capacity/augmentation signals and expanded regional water systems.

## Layer catalogue and spatial readiness

`layers/catalogue.json` records mapped evidence families, source/assurance state, geometry quality and serving mode. New durable map layers should be registered there rather than existing only inside frontend code.

`../assurance/spatial_readiness.json` records whether important datasets are:

- mapped with authoritative or representative geometry;
- map-ready but not yet rendered;
- blocked on an authoritative spatial join; or
- non-spatial.

`tools/validate_spatial_readiness.py` checks mapped readiness records against the catalogue and referenced datasets, and is part of assurance CI.

This prevents a critical interpretation error: **not mapped does not mean not ingested**. For example, AEMO generation/storage, Ausgrid capacity/demand and Ergon substation-load evidence can exist in the corpus while still being blocked from authoritative map use by missing spatial joins.

## Spatial serving boundary

Large authoritative source files should not be loaded wholesale into the browser in production. Current POCs deliberately prove the data and interaction model first. Roads alone are roughly 46 MB after POC simplification.

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
- `authoritative_AEMO_indicative_boundary`
- `representative_project_anchor`
- `representative_zone_anchor`
- `representative_locality_anchor`
- `representative_system_anchor`
- `generalised_endpoint_corridor`
- `generalised_corridor`

A representative project, capacity signal, route or zone is not an authoritative alignment, boundary, local connection-capacity claim or land-availability claim.

## Next map work

The next major analytical map family is Stage-2 survival screening: future climate, terrain/slope/buildability, protected/agricultural/native-title constraints, stronger flood/bushfire evidence and water-feasibility context. Authoritative spatial joins for currently blocked energy-capacity datasets can proceed in parallel, but should not delay Stage 2.
