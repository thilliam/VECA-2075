# POC-003 — Population, Settlements & Landscape

POC-003 extends the real transport foundation with the human and physical geography needed for VECA analysis.

## What it proves

- **Population is a surface, not a point layer.** The builder joins VECA's ABS 2025 SA2 ERP table to authoritative ASGS 2021 SA2 geometry.
- **Settlements are a semantic hierarchy.** ABS Urban Centres and Localities are ranked by 2021 Census population and culled progressively by zoom.
- **Metropolitan sub-centres are explicit exceptions.** Contiguous capital-city UCLs do not expose centres such as Parramatta and Penrith, so POC-003 derives those two validation cases from matching SA2 geography and marks them as VECA functional sub-centres rather than pretending they are separate ABS UCLs.
- **Landscape context stays external.** Satellite imagery and ABARES land-use are live contextual raster services; VECA does not duplicate their national raster payloads in Git.
- **Transport remains context.** POC-003 reuses POC-002 real rail and major-road derivatives.

## Sources

- ABS Regional Population 2024-25 (`data/derived/population_sa2_east.csv`)
- ABS ASGS Edition 3 SA2 FeatureServer
- ABS ASGS Edition 3 Urban Centres and Localities FeatureServer
- ABS 2021 Census General Community Profile DataPack for UCL
- ABARES / Digital Atlas of Australia: Land use of Australia 2020-21 v7.1 simplified image service
- Esri World Imagery for satellite context

## Build and run

From repo root:

```bash
python tools/build_map_poc003.py
python -m http.server 8000
```

Then open:

```text
http://localhost:8000/maps/poc-003/
```

`build_map_poc003.py` first runs the POC-002 builder, so the real rail/road derivatives are refreshed automatically.

## Expected controls

### Base map
- Standard
- Satellite

### Landscape
- ABARES land use 2020-21

### Population & settlement
- 2025 SA2 population density
- 2020-25 population growth
- ranked towns / centres

### Transport context
- rail
- major roads

## Settlement hierarchy

The POC uses a transparent first-pass population hierarchy:

| Rank | 2021 UCL population | First visible zoom |
|---|---:|---:|
| 1 | 1,000,000+ | 3 |
| 2 | 250,000+ | 4 |
| 3 | 50,000+ | 5 |
| 4 | 10,000+ | 6 |
| 5 | 2,000+ | 7 |
| 6 | under 2,000 | 8 |

This is intentionally not the final VECA centre-importance model. Population is only one signal. Later versions should combine service catchment, health/education role, employment, transport connectivity, remoteness and government intent.

## Important limitations

- SA2 density is an area-average choropleth. Large rural SA2s can visually imply population where nobody lives. The later population-grid layer should improve this substantially.
- UCL centres use a lightweight bounds-centre point for labeling, not a settlement CBD coordinate.
- Parramatta and Penrith are first validation exceptions, not a complete metropolitan-centre classification.
- Satellite imagery is visual evidence/context, not a land-use classification.
- ABARES national land use is appropriate for strategic context; catchment-scale mapping should replace it for detailed local candidate evaluation where available.
- Raster-service availability depends on the upstream providers and internet access.

## Next likely layer

After validating this POC visually, the next population improvement should be a **fine population grid / inhabited-footprint surface** so broad rural SA2 polygons do not overstate occupied land. Terrain/elevation/slope should follow as the next landscape constraint layer.
