# Distribution capacity findings — first DNSP sweep

**Date:** 9 September 2026  
**Status:** first ingestion slice; not a complete east-coast substation census.

## Why this layer matters

VECA previously had transmission projects and REZ geography, but transmission proximity is not the same thing as usable local connection capacity. Distribution and sub-transmission networks determine whether a settlement/industry/compute load can actually be served without major new local works.

The first DNSP sweep confirms that the useful unit is not a simple `spare MW` number. A location can be constrained by transformer ratings, N-1 criteria, feeder limits, voltage, protection/REFCL requirements, retirement, or upstream supply. Conversely, a planned new zone substation may be deliberate enabling infrastructure for a growth precinct rather than evidence of current spare capacity.

## Initial findings

### Western Sydney: power infrastructure is being used to manufacture new economic geography

Endeavour Energy's Aerotropolis program is unusually explicit:

- North Bradfield and Badgerys Creek project assessments specify new zone substations with **2 x 45 MVA** transformer configurations and new 132 kV supplies.
- Western Sydney Airport now has a commissioned 132 kV transmission substation designed to scale with airport expansion.
- A new airport zone substation is tied to Burra Park logistics/industrial development, Agribusiness North and Science Park.
- An approximately **30 km underground 132 kV backbone** is being staged through multiple Aerotropolis growth precincts.

For VECA this is evidence that local grid capital can be a city-shaping input, not merely a response to existing population.

### Southern Highlands: compute/industry demand is already creating new network nodes

The Berrima Junction project requires a new **33/11 kV 35 MVA** zone substation and associated feeder/fibre works to serve an enterprise growth area that explicitly includes a new data centre and industrial development.

This is an important coupling: a regional location's future economic role can depend on power capacity and fibre being created together.

### Victoria: inherited assets can carry both opportunity and liability

AusNet's DAPR shows several different reasons for future capital:

- Clyde North: augmentation associated with demand growth;
- Wollert and Pakenham South: proposed new zone substations associated with growth/industrial development;
- Wonthaggi: augmentation driven by load growth plus REFCL/network-operating requirements;
- Bairnsdale and Lilydale: further augmentation linked to technical compliance/capacitance growth.

VECA should therefore distinguish at least:

1. `growth_enabling_capacity`;
2. `demand_driven_augmentation`;
3. `replacement_or_compliance_liability`;
4. `constraint_without_committed_solution`;
5. `existing_capacity_observation`.

These categories have very different implications for future settlement economics.

## Source/data architecture discovered

The DNSP source family is richer and more machine-readable than a PDF-only research process would imply:

- **Ausgrid:** substation capacity/demand forecasts, feeder forecasts, retirement plans, system limitations and 11 kV feeder-capacity tables.
- **Ergon:** BSP/zone-substation forecasts and capacity tables, transmission-connection forecasts, feeder forecasts, committed/proposed limitation workbooks and an interactive constraint/capacity map.
- **Energex:** current and historical zone-substation raw MW/MVA load packages plus DAPR planning tables.
- **Essential Energy:** raw historical zone-substation load plus DAPR asset/constraint planning.
- **Endeavour Energy:** Rosetta portal exposing substations, sub-transmission, RIT-D projects, limitations and feeder overloads.
- **AusNet, Powercor/CitiPower, United Energy, Jemena:** DAPR/network-planning sources with zone-substation forecasts, limitations, projects and/or historical load.

This justifies a dedicated reproducible ingestion pipeline rather than manual project-by-project research.

## Guardrails

- Apparent `rating - peak load` is **not** guaranteed connection headroom.
- Preserve PoE/scenario and N/N-1 definitions; do not mix them.
- Raw load data can contain metering gaps, switching spikes and confidentiality omissions.
- A planned augmentation is not current capacity.
- Technical/compliance augmentation is not the same thing as growth capital.
- Single-large-customer substations may be excluded or confidential, which is particularly relevant to data centres and industrial loads.

## Next extraction step

Build an exhaustive machine import for the operators with downloadable tables, starting with:

1. Ergon BSP + zone-substation forecasts/capacity and limitation workbooks;
2. Ausgrid substation capacity/demand forecast and system limitations;
3. Energex zone-substation load package + current DAPR capacity tables;
4. Essential Energy zone-substation inventory/load and limitation tables;
5. then Endeavour/Victorian digital-map or report-derived inventories.

Each exhaustive source must independently reconcile its source IDs/counts before being labelled complete.
