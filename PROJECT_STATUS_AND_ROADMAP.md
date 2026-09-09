# VECA-2075 — Project Status and End-to-End Roadmap

**Status date:** 9 September 2026  
**Purpose:** canonical handover/status document for humans and agents. Read this before starting a new VECA task.

## 1. What VECA is trying to answer

VECA asks how eastern Australia could accommodate roughly **10 million additional residents** by around 2075 if settlement, infrastructure, water, energy, industry and transport were planned as one long-horizon system rather than by extending today's metropolitan pattern by default.

The 10 million figure is a forcing scenario, not a forecast. The project must be able to conclude that today's metropolitan pattern is best, that regional expansion is better, or that a hybrid is superior.

The governing doctrine is in `doctrine/design_principles.md`. The most important rules are: settlement before transport; use future climate; distinguish evidence/inference/hypothesis; current population is not destiny; sunk capital matters but does not dictate the answer; preserve optionality; and do not introduce a composite score before the evidence and sensitivity problem are understood.

## 2. Where the project is now

VECA has moved beyond bootstrap/source reconnaissance. It now has a meaningful inherited-system evidence base, structured domain research, and a working layered-map POC. It has **not** yet selected candidate settlement regions, assigned settlement rankings, designed a VECA transport network, or performed whole-system economics.

Current position:

**EXP-001 inherited-system mapping: first coherent pass substantially established; enrichment remains.**  
**EXP-002 habitat/resource screening: framework and source discovery established; material spatial screening is the next major analytical task.**  
**Government intent/future capital optionality: first regional and asset-level evidence established.**  
**Regional Anchor Cluster join: explicitly paused and placed in backlog until the physical survival screen is further advanced.**

## 3. What has been achieved

### Doctrine and research design

- Vision, geographic scope and 10m forcing scenario established.
- Fifteen design principles pin the research against technology-first, CBD-first and current-population bias.
- Evidence/inference/hypothesis separation established.
- Controlled infrastructure status logic established: completed, under construction, funded/committed, approved-not-started, planned-high-confidence, proposed, cancelled.
- Future concepts documented but intentionally unweighted: Capital Gravity, infrastructure inheritance per additional resident, habitat/resource suitability, economic potential, network value, AI infrastructure/economic/social resilience, life accessibility and voluntary migration attractiveness.

### Population

- ABS SA2 2001–2025 ERP layer materialised for QLD/NSW/ACT/VIC: 1,844 SA2s.
- 2024–25 components and state validation captured.
- Authoritative 1 km population-grid source preserved.
- Findings distinguish metropolitan-fringe growth, heterogeneous regional growth and one-year movement from long-run settlement suitability.

### Transport

- Geoscience Australia east-coast rail and major-road geometry materialised and corrected to QLD/NSW/ACT/VIC scope.
- Large authoritative GeoJSONs exist for rail and major roads.
- Freight research distinguishes physical inheritance, observed utilisation and latent network option value.
- Initial intermodal nodes, ports and airport activity represented.
- HSR/faster-rail evidence lineage assembled from VFT/Speedrail through the 2001 and 2013 Commonwealth studies to current HSRA work.
- HSR cost and corridor-obstacle evidence seeded. This is evidence reuse, not a VECA route proposal.

### Recent/committed infrastructure and Capital Gravity groundwork

- Major recent/committed transport and infrastructure projects seeded with status/value discipline.
- Western Sydney Airport/Aerotropolis/Bradfield case studied as evidence that governments can deliberately manufacture new economic gravity through coordinated airport, metro, road, land and industry investment.
- Capital Gravity is recognised as more than dollar totals; enabling investment must later be separated from congestion remediation and legacy replacement.

### Energy

- AEMO 2026 ISP transmission pipeline structured, including HumeLink, Hunter-Central Coast REZ, Central-West Orana REZ, Western Renewables Link, VNI West, New England REZ and relevant Queensland/Victorian reinforcements.
- REZ/network status distinctions documented.
- Important finding: connection/transfer/storage/generation capacity are different quantities and must not be collapsed.
- Asset-level generation/storage extraction remains outstanding.

