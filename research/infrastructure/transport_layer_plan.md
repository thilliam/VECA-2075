# EXP-001 transport base-layer plan

**Status:** active after completion of the first population source layer.

## Purpose

Build a factual picture of the inherited east-coast transport system before VECA proposes any future settlement pattern or high-speed rail network.

The transport layer must distinguish **physical infrastructure**, **actual network use**, **service/accessibility**, and **committed future changes**. A line on a map is not evidence of useful capacity.

## Base physical network

Initial classes:

- major roads and motorways;
- passenger rail corridors;
- freight rail corridors;
- airports;
- seaports;
- intermodal freight terminals; and
- major existing crossings / constrained links where authoritative data permits.

### National foundation source

Geoscience Australia's contemporary AUSTopo / foundation mapping is the preferred first national geometry source for roads, rail and aviation where practical. GA reports its current 1:250,000 mapping uses Road and Rail Transport data current to 2023 and Air Transport data current to 2023.

This is a national base-map source, not evidence of capacity or service quality.

## Network-use overlays

### Freight rail

Use the National Freight Data Hub (NFDH) freight-train products for observed train movements, train count/tonnage and speed where available.

The NFDH combines locomotive GPS/transponder data with ARTC schedules/attributes and assigns movements to a foundation rail map at rail-segment level.

Important limitation: this is strongest for trains using the ARTC/interstate network. It does not represent all local/private/intrastate rail movements and must not be labelled as complete national rail activity.

### Roads

Use NFDH harmonised traffic counts and heavy-vehicle data where useful, supplemented by state road agencies where national coverage is incomplete.

### Ports / freight gateways

Use NFDH imports/exports, volume-versus-value, port catchment and container products to distinguish gateway importance from merely having a port symbol on the map.

### Airports

Use BITRE airport traffic series to capture passenger and aircraft movements; international-airline activity data can later distinguish international passenger/freight connectivity.

The 2026 BITRE release contains annual airport traffic through 2025 and monthly top-20 airport traffic through April 2026.

## Passenger accessibility

Physical rail geometry alone is insufficient. Later derived fields should distinguish, where authoritative service data are obtainable:

- intercity passenger service exists;
- approximate service frequency;
- travel time between major centres;
- electrified / non-electrified where relevant;
- metropolitan rapid-transit access;
- airport passenger access; and
- major known capacity constraint.

Do not attempt a national timetable model in EXP-001 unless the base map demonstrates that it is necessary.

## Infrastructure status overlay

Existing transport network geometry must remain separate from projects classified under VECA's controlled status taxonomy:

- completed;
- under_construction;
- funded_committed;
- approved_not_started;
- planned_high_confidence;
- proposed; and
- cancelled.

Examples already registered include Cross River Rail, Inland Rail delivery sections, Sydney Metro West, Melbourne Metro Tunnel and North East Link.

## Derived analytical questions

The first transport map should enable questions such as:

- Which regional centres already sit on more than one major transport mode?
- Which corridors carry national freight versus mainly local passenger traffic?
- Where are airports and ports already creating non-CBD economic gravity?
- Which inland centres possess inherited road/rail connectivity that current population alone understates?
- Which metropolitan fringes require expensive new connectivity simply to remain attached to the existing city?
- Where has recent capital materially changed the inherited network?

These are observations/inferences only. Do not convert them into a proposed HSR alignment or settlement ranking during EXP-001.

## Extraction sequence

1. Obtain national road/rail/aviation geometry suitable for east-coast clipping.
2. Retain QLD/NSW/ACT/VIC coverage first; clip transparently to VECA scope only as a derived step.
3. Identify and classify airports, ports and major intermodal terminals.
4. Add NFDH observed freight use to the rail network where coverage exists.
5. Add road traffic/heavy-vehicle indicators where usable.
6. Add passenger rail/service attributes only after the physical base is coherent.
7. Overlay completed/committed/planned transport projects with project status kept separate from existing assets.
8. Record data gaps explicitly rather than fabricating completeness.

## Source limitations to preserve

- GA foundation geometry describes existence/location, not capacity.
- NFDH rail movement data are not complete for all Australian intrastate/private rail.
- Current traffic volumes do not by themselves measure strategic 2075 value.
- Airport passenger totals do not capture all freight, defence, general aviation or future airport potential.
- Port throughput can be dominated by a specialised bulk commodity and therefore should not automatically be treated as diversified economic connectivity.
