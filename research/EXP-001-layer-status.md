# EXP-001 layer status

**Updated:** 9 September 2026  
**Purpose:** distinguish source discovery, materialised data and analytical completeness. A script or seed file is not the same thing as a completed layer.

This file remains in legacy `research/` pending safe domain migration. Root `PROJECT_STATUS_AND_ROADMAP.md` is the canonical cross-project status.

| Layer | Current status | Notes / remaining work |
|---|---|---|
| Population — SA2 | **complete for EXP-001** | 1,844 QLD/NSW/ACT/VIC SA2s; ERP history + 2024–25 components; state validation. |
| Population — 1 km grid | **complete for base source** | Authoritative raster source/checksum preserved; later clipping/rendering is map work. |
| Roads — national/state highways | **represented / materialised** | Corrected GA east-coast extraction exists with state-scope filtering. Large GeoJSON should be tiled for browser use. |
| Rail — foundation geometry | **represented / materialised** | Corrected GA east-coast extraction exists; large GeoJSON should be tiled for browser use. |
| Rail freight utilisation | **active** | NFDH/ARTC evidence understood; broader utilisation/capacity still needs materialisation. |
| Road utilisation/capacity | **active** | Heavy-vehicle/traffic-count enrichment remains. Capacity/bottlenecks matter, not only geometry. |
| Airport current activity | **represented** | Current major-airport activity captured. |
| Airport history | **parked** | BITRE workbook extraction failed because source delivery was unreliable. Does not block current work. |
| Ports — activity | **represented** | Melbourne, Botany, Brisbane and broader container context seeded. |
| Ports — inland catchments | **active** | Catchment/container-flow detail remains. |
| Intermodal terminals | **represented / expanding** | Brisbane, Bomen/RiFL, Parkes/Goobang seeded; expand selectively. |
| HSR/faster-rail evidence | **strong / represented** | 1991→current lineage, cost/study evidence and obstacle register established. Evidence only; no VECA route. |
| Recent/committed transport capital | **represented / active** | Needs broader non-double-counted census and dependency/overlap handling. |
| Energy/REZ/transmission | **represented** | AEMO 2026 ISP transmission seed established. Generator/storage/substation/major-load asset extraction remains. |
| Water systems | **represented / active** | SEQ, Sydney, Canberra, Melbourne, Wagga, Albury, Goulburn seeded. Toowoomba/Darling Downs, New England, Hunter/coastal and sustainable-yield/augmentation comparison remain. |
| Industry/logistics | **represented / active** | Western Sydney, Parkes and Wagga structured. Broader QLD/Hunter/VIC/ACT coverage remains. |
| Government intent / future capital | **represented / active** | Regional plans, health, government land, universities/VET and school-growth signals now structured. |
| Interactive map | **POC complete** | `maps/poc-001/` proves layered evidence interaction. Production tiling/canonical spatial serving remains later work. |

## Interpretation

EXP-001 has achieved its main research purpose: the inherited system is coherent enough that cross-domain structures are visible and EXP-002 can proceed without waiting for exhaustive asset completeness.

Remaining EXP-001 work is **enrichment**, especially where it materially changes candidate survival or later cost analysis.

## Guardrail

Do not turn `represented` into `complete` merely because a seed CSV exists. Conversely, do not block habitat/resource screening while chasing exhaustive national asset inventories.

EXP-001 remains free of a VECA-preferred HSR route, candidate-city ranking or composite settlement score.