### Water

- Functional-system method established: analyse source + storage + regulated river/groundwater + treatment + transfer + desal/recycling + augmentation rather than treating a dam as a water score.
- Seed systems exist for SEQ, Greater Sydney, Canberra-Queanbeyan, Melbourne/South-Central, Wagga, Albury and Goulburn.
- Key insight: diversification and transfer capability can matter more than raw reservoir size.
- Toowoomba/Darling Downs, New England and Hunter/coastal coverage still needs completion and sustainable-yield/augmentation comparison is not yet mature.

### Industry and logistics

- Initial structured nodes include Western Sydney Aerotropolis/Bradfield, Parkes SAP/National Logistics Hub and Wagga/Bomen/RiFL SAP.
- Port and intermodal research has begun to treat ports as inland catchment systems rather than waterfront points.
- Broader QLD, Hunter, VIC and ACT node coverage remains incomplete.

### Climate, hazard, terrain and land

- EXP-002 framework established with staged gates rather than one score.
- Climate/hazard source register and first findings established: warming is universal; southern water stress requires explicit future-yield treatment; extreme rainfall and drought can worsen together; fire weather is a major future spatial filter; national flood evidence requires local/state refinement.
- Land source plan established for DEM/slope, ABARES land use, protected areas, native-title/ILUA context, agriculture, wetlands/floodplain and transformed land.
- The actual 2050/2070 regional climate profiles, slope/terrain surfaces and land constraint overlays are not yet materialised. This is a major next-stage gap.

### Government intent and Future Capital Optionality

A new evidence family now records what governments already assume about future settlement geography and how movable future public capital remains.

Established evidence includes:
- NSW regional growth plans;
- ShapingSEQ and preserved future-growth areas;
- Victorian statewide/housing-target direction;
- ACT district/service planning;
- health capital and site-role signals;
- government-controlled/growth land;
- universities, TAFE/VET/trade education and first school-growth signals.

Capital is conceptually separated into:
1. sunk/fixed inheritance;
2. committed low-flex capital;
3. planned capital;
4. renewal liability;
5. growth-triggered capital; and
6. optionality assets such as reserved land/corridors.

The economic question this enables is: **how much of the infrastructure needed by an alternative settlement pattern is genuinely incremental, versus expenditure governments would have made somewhere anyway?**

### Education and human-capital assets

- Anchor inventories now include major universities and vocational/trade institutions across Central Coast, New England, Canberra, Wagga/Albury, Gippsland and SEQ/Toowoomba.
- School work is intentionally focused on new-school reservations, major expansions, growth-driven capacity and later cost norms rather than cataloguing every school.
- `Human Capital Formation Capacity` has emerged as a future analytical family; it is not yet a score.

### Mapping

`maps/poc-001/` is a working layered-map proof of concept. It already demonstrates layer toggles, semantic zoom, time/status filtering, regional navigation and clickable evidence/interpretation panels. Hospital and tertiary assets are shown from the government-intent corpus; large road/rail datasets remain outside the browser POC and need tiled delivery for production-scale use.

The map is a view over evidence entities. It is not the analytical model itself.

## 4. Important findings so far — not conclusions

- Existing east-coast geography is more than three capital cities: deliberate non-CBD nodes, inland logistics nodes, energy nodes and cross-border service systems already exist.
- Western Sydney demonstrates that coordinated public capital and planning can create new economic gravity.
- Wagga combines an unusual set of existing service, logistics, water, industry and grid-position assets.
- Parkes is a useful test of whether exceptional network position can overcome a smaller urban/service base.
- New England is receiving energy-network investment at a scale disproportionate to current population and should not be judged only by today's Armidale/Tamworth economy.
- Canberra-Queanbeyan should be analysed functionally across the border.
- Albury-Wodonga is a live example of capital moving from spatial optionality toward site lock-in.
- Toowoomba's hospital relocation demonstrates that renewal capital can sometimes reshape service geography rather than simply reproduce it.
- Universities and major hospitals can be city-shaping anchors; schools are more often population-following growth liabilities.

None of these findings authorises a preferred candidate.

