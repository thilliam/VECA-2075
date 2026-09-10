#!/usr/bin/env python3
"""Build POC-004 integrated system derivatives on top of POC-003.

The POC distinguishes exact/source geometry from representative anchors. Where an
owned authoritative geometry source is available (AEMO indicative REZ GIS), use it;
otherwise keep representative geometry explicitly labelled.
"""
from __future__ import annotations

import csv
import io
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urljoin

import requests
from build_map_poc003 import main as build_poc003

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "maps" / "poc-004" / "data"
CACHE = OUT / "cache"
REGISTRY = ROOT / "maps" / "poc-004" / "spatial_overrides.csv"
TRANSMISSION = ROOT / "domains" / "energy" / "data" / "derived" / "transmission_projects_seed.csv"
ENERGY_ZONES = ROOT / "data" / "derived" / "energy_zones_seed.csv"
CAPITAL = ROOT / "data" / "derived" / "infrastructure_projects_seed.csv"
FREIGHT = ROOT / "data" / "derived" / "transport" / "intermodal_terminals_seed.csv"
WATER = ROOT / "domains" / "water" / "data" / "derived" / "water_systems_seed.csv"
PLANNING = ROOT / "domains" / "government-intent" / "data" / "derived" / "land_zoning_optionality_seed.csv"
GOV_LAND = ROOT / "domains" / "government-intent" / "data" / "derived" / "government_land_education_seed.csv"
AEMO_ISP_PAGE = "https://www.aemo.com.au/energy-systems/major-publications/integrated-system-plan-isp/2026-integrated-system-plan-isp"
AEMO_REZ_FALLBACK_URL = "https://www.aemo.com.au/-/media/files/major-publications/isp/2026/supporting-materials/indicative-rez-boundaries-2026-gis-data.kmz?rev=9b0bf7fc154b496aa8736928be26b015&sc_lang=en"

WATER_ANCHORS = {"WAT-SEQ": (152.80,-27.55),"WAT-SYD": (150.90,-33.85),"WAT-CBR": (149.10,-35.30),"WAT-MELB": (144.90,-37.85),"WAT-WAGGA": (147.37,-35.12),"WAT-ALBURY": (146.92,-36.08),"WAT-GOULBURN": (149.72,-34.75)}
PLANNING_ANCHORS = {"GI-LAND-SEQ-PFGA": (152.65,-27.62),"GI-LAND-TOOWOOMBA-PFGA": (151.95,-27.58),"GI-LAND-CC-SCP": (151.33,-33.28)}
GOV_LAND_ANCHORS = {"GLE-CC-003": (151.38,-33.30),"GLE-NE-001": (150.94,-31.08),"GLE-ACT-001": (149.09,-35.34),"GLE-SEQ-001": (153.05,-27.60),"GLE-SEQ-002": (152.76,-27.66),"GLE-SEQ-003": (151.95,-27.60)}


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fp: return list(csv.DictReader(fp))

def registry(): return {r["entity_id"]: r for r in read_csv(REGISTRY)}

def feature(entity_id,name,domain,props,reg):
    r=reg.get(entity_id)
    if not r:return None
    out=dict(props);out.update({"entity_id":entity_id,"name":name,"domain":domain,"geometry_quality":r["geometry_quality"],"geometry_note":r["geometry_note"]})
    return {"type":"Feature","geometry":{"type":"Point","coordinates":[float(r["longitude"]),float(r["latitude"])]},"properties":out}

def anchored_feature(entity_id,name,domain,props,lon,lat,quality,note):
    out=dict(props);out.update({"entity_id":entity_id,"name":name,"domain":domain,"geometry_quality":quality,"geometry_note":note})
    return {"type":"Feature","geometry":{"type":"Point","coordinates":[lon,lat]},"properties":out}

def transmission_status(raw):
    s=(raw or "").lower()
    if "committed" in s:return "committed"
    if "actionable" in s:return "actionable"
    if "future" in s:return "future"
    return "planned"

def build_transmission(reg):
    out,missing=[],[]
    for row in read_csv(TRANSMISSION):
        eid=row["project_id"];f=feature(eid,row["project_name"],"energy-transmission",{**row,"status":transmission_status(row.get("status_class")),"source_dataset":str(TRANSMISSION.relative_to(ROOT)),"assurance_state":"reconciled_entity_inventory"},reg)
        out.append(f) if f else missing.append(eid)
    return {"type":"FeatureCollection","features":out},missing

def build_zones(reg):
    out,missing=[],[]
    for row in read_csv(ENERGY_ZONES):
        if row.get("state") not in {"NSW","VIC"}:continue
        eid=row["zone_id"];status="declared" if row.get("zone_type")=="declared_REZ" else "proposed"
        f=feature(eid,row["name"],"energy-zone",{**row,"status":status,"source_dataset":str(ENERGY_ZONES.relative_to(ROOT)),"assurance_state":"provenance_reconciled"},reg)
        out.append(f) if f else missing.append(eid)
    return {"type":"FeatureCollection","features":out},missing

