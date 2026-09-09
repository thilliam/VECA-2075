#!/usr/bin/env python3
"""Build POC-005 derivatives from newly arrived VECA datasets.

POC-005 deliberately uses representative locality/corridor geometry where the
source dataset is non-spatial. Geometry quality is carried into every feature.
"""
from __future__ import annotations
import csv, json
from pathlib import Path

from build_map_poc004 import main as build_poc004

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'maps'/'poc-005'/'data'
COMPUTE=ROOT/'domains'/'digital-compute'/'data'/'derived'/'compute_campus_pipeline_seed.csv'
DIGITAL=ROOT/'domains'/'digital-connectivity'/'data'/'derived'/'digital_backbone_routes_seed.csv'
RAIL=ROOT/'domains'/'transport'/'data'/'derived'/'conventional_rail_capacity_investment_seed.csv'
PORTS=ROOT/'domains'/'industry'/'data'/'derived'/'port_catchments_seed.csv'
DNSP=ROOT/'domains'/'energy'/'data'/'derived'/'distribution_capacity_signals_seed.csv'
WATER=ROOT/'domains'/'water'/'data'/'derived'/'water_systems_seed.csv'

LOCALITIES={
'Macquarie Park':(151.123,-33.777),'Artarmon':(151.185,-33.808),'Horsley Park':(150.856,-33.843),'Eastern Creek':(150.795,-33.806),'Sydney West':(150.82,-33.80),'Sydney North':(151.15,-33.72),'Marsden Park':(150.84,-33.70),
'Port Melbourne':(144.94,-37.84),'Tullamarine':(144.88,-37.69),'West Footscray':(144.87,-37.80),'Melbourne West':(144.80,-37.82),'Melbourne North-West':(144.82,-37.70),'Brooklyn':(144.84,-37.82),'Laverton':(144.78,-37.86),'Geelong':(144.36,-38.15),
'Brisbane CBD':(153.03,-27.47),'Fortitude Valley':(153.04,-27.46),'Gold Coast':(153.40,-28.02),'Bruce':(149.09,-35.24),'Hume':(149.17,-35.39),'Fyshwick':(149.16,-35.33),'Beard':(149.22,-35.35),'Maroochydore':(153.09,-26.65),'Sunshine Coast':(153.05,-26.65),
'Sydney':(151.21,-33.87),'Canberra':(149.13,-35.28),'Melbourne':(144.96,-37.81),'Wollongong':(150.89,-34.43),'Newcastle':(151.78,-32.93),'Albury':(146.92,-36.08),'Wagga Wagga':(147.37,-35.12),'Parkes':(148.18,-33.14),'Narromine':(148.24,-32.23),'Narrabri':(149.78,-30.33),'North Star':(150.39,-28.93),'Goulburn':(149.72,-34.75),'Telarah':(151.54,-32.72),'Acacia Ridge':(153.00,-27.58),'Beveridge':(144.98,-37.48),'Illabo':(147.75,-34.98),'Stockinbingal':(147.88,-34.50),'Gowrie':(151.88,-27.53),'Helidon':(152.13,-27.55),'Calvert':(152.52,-27.67),
'Fisherman Islands / Brisbane':(153.18,-27.38),'Wollongong / Illawarra':(150.90,-34.43),'Newcastle / Hunter':(151.78,-32.93)
}
WATER_ANCHORS={'WAT-SEQ':(152.80,-27.55),'WAT-SYD':(150.90,-33.85),'WAT-CBR':(149.10,-35.30),'WAT-MELB':(144.90,-37.85),'WAT-WAGGA':(147.37,-35.12),'WAT-ALBURY':(146.92,-36.08),'WAT-GOULBURN':(149.72,-34.75),'WAT-TOOWOOMBA':(151.95,-27.56),'WAT-LOWER-HUNTER':(151.70,-32.90),'WAT-TAMWORTH':(150.93,-31.09),'WAT-ARMIDALE':(151.67,-30.51)}
DNSP_REGIONS={'Western Sydney Aerotropolis':(150.76,-33.90),'Western Sydney Airport':(150.72,-33.94),'Southern Highlands':(150.35,-34.55),'South-east Melbourne / Casey':(145.32,-38.05),'North Melbourne growth corridor':(145.02,-37.61),'Pakenham South':(145.49,-38.10),'Gippsland / Bass Coast':(145.59,-38.60),'Gippsland':(147.30,-37.85),'Eastern Melbourne':(145.27,-37.76)}
CITY={'Sydney':LOCALITIES['Sydney'],'Canberra':LOCALITIES['Canberra'],'Melbourne':LOCALITIES['Melbourne'],'Wollongong':LOCALITIES['Wollongong'],'Geelong':LOCALITIES['Geelong'],'Adelaide':(138.60,-34.93),'Perth':(115.86,-31.95)}

