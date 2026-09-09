# VECA-2075 Agent Guide

This file is the short operating contract for agents working in this repository.

## Read first

Before starting a task, read:

1. `README.md`
2. `PROJECT_STATUS_AND_ROADMAP.md`
3. `doctrine/design_principles.md`
4. `assurance/README.md` for any source discovery, ingestion or map-data task
5. the relevant `experiments/.../README.md`
6. the relevant `domains/<domain>/research/*layer_plan*.md` and source register.

For current work, `PROJECT_STATUS_AND_ROADMAP.md` is the canonical status/backlog document. `assurance/source_register.json` is the canonical cross-domain source-coverage/backlog register. `assurance/dataset_register.json` is the canonical inventory of current derived datasets and their assurance state.

## Current project state

VECA is **not** at settlement-ranking or transport-design stage.

- EXP-001 inherited-system evidence is substantially established but still being enriched.
- EXP-002 physical habitat/resource screening is the primary analytical stage.
- Government intent/future-capital optionality has a first structured evidence base.
- A layered map POC exists under `maps/poc-001/`.
- Regional Anchor Cluster joining/weighting is **paused** until explicitly resumed.
- Source Coverage & Ingestion Assurance is now the required control plane for new and migrated evidence.

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

Cross-domain source assurance lives under:

`assurance/source_register.json`  
`assurance/dataset_register.json`  
`assurance/curated_dataset_contracts.json`  
`assurance/manifests/`

Older `research/` and `data/` content is still live legacy material while workflow-dependent migration is unresolved. Search both before assuming evidence is absent.

**Government intent naming:** use `domains/government-intent/` for all new work. `domains/government_intent/` is legacy and must not receive new material.

Do not duplicate large files merely to satisfy the target directory layout.

## Evidence and ingestion standard

Prefer primary government/statistical/network/authority sources, while also tracking infrastructure-owner intent, committed/private development, industry propositions and market analysis as distinct source types. Capture source title, publisher, publication/data date, geography, status and limitations. A source register is part of the research output, not optional administration.

**First declare what the dataset claims to be.**

- An **exhaustive import** claims to reproduce a defined source inventory. Establish an independent source inventory before/independently of extraction, then account for every expected entity as `mapped`, `dataset_only`, `excluded`, `duplicate` or `unresolved`.
- A **curated synthesis** intentionally selects evidence. Do not invent a false 27/27 universe for it. Instead ensure every included row resolves to source provenance and give the dataset an explicit selection claim/policy/completeness test in `assurance/curated_dataset_contracts.json`.

For exhaustive imports the required invariant is:

`expected_count == mapped + dataset_only + excluded + duplicate + unresolved`

The expected count may not simply be the row count produced by the same extractor being tested. Record its independent basis and evidence locator in the source manifest. A source cannot become `verified` while unresolved entities remain.

`provenance_reconciled` on a curated set means all included rows are structurally sourced and its scope is explicit. It does **not** mean all possible real-world entities of that type have been discovered.

Completeness also does not prove correctness. Verify identity/location and decision-critical fields such as status, capacity, MW, value and timing against evidence, and use spatial sanity checks where relevant.

**Every new file under `data/derived/**` or `domains/*/data/derived/**` must be added to `assurance/dataset_register.json` in the same change.** This prevents a dataset from quietly entering analysis/map work without an assurance state. Support summaries are registered too, but are labelled `support_output` rather than treated as independent source imports.

Run for data/source changes:

```bash
python tools/audit_current_datasets.py
python tools/validate_dataset_register.py
python tools/validate_source_assurance.py --strict
```

See `assurance/README.md` for the full contract. See `assurance/migration/current_imported_sets_2026-09-09.md` for the baseline census of the 25 source-bearing datasets that existed when dataset-level assurance was introduced.

When a source gives multiple capacities or dollar values, preserve their definitions rather than choosing the most convenient number.

## Agent task boundaries

Parallel agents should receive bounded domains/regions/outputs. Avoid multiple agents editing the same synthesis, README or register concurrently.

A good source-ingestion task normally produces:
- `assurance/source_register.json` additions/status updates;
- `assurance/dataset_register.json` additions/status updates for any derived file;
- a source-specific `assurance/manifests/*.json` record for exhaustive imports, or a curated dataset scope contract for selective synthesis;
- a structured derived dataset where appropriate;
- a concise findings/limitations note;
- explicit unresolved questions/known gaps;
- evidence-backed accuracy checks;
- no unrequested ranking/recommendation.

If new work conflicts with doctrine or an existing decision, stop and surface the conflict rather than silently changing the method.

## Mapping

`maps/poc-001/` proves the layered-map interaction model. Do not rebuild it as part of a research task unless mapping is the assigned task. Preserve provenance/status/time semantics when adding spatial data.

A sparse map layer must not silently imply sparse real-world infrastructure when source coverage is incomplete. Map/data tasks should expose or preserve assurance status so `verified`, exhaustive/reconciled, curated/provenance-reconciled, partial and not-yet-researched coverage can be distinguished.

Large authoritative road/rail files already exist under legacy `data/derived/transport/`; production browser delivery should use tiling/serving rather than loading whole files.

## Current priority order

1. Use the assurance system to migrate/reconcile high-value existing evidence before scaling the next large ingestion wave.
2. EXP-002 physical survival screen: climate, terrain, land constraints, flood/fire and water feasibility.
3. Close high-value EXP-001 gaps: energy assets/distribution capacity, data centres/digital infrastructure, water gaps, industry/logistics, conventional rail capacity/investment, port catchments, transport utilisation/capacity and clean capital census.
4. Continue government-intent and non-government forward-intent evidence where it informs future-capital optionality.
5. Improve map delivery only where it helps inspect evidence.
6. Candidate discovery only after the survival screen is credible.

See `PROJECT_STATUS_AND_ROADMAP.md` for the full end-to-end sequence.