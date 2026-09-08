# Freight utilisation — initial evidence findings

**Status:** working evidence layer. Not a settlement or corridor recommendation.

## Why utilisation must be separate from geometry

A mapped railway or highway says that a physical corridor exists. It does not say whether the corridor is economically important, heavily used, constrained, redundant, or strategically valuable.

VECA will therefore keep at least three separate concepts:

1. **physical inheritance** — road/rail/port/intermodal geometry and status;
2. **observed utilisation** — trains, tonnage, traffic counts, heavy-vehicle share, containers, passenger movements;
3. **latent/option value** — corridors or assets that may be lightly used today but strategically useful under a different 2075 settlement/economic system.

## Rail freight: NFDH is strong but deliberately incomplete

The National Freight Data Hub's Freight Train Interactive Maps combine transponder GPS data with ARTC schedules/attributes, map movements onto rail segments, and report train count, gross mass and speed. The product maintains the latest 12 months of anonymised data and suppresses low-count segment values.

Its regional freight-train dashboard is explicit that only trains running on the ARTC network are represented; local/private rail is excluded.

**VECA implication:** NFDH can support an `observed_interstate_freight_intensity` layer, but it must not be labelled `all_rail_freight_intensity`.

Sources:
- https://datahub.freightaustralia.gov.au/freight-train-interactive-maps
- https://datahub.freightaustralia.gov.au/explore-freight-data/interactives/freight-train-movements-region

## BITRE Trainline reveals the missing freight-system detail

BITRE Trainline 12 documents corridor and terminal movements that matter to VECA's spatial model.

Examples include:

- Aurizon commenced Melbourne–Sydney–Brisbane intermodal rail services in September 2023, using the Brisbane Multimodal Terminal at the Port of Brisbane.
- Regional export-container rail services feed Port Botany from centres including Narrabri, Dubbo, Coonamble, Narromine, Warren South and Wee Waa, carrying agricultural and refrigerated products.
- Earlier Trainline work notes that some Sydney–Parkes/Perth intermodal traffic uses Transport for NSW track via Lithgow and is therefore not fully captured in ARTC tonnage data.

**VECA implication:** intermodal terminals and state-network interfaces are first-order network nodes. A freight system cannot be inferred from ARTC track intensity alone.

Sources:
- https://www.bitre.gov.au/sites/default/files/documents/trainline-12.pdf
- https://www.bitre.gov.au/sites/default/files/documents/infra6384-bitre-trainline-11.pdf

## Road freight: harmonised counts are suitable for heavy-vehicle intensity, with caveats

The NFDH Harmonised Traffic Counts product aggregates annual counter data and reports heavy vehicles as a share of all traffic. It is refreshed annually.

Important limitations:
- only counters that distinguish light/heavy vehicles are included;
- geographic coverage depends on available counters;
- 2023 data is explicitly noted as incomplete in the current product;
- counts represent counter locations, not a seamless traffic model for every road segment.

**VECA implication:** use traffic counters as observed evidence and interpolate/classify cautiously. Do not turn absence of a counter into evidence of low road use.

Source: https://datahub.freightaustralia.gov.au/explore/interactives/Harmonised%20Traffic%20Counts

## Ports are inland systems, not shoreline points

NFDH provides port catchment and container-movement products specifically to show the relationship between ports and inland regions and modes.

Current scale indicators already registered for EXP-001 include:
- Port of Melbourne: ~3.39m TEU in FY2025; its 2055 strategy forecasts ~7.13m TEU under stated capacity assumptions.
- Port Botany: ~2.82m TEU in FY2025.
- Port of Brisbane: ~1.62m TEU in FY2025.

These should eventually be joined to inland origin/destination and mode-share evidence.

**VECA implication:** a regional centre may have substantial economic connection to a port hundreds of kilometres away. Distance-to-port alone is weaker than `freight_access_to_port_system`.

## A potentially important regional-city insight

The freight evidence suggests one reason existing regional centres may be stronger future candidates than apparently similar greenfield locations: some already sit at intersections of agricultural/resource catchments, rail, highway and intermodal flows.

This is an **inference to test**, not a ranking criterion yet. It could explain why locations such as Parkes, Wagga/Bomen, Albury/Wodonga, Toowoomba/Darling Downs and Hunter nodes deserve explicit inherited-network analysis even when their present populations are modest relative to capitals.

## Next data work

1. Attach NFDH heavy-vehicle/count evidence to strategic highway corridors where geographically supportable.
2. Extract ARTC freight-train intensity as a separate, explicitly coverage-limited layer.
3. Create an intermodal-terminal node register with terminal function, rail/road/port connection and status.
4. Use NFDH port-catchment/container-movement data to map inland economic reach.
5. Preserve `unknown / not covered` separately from zero use.
