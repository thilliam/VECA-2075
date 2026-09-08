# EXP-001 layer status

**Purpose:** distinguish source discovery, tooling, materialised data and analytical completeness. A script or seed file is not the same thing as a completed layer.

| Layer | Source discovery | Reproducible extraction / structured data | QA | EXP-001 status | Notes |
|---|---|---|---|---|---|
| Population — SA2 | complete | complete | complete | **complete** | 1,844 QLD/NSW/ACT/VIC SA2s, ERP history + 2024–25 components; ASGS Edition 3. |
| Population — 1 km grid | complete | raw authoritative raster preserved | source/checksum QA | **complete for base layer** | Derived clipping/rendering still belongs to map build. |
| Roads — national/state highways | complete | materialised; corrected extraction rerun in progress | state-scope QA identified/fixed | **active** | Earlier rectangular extraction leaked SA; latest extractor enforces QLD/NSW/ACT/VIC. |
| Rail — foundation geometry | complete | materialised; corrected extraction rerun in progress | length/gauge/subtype QA implemented | **active** | Earlier rectangular extraction included SA source records; latest extractor excludes them. |
| Rail freight utilisation | complete | structured extraction not yet materialised | coverage limitations documented | **active** | NFDH strongest on ARTC/interstate network; do not label as complete intrastate freight. |
| Road utilisation | complete | not yet materialised | counter-coverage limitations documented | **active** | NFDH Harmonised Traffic Counts/heavy-vehicle share is next enrichment layer. |
| Airport current activity | complete | structured seed metrics | source cross-check | **represented** | 2025 domestic RPT volumes captured for major capitals/routes. |
| Airport 1985–2025 history | complete | extractor active | pending successful materialisation | **active** | BITRE large workbook source has slow delivery; resilient extractor is running. |
| Ports — activity | complete | structured seed metrics | source cross-check | **represented** | Melbourne, Botany, Brisbane metrics seeded; catchment detail still needed. |
| Ports — inland catchments | complete | not yet materialised | limitations understood | **active** | NFDH catchment/container products exclude some domestic flows. |
| Intermodal terminals | active | initial structured seed | node-by-node evidence | **active** | Brisbane BMT/Acacia Ridge, Bomen/RiFL, Parkes/Goobang seeded. |
| HSR/faster-rail historical evidence | strong | study/cost/obstacle seeds | evidence/proposal split enforced | **active / deepening** | 1991→current lineage identified; 2013 appendices remain a major evidence mine. |
| Recent/committed transport capital | strong | structured project seed | status/value-scope discipline | **active** | Needs broader census and overlap/dependency handling before Capital Gravity analysis. |
| Energy/REZ | strong | structured seed | known zone/status QA corrected | **represented** | Victorian names corrected; NSW zone declaration separated from project status. |
| Water | early | not materialised coherently | — | **not complete** | Major future EXP-001 layer. |
| Industrial/logistics | early | partial via ports/intermodal/project evidence | — | **not complete** | Needs coherent spatial layer. |

## Status definitions

- **complete** — sufficient authoritative data, materialised and QA'd for EXP-001's current base-map purpose; later refinement can still occur.
- **represented** — enough evidence exists to appear in the first combined map, but the domain is not fully extracted.
- **active** — authoritative sources identified and work is materially underway.
- **not complete** — insufficient coherent data for the first combined map.

## Guardrail

EXP-001 is not complete merely because every row says `represented`. Its completion criterion remains a coherent combined inherited-system map with all required layer classes represented or an explicit documented gap, provenance, status separation, limitations and no smuggled settlement/HSR recommendation.