## 5. End-to-end research plan

### Stage 0 — Doctrine and research controls — COMPLETE

Define question, scope, evidence standard, status taxonomies, anti-bias rules and repository discipline.

### Stage 1 — Inherited system — SUBSTANTIALLY COMPLETE, ENRICHMENT ACTIVE

Understand what already exists and what capital is already accumulating.

Required close-out work:
- energy generator/storage asset extraction;
- water gaps: Toowoomba/Darling Downs, New England, Hunter/coastal;
- broader industry/logistics nodes in QLD/Hunter/VIC/ACT;
- port catchments;
- clean non-double-counted capital register;
- transport utilisation/capacity enrichment;
- production-scale map delivery when useful.

Do not delay EXP-002 merely to achieve exhaustive Stage-1 completeness.

### Stage 2 — Physical survival / habitat-resource screen — CURRENT PRIMARY ANALYTICAL STAGE

Build the first broad east-coast `survival map`.

Gate A: structural exclusions/severe constraints.  
Gate B: water/resource feasibility.  
Gate C: 2050/2070 climate and hazard burden.  
Gate D: inherited-system optionality.  
Gate E: government intent/future-capital context.

First output is **pass / difficult / uncertain / major constraint by evidence family**, not a weighted ranking.

Immediate work:
- materialise 2050/2070 climate profiles;
- derive terrain/slope/buildability surfaces;
- add protected/agricultural/land-use/native-title context;
- improve flood and bushfire evidence;
- complete water feasibility/augmentation evidence;
- render the survival layers on/alongside the existing map POC.

### Stage 3 — Candidate-region discovery

Only after Stage 2 is credible, identify broad regions that survive the physical/resource screen and possess enough system potential to justify detailed investigation.

Candidates must emerge from evidence. Existing research candidates are prompts to interrogate, not a shortlist to validate.

Output: a deliberately small candidate set plus explicit rejected/uncertain regions and reasons.

### Stage 4 — Regional Anchor Clusters / inherited capability join — PAUSED BACKLOG TASK

Use the existing mapped points and layers to identify functional combinations within travel-time catchments: health + university + VET + schools + government land + water + energy + industry/logistics + transport + official growth intent.

Purpose: determine what useful systems already co-exist, what is missing, and which missing components require genuinely new capital.

Do **not** hide components behind a single cluster score. Keep node scale, reach, scarcity, replacement cost, scalability, strategic coupling and lock-in/optionality visible separately.

This task is intentionally paused until Stage-2 physical screening is more mature.

### Stage 5 — Attractiveness, economy and voluntary settlement

For surviving candidates ask why households and businesses would actually choose them.

Research:
- housing cost/quality and buildability;
- productive employment and industry diversity;
- universities/research/workforce formation;
- hospitals/schools/services;
- culture/community/sport/recreation/nature;
- local mobility and 15/30/60-minute life accessibility;
- airport/intercity accessibility;
- digital connectivity;
- ability to attract rather than coerce migration.

Output: regional propositions and failure modes, still with transparent dimensions.

### Stage 6 — AI / 2075 uncertainty stress tests

Stress-test candidates and later settlement systems under A0–A3 automation/location scenarios, including the counter-case that AI strengthens agglomeration around capital, universities and compute.

AI is a robustness test, not a forecast.

### Stage 7 — Construct alternative settlement systems

Build materially different 2075 spatial architectures, for example:
- metropolitan-concentration baseline;
- regional constellation;
- corridor/networked-city system;
- deliberate new-city strategy;
- hybrid.

Each scenario must allocate the forcing population and explain economic/service geography. No transport technology should define the scenario in advance.

### Stage 8 — Derive transport architecture

Only now derive passenger/freight transport from the settlement scenarios:
settlements -> trip markets -> freight -> airports -> regional rail -> HSR where justified -> roads -> local transit.

Compare conventional upgrades, branch lines, new corridors and HSR. Optimise door-to-door access and capacity, not merely headline station-to-station speed.

### Stage 9 — Whole-system infrastructure and economics

