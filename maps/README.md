# Maps

Spatial outputs live here. `layers/` is reserved for layer definitions or small derived spatial artefacts appropriate for Git.

## Interactive mapping

`poc-001/` is the first runnable VECA layered-map explorer. It uses MapLibre GL JS and a small spatially enabled subset of the existing corpus to prove layer toggles, semantic zoom, time/status filtering, regional navigation and feature-level evidence inspection.

The POC is intentionally lightweight. Large authoritative source files such as the east-coast Geoscience Australia rail and road extracts should not be loaded wholesale into the browser; the next mapping increment should introduce tiled delivery (PostGIS/vector tiles and/or PMTiles).

See `poc-001/README.md` for scope, run instructions and the proposed production boundary.
