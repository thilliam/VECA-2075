# Region Typology and Population-Change Drivers

**Status:** conceptual research framework. Do not assign causal labels from population change alone.

VECA needs to distinguish **what kind of region a place is** from **why its population is currently growing or shrinking**. A growth rate is an outcome, not an explanation.

## Region type — descriptive structure

A place may have more than one tag. Initial candidate types include:

- major metropolitan core;
- metropolitan middle/outer ring;
- metropolitan fringe / greenfield growth area;
- satellite / commuter-linked centre;
- large regional service centre;
- university / knowledge centre;
- lifestyle / amenity destination;
- coastal retirement / migration destination;
- tourism-dependent centre;
- mining / resources town;
- industrial / manufacturing centre;
- agricultural service centre;
- transport / logistics hub;
- defence / government centre;
- remote / small rural town; and
- mixed / transitioning economy.

These are analytical descriptors, not rankings. Byron Bay and a mining town may show similar population movement for completely different structural reasons.

## Population-change driver — causal hypothesis to evidence

For each material growth or decline pattern, later research should attempt to distinguish:

- housing supply / greenfield development;
- metropolitan spillover and commuting;
- lifestyle / amenity migration;
- retirement migration;
- remote/hybrid-work relocation;
- university/student population effects;
- resource-project expansion;
- resource-project closure or construction completion;
- industrial expansion/closure;
- defence/government investment or withdrawal;
- tourism expansion/contraction;
- agricultural restructuring;
- disaster displacement/recovery;
- housing affordability / displacement;
- infrastructure opening or accessibility change;
- natural increase;
- internal migration;
- overseas migration; and
- other / unresolved.

## Evidence discipline

`region_type` and `growth_driver` are different fields.

Example:
- `region_type = lifestyle / amenity destination`
- `observed_change = population growth`
- `growth_driver = lifestyle migration` only when migration/housing/economic evidence supports it.

Likewise:
- `region_type = mining / resources town`
- `observed_change = population decline`
- `growth_driver = mine closure` only when project/employment/migration evidence supports that causal claim.

Do not infer either example merely from the town name or reputation.

A population trend should eventually be decomposed where data permits into natural increase, net internal migration and net overseas migration, then supplemented with employment, housing, project and local evidence.

## Why this matters for VECA

Current trend persistence has very different implications depending on cause.

- Greenfield fringe growth may demonstrate available housing supply rather than inherent 2075 desirability.
- Amenity-led growth may reveal voluntary migration preferences relevant to VECA's revealed-attractiveness principle.
- Resource-boom growth may be economically powerful but cyclically concentrated.
- Resource-closure decline may say little about the physical suitability of the location for a different future economy.
- Decline caused by ageing/natural decrease is analytically different from working-age out-migration.
- A regional service centre gaining population from its hinterland can grow while the wider region becomes more spatially concentrated.

VECA should therefore avoid both errors: assuming today's fast-growing places are automatically future winners, and assuming today's declining places are inherently unsuitable.

## Future normalized fields

Candidate fields for later regional analysis:

- `region_id`
- `region_name`
- `region_type_primary`
- `region_type_secondary`
- `population_trend_period`
- `population_change_abs`
- `population_change_pct`
- `natural_increase`
- `net_internal_migration`
- `net_overseas_migration`
- `growth_driver_primary`
- `growth_driver_secondary`
- `driver_evidence_source_ids`
- `driver_confidence`
- `structural_or_cyclical`
- `notes`

No typology score or causal classification is authorised yet.
