# Strategic road foundation extraction validation

Source: Geoscience Australia-hosted National Roads by Geoscape.

Extracted **75,581 operational National or State Highway line features** for QLD, NSW, ACT and VIC within the broad EXP-001 envelope.

The tiled query returned 75,994 unique object IDs; 75,994 features were fetched before operational/state filtering. Explicitly out-of-scope state counts excluded: {'SA': 42}.

## Scope decision

The first base layer excludes arterials and South Australia. Earlier QA showed highway+arterial selection was too granular and a wider rectangular envelope leaked SA data. Both are now controlled at extraction time.

## Important limitations

- Geometry is not traffic volume, capacity or freight importance.
- Road importance must be enriched with NFDH traffic counts/heavy-vehicle share and state data.
- Source units are road segments, so feature counts are not road-length or capacity measures.
