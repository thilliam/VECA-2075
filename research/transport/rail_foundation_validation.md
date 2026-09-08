# Rail foundation extraction validation

Source: Geoscience Australia Foundation Rail Infrastructure, Railway_Lines layer.

Extracted **28,039 line features** intersecting the broad EXP-001 envelope (138.5E–154.2E, 39.8S–25.0S). The envelope is an extraction convenience, not a VECA preferred corridor.

## Network-length QA

Summing the source `length_km` attribute gives **29,284.6 km of source line-segments** across all statuses/types, of which approximately **18,948.2 km** are labelled Operational or Fully capable of operation.

By feature subtype the source contains approximately **27,940.8 km Railway**, **773.1 km Rail Siding** and **570.7 km Tramline** within the extraction envelope (all operational statuses combined).

`length_km` was missing/unparseable on 0 of 28,039 features.

These kilometre sums are more meaningful than feature counts but are still source-segment lengths, not unique corridor-km or track-km. Parallel tracks, sidings and overlapping source records can increase totals.

## Important limitations

- Foundation geometry does not measure service frequency, capacity, axle load, speed, ownership quality or freight importance.
- Usage/intensity must be layered separately from BITRE/NFDH/state/operator evidence.
- Historical/disused/dismantled records remain deliberately present and distinguishable; they may reveal corridor inheritance/option value.
- Gauge, subtype, jurisdiction and top-owner summaries are in `ga_rail_east_summary.csv`.
