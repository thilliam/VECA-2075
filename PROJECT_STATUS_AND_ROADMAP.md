# VECA-2075 — Project Status and End-to-End Roadmap

**Status date:** 10 September 2026  
**Purpose:** canonical handover/status document for humans and agents. Read this before starting a new VECA task.

## 1. Current position

VECA asks how eastern Australia could accommodate roughly **10 million additional residents** by around 2075 if settlement, infrastructure, water, energy, industry and transport were planned as one long-horizon system rather than by extending today's metropolitan pattern by default.

The 10 million figure is a forcing scenario, not a forecast. No settlement ranking, preferred regional candidate or preferred VECA HSR alignment is authorised yet.

Current stage state:

- **Stage 0 — doctrine/research controls:** complete.
- **Stage 1 — inherited system:** substantially complete; enrichment continues in parallel.
- **Stage 2 — physical survival / habitat-resource screen:** **current primary analytical stage**.
- **Stage 3+ — candidate selection, capability joins, settlement systems, transport and whole-system economics:** gated on Stage 2.
- **Regional Anchor Cluster join/weighting:** paused until Stage 2 is materially credible.

The latest cross-agent reconciliation is `session_summaries/RECONCILIATION_2026-09-10.md`.

## 2. What is now established

### Research controls and assurance

`assurance/` is the control plane for source coverage and ingestion integrity. Current controls include source lifecycle, dataset registration, exhaustive-vs-curated dataset semantics, independent expected inventories, entity disposition/reconciliation, curated scope contracts and strict validation.

The first assurance migration proved its value by finding a 17/21 AEMO transmission import and repairing it to 21/21. Later assurance work also exposed malformed CSV provenance, aggregated source entities and other defects that a plausible map would not reveal.

A new `assurance/spatial_readiness.json` layer now bridges corpus ingestion to mapping. It explicitly distinguishes mapped, map-ready, blocked-spatial-join and non-spatial evidence so a missing map symbol is not misread as missing evidence.

### Population and settlement geography

- ABS SA2 ERP: 1,844 east-coast SA2s, reconciled to authoritative source identity.
- LGA population/growth lens is available.
- ABS UCL settlement hierarchy plus curated metropolitan functional centres is available.
- Population needs multiple lenses: physical density, administrative geography and functional settlement systems.
- Medium-zoom functional settlement clusters remain future work.

### Transport

- GA rail and major-road source extracts are reconciled at 26,808 rail features and 75,581 road features.
- Conventional-rail capacity/investment evidence now distinguishes physical geometry, funded works, route capability, active projects and corridor preservation.
- HSR/faster-rail evidence lineage from earlier Australian studies through current HSRA work is preserved as inherited evidence, not route advocacy.
- Port/intermodal and inland-catchment framing has materially improved.
- Later Stage-8 methodology backlog now includes corridor co-location/optionality, accessible population per corridor-km, door-to-door journey burden, destination vehicle availability and FSD/shared first-last-mile scenarios.

### Energy

- AEMO 2026 ISP east-coast transmission set is reconciled at 21/21 scoped projects.
- Exhaustive AEMO July 2026 generation/storage source observations: 1,415 / 1,415 records across NSW1/QLD1/VIC1.
- Ausgrid capacity/demand: 210 / 210 substations, including firm capacity, transfer, embedded generation and demand forecasts.
- Essential Energy zone-substation capacity: 366 matched summer/winter assets.
- Ergon 2025-26 historical load: 265 / 265 substations with raw values preserved and a separately labelled empirical divide-by-1000 interpretation.
- Distribution-capacity signals remain screening evidence, not guaranteed connection headroom.
- Major remaining map limitation: several exhaustive asset/capacity datasets still require authoritative spatial joins.

### Water

Functional-system method is established: source + storage + regulated river/groundwater + treatment + transfer + desalination/recycling + augmentation, not nearest-dam scoring.

Coverage now includes SEQ, Sydney, Canberra-Queanbeyan, Melbourne/South-Central, Wagga, Albury, Goulburn, Toowoomba/Darling Downs, Lower Hunter, Tamworth and Armidale/Guyra/Uralla. Sustainable-yield and augmentation comparison remains incomplete and belongs in Stage 2.

### Digital / compute / industry / logistics

Structured first-pass evidence now includes:

- compute/data-centre campus pipeline;
- terrestrial and domestic subsea digital backbone;
- Brisbane, Botany, Kembla, Newcastle, Melbourne and Geelong port systems;
- Moorebank, Enfield, Cooks River and other intermodal nodes;
- ARTC/inland-rail capacity/investment evidence.

The project must continue to separate published capacity types and avoid summing incompatible MW or treating system capacity as local spare capacity.

### Government Intent / Future Capital Optionality

Government regional plans, growth assumptions, health/service capital, government land, education/VET and growth-school signals are now established evidence families.

The key economic framing remains: compare alternative settlement systems against the capital governments would otherwise spend somewhere, rather than comparing regional growth against a fictional zero-investment baseline.

Future analysis must keep sunk/fixed inheritance, committed low-flex capital, planned capital, renewal liabilities, growth-triggered capital and optionality assets distinct.

### Mapping

Current interactive lineage:

1. `maps/poc-001/` — interaction proof.
2. `maps/poc-002/` — authoritative road/rail spatial foundation.
3. `maps/poc-003/` — SA2/LGA population, settlements and landscape.
4. `maps/poc-004/` — transmission/REZ, water, capital, freight and planning geography; current builder includes robust AEMO REZ browser/cache fallback and KML parsing.
5. `maps/poc-005/` — compute, digital backbone, rail capacity/investment, ports, DNSP capacity signals and expanded water systems.