def parse_coords(text):
    ring=[]
    for token in (text or "").strip().split():
        parts=token.split(',')
        if len(parts)>=2:
            try:ring.append([float(parts[0]),float(parts[1])])
            except ValueError:pass
    if len(ring)>=3 and ring[0]!=ring[-1]:ring.append(ring[0])
    return ring

def local_name(tag): return tag.rsplit('}',1)[-1]

def children_named(node,name): return [x for x in node.iter() if local_name(x.tag)==name]

def first_text(node,name,default=''):
    for x in node.iter():
        if local_name(x.tag)==name and x.text:return x.text.strip()
    return default

def download_aemo_rez_kmz(cache: Path):
    if cache.exists() and cache.stat().st_size>1000:
        print(f"Using cached AEMO 2026 indicative REZ GIS: {cache.stat().st_size/1000:.0f} KB")
        return cache.read_bytes()

    session=requests.Session()
    session.headers.update({
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/150 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language":"en-AU,en;q=0.9",
    })
    page=session.get(AEMO_ISP_PAGE,timeout=60)
    page.raise_for_status()
    matches=re.findall(r'href=["\']([^"\']*indicative-rez-boundaries-2026-gis-data[^"\']*)["\']',page.text,re.I)
    candidates=[]
    for href in matches:
        url=urljoin(AEMO_ISP_PAGE,href.replace('&amp;','&'))
        if url not in candidates:candidates.append(url)
    if AEMO_REZ_FALLBACK_URL not in candidates:candidates.append(AEMO_REZ_FALLBACK_URL)
    print(f"AEMO REZ download: resolved {len(candidates)} candidate URL(s) from ISP page")

    errors=[]
    for url in candidates:
        try:
            r=session.get(url,headers={"Referer":AEMO_ISP_PAGE,"Accept":"application/octet-stream,application/vnd.google-earth.kmz,*/*"},timeout=180,allow_redirects=True)
            if r.status_code==200 and len(r.content)>1000 and r.content[:2]==b'PK':
                cache.write_bytes(r.content)
                print(f"Downloaded AEMO REZ GIS: {len(r.content)/1000:.0f} KB from {r.url}")
                return r.content
            errors.append(f"{r.status_code} {url}")
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")

    raise RuntimeError("AEMO blocked automated GIS download ("+'; '.join(errors)+"). Download 'Indicative REZ boundaries 2026 – GIS data' in a browser from the 2026 ISP page and save it as maps/poc-004/data/cache/aemo_indicative_rez_2026.kmz; the next build will use it automatically.")

def build_aemo_rez_boundaries():
    CACHE.mkdir(parents=True,exist_ok=True);cache=CACHE/"aemo_indicative_rez_2026.kmz"
    try:
        content=download_aemo_rez_kmz(cache)
        z=zipfile.ZipFile(io.BytesIO(content));kml_names=[n for n in z.namelist() if n.lower().endswith('.kml')]
        print(f"AEMO REZ KMZ: {len(kml_names)} KML file(s): {', '.join(kml_names[:5])}")
        out=[];placemark_count=polygon_count=ring_count=0
        for kml_name in kml_names:
            root=ET.fromstring(z.read(kml_name))
            placemarks=children_named(root,'Placemark');placemark_count+=len(placemarks)
            for pm in placemarks:
                name=first_text(pm,'name',f'REZ {placemark_count}');polys=[]
                for poly in children_named(pm,'Polygon'):
                    polygon_count+=1
                    outers=[]
                    for outer in children_named(poly,'outerBoundaryIs'):
                        coords=children_named(outer,'coordinates')
                        if coords:
                            ring=parse_coords(coords[0].text or '')
                            if len(ring)>=4:outers.append(ring);ring_count+=1
                    for ring in outers:polys.append([ring])
                if not polys:continue
                pts=[p for poly in polys for ring in poly for p in ring]
                if not any(140.5<=p[0]<=154.5 and -39.8<=p[1]<=-10.0 for p in pts):continue
                geom={"type":"Polygon","coordinates":polys[0]} if len(polys)==1 else {"type":"MultiPolygon","coordinates":polys}
                out.append({"type":"Feature","geometry":geom,"properties":{"entity_id":f"AEMO-REZ-2026-{len(out)+1}","name":name,"domain":"energy-zone-boundary","status":"indicative_2026","geometry_quality":"authoritative_AEMO_indicative_boundary","source_dataset":"AEMO 2026 ISP Indicative REZ boundaries GIS","source_url":AEMO_ISP_PAGE,"assurance_state":"authoritative_direct_source"}})
        print(f"AEMO REZ parse: placemarks={placemark_count}, polygons={polygon_count}, valid_outer_rings={ring_count}, east/NEM_features={len(out)}")
        if not out:raise RuntimeError("KMZ parsed but yielded zero east/NEM polygon features")
        return {"type":"FeatureCollection","features":out}
    except Exception as exc:
        print(f"WARNING: AEMO REZ GIS unavailable/parse failed: {exc}")
        return {"type":"FeatureCollection","features":[]}

