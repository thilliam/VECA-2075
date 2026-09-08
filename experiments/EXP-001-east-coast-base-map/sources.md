# EXP-001 Sources

Authoritative metadata is held in `research/source_register.csv`; this file maps registered sources to EXP-001 layers and records experiment-specific cautions.

| Source ID | EXP-001 layer(s) | Use | Material caution |
|---|---|---|---|
| `SRC-ABS-POP-2024` | 1 population | SA2 Estimated Resident Population baseline | Native geography predates ASGS Edition 4; do not silently join to 2026 SA2 polygons. |
| `SRC-ABS-ASGS-2026` | 1 population / base geography | Latest ABS statistical boundaries | Requires concordance if used with 2024 ERP. |
| `SRC-BITRE-YB-2025` | 2 transport | Nationally consistent transport/infrastructure statistics | Statistical tables are not necessarily map geometry. |
| `SRC-NFDH-2026` | 2 transport / 8 logistics | Freight networks and operational evidence | Verify underlying dataset dates and operator coverage per product. |
| `SRC-IA-MCAP-2025` | 3–5 capital/infrastructure | National infrastructure pipeline context | $242b pipeline is not strategic value and not a settlement score. |
| `SRC-QLD-CRR-2026` | 4 committed infrastructure | Cross River Rail status/cost | Current completion expectation is 2029; retain source date. |
| `SRC-INLAND-PROGRESS-2026` | 2–4 freight rail | Inland Rail status by section | Do not imply the full Melbourne–Brisbane corridor has one delivery status. |
| `SRC-NSW-METROWEST-2026` | 4 committed infrastructure | Metro West delivery status and signed packages | $11.5b is value of four contracts, not total project cost. |
| `SRC-NSW-CWO-2026` | 4 / 6 energy | Central-West Orana transmission delivery | Construction status applies to transmission project, not every generator in the REZ. |
| `SRC-NSW-REZ-2026` | 6 energy | NSW declared REZ geography/index | Declaration does not mean every project is committed. |
| `SRC-NSW-HUMELINK-2026` | 4 / 6 energy | HumeLink route, status and project value | Network project value and eventual consumer cost are different concepts. |
| `SRC-VIC-METROTUNNEL-2026` | 3 recent infrastructure | Major completed rail investment | Completed in 2025; belongs in recent-capital layer, not committed pipeline. |
| `SRC-VIC-NEL-2026` | 4 committed infrastructure | North East Link construction status | Cost not populated until a clean current project-value source is registered. |
| `SRC-VIC-TRANS-2025` | 5 / 6 planned energy | Proposed Victorian REZs/transmission planning | Proposed is not committed. |
| `SRC-QLD-REZ-2024` | 5 / 6 historical planning | Legacy Queensland 12-REZ roadmap | Superseded/modified framework; never render as current committed REZs. |
| `SRC-QLD-ENERGY-AMEND-2025` | 6 energy governance | Evidence of Queensland framework change | Legislation describes framework change; project geography still requires current extraction. |

## Current derived datasets

- `data/derived/infrastructure_projects_seed.csv` — first normalized major-project records.
- `data/derived/energy_zones_seed.csv` — first normalized REZ/planning records with explicit status distinctions.

These are seed datasets, not comprehensive east-coast coverage.
