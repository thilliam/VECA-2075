# Maps

Spatial outputs live here. `layers/` contains the canonical map-layer catalogue and small map-definition artefacts appropriate for Git. The map is a view over VECA evidence entities; it is not the analytical model itself.

## Interactive mapping lineage

- `poc-001/` — first runnable layered explorer: toggles, semantic zoom, time/status filtering, regional navigation and feature evidence panels.
- `poc-002/` — real east-coast spatial foundation: Geoscience Australia rail/major roads plus corpus-backed health, education and regional anchors; introduced reproducible map derivatives and spatial-gap reporting.
- `poc-003/` — population, settlements and landscape: ABS SA2 density/growth, ABS LGA population/growth, ranked settlements/functional centres, satellite and ABARES land use.
- `poc-004/` — energy and capital geography: AEMO transmission/REZ, major capital, freight, water, planning optionality and restored social infrastructure over the earlier spatial/population foundations. The current builder includes the AEMO browser-download attempt, local KMZ cache fallback and robust KML parsing/diagnostics.
- `poc-005/` — systems capacity and digital: compute/data-centre campuses, digital backbone corridors, conventional-rail capacity/investment, port systems, DNSP capacity/augmentation signals and expanded regional water systems.
- `poc-006/` — first Stage-2 survival-screen map: terrain/buildability from GA 1-second elevation, preserving continuous elevation/slope analysis separately from a coarse 10 km browser grid and descriptive P90-slope bands.

## Layer catalogue and spatial readiness

`layers/catalogue.json` records mapped evidence families, source/assurance state, geometry quality and serving mode. New durable map layers should be registered there rather than existing only inside frontend code.

`../assurance/spatial_readiness.json` records whether important datasets are mapped, map-ready, blocked on an authoritative spatial join or non-spatial. `tools/validate_spatial_readiness.py` checks mapped readiness records against the catalogue and referenced datasets, and is part of assurance CI.

This prevents a critical interpretation error: **not mapped does not mean not ingested**. For example, AEMO generation/storage, Ausgrid capacity/demand and Ergon substation-load evidence can exist in the corpus while still being blocked from authoritative map use by missing spatial joins.

## Analytical surface vs map representation

POC-006 makes another distinction explicit: **mapped resolution is not analytical resolution**.

For terrain v1, the source is ~30 m, the default continuous analytical elevation/slope surfaces are 250 m, and the browser view is a 10 km grid carrying summary statistics. The coarse grid must not be treated as the terrain dataset itself.

The same pattern should be used for future climate/hazard/resource rasters: retain an appropriate analytical surface, then serve a fit-for-purpose representation by zoom/use case.

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

GeoJSON remains appropriate for small POC/diagnostic derivatives. Large roads, rail, population, terrain and future hazard/resource layers should move to tiled delivery.

## Geometry-quality rule

Every spatial representation must distinguish source truth from map convenience. Examples include:

- `authoritative_source_simplified`
- `authoritative_AEMO_indicative_boundary`
- `derived_regular_grid_from_authoritative_raster`
- `representative_project_anchor`
- `representative_zone_anchor`
- `representative_locality_anchor`
- `representative_system_anchor`
- `generalised_endpoint_corridor`
- `generalised_corridor`

A representative project, capacity signal, route or zone is not an authoritative alignment, boundary, local connection-capacity claim or land-availability claim.

## Next map work

Complete and inspect the POC-006 terrain full-source build, then add the remaining Stage-2 evidence families separately: protected/agricultural/native-title constraints, future climate, stronger flood/bushfire evidence and water-feasibility context. Authoritative spatial joins for currently blocked energy-capacity datasets can proceed in parallel, but should not delay Stage 2.
