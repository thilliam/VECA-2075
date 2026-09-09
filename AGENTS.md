# VECA-2075 Agent Guide

This file is the short operating contract for agents working in this repository.

## Read first

Before starting a task, read:

1. `README.md`
2. `PROJECT_STATUS_AND_ROADMAP.md`
3. `doctrine/design_principles.md`
4. the relevant `experiments/.../README.md`
5. the relevant `domains/<domain>/research/*layer_plan*.md` and source register.

For current work, `PROJECT_STATUS_AND_ROADMAP.md` is the canonical status/backlog document.

## Current project state

VECA is **not** at settlement-ranking or transport-design stage.

- EXP-001 inherited-system evidence is substantially established but still being enriched.
- EXP-002 physical habitat/resource screening is the primary analytical stage.
- Government intent/future-capital optionality has a first structured evidence base.
- A layered map POC exists under `maps/poc-001/`.
- Regional Anchor Cluster joining/weighting is **paused** until explicitly resumed.

## Hard research guardrails

- Settlement before transport.
- No preferred HSR alignment unless a later task explicitly authorises transport design.
- Current population is evidence, not destiny.
- Government plans are evidence of intent/path dependency, not VECA truth.
- Keep evidence / inference / hypothesis distinguishable.
- Keep completed / under-construction / committed / approved / planned / proposed distinct.
- Use 2050–2075 climate evidence where relevant.
- A dam, river or REZ is not automatically usable water/power capacity.
- Cheap/open land is not automatically developable land.
- Do not introduce a composite settlement score without explicit authorisation and sensitivity testing.

## Repository rules

Canonical new work is domain-first:

`domains/<domain>/research/`  
`domains/<domain>/data/raw/`  
`domains/<domain>/data/derived/`

Older `research/` and `data/` content is still live legacy material while workflow-dependent migration is unresolved. Search both before assuming evidence is absent.

**Government intent naming:** use `domains/government-intent/` for all new work. `domains/government_intent/` is legacy and must not receive new material.

Do not duplicate large files merely to satisfy the target directory layout.

## Evidence standard

Prefer primary government/statistical/network/authority sources. Capture source title, publisher, publication/data date, geography, status and limitations. A source register is part of the research output, not optional administration.

When a source gives multiple capacities or dollar values, preserve their definitions rather than choosing the most convenient number.

## Agent task boundaries

Parallel agents should receive bounded domains/regions/outputs. Avoid multiple agents editing the same synthesis, README or register concurrently.

A good agent task normally produces:
- source-register additions;
- a structured derived dataset where appropriate;
- a concise findings/limitations note;
- explicit unresolved questions;
- no unrequested ranking/recommendation.

If new work conflicts with doctrine or an existing decision, stop and surface the conflict rather than silently changing the method.

## Mapping

`maps/poc-001/` proves the layered-map interaction model. Do not rebuild it as part of a research task unless mapping is the assigned task. Preserve provenance/status/time semantics when adding spatial data.

Large authoritative road/rail files already exist under legacy `data/derived/transport/`; production browser delivery should use tiling/serving rather than loading whole files.

## Current priority order

1. EXP-002 physical survival screen: climate, terrain, land constraints, flood/fire and water feasibility.
2. Close high-value EXP-001 gaps: energy assets, water gaps, industry/logistics, port catchments, transport utilisation/capacity and clean capital census.
3. Continue government-intent evidence where it directly informs future-capital optionality.
4. Improve map delivery only where it helps inspect evidence.
5. Candidate discovery only after the survival screen is credible.

See `PROJECT_STATUS_AND_ROADMAP.md` for the full end-to-end sequence.