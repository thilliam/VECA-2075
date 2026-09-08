# VECA-2075

**Vision East Coast Australia 2075**

VECA-2075 is a long-horizon, evidence-driven investigation into how eastern Australia could be deliberately reshaped over the next 50 years to accommodate substantial population growth while improving quality of life, housing affordability, infrastructure efficiency, climate resilience, water security, renewable energy utilisation, economic productivity, transport efficiency and environmental outcomes.

## Core research question

> If eastern Australia expected roughly 10 million additional residents over the coming decades, where should those people ideally live if we could plan the system deliberately for 2075 rather than simply extending today's cities?

Secondary question:

> What combination of settlement, infrastructure, water, energy, industry and transport investment would produce the best long-term Australian outcome?

## Vision

Australia will invest enormous sums in housing, energy, water, transport and urban infrastructure to 2075 regardless of VECA. The opportunity is not simply to advocate more spending. It is to investigate whether those investments can be coordinated around a coherent 50-year spatial strategy rather than thousands of individually rational but disconnected decisions.

Australia deliberately built Canberra. Modern engineering, data, climate modelling, AI, renewables and computational optimisation may allow far more ambitious spatial planning. VECA asks what a modern equivalent could achieve at continental scale.

## Initial working hypothesis

Australia may achieve better long-term outcomes by deliberately creating or greatly expanding several regional population centres rather than concentrating most future growth into the existing Brisbane, Sydney and Melbourne metropolitan footprints.

This is a hypothesis to test, not a conclusion. High-speed rail may eventually be enabling infrastructure, but the settlement pattern must be derived before the transport solution.

The initial geographic scope is eastern Australia from South East Queensland to Melbourne, including inland regions that could plausibly form part of a future urban and economic system. South Australia is outside the base model unless evidence later shows that Adelaide or South Australia materially improves the national spatial system.

## Initial target

Explore alternative ways to accommodate approximately 10 million additional residents across eastern Australia. The number is a scenario forcing meaningful spatial choices, not a fixed population forecast.

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

The project separates **evidence**, **inference** and **hypothesis**. It begins by understanding the spatial system that already exists and the capital already accumulating around it. Only after that base is coherent will the project develop settlement candidates, scoring models or transport architectures.

The first experiment, `EXP-001-east-coast-base-map`, therefore contains no proposed HSR route and no candidate new cities.

## Repository guide

The canonical organising principle is now **research domain**, not file type. Evidence, source registers and derived datasets for a subject should live together wherever practical.

- `domains/<domain>/research/` — plans, source registers, findings and evidence notes for that domain.
- `domains/<domain>/data/raw/` — preserved source data where practical.
- `domains/<domain>/data/derived/` — reproducible/structured outputs for that domain.
- `doctrine/` — project purpose and durable design principles.
- `experiments/` — bounded cross-domain research experiments and synthesis.
- `maps/` — rendered spatial outputs and map-specific documentation.
- `scenarios/` — later alternative 2075 spatial scenarios.
- `decisions/` — consequential project decisions and rationale.
- `tools/` — only tooling necessary to answer research questions.
- `research/` and `data/` — legacy/migration locations only while older generated layers and CI workflows are moved safely into the domain structure.

The one-time automated migration of the older population/transport files staged successfully but its push was blocked because the GitHub App lacks permission to rewrite workflow files. New work is domain-first; legacy paths will be retired once the workflow migration can be completed without breaking reproducibility.

## Current phase

**EXP-001 inherited-system synthesis + habitat/resource layer build.** Population and core transport geometry are established; energy, water and industry/logistics are being structured; climate, hazard and land constraints are now being added before any settlement ranking or transport architecture is proposed.
