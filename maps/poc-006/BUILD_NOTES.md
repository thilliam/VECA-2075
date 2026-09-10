# POC-006 full-source build notes

Run from repository root:

```powershell
python -m pip install -r tools/requirements-terrain.txt
python tools/build_map_poc004.py
python tools/build_terrain_screen.py
python -m http.server 8000
```

Then open `/maps/poc-006/`.

The terrain build streams the DEA-hosted GA elevation GeoTIFF and writes generated analytical rasters under `experiments/EXP-002-habitat-resource-screening/data/terrain/` plus the generated browser grid under `maps/poc-006/data/`. Both locations intentionally ignore generated products in Git.