def build_capital(reg):
    out,missing=[],[]
    for row in read_csv(CAPITAL):
        eid=row["project_id"];f=feature(eid,row["name"],"capital-project",{**row,"status":row.get("status") or "unknown","source_dataset":str(CAPITAL.relative_to(ROOT)),"assurance_state":"provenance_reconciled"},reg)
        out.append(f) if f else missing.append(eid)
    return {"type":"FeatureCollection","features":out},missing

def build_freight(reg):
    out,missing=[],[]
    for row in read_csv(FREIGHT):
        eid=row["terminal_id"];f=feature(eid,row["name"],"freight-intermodal",{**row,"status":row.get("status") or "unknown","source_dataset":str(FREIGHT.relative_to(ROOT)),"assurance_state":"provenance_reconciled"},reg)
        out.append(f) if f else missing.append(eid)
    return {"type":"FeatureCollection","features":out},missing

def build_water():
    out,missing=[],[]
    for row in read_csv(WATER):
        eid=row["system_id"];loc=WATER_ANCHORS.get(eid)
        if not loc:missing.append(eid);continue
        out.append(anchored_feature(eid,row["system_name"],"water-system",{**row,"source_dataset":str(WATER.relative_to(ROOT)),"assurance_state":"structured_research_seed"},loc[0],loc[1],"representative_system_anchor","Representative urban water-system anchor; not dam, pipe, catchment or service-area geometry"))
    return {"type":"FeatureCollection","features":out},missing

def build_planning_optionality():
    out,missing=[],[]
    for row in read_csv(PLANNING):
        eid=row["area_id"];loc=PLANNING_ANCHORS.get(eid)
        if not loc:continue
        out.append(anchored_feature(eid,row["area_or_program"],"planning-optionality",{**row,"source_dataset":str(PLANNING.relative_to(ROOT)),"assurance_state":"provenance_reconciled"},loc[0],loc[1],"representative_program_anchor","Representative program/growth-area anchor; not statutory boundary or parcel geometry"))
    for row in read_csv(GOV_LAND):
        if row.get("record_type") not in {"government_land","growth_land"}:continue
        eid=row["record_id"];loc=GOV_LAND_ANCHORS.get(eid)
        if not loc:missing.append(eid);continue
        out.append(anchored_feature(eid,row["asset_or_area"],"planning-optionality",{**row,"source_dataset":str(GOV_LAND.relative_to(ROOT)),"assurance_state":"provenance_reconciled"},loc[0],loc[1],"representative_program_anchor","Representative government/growth-land anchor; not parcel boundary"))
    return {"type":"FeatureCollection","features":out},missing

def write(name,data):
    OUT.mkdir(parents=True,exist_ok=True);p=OUT/name;p.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');print(f"{name}: {len(data.get('features',[])):,} features, {p.stat().st_size/1_000_000:.2f} MB")

def main():
    build_poc003();reg=registry()
    transmission,a=build_transmission(reg);zones,b=build_zones(reg);rez_boundaries=build_aemo_rez_boundaries();capital,c=build_capital(reg);freight,d=build_freight(reg);water,e=build_water();planning,f=build_planning_optionality()
    write("transmission_projects.geojson",transmission);write("energy_zones.geojson",zones);write("aemo_rez_boundaries.geojson",rez_boundaries);write("capital_projects.geojson",capital);write("freight_intermodal.geojson",freight);write("water_systems.geojson",water);write("planning_optionality.geojson",planning)
    gaps={"transmission":a,"energy_zones":b,"capital":c,"freight":d,"water":e,"planning_optionality":f};(OUT/"spatial-gaps.json").write_text(json.dumps(gaps,indent=2),encoding='utf-8')
    manifest={"transmission":{"features":len(transmission['features']),"geometry_mode":"representative anchors"},"energy_zones":{"features":len(zones['features']),"geometry_mode":"representative anchors"},"aemo_rez_boundaries":{"features":len(rez_boundaries['features']),"geometry_mode":"authoritative indicative polygons"},"capital_projects":{"features":len(capital['features']),"geometry_mode":"representative anchors"},"freight_intermodal":{"features":len(freight['features']),"geometry_mode":"approximate asset points"},"water_systems":{"features":len(water['features']),"geometry_mode":"representative system anchors"},"planning_optionality":{"features":len(planning['features']),"geometry_mode":"representative program anchors"},"health":{"mode":"reuse POC-002 corpus derivative"},"education":{"mode":"reuse POC-002 corpus derivative"}}
    (OUT/"manifest.json").write_text(json.dumps(manifest,indent=2),encoding='utf-8');print(f"POC-004 spatial gaps: {sum(len(v) for v in gaps.values())} -> maps/poc-004/data/spatial-gaps.json");print("POC-004 complete")

if __name__=="__main__":main()