# Ausgrid substation capacity and demand findings — 2025 DTAPR

## Scope

The Ausgrid 2025 `Substation Capacity and Demand Forecast` workbook has been exhaustively extracted across its technical specification, recent actual-demand and five-year demand-forecast sheets.

- 177 zone substations
- 33 subtransmission substations
- 210 assets total
- 210/210 independently reconciled
- zero missing/extra/duplicate source records
- zero actual-demand or forecast join gaps

## Fields now available per asset

- voltage level
- summer/winter total capacity MVA
- summer/winter firm capacity MVA
- load-transfer capacity MVA
- annual hours above 95% peak
- embedded solar and other generation
- summer actual demand for 2022/23–2024/25
- winter actual demand for 2022–2024
- summer forecasts 2025/26–2029/30
- winter forecasts 2025–2029
- associated power factors

VECA additionally calculates a labelled arithmetic `apparent_firm_margin` = published firm capacity minus published actual/forecast MVA. This is deliberately **not** called connection headroom.

## Findings

- **20 of 210 assets** have a negative latest-season apparent firm margin in at least summer or winter.
- **22 of 210 assets** have a negative 2029 apparent firm margin in at least one season.
- Load-transfer capability materially changes the interpretation of many substations, so raw `firm capacity - demand` cannot be used as a binary connectability test.
- Zone and subtransmission assets sometimes share a locality/name and must remain separate assets; the identity key includes asset type and voltage.

## VECA implication

This is the first broad source that allows VECA to distinguish "there is electricity infrastructure nearby" from "the local network is lightly/heavily loaded relative to its published firm rating" across Sydney, the Central Coast and Hunter.

The next Ausgrid join should add:

1. system limitation records and timing;
2. committed/proposed augmentation or retirement projects;
3. DTAPR portal coordinates/geometry;
4. large-load/connection evidence where published.

Only after those joins should VECA expose a local grid-capability interpretation. A negative arithmetic margin is a strong investigation signal, not proof a connection cannot be made; a positive margin is equally not a guaranteed connection offer.
