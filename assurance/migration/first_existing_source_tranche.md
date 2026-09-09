# Existing-source assurance migration — tranche 001

Date: 2026-09-09

Purpose: move existing VECA evidence through the source-assurance system without retroactively declaring plausible-looking datasets complete.

## 1. AEMO 2026 ISP transmission seed — assurance failure found

Source: `ENERGY-AEMO-ISP-2026`  
Derived dataset: `domains/energy/data/derived/transmission_projects_seed.csv`

An independent inventory was rebuilt from AEMO 2026 ISP Executive Summary Table 1 before comparing it with the VECA seed.

For the scoped QLD/NSW/VIC **transmission** inventory (excluding SA/Tasmania projects and separately classified NSW distribution-project rows):

- expected from source: **21**
- present in VECA dataset: **17**
- unresolved/missing: **4**

Missing source-listed projects:

1. Gladstone Project
2. Switching Station Near Wondalga
3. Gippsland Offshore Wind Transmission
4. Central to North Queensland Reinforcement (Stage 2)

This is exactly the failure class the assurance system was introduced to catch. The existing seed looked coherent but was about 19% incomplete against this defined source inventory.

The corresponding manifest is `assurance/manifests/ENERGY-AEMO-ISP-2026.json` and intentionally records `verification.state = failed` until the four entities are resolved.

## 2. ABS SA2 ERP layer — ingestion exists, independent inventory still required

Source: `POP-ABS-SA2-ERP-2001-2025`  
Derived dataset: `data/derived/population_sa2_east.csv`

Existing extraction evidence says the VECA layer contains **1,844 SA2 records** across:

- ACT: 134
- NSW: 642
- QLD: 546
- VIC: 522

The extractor already validates duplicate SA2 codes, state scope, missing ERP values and state-level totals. However, those counts are produced by the extraction itself. They therefore **cannot** satisfy the independent-inventory rule.

Required before manifest/reconciliation:

- independently count the target-state SA2 inventory from the official ABS 2024-25 SA2 cube or SA2 geospatial web service;
- compare the independent code set, not only the count, with `population_sa2_east.csv`;
- record missing/extra codes explicitly;
- cross-check state ERP totals and a sample of SA2 values directly against ABS.

Until that is done, the source must not move to `reconciled` or `verified` merely because 1,844 rows exist.

## 3. Geoscience Australia east-coast rail — ingestion exists, independent API count still required

Source: `TRANSPORT-GA-EAST-RAIL`  
Derived dataset: `data/derived/transport/ga_rail_east.geojson`

The derived QA summary contains **26,808** features (Railway 22,452; Rail Siding 3,296; Tramline 1,060), and the extractor checks duplicate service object IDs.

Again, this feature count comes from the extracted dataset itself. It is not an independent source inventory.

Required before manifest/reconciliation:

- query the authoritative Geoscience Australia Railway_Lines service independently with the same extraction envelope using `returnCountOnly=true`;
- separately count and subtract explicitly out-of-scope `source_jurisdiction=SA` features, matching the extractor's scope rule;
- compare the resulting authoritative expected count to the GeoJSON feature count;
- compare the authoritative OBJECTID set to the extracted OBJECTID set, so equal counts cannot hide substitutions;
- sample operational status, gauge, owner and geometry against direct service responses.

Until this independent API inventory exists, the source remains unverified.

## Next order

1. Add the four missing AEMO transmission projects and rerun that reconciliation.
2. Establish the independent ABS source code inventory and create its manifest.
3. Establish the independent GA rail count/OBJECTID inventory and create its manifest.
4. Repeat the pattern across roads, airports, Inland Rail and the remaining existing Stage-1 evidence before the large new non-government ingestion wave.
