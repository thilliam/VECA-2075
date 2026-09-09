# POC-005 — Systems Capacity & Digital

POC-005 is an additive map increment over POC-004. It was triggered by new datasets arriving through the assurance/ingestion process on `main`.

## New layers

- **Compute / data-centre campuses** from `domains/digital-compute/data/derived/compute_campus_pipeline_seed.csv`.
  - Symbol size reflects published MW where available.
  - Geometry is a locality-level representative anchor, not parcel/building geometry.
- **Digital backbone routes** from `domains/digital-connectivity/data/derived/digital_backbone_routes_seed.csv`.
  - Routes are generalised between published endpoints.
  - They do not imply exact fibre alignment, local on-ramps or available spare capacity.
- **Conventional rail capacity / investment** from `domains/transport/data/derived/conventional_rail_capacity_investment_seed.csv`.
  - Generalised corridor overlays sit over the authoritative operational rail reference layer.
  - Completed, active and preserved future corridors remain distinct through source status fields.
- **Port systems / catchment role** from `domains/industry/data/derived/port_catchments_seed.csv`.
  - Points represent the port system and its hinterland evidence, not berth or estate polygons.
- **Distribution-network capacity signals** from `domains/energy/data/derived/distribution_capacity_signals_seed.csv`.
  - These are curated strategic signals and representative regional anchors.
  - They must not be interpreted as exact substation locations or guaranteed connection headroom.
- **Expanded regional water systems** from the enlarged `domains/water/data/derived/water_systems_seed.csv`.
  - Adds Toowoomba/Darling Downs, Lower Hunter, Tamworth and Armidale/Guyra/Uralla to the seven POC-004 systems.

## Deliberately not mapped yet

Two important direct imports arrived but are not spatially ready:

- `domains/energy/data/derived/aemo_generation_information_east_july_2026.csv`
- `domains/energy/data/derived/ausgrid_substation_capacity_demand_2025.csv`
- `domains/energy/data/derived/ergon_zone_substation_load_summary_2025-26.csv`

They contain valuable asset/capacity evidence but the current derived tables do not carry authoritative coordinates. POC-005 does **not** geocode hundreds of asset names heuristically. They should enter the map after an authoritative or independently reconciled spatial join.

This distinction is important: **not mapped does not mean not ingested**.

## Build

From the repo root:

```bash
python tools/build_map_poc005.py
```

The builder reuses locally generated POC-004 derivatives when available. This preserves a validated/cached AEMO REZ build rather than forcing a new external download. It mirrors the POC-004 derivatives into `maps/poc-005/data/` and then adds POC-005 derivatives.

Generated products are ignored by Git.

## Run

```bash
python -m http.server 8000
```

Open:

```text
http://localhost:8000/maps/poc-005/
```

## Geometry doctrine

Every new POC-005 feature carries a `geometry_quality` and explanatory `geometry_note`.

Current POC-005 geometry classes include:

- `representative_locality_anchor`
- `generalised_endpoint_corridor`
- `generalised_corridor`
- `representative_port_anchor`
- `representative_region_anchor`
- `representative_system_anchor`

These are visual/analytical context until authoritative geometry replaces them.

## Support-system lesson

The assurance system is now successfully producing new datasets faster than the map can discover them manually. The next support improvement should connect `assurance/dataset_register.json` to a machine-readable **spatial readiness** state so each dataset can be classified as:

- already mapped;
- map-ready with authoritative geometry;
- map-ready with explicitly permitted representative geometry;
- blocked on a spatial join;
- non-spatial / not a map candidate.

A CI/report should then flag new map candidates that have no catalogue entry, and mapped layers whose dataset/provenance records have drifted. This turns the current manual repo sweep into a controlled pipeline.
