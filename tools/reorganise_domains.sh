#!/usr/bin/env bash
set -euo pipefail

# Consolidate each evidence layer so its narrative, data and validation live together.
# Durable cross-domain doctrine/experiments/scenarios/tools remain top-level.
mkdir -p domains/{population,transport,energy,water,economy,land,climate}/{research,data/raw,data/derived}

# Population
for f in research/population/*.md; do [ -e "$f" ] && git mv "$f" domains/population/research/; done
[ -d data/raw/population ] && git mv data/raw/population/* domains/population/data/raw/ || true
for f in data/derived/population_*; do [ -e "$f" ] && git mv "$f" domains/population/data/derived/; done

# Transport narrative + derived evidence/data
for f in research/transport/*; do [ -e "$f" ] && git mv "$f" domains/transport/research/; done
[ -d data/derived/transport ] && git mv data/derived/transport/* domains/transport/data/derived/ || true
for f in data/derived/hsr_* data/derived/transport_system_metrics_seed.csv; do [ -e "$f" ] && git mv "$f" domains/transport/data/derived/; done

# Energy
for f in research/energy/*.md; do [ -e "$f" ] && git mv "$f" domains/energy/research/; done
[ -e data/derived/energy_zones_seed.csv ] && git mv data/derived/energy_zones_seed.csv domains/energy/data/derived/

# Cross-domain infrastructure projects stays EXP-001-wide rather than being falsely owned by transport.
mkdir -p experiments/EXP-001-east-coast-base-map/data
[ -e data/derived/infrastructure_projects_seed.csv ] && git mv data/derived/infrastructure_projects_seed.csv experiments/EXP-001-east-coast-base-map/data/

# Remove obsolete keepers where directories are now empty.
rm -f research/population/.gitkeep research/energy/.gitkeep data/derived/.gitkeep data/raw/.gitkeep

# Update known tooling/workflow paths.
grep -rlZ 'data/derived/transport/' tools .github 2>/dev/null | xargs -0 -r sed -i 's#data/derived/transport/#domains/transport/data/derived/#g'
grep -rlZ 'research/transport/' tools .github 2>/dev/null | xargs -0 -r sed -i 's#research/transport/#domains/transport/research/#g'
grep -rlZ 'data/derived/population_' tools .github 2>/dev/null | xargs -0 -r sed -i 's#data/derived/population_#domains/population/data/derived/population_#g'
grep -rlZ 'data/raw/population/' tools .github 2>/dev/null | xargs -0 -r sed -i 's#data/raw/population/#domains/population/data/raw/#g'

echo 'Domain consolidation staged.'
