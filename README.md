# VECA-2075

**Vision East Coast Australia 2075**

VECA-2075 is a long-horizon, evidence-driven investigation into how eastern Australia could accommodate roughly 10 million additional residents by around 2075 while improving housing, infrastructure efficiency, climate resilience, water security, energy utilisation, productivity, transport efficiency and environmental outcomes.

The 10 million figure is a forcing scenario, not a forecast. VECA may conclude that metropolitan concentration, regional expansion or a hybrid spatial system is superior.

## Start here

Read in this order:

1. `PROJECT_STATUS_AND_ROADMAP.md` — canonical current state, stage gates and next work.
2. `AGENTS.md` — repository/assurance rules for agents.
3. `doctrine/design_principles.md` — durable research rules.
4. `session_summaries/RECONCILIATION_2026-09-10.md` — latest cross-agent reconciliation and recovered backlog.
5. the relevant domain/experiment README and findings files.

Session summaries are historical evidence about work performed; they are not automatically current truth. Current `main` plus canonical assurance/register/consumer files wins after reconciliation.

## Core research question

> If eastern Australia expected roughly 10 million additional residents over the coming decades, where should those people ideally live if we could plan the system deliberately for 2075 rather than simply extending today's cities?

Secondary question:

> What combination of settlement, infrastructure, water, energy, industry and transport investment would produce the best long-term Australian outcome?

## Current phase — 10 September 2026

**Primary analytical stage: EXP-002 physical survival / habitat-resource screening.**

Stage 1 inherited-system evidence is substantially established and continues to be enriched in parallel. The repository now includes:

- reconciled ABS population and authoritative road/rail foundations;
- historical/current HSR and conventional-rail evidence;
- AEMO transmission and exhaustive generation/storage source observations;
- DNSP distribution-capacity/load datasets including Ausgrid, Essential Energy and Ergon evidence;
- regional water-system, ports/intermodal, digital-backbone and compute-capital evidence;
- Government Intent / Future Capital Optionality research;
- a source/dataset assurance control plane;
- a multi-generation MapLibre map through **POC-005**, including population, transport, energy, water, capital, compute, digital, ports and capacity/investment context;
- a machine-readable spatial-readiness register distinguishing mapped evidence from datasets blocked on authoritative spatial joins.

**No settlement ranking is authorised yet. No preferred VECA HSR route is authorised yet.**

The Regional Anchor Cluster join/weighting task remains paused until Stage 2 is materially advanced.

## Map lineage

- `maps/poc-001/` — interaction proof.
- `maps/poc-002/` — real east-coast road/rail spatial foundation.
- `maps/poc-003/` — SA2/LGA population, settlements and landscape.
- `maps/poc-004/` — energy, REZ, water, capital, freight and planning geography.
- `maps/poc-005/` — compute, digital backbone, conventional-rail capacity/investment, ports, DNSP signals and expanded regional water evidence.

Map absence must not be interpreted as data absence. `assurance/spatial_readiness.json` records whether a dataset is mapped, map-ready, blocked on a spatial join or non-spatial.

## Research sequence

1. inherited system and capital accumulation;
2. physical survival / habitat-resource screening;
3. evidence-led candidate-region discovery;
4. inherited service/economic capability and missing capital;
5. attractiveness, productive economy and voluntary migration;
6. AI/automation uncertainty stress tests;
7. materially different settlement systems;
8. transport derived from those systems;
9. whole-system infrastructure/economic comparison;
10. scenario and sensitivity analysis;
11. 2075 spatial vision plus near-term option-preservation decisions.

Transport concepts such as HSR, corridor co-location, autonomous/shared first-last-mile mobility and airport/interchange network value remain later-stage scenario/method questions, not current route choices.

## Repository guide

The canonical organising principle is **research domain**, not file type.

- `domains/<domain>/research/` — plans, source registers, findings and evidence notes.
- `domains/<domain>/data/raw/` — preserved source data where practical.
- `domains/<domain>/data/derived/` — reproducible structured outputs.
- `assurance/` — source coverage, dataset registration, reconciliation and spatial-readiness controls.
- `doctrine/` — project purpose and durable design principles.
- `experiments/` — bounded cross-domain experiments/synthesis.
- `maps/` — spatial outputs and map-specific documentation.
- `scenarios/` — later alternative 2075 spatial systems.
- `decisions/` — consequential project decisions and rationale.
- `session_summaries/` — agent-session history and reconciliation records.
- `tools/` — tooling necessary to answer research questions.
- `research/` and `data/` — live legacy/migration locations while older content is consolidated safely.

`domains/government-intent/` is canonical for new Government Intent work. `domains/government_intent/` is legacy and must not receive new material.
