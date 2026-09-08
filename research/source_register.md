# Source Register

The source register is the provenance spine of VECA-2075. Important evidence should be traceable back to an authoritative source and to the date/geography/status that the source actually supports.

## Source priority

Prefer primary sources in roughly this order where relevant:

1. Australian Bureau of Statistics (ABS)
2. Bureau of Meteorology (BOM)
3. Geoscience Australia
4. Infrastructure Australia
5. Australian Government departments and agencies
6. State infrastructure and planning agencies
7. Energy-market, transmission and network bodies
8. Water authorities
9. Local government where appropriate
10. Company filings and official project documents for private investment

Secondary sources are useful for discovery and context. Important claims should preferably be verified against primary material.

## Register format

One record should represent one source or clearly versioned dataset. Capture these fields where applicable:

| Field | Purpose |
|---|---|
| `source_id` | Stable local identifier |
| `title` | Dataset/document/project source title |
| `publisher` | Responsible organisation |
| `source_type` | Dataset, report, project page, filing, map, etc. |
| `url` | Canonical source location |
| `publication_date` | Date published or released |
| `data_date` | Date/period represented by the data |
| `retrieved_date` | Date VECA accessed it |
| `geographic_coverage` | Spatial scope |
| `project_status` | Controlled infrastructure status where applicable |
| `ownership` | `public`, `private`, `mixed`, or `not_applicable` |
| `reliability_authority` | Short assessment of authority and limitations |
| `dollar_value` | Reported project/investment value where relevant |
| `dollar_basis` | Nominal/real, price year and other basis if known |
| `notes` | Caveats, definitions, transformations, exclusions |

Do not invent unavailable metadata. Record `unknown` or leave the field explicitly empty according to the storage format.

## Infrastructure status taxonomy

Use only these values for infrastructure/project status:

- `completed`
- `under_construction`
- `funded_committed`
- `approved_not_started`
- `planned_high_confidence`
- `proposed`
- `cancelled`

Never mix proposed projects with committed projects in analysis or visualisation. Capture public/private ownership separately from status.

A declaration or planning-zone status that is not itself an infrastructure project — for example a declared Renewable Energy Zone — must not be forced into this project-delivery taxonomy. Store the zone/declaration status separately and apply the controlled delivery status only to actual infrastructure projects.

## Evidence discipline

A source's existence does not prove every claim made about a project. Record the precise status, cost, date and scope supported by the source. Where sources conflict, retain the conflict rather than silently selecting the most convenient figure.

Derived datasets must preserve enough provenance to reconstruct which source records and transformations produced them.

## Current implementation

Substantive sources are now being registered and used by EXP-001.

- `research/source_register.csv` is the main structured cross-domain source register.
- Domain-specific registers may supplement it where a research stream needs additional fields; for example `research/transport/transport_source_register.csv`.
- Derived datasets should carry stable `source_id` values back to these registers where practical.
- Raw archives and source contracts under `data/raw/` preserve authoritative source material when redistribution/size permits.
- Reproducible extractors under `tools/` document transformations for datasets such as ABS population and Geoscience Australia rail geometry.

This Markdown file defines provenance policy; the CSV registers contain the live source records. Do not infer research completeness from this policy page alone.
