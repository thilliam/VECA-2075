# Existing imported-dataset assurance migration — completion record

**Date:** 2026-09-09  
**Scope:** all 25 source-bearing derived datasets that existed when dataset-level assurance was introduced, plus their 3 generated QA/support outputs.

## Result

All 25 current source-bearing datasets have now been moved out of the undifferentiated legacy assurance backlog.

- **4 exhaustive imports are reconciled** against independently established source inventories.
- **19 canonical curated syntheses are provenance-reconciled** under explicit selection/scope contracts.
- **2 legacy curated snapshots are deprecated and non-canonical**; they are retained for history but must not feed new map/data work.
- **3 support/QA outputs** remain registered and inherit assurance from their upstream datasets.
- **0 current derived files are unregistered.**
- **0 canonical curated datasets have unresolved structural provenance.**

`reconciled` and `provenance_reconciled` deliberately mean different things. An exhaustive import claims a defined source universe and must reconcile every identity. A curated synthesis intentionally selects evidence and therefore proves provenance and scope rather than inventing a false claim that it contains every possible real-world entity.

## Exhaustive imports

| Dataset | Result | Independent source test | Remaining limitation |
|---|---:|---|---|
| `data/derived/population_sa2_east.csv` | **1,844 / 1,844 reconciled** | Separate ABS SA2 Regional Population 2025 FeatureServer identity set; all `erp_2025` values also compared | Historical ERP years and migration-component fields have not all received a second independent field-by-field verification |
| `data/derived/transport/ga_major_roads_east.geojson` | **75,581 / 75,581 reconciled** | Independent GA National Roads OBJECTID inventory for operational National/State Highways in QLD/NSW/ACT/VIC within the extraction envelope | Identity is complete; geometry/attribute QA is not an engineering-grade verification and road capacity/congestion evidence remains separate |
| `data/derived/transport/ga_rail_east.geojson` | **26,808 / 26,808 reconciled** | Independent GA Foundation Rail OBJECTID inventory for NSW/VIC/QLD source-jurisdiction records within the extraction envelope | Identity is complete; geometry/attribute QA is not exhaustive and physical geometry does not establish capacity/utilisation |
| `domains/energy/data/derived/transmission_projects_seed.csv` | **21 / 21 reconciled** | Independent reconstruction of the scoped QLD/NSW/VIC transmission inventory from AEMO 2026 ISP Table 1 | Project/status field verification remains sampled; generation/storage assets are a separate outstanding layer |

The machine-readable ABS/GA results are in `assurance/direct_import_reconciliation.json`; source-level manifests are in `assurance/manifests/`.

## Canonical curated syntheses — provenance reconciled

These files intentionally do **not** claim to be exhaustive inventories of their broad real-world classes. Every included row now has resolvable provenance and each file has an explicit selection claim, policy and completeness test in `assurance/curated_dataset_contracts.json`.

| # | Dataset | Records | Selection meaning |
|---:|---|---:|---|
| 1 | `data/derived/energy_zones_seed.csv` | 23 | Enumerated named source families: NSW 5 declared REZs, Victoria 6 proposed 2025 REZs, Queensland 12 historical 2024 potential REZs |
| 2 | `data/derived/hsr_corridor_obstacles_seed.csv` | 7 | Selected high-consequence engineering/physical constraints from reviewed studies |
| 3 | `data/derived/hsr_studies_seed.csv` | 8 | Major-study evidence-lineage bibliography, not every HSR proposal ever published |
| 4 | `data/derived/hsr_study_evidence_seed.csv` | 22 | Selected decision-relevant findings/metrics from reviewed studies |
| 5 | `data/derived/infrastructure_projects_seed.csv` | 13 | Selected major inherited/committed capital projects, not the complete infrastructure pipeline |
| 6 | `data/derived/transport/intermodal_terminals_seed.csv` | 5 | Selected strategic intermodal anchors encountered in current corridor research |
| 7 | `data/derived/transport_system_metrics_seed.csv` | 20 | Selected transport metrics useful to whole-system comparison |
| 8 | `domains/government-intent/data/derived/anchor_assets_seed.csv` | 19 | Selected high-consequence public/service anchors in studied regions |
| 9 | `domains/government-intent/data/derived/education_assets_seed.csv` | 20 | Selected major university/TAFE/VET anchors, not all campuses/providers |
| 10 | `domains/government-intent/data/derived/government_land_education_seed.csv` | 14 | Selected government land/education assets with optionality significance |
| 11 | `domains/government-intent/data/derived/health_capital_optionality_seed.csv` | 6 | Selected health programs/masterplans exposing relocation/renewal choices |
| 12 | `domains/government-intent/data/derived/health_capital_signals_v1.csv` | 11 | Selected health-capital/service-planning signals |
| 13 | `domains/government-intent/data/derived/land_zoning_optionality_seed.csv` | 6 | Selected planning/zoning/future-growth mechanisms preserving or constraining options |
| 14 | `domains/government-intent/data/derived/regional_growth_baselines_seed.csv` | 10 | Official baseline assumptions for the currently scoped comparison regions |
| 15 | `domains/government-intent/data/derived/regional_health_assets_seed.csv` | 6 | Selected major regional health anchors with material inherited/committed capital |
| 16 | `domains/government-intent/data/derived/regional_plan_assumptions_v1.csv` | 8 | Selected decision-relevant assumptions from reviewed regional plans |
| 17 | `domains/government-intent/data/derived/school_growth_seed.csv` | 6 | Selected growth/new-school/reservation signals; explicitly not all schools |
| 18 | `domains/industry/data/derived/industry_logistics_nodes_seed.csv` | 3 | Selected major industry/logistics precinct anchors |
| 19 | `domains/water/data/derived/water_systems_seed.csv` | 7 | Selected functional water systems in currently researched regions; geographic gaps remain explicit |

