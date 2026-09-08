# EXP-001 energy layer plan

## Purpose

Build a spatially coherent picture of eastern Australia's inherited and committed electricity system before VECA evaluates future settlement locations.

Energy is not a generic `renewables score`. The layer must distinguish:

1. existing generation and storage;
2. existing high-voltage transmission and interconnectors;
3. declared/planned renewable energy zones;
4. committed/anticipated transmission augmentation;
5. future/actionable transmission identified by system planners;
6. generation/storage development potential; and
7. major load opportunities/constraints relevant to future industry and AI infrastructure.

## Primary authority

AEMO's 2026 Integrated System Plan is the national system backbone. State planners (EnergyCo NSW, VicGrid, Powerlink/Queensland agencies) provide finer project and zone status.

Do not collapse these status classes. A declared REZ is geography/policy; an access right is connection entitlement; a committed generator is a project; an actionable ISP project is not the same as a line under construction.

## Initial outputs

- `data/derived/energy_zones_seed.csv` — retained/expanded zone register.
- `data/derived/transmission_projects.csv` — project/status/timing backbone from 2026 ISP plus state sources.
- `data/derived/energy_system_nodes.csv` — later generation, storage, substations and major loads.
- `research/energy_findings_v1.md` — observations/inferences/hypotheses kept separate.

## Questions for VECA

- Where is new transfer capacity already being created independent of future settlement choices?
- Which regional areas combine strong renewable resource with existing/committed transmission?
- Where is apparent generation potential stranded behind weak transfer capacity?
- Which corridors become materially better connected by 2030–35?
- Which regions could host large flexible loads (industry, hydrogen, data centres) without assuming electricity can be moved costlessly across the continent?
- Where do energy plans collide with agriculture, biodiversity, Traditional Owner interests, community acceptance or scarce water?

## Current evidence anchors — 2026-09-09

- AEMO 2026 ISP: least-cost NEM transition remains renewables connected by transmission/distribution, firmed with storage and backed by gas; the ISP provides the national optimal-development-path project taxonomy through 2050.
- NSW Central-West Orana: transmission is being built initially to operate at 4.5 GW; transfer capacity has been determined at 6 GW and aggregate generation/storage connection capacity at 7.7 GW. These are deliberately different quantities.
- NSW New England: centred around Armidale, planned initial network capacity 6 GW across two stages with potential to 8 GW by 2034.
- Victoria 2025 VTP: six onshore REZs were proposed in the plan; current VicGrid material says five zones plus the Gippsland Shoreline zone have since been declared. Treat plan-era `proposed` and later `declared` status separately.

## Guardrails

- No settlement score yet.
- No assumption that proximity to a REZ means cheap or unconstrained power.
- Do not add generation MW to transmission MW as though they are the same capacity concept.
- Preserve project timing/status and source date.
- Treat social licence, land use and environmental constraints as system constraints, not footnotes.
