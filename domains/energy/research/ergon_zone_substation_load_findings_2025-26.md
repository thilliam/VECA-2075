# Ergon zone-substation load data 2025-26 — ingestion findings

**Source:** Ergon Energy Network, Zone Substation Load Data 2025-26  
**Local source archive:** `research/energy/Ergon-Network-Substation-Load-Data-2025-26.zip`  
**Derived summary:** `domains/energy/data/derived/ergon_zone_substation_load_summary_2025-26.csv`

## What was ingested

The authoritative archive contains **265 CSV files**, one per published zone substation. Each sampled file contains half-hourly `Date`, `Time`, `MW`, `MVA` observations for 1 July 2025 through 30 June 2026. The independent archive-profile pass established the source member inventory before the extraction pass.

The extraction reconciles **265 expected / 265 extracted / 0 missing / 0 extra source-record IDs**. No substation is silently dropped.

The derived file keeps one row per source CSV and records:
- source record/file identity and substation name;
- period and valid/missing/negative row counts;
- raw reported mean, P95, P99 and peak `MW` and `MVA`;
- separate interpreted `/1000` values;
- an explicit scale/meter anomaly flag and interpretation metadata.

## Critical source-scale issue

Ergon's public documentation describes these fields as raw half-hourly **MW and MVA** on the secondary side of zone-substation transformers. However, the 2025-26 archive values are systematically three orders of magnitude above physically plausible zone-substation loads if read literally: for example, Aitkenvale reaches about 20,780 in the raw `MW` field and Cairns-area substations reach tens of thousands.

This is not an isolated spike: the first QA pass flagged 245 of 265 substations using a deliberately loose 500 reported-MW/MVA P99 threshold.

Cross-source evidence strongly supports interpreting the archive numeric values as effectively **/1000 of the literal field labels**:
- Ergon planning evidence discusses Belgian Gardens and comparable Townsville substations in ordinary tens-of-MW terms, consistent with dividing the archive values by 1000.
- Powerlink connection-point forecasts for Cairns/Townsville loads are also in tens to low hundreds of MW, again consistent with the /1000 interpretation.

VECA therefore preserves both representations:
1. `reported_*` = exact source numbers, no correction;
2. `interpreted_*` = `reported / 1000`, marked with `source_scale_interpretation=empirical_divide_by_1000_crosschecked_against_ergon_powerlink_planning_evidence`.

This is an **interpretation**, not a claimed Ergon correction notice. If Ergon later publishes clarification, update the interpretation metadata rather than overwriting the raw evidence.

## Other data-quality cautions

Ergon itself warns that these are raw SCADA/meter readings and may contain gaps, estimates, switching-related spikes/dips or metering errors. Negative load is therefore retained and counted rather than automatically clipped. P95/P99 are more useful for broad regional comparison than raw maximum alone, but neither is equivalent to firm connection capability.

## What this dataset can and cannot answer

It **can** show historical distribution-load magnitude and shape across Ergon's published zone-substation estate and can later be joined to substation locations, DAPR rated capacity and forecast demand.

It **cannot** by itself establish available headroom. Connection capability also depends on transformer/feeder ratings, upstream constraints, contingency requirements, committed connections and network configuration. Ergon's Network Load and Export Capacity Map is therefore a complementary source, not a substitute for this historical-load archive.

## Next join

The high-value next step is to join these 265 names to Ergon DAPR / network-capacity-map substation records so VECA can compare:

`historical P95/P99 load -> rated/firm capacity -> forecast load -> constraint/augmentation -> apparent headroom`

Apparent headroom must remain explicitly labelled as indicative rather than guaranteed connection capacity.
