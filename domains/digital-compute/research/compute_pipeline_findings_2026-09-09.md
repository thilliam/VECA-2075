# Digital compute / data-centre pipeline — first east-coast sweep

**Date:** 9 September 2026  
**Status:** operator-primary-source first pass; selective but broad campus coverage, not a complete planning-approval census.

## Why this matters to VECA

Data centres are simultaneously:

- very large new electricity loads;
- consumers/competitors for scarce powered industrial land;
- fibre/connectivity anchors;
- high-value private capital commitments;
- potential drivers of grid augmentation;
- possible low-direct-employment but high-economic-infrastructure nodes;
- water/cooling users whose requirements vary materially by design.

They therefore belong in both the inherited/future-capital map and later AI-location stress tests. They must not be reduced to a generic `technology jobs` point layer.

## Scale already visible from primary operator sources

The first structured sweep contains 33 records across NEXTDC, AirTrunk, CDC and Goodman, including one portfolio-contract record that is intentionally not a physical map asset.

Examples of individual future or expanding campuses include:

- NEXTDC S7 Eastern Creek — **550+ MW** planned power;
- AirTrunk SYD3 Western Sydney — **400+ MW** campus capacity;
- CDC Marsden Park — **504 MW** planned ICT capacity, with the operator describing scalability toward 1 GW;
- AirTrunk MEL2 — **354+ MW**, more than A$5 billion announced direct investment;
- CDC Laverton — **400+ MW** upon completion;
- CDC Brooklyn — **350+ MW** upon completion;
- NEXTDC M3 West Footscray — **225 MW** planned capacity;
- AirTrunk MEL1 — **185+ MW**;
- Goodman SYD01 Artarmon — **90 MW secured utility power supporting 61 MW IT capacity**.

The important observation is not their sum. The capacity definitions differ and the projects sit at different stages. The evidence shows that future compute demand is already large enough to shape electricity, industrial-land and infrastructure planning.

## Geography

The current pipeline remains highly metropolitan, especially Western Sydney and western/north-western Melbourne. However, smaller established or planned nodes exist in:

- Canberra;
- Geelong;
- Sunshine Coast;
- Gold Coast.

These matter because VECA should test whether future compute must remain concentrated near today's hyperscale clusters or whether power/fibre/water/land availability could support larger regional nodes.

## Power is the scarce enabling asset

The operator evidence repeatedly exposes power as a first-class development variable:

- AirTrunk publishes 132 kV feeds for Sydney campuses and 66 kV feeds for Melbourne campuses;
- SYD2 has been supported by a dedicated 200 MVA 132 kV substation;
- Goodman describes SYD01 primarily through **90 MW of secured utility power** in a supply-constrained market;
- NEXTDC's pipeline contains several campuses in the 150–550+ MW range.

This validates the sequencing of the VECA data work: DNSP/sub-transmission capacity and compute pipeline should be analysed together.

## Capacity definitions must remain separate

The dataset deliberately records a `capacity_definition` because the following are not interchangeable:

- utility/secured power MW;
- IT load MW;
- total campus capacity;
- planned ultimate capacity;
- built capacity;
- capacity currently being fitted out;
- contracted customer capacity.

For example, Goodman SYD01 reports 90 MW secured utility power but 61 MW IT capacity. CDC's May 2026 555 MW contract is customer-contracted capacity delivered across multiple campuses, not a new 555 MW physical site.

No VECA aggregate should sum these quantities without normalization and explicit scope.

## Water/cooling is not uniform

Data-centre water burden should not be inferred from MW alone. Operator designs vary materially. AirTrunk promotes lower-water designs at newer facilities and CDC reports closed-loop liquid cooling with very low operational water use at Brooklyn. Later analysis should therefore capture cooling technology, WUE where published, potable/non-potable source and heat-reuse potential rather than applying one generic water factor.

## Settlement implications — evidence, not conclusion

The first pass creates several hypotheses to test later:

1. **Compute can deepen metro grid lock-in.** Hundreds of MW of new committed/private load may consume network capacity that otherwise appears available for housing, industry or electrification.
2. **Compute can justify new grid capital.** Large anchor loads can make substations/transmission/fibre investment viable in new locations.
3. **Regional compute is technically plausible but currently weakly evidenced at hyperscale.** Geelong, Canberra and Sunshine Coast are useful footholds; the very largest announced campuses remain in Sydney/Melbourne.
4. **Operational employment is not proportional to capital/MW.** Compute should be treated as enabling economic infrastructure, not automatically as a mass-employment industry.
5. **AI may alter location economics.** Training, inference, sovereign workloads and latency-sensitive services may have different geography. VECA should preserve those distinctions rather than assuming one future data-centre archetype.

## Next compute ingestion work

- add planning-approval/system pipeline sources to capture projects beyond the four operators in this first pass;
- add precise coordinates/site polygons where authoritative planning data permits;
- connect campuses to DNSP/transmission assets without claiming a connection capacity unless explicitly sourced;
- add fibre/backbone/subsea-cable context;
- capture cooling/water source and WUE where published;
- add market-level capacity/demand evidence separately from asset records;
- build change detection because campus ultimate MW and status change rapidly.