For each settlement system estimate incremental requirements for:
- housing/site preparation;
- roads/local transit/rail/HSR/airports/freight;
- electricity/transmission/storage;
- water/wastewater/recycling;
- hospitals/health;
- schools/VET/universities;
- digital;
- industry enabling works;
- environmental mitigation.

Compare against the **counterfactual cost of accommodating the same population under the metropolitan/default plan**, including renewal, congestion remediation and growth-triggered expenditure that would occur anyway.

A likely useful denominator is whole-system incremental infrastructure cost per additional resident, but this is not yet pinned.

### Stage 10 — Scenario comparison and optimisation

Test trade-offs across housing, infrastructure cost, productivity, accessibility, water, energy, climate resilience, environment/agriculture, lifestyle, optionality and migration attractiveness.

Only here introduce composite weighting if required. Run sensitivity analysis: a robust result should survive materially different reasonable weights.

### Stage 11 — VECA-2075 vision and near-term option-preservation program

Produce a coherent spatial future plus the decisions that matter in the 2030s/2040s: land/corridor reservations, service-location decisions, infrastructure sequencing and experiments that preserve valuable future options.

The final product should show not just a 2075 picture but **what Australia would need to do differently, and when, for that option to remain available**.

## 6. Agent-ready work queue

Good parallel tasks now include:

**P0 — EXP-002 physical screening**
- climate 2050/2070 regional profiles and spatial surfaces;
- terrain/slope/buildability;
- protected/agriculture/land-use constraints;
- flood/bushfire evidence;
- water augmentation/yield comparison.

**P1 — Stage-1 enrichment**
- AEMO generator/storage extraction;
- Hunter/New England/Toowoomba water completion;
- QLD/Hunter/VIC/ACT industry-logistics nodes;
- port catchments;
- transport capacity/utilisation;
- clean capital census.

**P1 — Government intent**
- new-school reservations/major school pipeline rather than all schools;
- tertiary/VET expansion and specialist capability;
- government-owned development land/corridors;
- hospital/service renewal windows and site flexibility.

**P2 — Map/data engineering**
- add authoritative derived layers to map serving pipeline;
- tiled delivery for large road/rail/spatial surfaces;
- provenance/status/time metadata preserved in map entities.

**PAUSED — Regional Anchor Clusters v1**
- do not start until explicitly resumed.

**LATER**
- candidate ranking;
- settlement scenarios;
- VECA HSR/transport design;
- AI stress testing;
- whole-system cost model;
- optimisation.

## 7. Known repository/QA issues

- Canonical organisation is domain-first, but older `research/` and `data/` paths remain because the automated migration push was blocked by GitHub workflow-update permissions. Do not duplicate large datasets merely to make the tree look tidy.
- Both `domains/government-intent/` and an older `domains/government_intent/` currently exist. **Use `domains/government-intent/` for all new work.** The underscore directory is legacy and must be consolidated carefully; do not add new evidence there.
- `research/EXP-001-layer-status.md` and the original EXP-001 README became stale as work progressed; they are being updated as part of this documentation pass.
- BITRE airport-history extraction failed/was parked because the source workbook delivery was unreliable. Current airport activity is represented; history is not required to block current work.
- Exact road/rail QA should rely on materialised summaries and source validation, not old conversational counts.
- Seed datasets are structured research artefacts, not necessarily exhaustive asset censuses.

## 8. Rules for agents

1. Read `README.md`, this document, `doctrine/design_principles.md`, and the relevant experiment/domain plan before work.
2. Search the repository before creating a new file or taxonomy.
3. Prefer primary authoritative sources.
4. Record provenance and source dates.
5. Keep proposed/planned/committed/completed distinct.
6. Keep evidence, inference and hypothesis distinct.
7. Do not rank settlements or design HSR unless the assigned task explicitly authorises it.
8. Do not turn a government forecast into VECA truth.
9. Do not equate infrastructure dollars with strategic value.
10. Add findings and limitations, not just data.
11. Avoid parallel agents editing the same canonical file; give agents bounded outputs that can be reviewed/merged.
12. If a task reveals a doctrine-level decision, update `decisions/README.md` or propose a decision record rather than silently embedding it in code/data.