## Deprecated legacy snapshots

The following duplicate legacy-tree datasets remain for historical traceability only. They are now `legacy_deprecated`, `canonical=false`, and `map_relevance=false`:

1. `domains/government_intent/data/derived/future_capital_optionality_seed.csv` — 9 rows
2. `domains/government_intent/data/derived/government_intent_seed.csv` — 9 rows

All new government-intent work belongs under `domains/government-intent/`.

## Support outputs

Registered but not treated as independent source imports:

1. `data/derived/population_state_validation.csv`
2. `data/derived/transport/ga_major_roads_east_summary.csv`
3. `data/derived/transport/ga_rail_east_summary.csv`

## Defects found and corrected during migration

### 1. AEMO transmission completeness defect

The pre-assurance transmission seed contained 17 of 21 scoped AEMO 2026 ISP east-coast transmission projects. Four missing projects were identified and added:

- Gladstone Project
- Switching Station Near Wondalga
- Gippsland Offshore Wind Transmission
- Central to North Queensland Reinforcement Stage 2

The set now reconciles 21/21.

### 2. Queensland REZ aggregation hid entity-level completeness

The energy-zone seed originally represented the Queensland 2024 Roadmap's 12 potential REZs as one aggregate row. That is inadequate for an entity-level map. The 12 source-listed zones are now individual rows and explicitly labelled historical 2024 planning evidence rather than current committed zones.

### 3. Government-intent provenance gaps

Four canonical government-intent datasets carried human-readable source notes but did not expose canonical source IDs per row. Canonical `source_ids` were added and missing source-register entries were created for the underlying health/regional-plan evidence.

### 4. CSV field-alignment defect

Four sparse rows in `regional_growth_baselines_seed.csv` had one too few delimiters. They looked plausible in text form, but a CSV parser shifted later fields left and effectively lost their provenance. The rows were repaired and the structural audit now reports zero canonical curated provenance failures.

### 5. Multi-source provenance schema support

Industry/logistics and water datasets already used semicolon-separated `source_ids`; the first audit only recognised singular `source_id`. The audit was corrected to validate both singular and multi-source provenance rather than falsely labelling these rows unsourced.

### 6. Airport evidence clarified

A BITRE airport extractor/workflow exists, but no current airport derived dataset is present. Airports therefore remain `ingestion_planned`, not falsely counted among existing imported evidence.

## Permanent controls added

- `assurance/dataset_register.json` — exhaustive current derived-file register.
- `assurance/curated_dataset_contracts.json` — scope contracts for selective evidence syntheses.
- `tools/audit_current_datasets.py` — row/feature and provenance audit across every derived file.
- `tools/reconcile_direct_imports.py` — independent identity reconciliation for ABS/GA direct imports.
- `tools/sync_curated_assurance.py` — applies curated scope/provenance contracts.
- `tools/validate_dataset_register.py` — fails unregistered/missing/invalid-state datasets.
- `tools/validate_source_assurance.py --strict` — source-manifest reconciliation gate.
- `.github/workflows/validate-assurance.yml` — permanent PR/main assurance validation gate.
- regression tests retain the explicit 27-expected/23-accounted failure case and now pin the curated/exhaustive dataset-state invariants.

## What this does not mean

This migration proves the state of the **data VECA has already imported**. It does not prove VECA has discovered every important external source family or every real-world asset. The source-coverage register remains the separate mechanism for that question.

The next ingestion wave should therefore proceed from the identified source backlog — particularly electricity distribution capacity, conventional rail/freight investment and capacity, data-centre/compute pipelines, private infrastructure capital, regional planning bodies, industrial/logistics development and digital connectivity — while every new dataset enters through these assurance controls from day one.
