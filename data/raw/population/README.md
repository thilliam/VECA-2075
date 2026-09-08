# Raw Population Sources

This directory documents the authoritative source assets for EXP-001 population work. Large upstream binaries should not be duplicated into the repository unless there is a clear reproducibility reason; preserve canonical source URLs, versions and transformations instead.

## Preferred current sources

### `SRC-ABS-SA2-ERP-2025`

ABS hosted feature layer:

`https://geo.abs.gov.au/arcgis/rest/services/Hosted/SA2_Regional_Population_2025/FeatureServer/3`

The service is native to **ASGS Edition 3** and contains:

- State / GCCSA / SA4 / SA3 / SA2 hierarchy and codes;
- SA2 polygon geometry;
- ERP for every year 2001–2025;
- 2024–25 absolute and percentage population change;
- area and 2025 population density; and
- births, deaths, internal migration and overseas migration components for 2021–22 through 2024–25.

Supported query formats include JSON and GeoJSON. The service maximum record count is 2,000, so extraction should be paginated or partitioned by state where necessary.

### `SRC-ABS-POPGRID-2025`

ABS 1 km Australian population grid for June 2025, available as GeoTIFF from the `Regional population, 2024-25` release.

Use this raster to show the actual spatial distribution of resident population at finer resolution than SA2 polygons. It complements rather than replaces the SA2 analytical dataset.

## Initial extraction scope

Retain all records from:

- Queensland — ABS state code `3`
- New South Wales — `1`
- Australian Capital Territory — `8`
- Victoria — `2`

Do not clip these records to a hand-drawn VECA corridor during raw extraction. A study-area subset should be a later, reproducible derived transformation.

## Required normalized fields

For the first derived table retain at least:

- `state_code_2021`
- `state_name_2021`
- `sa4_code_2021`
- `sa4_name_2021`
- `sa3_code_2021`
- `sa3_name_2021`
- `sa2_code_2021`
- `sa2_name_2021`
- `erp_2015`
- `erp_2024`
- `erp_2025`
- `erp_change_number_2024_25`
- `erp_change_per_cent_2024_25`
- `area_km2`
- `pop_density_2025_people_per_km2`
- source and geography-version metadata

Later demographic work can add the migration-component fields and age/sex structure without changing the baseline population layer.

## Geography rule

The first EXP-001 population layer remains native to ASGS Edition 3. ASGS Edition 4 (July 2026–June 2031) is a later geography and must not be substituted without an explicit ABS concordance/transformation step.