def rows(path):
    with path.open(newline='',encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def fc(features):return {'type':'FeatureCollection','features':features}
def point(eid,name,domain,lonlat,props,quality,note):
    p=dict(props);p.update({'entity_id':eid,'name':name,'domain':domain,'geometry_quality':quality,'geometry_note':note})
    return {'type':'Feature','geometry':{'type':'Point','coordinates':[lonlat[0],lonlat[1]]},'properties':p}
def line(eid,name,domain,coords,props,quality,note):
    p=dict(props);p.update({'entity_id':eid,'name':name,'domain':domain,'geometry_quality':quality,'geometry_note':note})
    return {'type':'Feature','geometry':{'type':'LineString','coordinates':[[x,y] for x,y in coords]},'properties':p}
def write(name,data):
    OUT.mkdir(parents=True,exist_ok=True);p=OUT/name;p.write_text(json.dumps(data,separators=(',',':')),encoding='utf-8');print(f'{name}: {len(data["features"]):,} features')

def build_compute():
    out=[];missing=[]
    for r in rows(COMPUTE):
        if r.get('record_type')!='campus':continue
        loc=LOCALITIES.get(r.get('locality',''))
        if not loc:missing.append(r['compute_id']);continue
        out.append(point(r['compute_id'],f"{r['operator']} {r['campus_or_site']}",'digital-compute',loc,{**r,'source_dataset':str(COMPUTE.relative_to(ROOT))},'representative_locality_anchor','Locality-level anchor from published campus locality; not parcel/building geometry'))
    return fc(out),missing

def build_digital():
    out=[];missing=[]
    for r in rows(DIGITAL):
        ep=r.get('endpoints','').replace('–','-').split('-')
        pts=[]
        for name in ep:
            name=name.strip()
            if name in CITY:pts.append(CITY[name])
        if len(pts)<2:missing.append(r['route_id']);continue
        out.append(line(r['route_id'],r['route_name'],'digital-connectivity',pts,{**r,'source_dataset':str(DIGITAL.relative_to(ROOT))},'generalised_endpoint_corridor','Straight/generalised endpoint corridor for system context; not fibre alignment or access-point geometry'))
    return fc(out),missing

def rail_endpoints(rid,name):
    explicit={
    'RAIL-NIP-ALBURY-SYDNEY':['Albury','Sydney'],'RAIL-NIP-MELB-ALBURY':['Melbourne','Albury'],'RAIL-NIP-TELARAH-ACACIA':['Telarah','Acacia Ridge'],
    'IR-B2A':['Beveridge','Albury'],'IR-A2I':['Albury','Illabo'],'IR-I2S':['Illabo','Stockinbingal'],'IR-S2P':['Stockinbingal','Parkes'],'IR-P2N':['Parkes','Narromine'],'IR-N2N':['Narromine','Narrabri'],'IR-NNS1':['Narrabri','North Star'],'IR-NNS2':['Narrabri','North Star'],'IR-BG':['North Star','Gowrie'],'IR-GH':['Gowrie','Helidon'],'IR-HC':['Helidon','Calvert']}
    return explicit.get(rid)
def build_rail():
    out=[];missing=[]
    for r in rows(RAIL):
        ep=rail_endpoints(r['rail_signal_id'],r['program_or_corridor'])
        if not ep:continue
        pts=[LOCALITIES.get(x) for x in ep]
        if any(x is None for x in pts):missing.append(r['rail_signal_id']);continue
        out.append(line(r['rail_signal_id'],r['program_or_corridor'],'rail-capacity-investment',pts,{**r,'source_dataset':str(RAIL.relative_to(ROOT))},'generalised_corridor','Generalised corridor between named endpoints; not project alignment or engineering geometry'))
    return fc(out),missing

def build_ports():
    out=[];missing=[]
    for r in rows(PORTS):
        key=r.get('locality','');loc=LOCALITIES.get(key)
        if not loc:
            if r.get('port_id')=='PORT-BOTANY':loc=(151.20,-33.97)
            elif r.get('port_id')=='PORT-MEL':loc=(144.90,-37.82)
            elif r.get('port_id')=='PORT-GEELONG':loc=LOCALITIES['Geelong']
        if not loc:missing.append(r['port_id']);continue
        out.append(point(r['port_id'],r['port_name'],'port-system',loc,{**r,'source_dataset':str(PORTS.relative_to(ROOT))},'representative_port_anchor','Port-system anchor; not berth, estate or inland catchment boundary'))
    return fc(out),missing

def build_dnsp():
    out=[];missing=[]
    for r in rows(DNSP):
        loc=DNSP_REGIONS.get(r.get('region',''))
        if not loc:missing.append(r['signal_id']);continue
        out.append(point(r['signal_id'],r['asset_name'],'distribution-capacity-signal',loc,{**r,'source_dataset':str(DNSP.relative_to(ROOT))},'representative_region_anchor','Regional anchor for a curated DNSP planning/capacity signal; not authoritative substation coordinates'))
    return fc(out),missing

def build_water():
    out=[];missing=[]
    for r in rows(WATER):
        loc=WATER_ANCHORS.get(r['system_id'])
        if not loc:missing.append(r['system_id']);continue
        out.append(point(r['system_id'],r['system_name'],'water-system',loc,{**r,'source_dataset':str(WATER.relative_to(ROOT))},'representative_system_anchor','Representative system anchor; not dam, pipe, service-area or catchment geometry'))
    return fc(out),missing

def main():
    build_poc004()
    layers={}
    for name,fn in [('compute_campuses.geojson',build_compute),('digital_backbone.geojson',build_digital),('rail_capacity_investment.geojson',build_rail),('ports.geojson',build_ports),('dnsp_capacity_signals.geojson',build_dnsp),('water_systems_expanded.geojson',build_water)]:
        data,gaps=fn();write(name,data);layers[name]={'features':len(data['features']),'gaps':gaps}
    (OUT/'manifest.json').write_text(json.dumps(layers,indent=2),encoding='utf-8')
    print('POC-005 complete')
if __name__=='__main__':main()