Current map architecture remains MapLibre for interaction, with PMTiles/vector tiles/PostGIS as the production direction. Browser GeoJSON is POC delivery, not final serving architecture.

## 3. Reconciled branch/session state

The 10 September reconciliation established:

- the old `docs/roadmap-assurance-next-ingestion` branch is superseded; do not merge it;
- POC-004's final AEMO REZ reliability work is already present despite an older session summary saying it was missing;
- the Ergon branch is historically diverged but its logical outputs are already in current main;
- POC-005 / spatial-readiness was the material active delta absent from main and has been recovered from stale ancestry onto the current-main reconciliation branch;
- branch count is therefore not a measure of unfinished work.

See `session_summaries/RECONCILIATION_2026-09-10.md` for the current-state matrix and discovery recovery.

## 4. Current primary work — Stage 2 survival screen

The next analytical product should be a broad east-coast survival map using future conditions. The first output is **pass / difficult / uncertain / major constraint by evidence family**, not a weighted ranking.

### Gate A — structural exclusions / severe constraints

Materialise terrain and slope/buildability; protected areas; agricultural/strategic land context; native-title/ILUA context and other material legal/spatial constraints; and stronger floodplain/coastal constraints where authoritative data exists.

### Gate B — water/resource feasibility

For broad regions, compare sustainable yield/current system stress, diversification and transfer capability, augmentation options and plausible cost/order of magnitude, drought/climate sensitivity, and treatment/desal/recycling opportunities.

### Gate C — future climate/hazard burden

Materialise 2050/2070 profiles/surfaces for heat, rainfall/water stress, bushfire/fire weather, extreme rainfall/flood and other regionally material hazards.

### Gate D — inherited-system optionality

Use Stage-1 evidence to show useful inherited energy, transport, logistics, services, digital and capital-optionality context without letting inherited assets override physical survival.

### Gate E — government intent / future-capital context

Show what governments currently assume, what is already committed, and where future capital/location remains flexible. Government forecasts are policy-shaped baselines, not independent proof of optimal settlement.

## 5. Parallel enrichment that should not block Stage 2

Continue, where useful: authoritative spatial joins for AEMO generation/storage, Ausgrid, Ergon, Essential Energy and other network assets; remaining Queensland/Victorian DNSP capacity/constraint ingestion; route-access/utilisation evidence for conventional rail; broader private/institutional capital and industrial/logistics pipelines; authoritative geometry replacement for representative map anchors; and a non-double-counted capital census.

Do **not** hold Stage 2 hostage to exhaustive Stage-1 completion.

## 6. Later gated stages

### Stage 3 — candidate-region discovery

Only after Stage 2 is credible, identify a deliberately small set of broad regions that survive the screen and justify deeper investigation. Existing named regions are prompts to interrogate, not a shortlist to validate.

### Stage 4 — inherited capability / Regional Anchor Clusters

Use travel-time catchments to join health, education, government land, water, energy, industry/logistics, transport and official growth intent. Keep each component visible; do not hide them behind one score. This stage remains paused.

### Stage 5 — attractiveness, economy and voluntary settlement

Test housing, employment, services, human-capital formation, lifestyle/amenity, local mobility, airport/intercity access, digital connectivity and the ability to attract rather than coerce migration.

### Stage 6 — AI/automation robustness

Stress-test candidates under multiple AI/location scenarios, including the counter-case that AI strengthens agglomeration around capital, universities and compute.

### Stage 7 — alternative settlement systems

Construct materially different spatial systems: metropolitan baseline, regional constellation, corridor/networked-city, deliberate new-city and hybrid examples. Allocate the forcing population before selecting transport technology.

### Stage 8 — derive transport

Derive transport from settlement/trip/freight markets. Later methodology backlog includes door-to-door/generalised journey burden rather than trunk time alone; accessible population by station/interchange catchment; shared corridor/co-location versus shared track; corridor protectability/future-proofing; FSD/shared-car first-last-mile scenarios; airport/HSR/shared-vehicle mobility hubs; and regional-centre-to-international-airport network value.

A useful bounded future accessibility demonstration is a population-weighted `time_to_SYD - time_to_WSI` surface, with separate road and public-transport cases. WSI terminal, airport-edge and Bradfield interchange options remain hypotheses for this later stage, not current route recommendations.

### Stages 9–11 — economics, sensitivity, vision

Compare whole-system infrastructure/economics against the default-growth counterfactual; run sensitivity/uncertainty; then produce the 2075 spatial vision and near-term option-preservation decisions.

## 7. Immediate recommended work packages

1. **EXP-002 climate surfaces:** materialise 2050/2070 regional climate/hazard layers with explicit source/scenario metadata.
2. **Terrain/buildability:** derive DEM/slope classes and structural buildability constraints.
3. **Land constraints:** combine protected/agricultural/native-title and other severe-constraint layers without premature weighting.
4. **Water feasibility:** convert the expanded water-system corpus into broad-region feasibility/augmentation evidence.
5. **Survival-map POC:** add those Stage-2 layers to the map with assurance and geometry-quality metadata.
6. **Spatial joins in parallel:** connect exhaustive energy/network datasets to authoritative coordinates so capacity evidence can later participate in Stage 4 without heuristic geocoding.

The coordination rule for parallel agents is: bounded ownership, source/dataset assurance in the same change, findings as first-class outputs, and session closeout before the workstream ends. Global roadmap synthesis belongs to a reconciliation/coordinator pass rather than every feature branch.
