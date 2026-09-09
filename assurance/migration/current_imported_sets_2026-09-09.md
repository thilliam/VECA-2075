# Current imported-set assurance sweep

**Date:** 2026-09-09  
**Scope:** every current file under `data/derived/**` and `domains/*/data/derived/**`, excluding `.gitkeep`.

This sweep closes a different control gap from the source register: it proves that every dataset currently capable of feeding analysis/map work is visible in the assurance queue.

## Totals

- Derived files discovered: **28**
- Source-bearing imported datasets: **25**
- Generated support/QA outputs: **3**
- Reconciled imported datasets: **1**
- Independent inventory required: **3**
- Source decomposition required: **21**
- Unregistered derived datasets after this sweep: **0**

The canonical machine-readable inventory is `assurance/dataset_register.json`. `tools/validate_dataset_register.py` fails when a derived file exists without a register entry, or a register entry points to a missing file.

## Dataset-by-dataset status

| # | Dataset | Domain | Assurance state | Main next control |
|---:|---|---|---|---|
| 1 | `data/derived/energy_zones_seed.csv` | energy | source decomposition required | Reconcile zones/projects by AEMO/EnergyCo/VicGrid primary inventory. |
| 2 | `data/derived/hsr_corridor_obstacles_seed.csv` | transport | source decomposition required | Reconcile obstacle/evidence families to study tables/pages. |
| 3 | `data/derived/hsr_studies_seed.csv` | transport | source decomposition required | Build independent study bibliography/inventory. |
| 4 | `data/derived/hsr_study_evidence_seed.csv` | transport | source decomposition required | Reconcile evidence rows to each study/page/table. |
| 5 | `data/derived/infrastructure_projects_seed.csv` | cross-domain capital | source decomposition required | Decompose by authoritative project/program source. |
| 6 | `data/derived/population_sa2_east.csv` | population | independent inventory required | Compare 1,844 extracted codes against independent ABS SA2 code set. |
| 7 | `data/derived/transport/ga_major_roads_east.geojson` | transport | independent inventory required | GA API count + feature-ID set against 75,581 extracted features. |
| 8 | `data/derived/transport/ga_rail_east.geojson` | transport | independent inventory required | GA API count + OBJECTID set against 26,808 extracted features. |
| 9 | `data/derived/transport/intermodal_terminals_seed.csv` | transport | source decomposition required | Define operator/authority terminal inventory by region/corridor. |
| 10 | `data/derived/transport_system_metrics_seed.csv` | transport | source decomposition required | Verify metric definitions/completeness source-by-source. |
| 11 | `domains/energy/data/derived/transmission_projects_seed.csv` | energy | **reconciled** | 21/21 AEMO scoped projects; field verification remains sampled. |
| 12 | `domains/government-intent/data/derived/anchor_assets_seed.csv` | government intent | source decomposition required | Split/reconcile health, education and land source families. |
| 13 | `domains/government-intent/data/derived/education_assets_seed.csv` | government intent | source decomposition required | Independent university/TAFE/VET campus inventories. |
| 14 | `domains/government-intent/data/derived/government_land_education_seed.csv` | government intent | source decomposition required | Separate mixed land/education inventories and exclusions. |
| 15 | `domains/government-intent/data/derived/health_capital_optionality_seed.csv` | government intent | source decomposition required | Jurisdiction-by-jurisdiction health capital program inventories. |
| 16 | `domains/government-intent/data/derived/health_capital_signals_v1.csv` | government intent | source decomposition required | Reconcile capital/planning signals to source program lists. |
| 17 | `domains/government-intent/data/derived/land_zoning_optionality_seed.csv` | government intent | source decomposition required | Reconcile state/regional planning and growth-area inventories. |
| 18 | `domains/government-intent/data/derived/regional_growth_baselines_seed.csv` | government intent | source decomposition required | Plan-by-plan geographic coverage and assumption inventory. |
| 19 | `domains/government-intent/data/derived/regional_health_assets_seed.csv` | government intent | source decomposition required | Independent major hospital/health-asset inventories by region. |
| 20 | `domains/government-intent/data/derived/regional_plan_assumptions_v1.csv` | government intent | source decomposition required | Reconcile every assumption to source plan/page/table. |
| 21 | `domains/government-intent/data/derived/school_growth_seed.csv` | government intent | source decomposition required | State education capital/growth program inventories. |
| 22 | `domains/industry/data/derived/industry_logistics_nodes_seed.csv` | industry/logistics | source decomposition required | Regional operator/government/port/intermodal inventories. |
| 23 | `domains/water/data/derived/water_systems_seed.csv` | water | source decomposition required | Utility-by-utility functional system inventory; close known region gaps. |
| 24 | `domains/government_intent/data/derived/future_capital_optionality_seed.csv` | government intent (legacy) | source decomposition required | Reconcile/de-duplicate against canonical government-intent data. |
| 25 | `domains/government_intent/data/derived/government_intent_seed.csv` | government intent (legacy) | source decomposition required | Reconcile/de-duplicate against canonical government-intent data. |

## Support outputs — tracked but not independent imports

These are generated from imported datasets and therefore do not require separate source inventories, but they are registered so the derived tree is exhaustively controlled:

1. `data/derived/population_state_validation.csv`
2. `data/derived/transport/ga_major_roads_east_summary.csv`
3. `data/derived/transport/ga_rail_east_summary.csv`

## Important findings from the sweep

### AEMO proved the control is necessary

The first source reconciliation found the existing transmission seed contained 17 of 21 scoped AEMO projects. The four omissions were added and the dataset now reconciles 21/21. This was a material completeness defect in a dataset that looked plausible before assurance.

### Curated seed files are the major legacy assurance debt

Most existing VECA seed datasets are not direct one-source imports. They are curated syntheses built from several planning documents, project pages or authorities. Counting their current rows would repeat the same failure pattern as calling 23 extracted records "23/23" when the source really contained 27.

They therefore remain explicitly `source_decomposition_required` until their source families receive independent inventories and manifests.

### Population and GA geometry are structurally stronger but not yet independently reconciled

The ABS extractor already checks uniqueness/scope/totals and the GA extractors perform pagination/scope/duplicate-ID checks. Those are good extraction controls, but their observed counts are still produced by the extraction path itself. Independent code/feature-ID inventories remain required before they can be declared reconciled.

### BITRE airports are not a current imported set

The repository contains an airport extractor/workflow, but no current airport dataset appears under the derived data trees. It therefore does **not** appear among the 25 current imports and should remain an ingestion task rather than being treated as existing evidence.

## Completion rule going forward

A new derived dataset must be added to `assurance/dataset_register.json` in the same change that creates it. Dataset registration does not itself prove source completeness: source-bearing datasets must still progress through independent inventory, reconciliation and critical-field verification under `assurance/manifests/`.
