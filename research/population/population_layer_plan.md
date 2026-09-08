# EXP-001 Population Layer — Extraction Plan

**Status:** active research, 2026-09-08.

## Baseline source decision

Use the ABS `Regional population, 2024–25` Estimated Resident Population (ERP) release as the current population baseline. The release provides population estimates by SA2 and above for 2001–2025 and an Australian population grid for 2025.

This supersedes the initial reconnaissance reference to the 2024 age-and-sex release as the preferred current baseline. The age-and-sex product remains useful for demographic structure; the 2024–25 Regional Population product is preferable for the main current-population layer because it is newer and includes 2025 ERP.

## Two complementary population representations

### 1. SA2 population layer

Use the ABS SA2-and-above ERP workbook as the main analytical population table.

Purpose:
- comparable population totals by statistical area;
- growth over time;
- aggregation into functional/candidate regions later;
- population inherited by existing towns and urban systems.

Do not treat current SA2 population as a suitability score.

### 2. 2025 population grid

Use the ABS 2025 population grid as the spatial-density representation.

Purpose:
- show where population actually occupies space rather than colouring whole administrative/statistical polygons uniformly;
- identify settlement continuity, sparse corridors and urban edges;
- provide a neutral base for later overlays.

The grid is a derived/modelled spatial representation of ERP and should not be treated as address-level population truth.

## Geography/version discipline

The current Regional Population release uses ASGS statistical areas associated with the release. ABS also released ASGS Edition 4 boundaries for July 2026–June 2031. Do not silently combine population values and boundary editions.

For the first layer:
1. retain ABS geography codes exactly as supplied with the population data;
2. record the ASGS edition/version used by every geometry file;
3. use a concordance if population data is transferred to a newer geography;
4. never join on SA2 name alone when a stable code is available.

## Derived schema

The normalized SA2 population dataset should contain at least:

- `sa2_code`
- `sa2_name`
- `state`
- `erp_2025`
- `erp_2024`
- `erp_2015` where available
- `growth_2024_25_abs`
- `growth_2024_25_pct`
- `growth_2015_25_abs`
- `growth_2015_25_pct`
- `source_id`
- `geography_version`

Do not manufacture missing historic values where ABS geography changes prevent direct comparison. Preserve source-provided series/concordances and flag discontinuities.

## East-coast extraction scope

Retain complete SA2 records for Queensland, New South Wales, ACT and Victoria during raw normalization. Geographic clipping to the VECA study area should occur as a transparent derived step rather than deleting potentially relevant inland records at ingestion.

This preserves our ability to discover unexpected candidate regions and avoids defining the answer through an early hand-drawn corridor.

## Next actions

1. Register the 2024–25 Regional Population release and 2025 population grid as sources.
2. Acquire the SA2 ERP workbook and population-grid asset.
3. Normalize the SA2 series into a machine-readable table.
4. Obtain the matching native SA2 geometry.
5. Produce an east-coast subset only after retaining the full four-jurisdiction normalized source.
6. Inspect the resulting density/growth patterns before adding any settlement interpretation.
