# EXP-002 — Habitat and Resource Screening

**Status:** Stage-2 implementation active; terrain/buildability v1 is the first implemented structural screen; no rankings authorised yet.

## Purpose

Identify broad eastern-Australian areas that remain plausible for substantial 2075 population growth after future climate, water, terrain, hazard, land-use and environmental constraints are made visible.

This experiment does **not** choose cities and does **not** design transport.

## Current implementation

Terrain/buildability is the first active slice. See `terrain_buildability_v1.md` and `terrain_source_profile_v1.json`.

The v1 terrain pipeline preserves three distinct levels:
- authoritative GA 1-second elevation source family;
- continuous 250 m elevation and slope analytical rasters by default;
- a 10 km browser/summary grid carrying continuous slope/elevation summaries plus descriptive terrain bands.

POC-006 is the first survival-map generation. Full-source terrain status remains pending until the continental build and sanity checks pass; implementation existence is not being treated as data verification.

## Core question

> If current population size and existing CBD gravity are deliberately given little weight, which broad regions retain enough physical, resource and environmental capacity to merit detailed settlement investigation for 2075?

## Inputs

### Physical/habitat
- 2050/2070 heat and extreme heat
- rainfall and drought projection ranges
- fire weather
- flood exposure
- elevation/slope/terrain
- coastal hazard where relevant

### Water
- functional water-system inheritance
- climate-independent supply
- regulated-river / groundwater dependence
- treatment and transfer infrastructure
- plausible augmentation pathways

### Land/environment
- protected areas
- current agricultural/intensive land use
- native-title/ILUA context
- floodplains/wetlands
- already-disturbed/industrial land

### Inherited-system context
Population, transport, energy and industrial/logistics evidence from EXP-001 may be displayed alongside the screening result but should not dominate the physical suitability screen.

### Government intent / future capital optionality
Government plans are not treated as truth, but they are required context before candidate discovery. Include:
- statutory regional growth plans and population assumptions;
- housing targets, urban footprints, rezoning and growth areas;
- health, education and other service plans;
- infrastructure pipelines and corridor/land reservations;
- major asset-renewal or replacement signals;
- planned capital whose need is triggered by today's assumed growth geography.

Keep **current government intent** separate from **VECA preferred geography**. The purpose is to identify path dependency and capital that may still be redirectable.

## Screening method — staged, not one score

### Gate A — structural exclusions / severe constraints
Examples: major protected areas, persistently inundated land, clearly unsuitable terrain, or hazards that would make large-scale urbanisation implausible.

### Gate B — resource feasibility
Test water-system pathways, broad energy access and developable land area. Failure means a region requires a clearly identified engineering pathway rather than receiving an assumed pass.

### Gate C — climate/hazard burden
Compare 2050/2070 heat, drought, fire, flood and coastal burden. Keep variables visible separately.

### Gate D — inherited optionality
Only after A-C: examine how much useful transport, energy, industry and service inheritance a surviving region already possesses.

### Gate E — government-intent / capital-optionality context
Before candidate nomination, compare surviving regions against current Commonwealth/state plans:
- what growth is already assumed there or elsewhere;
- what future service/infrastructure spend is committed, planned or merely growth-triggered;
- which renewal liabilities may be relocatable or consolidatable;
- which government land/corridor reservations preserve strategic choice.

Gate E does **not** reward alignment with current plans. It measures how much institutional momentum and redirectable future capital exists.

## Explicit anti-bias rules

- Do not reward a region primarily for current population.
- Do not reward proximity to Sydney/Melbourne/Brisbane unless it improves an explicit system metric.
- Do not punish inland locations merely because they lack today's aviation scale.
- Do not assume a REZ supplies unconstrained electricity.
- Do not assume a river or dam means available urban water.
- Do not turn protected/native-title layers into simplistic blanket exclusions.
- Do not treat a government population forecast as an independent fact if the infrastructure plan itself helps create that forecast outcome.
- Do not produce a single weighted score until sensitivity testing shows that weighting does not predetermine the answer.

## First output

A broad **survival map**, not a ranking: areas pass, fail, or remain uncertain against each evidence family. The result should deliberately expose disagreements between layers.

The survival map must be accompanied by a **government-intent overlay** showing where current planning is concentrating future population/capital and where major renewal/optionality decisions remain open.

Only after both views exist should VECA define a short list of detailed candidate settlement regions.
