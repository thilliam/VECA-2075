# VECA Source Coverage & Ingestion Assurance

This directory is the control plane for research-source completeness and ingestion accuracy.

The map is persuasive only if sparse areas mean "little evidence/infrastructure" rather than "we forgot to ingest it". This system tracks three related questions:

1. **Coverage:** have we identified and reviewed the important source families?
2. **Exhaustive-ingest assurance:** where a dataset claims to reproduce a source inventory, have we accounted for every expected entity and checked critical fields?
3. **Curated-synthesis assurance:** where VECA intentionally selects evidence, is every included row traceable and is the selection scope explicit enough that it cannot masquerade as a complete universe?

## Dataset kinds

Do not apply the 27/27 rule to a dataset that never claims to contain all 27 entities.

- **`exhaustive_import`** — intended to reproduce a defined source universe. It requires an independent expected inventory and exact reconciliation.
- **`curated_synthesis`** — intentionally selected evidence from one or more sources. It requires row-level provenance plus an explicit `selection_claim`, `selection_policy` and `completeness_test` in `curated_dataset_contracts.json`.
- **`support_output`** — generated QA/summary output. It inherits assurance from its upstream dataset.
- **`legacy_deprecated`** — retained for history only; non-canonical and not a new map/data input.

`provenance_reconciled` means a curated set passed its scope contract and every included row resolves to registered provenance. It does **not** mean all possible real-world entities of that class have been collected.

## Source lifecycle

Each source in `source_register.json` moves through:

`discovered -> triaged -> relevant -> ingestion_planned -> ingested -> reconciled -> verified`

`stale` means a previously useful source needs refresh. `not_relevant` means it was reviewed and intentionally excluded.

Only `verified` means the source has passed both completeness reconciliation and evidence-backed accuracy checks.

## Source types

Keep motivation/authority visible rather than collapsing everything into government intent:

- `authoritative_reality` — operating assets, statistics, authoritative geometry/data.
- `government_intent` — statutory plans, budgets, funded/approved public projects.
- `infrastructure_owner_intent` — network owner/operator forecasts and investment plans.
- `committed_private_capital` — contracted/financed/under-construction private projects.
- `private_development_pipeline` — approved or announced private projects not yet committed.
- `industry_consortium_proposition` — advocacy/industry/regional-body proposals and analysis.
- `market_analysis` — commercial research on demand, capacity, investment or constraints.
- `veca_inference` — derived VECA interpretation; never masquerades as source fact.

## The independent inventory rule

An exhaustive source cannot be marked complete by counting the rows produced by its own extractor.

For entity-bearing exhaustive sources, the manifest must establish an **independent expected inventory** first, using one of:

- `table_rows`
- `appendix_inventory`
- `api_count`
- `gis_feature_count`
- `official_index`
- `manual_inventory`

The manifest records the exact page/table/API/layer/index in `inventory.evidence_locator` and must set `independent_from_extraction: true`.

Example: a report contains 27 sites. The extraction creates 23 records. Reconciliation fails until all 27 have an explicit disposition.

## Entity dispositions

Every expected entity in an exhaustive source must land in exactly one bucket:

- `mapped` — present in the VECA spatial layer.
- `dataset_only` — intentionally present in the derived dataset but not mapped.
- `excluded` — deliberately out of scope, with reason documented by the ingest task.
- `duplicate` — alias/repeated source entry resolved to another entity.
- `unresolved` — expected entity not yet correctly resolved.

The invariant is:

`expected_count == mapped + dataset_only + excluded + duplicate + unresolved`

If `map_required: true`, `dataset_only` must be zero. A verified entity-count source must also have zero unresolved entities.

## Accuracy verification

Completeness does not prove correctness. A reconciled source can still contain wrong coordinates, capacities, statuses or dates.

Each manifest has a `verification` section. Evidence-backed checks should prioritise:

- **identity-critical:** name, location, owner/operator, status;
- **decision-critical:** capacity, MW, hectares, value, completion date, service population;
- **spatial sanity:** expected state/region, plausible town proximity, no default/HQ geocodes, no suspicious coordinate duplication.

`verification.state: passed` requires one or more checks with an evidence locator and result. For high-consequence fields, prefer independent or direct-source checking rather than simply re-reading the derived record.

## Files

- `source_register.json` — canonical cross-domain research-source backlog/status register.
- `dataset_register.json` — canonical inventory/status of every current derived dataset.
- `curated_dataset_contracts.json` — explicit scope contract for every current curated synthesis.
- `manifests/*.json` — source-specific exhaustive-ingestion/reconciliation records.
- `current_dataset_audit.md/json` — generated structural provenance audit.
- `coverage_report.md/json` — source-coverage dashboard outputs.

## Commands

```bash
python tools/validate_source_assurance.py --strict
python tools/validate_dataset_register.py
python tools/audit_current_datasets.py
python tools/sync_curated_assurance.py
```

Direct authoritative imports with independent source services can additionally use:

```bash
python tools/reconcile_direct_imports.py
```

## Migration rule for existing VECA data

Do not retroactively label existing layers `verified` merely because they look sound.

For an **exhaustive import**:

1. register the source and dataset;
2. establish the independent source inventory;
3. reconcile all derived/map entities against it;
4. record exclusions/duplicates/unresolved items explicitly;
5. perform accuracy checks;
6. only then move the source/dataset to the appropriate reconciled/verified state.

For a **curated synthesis**:

1. register the dataset;
2. make its selection claim explicit;
3. ensure every included row has resolvable source provenance;
4. state what the file does **not** claim to cover;
5. mark it `provenance_reconciled`, not `verified`, unless a later exhaustive inventory justifies a stronger claim.

## Agent completion contract

A research ingestion task is not complete merely because it writes a CSV/GeoJSON or adds map points. It should leave the dataset and source assurance records in a state that accurately describes what has and has not been proven. New derived files must be added to `dataset_register.json` in the same change.
