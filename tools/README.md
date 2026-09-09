# Tools

Add tooling only when a research task requires it. Prefer the smallest reproducible mechanism that answers the current question.

## Current tools

The repository now contains reproducible extraction/summarisation tooling for key inherited-system layers, including ABS population and Geoscience Australia road/rail geometry, plus GitHub Actions used where direct source acquisition is more reliable in CI than in an interactive environment.

A MapLibre-based interactive evidence POC exists under `maps/poc-001/`.

These implementations solve current research needs; they do **not** pin the final VECA architecture.

## Architecture status

No permanent decision has been made on:
- production GIS/database;
- spatial serving stack;
- vector-tile/PMTiles split;
- optimisation library;
- scenario engine;
- scoring framework.

Large authoritative road/rail files should not be loaded wholesale into browser applications. A later map increment should introduce tiled/viewport delivery when EXP-002 spatial surfaces make that worthwhile.

## Repository migration note

`tools/reorganise_domains.sh` and its workflow were created for the domain-first migration. The migration staged correctly but the workflow push was blocked by GitHub workflow-update permissions. Do not assume the legacy `research/` and `data/` trees are obsolete until that migration is completed safely.

See root `PROJECT_STATUS_AND_ROADMAP.md` and `AGENTS.md` before adding new infrastructure.