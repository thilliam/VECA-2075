# EXP-001 Source Reconnaissance — 2026-09-08

**Classification:** research inventory. This document records sources and methodological choices; it is not a settlement finding.

## Population

The first population layer should use ABS Estimated Resident Population (ERP) rather than Census counts. The current authoritative release is `Regional population by age and sex, 2024` (`SRC-ABS-POP-2024`), with SA2-level estimates at 30 June 2024.

A geography-version issue must be handled explicitly. The 2024 population release is based on the 2021-era ASGS geography, while ABS released ASGS Edition 4 boundaries for 2026–2031 in July 2026 (`SRC-ABS-ASGS-2026`). We should either:

1. build the initial population layer on the geography native to the 2024 ERP data; or
2. apply an explicit ABS concordance before moving to 2026 boundaries.

Do **not** join SA2 names alone or silently place 2024 values onto changed 2026 polygons.

## Existing transport and freight

Two national Commonwealth foundations have been registered:

- BITRE's `Australian Infrastructure and Transport Statistics—Yearbook 2025` (`SRC-BITRE-YB-2025`) for nationally consistent transport/infrastructure statistics; and
- the National Freight Data Hub (`SRC-NFDH-2026`) for spatial and operational freight evidence, including freight-train maps, traffic counts, road condition/expenditure and freight performance.

These should be complemented with state/operator geospatial network files where national products do not provide sufficiently precise geometry.

## Recent and committed infrastructure

Infrastructure Australia's 2025 Market Capacity Report (`SRC-IA-MCAP-2025`) provides a national five-year Major Public Infrastructure Pipeline of $242 billion. It is useful context for capital demand and sector/regional momentum, but **must not become a settlement score**. High spending can reflect legacy congestion remediation as easily as strategic enabling capacity.

A first project seed dataset is in `data/derived/infrastructure_projects_seed.csv`. It intentionally includes recent-completed projects as well as current construction because EXP-001 asks where capital has accumulated since roughly 2015.

## Energy

NSW has a particularly clear current primary source: EnergyCo identifies five declared REZs (`SRC-NSW-REZ-2026`). Central-West Orana transmission is already under construction (`SRC-NSW-CWO-2026`).

Victoria's 2025 Transmission Plan identifies six **proposed** REZs (`SRC-VIC-TRANS-2025`). They remain proposed in the seed dataset and are not visually or analytically equivalent to committed NSW infrastructure.

Queensland requires temporal care. The earlier REZ Roadmap identified 12 potential locations (`SRC-QLD-REZ-2024`), but the Energy Roadmap Amendment Act 2025 altered the framework and terminology (`SRC-QLD-ENERGY-AMEND-2025`). The initial dataset therefore retains the 12-zone concept only as a legacy/planning record until the post-amendment regional-energy-hub geography and project status are individually verified.

## Water

Water is deliberately not yet reduced to a single national layer. The initial search confirms that useful evidence is split among state bulk-water authorities, regional water strategies, dam/catchment datasets and infrastructure operators. The next tranche should create separate records for:

- physical assets: dams, storages, desalination, recycling and major pipelines;
- system connectivity: water grids and transfer capacity;
- yield/security: reliable yield and drought/security indicators rather than storage percentage alone; and
- future augmentation: committed versus proposed projects.

Current dam level is a poor long-horizon settlement metric and must not be confused with sustainable system yield.

## Immediate next extraction tasks

1. Download/transform ABS SA2 ERP 2024 and matching native SA2 geometry.
2. Build the national transport geometry inventory and identify gaps requiring state datasets.
3. Expand the infrastructure project register systematically across QLD, NSW, ACT and VIC, including major private capital.
4. Extract current post-2025 Queensland energy-hub/project geography.
5. Build the first water-asset and water-system register.
6. Add ports, airports and intermodal terminals as explicit point/area assets.

## Premature decisions still avoided

No GIS stack, database, application framework, map host, scoring weights, candidate cities or HSR route has been selected. CSV is being used only as a portable first normalization format; it is not an architecture decision.
