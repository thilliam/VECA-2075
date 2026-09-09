# VECA-2075

**Vision East Coast Australia 2075**

VECA-2075 is a long-horizon, evidence-driven investigation into how eastern Australia could be deliberately reshaped over the next 50 years to accommodate substantial population growth while improving quality of life, housing affordability, infrastructure efficiency, climate resilience, water security, renewable energy utilisation, economic productivity, transport efficiency and environmental outcomes.

## Start here

For the current state of the project, completed work, open tasks and the full end-to-end research sequence, read **`PROJECT_STATUS_AND_ROADMAP.md`**.

Agents should also read **`AGENTS.md`** before starting work.

The durable research rules are in `doctrine/design_principles.md`.

## Core research question

> If eastern Australia expected roughly 10 million additional residents over the coming decades, where should those people ideally live if we could plan the system deliberately for 2075 rather than simply extending today's cities?

Secondary question:

> What combination of settlement, infrastructure, water, energy, industry and transport investment would produce the best long-term Australian outcome?

The 10 million figure is a forcing scenario, not a population forecast.

## Vision

Australia will invest enormous sums in housing, energy, water, transport, health, education and urban infrastructure to 2075 regardless of VECA. The opportunity is not simply to advocate more spending. It is to investigate whether those investments can be coordinated around a coherent 50-year spatial strategy rather than thousands of individually rational but disconnected decisions.

Australia deliberately built Canberra. Modern engineering, data, climate modelling, AI, renewables and computational optimisation may allow far more ambitious spatial planning. VECA asks what a modern equivalent could achieve at continental scale.

## Working hypothesis

Australia may achieve better long-term outcomes by deliberately creating or greatly expanding several regional population centres rather than concentrating most future growth into the existing Brisbane, Sydney and Melbourne metropolitan footprints.

This is a hypothesis to test, not a conclusion. High-speed rail may eventually be enabling infrastructure, but the settlement pattern must be derived before the transport solution.

The initial geographic scope is eastern Australia from South East Queensland to Melbourne, including inland regions that could plausibly form part of a future urban and economic system. South Australia is outside the base model unless evidence later shows that Adelaide or South Australia materially improves the national spatial system.

## Non-goals

VECA-2075 is not:

- high-speed-rail advocacy;
- a political platform;
- an engineering design;
- a population forecast;
- an argument for any particular new city; or
- a recommendation to abandon existing cities.

It is an evidence-driven exploration of possible long-term spatial systems.

## Research method

The project separates **evidence**, **inference** and **hypothesis**.

The broad sequence is:

1. understand the inherited system and current capital accumulation;
2. screen physical habitat/resource constraints using 2050–2075 conditions;
3. discover candidate regions from evidence;
4. analyse inherited service/economic capability and missing capital;
5. test attractiveness, productive economy and voluntary migration;
6. stress-test long-horizon AI/automation uncertainty;
7. construct materially different settlement systems;
8. derive transport from those settlement systems;
9. compare whole-system infrastructure and economics against the default-growth counterfactual;
10. run scenario/weight sensitivity; and
11. produce a 2075 spatial vision plus near-term option-preservation decisions.

See `PROJECT_STATUS_AND_ROADMAP.md` for stage gates and current priorities.

## Current phase — September 2026

**Primary analytical work: EXP-002 habitat/resource survival screening.**

EXP-001 has progressed far beyond source reconnaissance: population, road/rail geometry, HSR evidence, infrastructure capital, energy, water and industry/logistics all have meaningful first-pass evidence, although several enrichment gaps remain.

Government intent / Future Capital Optionality is now a formal evidence family covering regional growth assumptions, health/service capital, government land, universities/VET and school-growth signals.

A working layered-map POC exists at `maps/poc-001/`, with layer toggles, time/status filtering, regional navigation and feature-level evidence inspection.

**No settlement ranking is authorised yet. No VECA HSR route is authorised yet.**

The proposed Regional Anchor Cluster join/weighting task is currently **paused** and recorded in the roadmap backlog.

## Repository guide

The canonical organising principle is **research domain**, not file type. Evidence, source registers and derived datasets for a subject should live together wherever practical.

- `domains/<domain>/research/` — plans, source registers, findings and evidence notes.
- `domains/<domain>/data/raw/` — preserved source data where practical.
- `domains/<domain>/data/derived/` — reproducible/structured outputs.
- `doctrine/` — project purpose and durable design principles.
- `experiments/` — bounded cross-domain research experiments and synthesis.
- `maps/` — spatial outputs and map-specific documentation.
- `scenarios/` — later alternative 2075 spatial systems.
- `decisions/` — consequential project decisions and rationale.
- `tools/` — only tooling necessary to answer research questions.
- `research/` and `data/` — live legacy/migration locations while older generated layers and CI workflows are moved safely into the domain structure.

The automated migration staged successfully but its push was blocked because the GitHub App lacked permission to rewrite workflow files. Do not duplicate large datasets simply to make the tree conform visually.

### Naming note

`domains/government-intent/` is canonical for new government-intent work. The older `domains/government_intent/` directory is legacy and awaits careful consolidation; agents must not add new material there.

## Mapping

`maps/poc-001/` is the first runnable VECA layered-map explorer. It is already a useful evidence-inspection POC, not merely a future proposal. Large authoritative rail/road extracts should ultimately be served through tiles rather than loaded wholesale into the browser.

## Agent handoff

A new agent should normally begin with:

`README.md` -> `PROJECT_STATUS_AND_ROADMAP.md` -> `AGENTS.md` -> `doctrine/design_principles.md` -> relevant experiment/domain plan.
