# VECA Source Coverage & Ingestion Assurance

This directory is the control plane for research-source completeness and ingestion accuracy.

The map is persuasive only if sparse areas mean "little evidence/infrastructure" rather than "we forgot to ingest it". This system therefore tracks two independent questions:

1. **Coverage:** have we identified and reviewed the important source families?
2. **Ingestion assurance:** for every source we use, have we accounted for every expected entity and verified critical fields?

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

A source cannot be marked complete by counting the rows produced by its own extractor.

For entity-bearing sources, the manifest must establish an **independent expected inventory** first, using one of:

- `table_rows`
- `appendix_inventory`
- `api_count`
- `gis_feature_count`
- `official_index`
- `manual_inventory`

The manifest records the exact page/table/API/layer/index in `inventory.evidence_locator` and must set `independent_from_extraction: true`.

Example: a report contains 27 sites. The extraction creates 23 records. Reconciliation fails until all 27 have an explicit disposition.

## Entity dispositions

Every expected entity must land in exactly one bucket:

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

- `source_register.json` — canonical research-source backlog and status register.
- `manifests/*.json` — one ingestion/reconciliation record per ingested source.
- `manifests/_template.json` — copy for a new ingestion.
- `coverage_report.md` / `coverage_report.json` — generated dashboard outputs.
- `../tools/validate_source_assurance.py` — stdlib-only validator and report generator.

## Commands

Validate structural and reconciliation rules:

```bash
python tools/validate_source_assurance.py
```

Apply stricter verified/reconciled rules:

```bash
python tools/validate_source_assurance.py --strict
```

Generate the dashboard after a successful update:

```bash
python tools/validate_source_assurance.py --strict --write-report
```

## Migration rule for existing VECA data

Do not retroactively label existing layers `verified` merely because they look sound.

For each existing source:

1. add/register the source;
2. establish the independent source inventory;
3. reconcile existing derived/map entities against that inventory;
4. record exclusions/duplicates/unresolved items explicitly;
5. perform accuracy checks;
6. only then move the source to `verified`.

This allows current map work to continue while making uncertainty and incomplete migration visible.

## Agent completion contract

A research ingestion task is not complete merely because it writes a CSV/GeoJSON or adds map points. It should leave:

- a source-register status update;
- an ingestion manifest;
- all expected source entities explicitly accounted for;
- evidence-backed verification checks;
- known gaps captured in the register;
- a passing `python tools/validate_source_assurance.py --strict` once the source is declared reconciled/verified.
