# Terrain v1 acceptance

The implementation branch is complete when code/docs/tests are merged. The **terrain data product itself** is accepted only after a full-source build records all of the following in `terrain_summary.json`:

- GA/DEA source opens successfully and produces non-empty elevation/slope surfaces;
- slope remains within 0–90 degrees;
- Brisbane, Sydney, Melbourne, Wagga Wagga, Katoomba and Mount Kosciuszko broad elevation sanity checks pass;
- elevation extrema are physically plausible for the mainland processing extent;
- map derivative contains non-zero terrain cells;
- visual inspection distinguishes inland plains from Great Dividing Range/alpine terrain;
- ocean/nodata is not presented as low-gradient developable land.

A failed source download/build is a failed acceptance, not permission to substitute heuristic elevation or geocoded terrain.
