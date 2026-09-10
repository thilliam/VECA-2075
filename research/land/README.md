# Land / corridor source acquisition

Raw authoritative source files stay local and are not committed to Git. POC-008 writes normalized browser derivatives under `maps/poc-008/data/`, which are also generated/local by default.

## First two sources to download

### 1. NSW Land Tenure 2024

Direct authoritative SEED download:

`https://datasets.seed.nsw.gov.au/dataset/6884bc76-7b9d-4fcc-b3cc-a3416699dcb5/resource/d4e3fc9c-11f8-433c-8fe1-751148136635/download/nswlandtenure_dec2024_v2_seed.gdb.zip`

Suggested local destination after extraction:

`research/source/land/nsw_land_tenure_2024/`

Do not rely on this source alone for Greater Sydney roads/public-space tenure; its own documentation flags incomplete mapping there. Explicit NSW road/rail corridor layers are a follow-up source.

### 2. ABS Mesh Blocks 2021, GDA2020

Authoritative ABS download:

`https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs/edition-3-july-2021-june-2026/access-and-downloads/digital-boundary-files/MB_2021_AUST_SHP_GDA2020.zip`

Suggested local destination after extraction:

`research/source/land/abs_meshblocks_2021/`

The expected category field is `MB_CAT21`; relevant values include Residential, Commercial, Industrial, Parkland, Education, Hospital/Medical and Transport.

## Inspect before normalizing

Install dependencies once:

```powershell
python -m pip install -r tools/requirements-land.txt
```

Then inspect the actual downloaded source schema rather than guessing layer/field names:

```powershell
python tools/build_land_corridor_screen.py --inspect "research\source\land\nsw_land_tenure_2024\<dataset>.gdb"
python tools/build_land_corridor_screen.py --inspect "research\source\land\abs_meshblocks_2021\MB_2021_AUST_GDA2020.shp"
```

## Initial POC-008 build

Once the NSW GDB/layer name is confirmed:

```powershell
python tools/build_land_corridor_screen.py ^
  --nsw-tenure "research\source\land\nsw_land_tenure_2024\<dataset>.gdb" ^
  --abs-meshblocks "research\source\land\abs_meshblocks_2021\MB_2021_AUST_GDA2020.shp"
```

The default 50 km buffer around POC-007 is only the first detailed QA/browser extraction window. It is explicitly not a route-search corridor.

## Victoria next

Pinned authoritative sources:

- Vicmap Property — cadastral parcels with Crown/freehold differentiation;
- Vicmap Crown Land Tenure — Crown tenure/reserves plus `GOV_ROAD_POLYGON`.

Download from Data.Vic / Vicmap DataShare, then run `--inspect` on each local dataset. We intentionally do not guess Victoria's semantic field mapping from metadata alone.
