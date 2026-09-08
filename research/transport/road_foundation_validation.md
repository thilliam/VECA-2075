# Strategic road foundation extraction validation

Source: Geoscience Australia-hosted National Roads by Geoscape.

Extracted **79,882 operational National or State Highway line features** intersecting the broad EXP-001 envelope.

The tiled spatial/hierarchy query returned 80,254 unique object IDs before client-side operational-status filtering, using 20 small spatial tiles.

## Scope decision

The first base layer deliberately excludes arterials, sub-arterials, collectors and local streets. A previous test showed highway+arterial selection produced about 220,000 segments, which is too granular for EXP-001's inter-regional inherited-system map. Arterials should be introduced later for city/access analysis.

## Important limitations

- Geometry is not traffic volume, capacity or strategic freight importance.
- Road importance must be enriched with NFDH traffic counts/heavy-vehicle share and state data.
- The broad extraction envelope is not a future settlement or transport corridor.
- Source units are road segments, so feature counts are not road-length or capacity measures.
