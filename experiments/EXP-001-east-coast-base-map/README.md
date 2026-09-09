# EXP-001 — East Coast Base Map

**Status:** first coherent inherited-system pass substantially established; enrichment active  
**Scope:** eastern Australia base system  
**Principle:** observe before proposing

## Goal

Build a coherent multilayer spatial picture of eastern Australia **before** proposing a future settlement pattern or transport network.

EXP-001 establishes the inherited physical and investment system: where people, transport, recent capital, committed projects, energy, water, industry and logistics are located and how those layers relate spatially.

## Current position — September 2026

EXP-001 is no longer at source-discovery stage.

Established/represented:
- ABS SA2 population and population-grid source;
- authoritative east-coast major road and rail geometry;
- ports/intermodal/airport first-pass evidence;
- deep historical/current HSR/faster-rail evidence corpus;
- recent/committed infrastructure capital seed;
- AEMO transmission/REZ first pass;
- functional water-system seed;
- industry/logistics node seed;
- cross-domain synthesis;
- a working layered-map POC under `maps/poc-001/`.

Remaining enrichment includes energy generation/storage assets, water gaps, broader industry/logistics, port catchments, transport utilisation/capacity and a clean non-double-counted capital register.

EXP-002 habitat/resource screening has begun in parallel. EXP-001 does not need exhaustive asset completeness before that work proceeds.

## Why this experiment exists

Starting with candidate cities or a high-speed rail alignment would anchor the project to a preferred answer. The base map instead gives later experiments a common evidence surface from which surprising candidate regions and constraints can emerge.

## Geographic scope

Approximately Brisbane / South East Queensland to Melbourne, including inland regions plausibly connected to a future eastern Australian urban and economic system. Do not restrict the map to existing passenger-rail corridors.

South Australia is outside EXP-001.

## Layer classes

1. Current population.
2. Existing major transport infrastructure.
3. Major infrastructure completed approximately 2015–2026.
4. Major infrastructure currently committed or under construction.
5. Credible planned infrastructure, visibly distinct from committed work.
6. Electricity generation, major transmission and Renewable Energy Zones.
7. Major water infrastructure and water-security systems.
8. Major industrial, logistics and port infrastructure.

Climate, land suitability and future habitat screening belong primarily to EXP-002.

## Hard exclusions

EXP-001 contains:

- **no VECA-proposed HSR route**;
- **no preferred candidate new cities**;
- **no settlement suitability ranking**;
- **no multi-factor weighting model**; and
- **no assumption that current CBDs are future network centres**.

Historical/current government HSR alignments may appear as evidence and must remain clearly identified as external proposals/studies.

## Evidence requirements

- Important claims and layers must have traceable source provenance.
- Prefer primary authoritative sources.
- Infrastructure status must use controlled taxonomy.
- Proposed projects must never be visually or analytically merged with committed projects.
- Public/private ownership should be captured separately where applicable.
- Dollar values should record scope and price-year basis where available.
- Evidence, inference and hypothesis must remain distinguishable.

## Mapping

`maps/poc-001/` is the current interactive evidence-view POC. It proves layer toggles, semantic zoom, time/status filtering, regional navigation and feature evidence panels.

It currently uses a small spatially enabled feature subset. Large authoritative road/rail files should be served via tiles/viewport delivery rather than loaded wholesale into the browser.

The map is a view over VECA evidence entities, not the source of truth.

## Completion interpretation

EXP-001 should be considered **sufficient to support parallel EXP-002 work**, but not closed to enrichment.

Formal close-out requires:
- all eight layer classes usable or an explicit documented gap;
- provenance/status separation;
- a coherent combined spatial view;
- findings and limitations;
- no smuggled settlement/HSR recommendation.

See `synthesis_v1.md` and root `PROJECT_STATUS_AND_ROADMAP.md` for current findings and remaining work.