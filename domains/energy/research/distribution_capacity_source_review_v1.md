# Distribution-network capacity source review v1

**Date:** 9 September 2026  
**Purpose:** turn the P0 DNSP entries in `assurance/source_register.json` into a concrete ingestion sequence for VECA and the map.

## Why this matters

A transmission line or REZ nearby does not prove a location can accept a major new settlement, industrial load or data centre. VECA needs local network evidence: bulk supply points, zone substations, normal/emergency capacity, forecast peak load, load at risk, constraints, retirements and planned augmentation.

The map should eventually distinguish:

- existing transmission backbone;
- distribution substations / supply points;
- spare or constrained capacity;
- forecast demand pressure;
- planned augmentation / retirement;
- connection-opportunity indicators where the DNSP itself publishes them.

No single composite `energy capacity score` should be inferred from proximity alone.

## Source review

### Energex — SEQ — highest first-pass value

Public DAPR map publishes network topology, transmission connection points, substations, sub-transmission network, forecast loads, substation/feeder capacity and constraints forecast in the next five years.

The DAPR site also exposes peak-load/capacity tables. Separately, Energex publishes annual zone-substation raw load CSVs; 2025-26 is available and contains half-hourly MW/MVA measurements by substation.

**VECA use:** SEQ is a primary settlement-growth geography and already appears heavily in the map. This source can convert `power nearby` into `local inherited electrical capacity / constraint` evidence.

**Ingestion target:** exhaustive zone-substation inventory with identity, location, capacity, current/forecast load, load-at-risk/constraint and source-year fields. Preserve raw time-series separately from annual planning attributes.

### Ergon Energy Network — regional Queensland — highest regional value

Public DAPR map publishes network topology, substations, sub-transmission/distribution feeders and forecast constraints. Published Substation Forecasts include five-year capacity/loading information for owned Bulk Supply and Zone Substations, including Normal Cyclic Capacity (MVA), contracted non-network support, 10 PoE load and load-at-risk fields.

**VECA use:** exposes regional Queensland electrical inheritance and constraint, important when comparing inland/regional options against SEQ.

**Ingestion target:** exhaustive bulk-supply/zone-substation table joined to authoritative map location/topology where possible.

### Endeavour Energy — Western Sydney / Blue Mountains / Illawarra — very high value

The Rosetta DAPR portal exposes 132/66/33 kV sub-transmission lines, zone substations, transmission substations, bulk supply points, augmentation RIT-D projects, retirement/derating projects, identified network limitations and feeder overloads.

The separate Connection Opportunity Map combines available capacity and distance from connection sources into a published connection-opportunity heatmap.

**VECA use:** particularly valuable for Western Sydney/Penrith/Blue Mountains/Illawarra comparisons and for future large-load/data-centre geography.

**Ingestion target:** first extract authoritative substation/line/limitation geometry and attributes; treat the connection-opportunity heatmap as a DNSP-published indicator, not as VECA truth or a substitute for connection studies.

### Ausgrid — Sydney / Hunter / Central Coast — high value

Ausgrid publishes annual distribution-zone-substation data in zipped CSVs, including 2025. Raw series provide historical demand/load evidence per zone substation.

**VECA use:** Sydney/Hunter/Central Coast are central to current settlement/capital comparisons; load history will help distinguish heavily utilised inherited networks from apparently nearby but constrained infrastructure.

**Ingestion target:** zone-substation inventory + latest annual load characteristics first; then DAPR augmentation/constraint context and authoritative location geometry.

### Essential Energy — regional NSW — high value

Essential Energy publishes annual raw historical zone-substation data covering its regional NSW network, with half-hourly kW/kVAr measurements, and identifies zone-substation names through its DAPR.

**VECA use:** broadest direct view of local electrical demand inheritance across many regional candidates.

**Ingestion target:** independent DAPR zone-substation inventory first, then reconcile raw-load records to that inventory; add coordinates/capacity/forecast constraints from planning sources rather than inferring them from load history.

### Victorian DNSPs — decomposition still required

AusNet, Powercor/CitiPower, United Energy and Jemena need source-by-source review because Victoria does not have one equivalent public interface across all DNSPs.

**VECA use:** required before comparing Victorian regional centres and Gippsland against NSW/QLD on equivalent local electrical-capacity evidence.

## Recommended ingestion order

1. **Energex** — best combination of strategic relevance, current capacity tables, topology and constraints.
2. **Ergon** — same data family and schema opportunity; extends coverage beyond SEQ.
3. **Endeavour** — rich spatial portal and connection-opportunity/constraint evidence.
4. **Ausgrid** — zone-substation load history + DAPR planning enrichment.
5. **Essential Energy** — regional NSW coverage; reconcile large inventory carefully.
6. **Victorian DNSPs** — decompose and normalise after the common schema has survived NSW/QLD.

## Common schema target

At minimum:

```text
substation_id
name
dnsp
jurisdiction
longitude
latitude
asset_type
voltage_kv
normal_capacity_mva
emergency_capacity_mva
current_peak_mva
forecast_peak_mva
forecast_year
load_at_risk_mva
constraint_status
constraint_year
augmentation_status
augmentation_timing
retirement_or_derating
source_year
source_id
geometry_quality
assurance_state
```

Not every DNSP publishes every field. Missing values must remain missing rather than being estimated silently.

## Assurance requirement

For each DNSP, establish an independent expected inventory before claiming completeness. Reconcile every published zone substation / bulk supply point to `mapped`, `dataset_only`, `excluded`, `duplicate` or `unresolved`. Capacity and constraint fields are decision-critical and require evidence-backed verification; a row count alone is not verification.

## Map behaviour

Suggested semantic zoom:

- zoom 3-5: only major bulk supply / constrained regions or aggregated capacity context;
- zoom 6-8: zone substations, capacity/constraint symbolisation;
- zoom 9+: detailed sub-transmission topology where available.

Never colour a whole region as `high capacity` simply because a high-voltage line or substation is nearby. Connection feasibility remains network-specific and time-dependent.
