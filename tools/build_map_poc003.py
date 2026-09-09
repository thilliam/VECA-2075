#!/usr/bin/env python3
"""Build POC-003 population, settlement and landscape derivatives.

Runs/reuses POC-002, then adds:
- 2025 SA2 ERP polygons (ABS geometry + committed VECA ERP table)
- 2021 Urban Centres and Localities settlement hierarchy
- explicit metropolitan sub-centres (Parramatta/Penrith validation cases)

No heavy GIS dependency is required; ABS ArcGIS services return GeoJSON.
Remote ABS responses are cached locally so iterative reruns are fast.
"""
from __future__ import annotations

import csv, io, json, math, zipfile
from pathlib import Path
import requests

from build_map_poc002 import main as build_poc002

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "maps" / "poc-003" / "data"
CACHE = OUT / "cache"
POC2_DATA = ROOT / "maps" / "poc-002" / "data"
POP = ROOT / "data" / "derived" / "population_sa2_east.csv"
SA2_URL = "https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/SA2/FeatureServer/0/query"
UCL_URL = "https://geo.abs.gov.au/arcgis/rest/services/ASGS2021/UCL/FeatureServer/0/query"
UCL_GCP = "https://www.abs.gov.au/census/find-census-data/datapacks/download/2021_GCP_UCL_for_AUS_short-header.zip"
TARGET_STATES = {"1","2","3","8"}


def request_json(url, params):
    r=requests.get(url,params=params,timeout=180); r.raise_for_status(); data=r.json()
    if "error" in data: raise RuntimeError(data["error"])
    return data


def feature_pages(url, where, out_fields, cache_name):
    CACHE.mkdir(parents=True,exist_ok=True)
    cache=CACHE/cache_name
    if cache.exists():
        data=json.loads(cache.read_text(encoding='utf-8'))
        print(f"Using cached {cache_name}: {len(data):,} features")
        return data
    out=[]; offset=0
    while True:
        data=request_json(url,{"where":where,"outFields":out_fields,"returnGeometry":"true","outSR":4326,"f":"geojson","resultOffset":offset,"resultRecordCount":2000})
        batch=data.get("features",[]); out.extend(batch)
        print(f"Downloaded {cache_name}: {len(out):,} features")
        if len(batch)<2000: break
        offset += len(batch)
    cache.write_text(json.dumps(out,separators=(',',':')),encoding='utf-8')
    return out


def simplify_line(coords,tol):
    if len(coords)<=2:return coords
    a,b=coords[0],coords[-1]
    def d(p):
        if a==b:return math.hypot(p[0]-a[0],p[1]-a[1])
        t=max(0,min(1,((p[0]-a[0])*(b[0]-a[0])+(p[1]-a[1])*(b[1]-a[1]))/((b[0]-a[0])**2+(b[1]-a[1])**2)))
        return math.hypot(p[0]-(a[0]+t*(b[0]-a[0])),p[1]-(a[1]+t*(b[1]-a[1])))
    idx=max(range(1,len(coords)-1),key=lambda i:d(coords[i]),default=0)
    if idx and d(coords[idx])>tol:
        l=simplify_line(coords[:idx+1],tol); r=simplify_line(coords[idx:],tol); return l[:-1]+r
    return [a,b]


def simplify_geom(g,tol=.002):
    if not isinstance(g,dict):return None
    t=g.get("type"); c=g.get("coordinates",[])
    if t=="Polygon":return {"type":t,"coordinates":[simplify_line(r,tol) for r in c if len(r)>=4]}
    if t=="MultiPolygon":return {"type":t,"coordinates":[[simplify_line(r,tol) for r in p if len(r)>=4] for p in c]}
    return g


def bounds_center(g):
    if not isinstance(g,dict):return None
    pts=[]
    def walk(v):
        if isinstance(v,list) and len(v)>=2 and all(isinstance(x,(int,float)) for x in v[:2]):pts.append(v)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(g.get("coordinates",[]))
    if not pts:return None
    xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
    return [(min(xs)+max(xs))/2,(min(ys)+max(ys))/2]


def read_pop():
    with POP.open(newline="",encoding="utf-8-sig") as f:return {r["sa2_code"]:r for r in csv.DictReader(f)}


def build_population():
    rows=read_pop()
    features=feature_pages(SA2_URL,"state_code_2021 IN ('1','2','3','8')","sa2_code_2021,sa2_name_2021,area_albers_sqkm,state_code_2021,state_name_2021","abs_sa2_east.json")
    out=[]; skipped_geometry=0
    for f in features:
        geom=f.get('geometry')
        if not isinstance(geom,dict):
            skipped_geometry+=1; continue
        p=f.get("properties",{}); code=str(p.get("sa2_code_2021") or "")
        row=rows.get(code)
        if not row:continue
        area=float(p.get("area_albers_sqkm") or 0) or 0
        erp=float(row.get("erp_2025") or 0); density=erp/area if area else 0
        growth=float(row.get("change_2020_25_abs") or 0); growth_pct=float(row.get("change_2020_25_pct") or 0)
        props={"entity_id":f"SA2-{code}","name":p.get("sa2_name_2021"),"domain":"population","status":"existing","valid_from":2025,"sa2_code":code,"state":row.get("state"),"erp_2025":erp,"density_2025":round(density,2),"change_2020_25_abs":growth,"change_2020_25_pct":growth_pct,"geometry_quality":"ABS_ASGS2021_simplified","source_dataset":"ABS Regional Population 2024-25 + ASGS2021 SA2"}
        out.append({"type":"Feature","geometry":simplify_geom(geom,.003),"properties":props})
    if skipped_geometry:print(f"SA2: skipped {skipped_geometry} features with null/invalid geometry")
    return {"type":"FeatureCollection","features":out}, features


