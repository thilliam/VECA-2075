# POC-008 — Land / corridor feasibility v1

## Purpose

POC-008 adds land-use, tenure and corridor evidence to the terrain-only POC-007 Sydney–Melbourne HST candidate. It is an explainability and calibration step, not a preferred-route model.

The immediate question is not "what is the best route?" but "what horizontal evidence must a credible route model understand, and how should each observation influence later search?"

## Core rule model

Every observation is normalized into:

- `factor_class`
- `rule_role`: `hard_exclusion`, `very_high_penalty`, `soft_penalty`, `neutral_evidence`, or `positive_preference`
- dimensionless `rule_weight` used only as a tunable diagnostic lever
- source class/subtype
- source ID
- plain-language rationale

No composite score is accepted as evidence by itself. Future optimizers may consume weights, but click/detail and diagnostics must preserve the underlying factors.

## Important ownership rule

Government ownership is **not** treated as synonymous with easy or available land.

Examples:

- existing transport reservation/corridor: potentially favourable;
- government road: useful corridor evidence subject to geometry/operations;
- general Crown/government parcel: evidence only until purpose is known;
- Crown leasehold: occupied/encumbered, therefore not equivalent to vacant land;
- national park/conservation estate: near-hard exclusion in v1;
- state forest: strong constraint despite public ownership.

## Initial sources

Pinned in `research/land/land_corridor_sources_v1.json`:

- NSW Land Tenure 2024;
- NSW Government Property Index;
- NSW cadastral road and railway corridor layers;
- Vicmap Property;
- Vicmap Crown Land Tenure / government roads;
- ABS 2021 Mesh Blocks;
- ABS Urban Centres and Localities for context.

## Initial QA extraction window

`tools/build_land_corridor_screen.py` initially extracts detailed polygons within a default 50 km buffer of the POC-007 alignment. This is purely a browser/performance QA window and **must never be interpreted as a route-search corridor or exclusion of alternatives**.

The purpose is to inspect known failure areas (for example a terrain route crossing dense settlement or major infrastructure) at parcel/Mesh-Block scale before introducing these factors into route search.

## Local corridor quality / future solver doctrine

Future search must be able to preserve high-quality local corridor sections independently of the current end-to-end route. A globally optimal path can miss a sequence of excellent corridor segments if an earlier barrier diverts it away; conversely, a major bridge or tunnel may be justified to connect into a long sequence of exceptionally favourable corridor.

Therefore POC-008 rules are designed for both:

1. end-to-end route scoring; and
2. local segment/corridor scoring that can later feed corridor stitching, beam search, multi-stage graph search, dynamic programming or other higher-order optimizers.

## Build sequence

Install:

```bash
python -m pip install -r tools/requirements-land.txt
```

Inspect a downloaded source before normalizing it:

```bash
python tools/build_land_corridor_screen.py --inspect path/to/source.gdb
```

Initial NSW + ABS build:

```bash
python tools/build_land_corridor_screen.py \
  --nsw-tenure path/to/nsw_land_tenure.gdb \
  --abs-meshblocks path/to/MB_2021_AUST_GDA2020.shp
```

The script writes normalized browser layers plus `land_corridor_summary.json`, including intersections of the POC-007 path with each factor class.

Victoria normalization is intentionally gated on inspecting the downloaded Vicmap layer/field schema rather than guessing semantic fields from metadata.

## Next increments

After source-schema validation:

- normalize Vicmap Property and Crown Land Tenure;
- add explicit NSW/Victoria transport reservation/corridor polygons;
- derive major interchange/conflict footprints separately from ordinary crossings;
- annotate every POC-007 segment with encountered factors;
- visually validate the rule roles and penalties;
- only then produce the first terrain + land constrained alternative path.

Historical/proposed HSR alignments should be imported as benchmark lines and scored by this same evidence model before they are used as route preferences.
