# Terrain build runbook

1. `python -m pip install -r tools/requirements-terrain.txt`
2. `python -m unittest tests.test_terrain_screen`
3. `python tools/build_terrain_screen.py`
4. Inspect `experiments/EXP-002-habitat-resource-screening/data/terrain/terrain_summary.json`.
5. Run `python -m http.server 8000` and inspect `/maps/poc-006/`.
6. Accept only if `terrain_buildability_acceptance_v1.md` passes.