def read_ucl_population():
    CACHE.mkdir(parents=True,exist_ok=True)
    cache=CACHE/'2021_GCP_UCL.zip'
    if cache.exists():
        content=cache.read_bytes(); print('Using cached ABS UCL Census DataPack')
    else:
        r=requests.get(UCL_GCP,timeout=180);r.raise_for_status();content=r.content;cache.write_bytes(content);print(f"Downloaded ABS UCL Census DataPack: {len(content)/1_000_000:.1f} MB")
    z=zipfile.ZipFile(io.BytesIO(content)); result={}
    for name in z.namelist():
        if not name.lower().endswith('.csv') or 'g01' not in name.lower():continue
        text=io.TextIOWrapper(z.open(name),encoding='utf-8-sig'); reader=csv.DictReader(text)
        fields=[x or '' for x in (reader.fieldnames or [])]
        code_col=next((x for x in fields if 'ucl' in x.lower() and 'code' in x.lower()),None)
        pop_col=next((x for x in fields if x.lower() in {'tot_p_p','total_persons_persons'}),None) or next((x for x in fields if 'tot_p_p' in x.lower()),None)
        if not code_col or not pop_col:continue
        for row in reader:
            code=str(row.get(code_col) or '').strip(); val=str(row.get(pop_col) or '').replace(',','').strip()
            try:result[code]=int(float(val))
            except ValueError:pass
        if result:break
    if not result:raise RuntimeError('Could not find UCL population fields in ABS G01 DataPack')
    return result


def rank_for(pop):
    if pop>=1_000_000:return 1,3.0
    if pop>=250_000:return 2,4.0
    if pop>=50_000:return 3,5.0
    if pop>=10_000:return 4,6.0
    if pop>=2_000:return 5,7.0
    return 6,8.0


def build_settlements(sa2_source):
    pops=read_ucl_population()
    features=feature_pages(UCL_URL,"1=1","ucl_code_2021,ucl_name_2021,sosr_code_2021,sosr_name_2021,area_albers_sqkm","abs_ucl_all.json")
    out=[]; skipped_geometry=0
    for f in features:
        p=f.get('properties',{});code=str(p.get('ucl_code_2021') or '')
        if not code or code[0] not in TARGET_STATES:continue
        centre=bounds_center(f.get('geometry'))
        if not centre:
            skipped_geometry+=1; continue
        pop=int(pops.get(code,0));rank,minz=rank_for(pop)
        out.append({"type":"Feature","geometry":{"type":"Point","coordinates":centre},"properties":{"entity_id":f"UCL-{code}","name":p.get('ucl_name_2021'),"domain":"settlement","settlement_type":"ABS UCL","population_2021":pop,"settlement_rank":rank,"min_zoom":minz,"geometry_quality":"UCL_bounds_centre","source_dataset":"ABS ASGS2021 UCL + Census 2021 GCP"}})
    if skipped_geometry:print(f"UCL: skipped {skipped_geometry} in-scope features with null/invalid geometry")

    overrides={"Parramatta":("parramatta",3,5.2),"Penrith":("penrith",3,5.2)}
    for label,(needle,rank,minz) in overrides.items():
        matches=[f for f in sa2_source if needle in str(f.get('properties',{}).get('sa2_name_2021','')).lower()]
        centres=[bounds_center(f.get('geometry')) for f in matches]; centres=[c for c in centres if c]
        if centres:
            centre=[sum(c[0] for c in centres)/len(centres),sum(c[1] for c in centres)/len(centres)]
            out.append({"type":"Feature","geometry":{"type":"Point","coordinates":centre},"properties":{"entity_id":f"VECA-METRO-{label.upper()}","name":label,"domain":"settlement","settlement_type":"VECA metropolitan sub-centre","population_2021":None,"settlement_rank":rank,"min_zoom":minz,"geometry_quality":"derived_from_matching_SA2","source_dataset":"ABS ASGS2021 SA2; VECA functional-centre classification"}})
    return {"type":"FeatureCollection","features":out}


def write(name,data):
    OUT.mkdir(parents=True,exist_ok=True); path=OUT/name; path.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8')
    print(f"{name}: {len(data.get('features',[])):,} features, {path.stat().st_size/1_000_000:.1f} MB")


def ensure_poc002():
    required=[POC2_DATA/'rail.geojson',POC2_DATA/'roads.geojson',POC2_DATA/'manifest.json']
    if all(p.exists() for p in required):
        print('POC-002 derivatives already exist; reusing them')
    else:
        print('POC-002 derivatives missing; rebuilding them')
        build_poc002()


def main():
    ensure_poc002()
    pop,sa2_source=build_population(); settlements=build_settlements(sa2_source)
    write('population_sa2.geojson',pop);write('settlements.geojson',settlements)
    manifest={"population_sa2":{"features":len(pop['features'])},"settlements":{"features":len(settlements['features'])},"land_use":{"mode":"ABARES WMS live"},"satellite":{"mode":"Esri World Imagery live"}}
    (OUT/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('POC-003 complete')

if __name__=='__main__':main()
