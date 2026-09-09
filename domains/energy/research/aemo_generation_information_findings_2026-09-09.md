# AEMO generation and storage asset findings — July 2026 source

## Scope and assurance

AEMO's July 2026 NEM Generation Information workbook was exhaustively extracted for NEM regions NSW1, QLD1 and VIC1. The unit-level source layer contains **1,415 rows** across **165 source columns**. Independent openpyxl inventory and separate stdlib/XML extraction reconcile exactly: zero missing, extra or duplicate composite source records.

AEMO's `Gen Info Unit ID` is not by itself unique in the published worksheet. VECA therefore retains it but uses a source-native composite identity of Gen Info Unit ID + Survey ID + Unit Name + DUID + Technology Type + Technology Detail for source-record reconciliation.

## What the source contains

The source retains site/unit identity, owner/custodian, NEM region, site and unit generation capacity, AC/DC nameplate capacity, storage MWh, technology/fuel detail, dispatch type, AEMO commitment status, commercial-use/closure timing, and seasonal scheduled generation/storage capacity through the published horizon.

Scoped row counts:

- NSW1: **570**
- QLD1: **469**
- VIC1: **376**

Technology rows:

- Battery Storage: **524**
- Solar PV: **314**
- Wind: **248**
- Gas Turbine: **129**
- Hydro: **113**
- Coal: **44**
- Other: **43**

Commitment/status rows:

- In Service: **459**
- In Commissioning: **28**
- Committed: **38**
- Committed*: **13**
- Anticipated: **94**
- Publicly Announced: **768**
- Announced Withdrawal: **14**
- Withdrawn: **1**

## VECA implications

1. **The project pipeline is much larger than operating inheritance.** More than half the scoped source rows are merely `Publicly Announced`. These must not render with the same semantics as `In Service` or `Committed` assets.
2. **Storage is now a first-class inherited-system family.** Battery rows are the largest technology category in the source observations. Power capacity (MW) and storage energy (MWh) must remain distinct.
3. **Site-level mapping should be derived, not substituted for the source layer.** Multiple unit/technology records can belong to one AEMO Survey ID/site. A future map derivative should aggregate by site while preserving links to every unit-level source observation.
4. **ACT cannot be isolated from the Region field alone.** AEMO assigns ACT-connected assets within NSW1; ACT-specific filtering requires a site/location/KCI join.
5. **Reconciled ingestion is not truth verification.** AEMO explicitly publishes owner/operator/developer-submitted future-project data and warns that forecasts may contain errors or omissions. VECA preserves those source statuses rather than upgrading them.

## Next enrichment

- Join AEMO Survey ID / KCI identity to site geography and connection-point evidence.
- Produce a map-ready site derivative with separate existing / commissioning / committed / anticipated / publicly-announced / withdrawal states.
- Preserve MW generation capacity and MWh storage capacity independently.
- Use site geography to examine generation/storage inheritance around candidate regional systems without treating nearby generation as guaranteed local connection headroom.
