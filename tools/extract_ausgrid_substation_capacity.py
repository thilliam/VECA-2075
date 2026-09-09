#!/usr/bin/env python3
"""Extract Ausgrid 2025 ZS/STS technical capacity, actual demand and forecast.

Source records are technical-spec assets keyed by asset type + name + voltage.
An independent openpyxl inventory is supplied by CI. Demand sheets are joined by
asset type + name. Derived margins are labelled *apparent* and are not connection
headroom or guaranteed spare capacity.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS={"m":"http://schemas.openxmlformats.org/spreadsheetml/2006/main","r":"http://schemas.openxmlformats.org/officeDocument/2006/relationships","p":"http://schemas.openxmlformats.org/package/2006/relationships"}
CELL_RE=re.compile(r"([A-Z]+)(\d+)")


def col_index(ref:str)->int:
    m=CELL_RE.match(ref); n=0
    if not m:return 0
    for ch in m.group(1): n=n*26+ord(ch)-64
    return n-1


def strings(zf):
    try: root=ET.fromstring(zf.read('xl/sharedStrings.xml'))
    except KeyError:return []
    return [''.join(t.text or '' for t in si.iterfind('.//m:t',NS)) for si in root.findall('m:si',NS)]


def sheets(zf):
    wb=ET.fromstring(zf.read('xl/workbook.xml')); rel=ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    targets={x.attrib['Id']:x.attrib['Target'] for x in rel.findall('p:Relationship',NS)}; out={}
    for s in wb.find('m:sheets',NS):
        rid=s.attrib[f"{{{NS['r']}}}id"]; t=targets[rid]
        out[s.attrib['name']]=t.lstrip('/') if t.startswith('/') else 'xl/'+t.lstrip('/')
    return out


def value(c,ss):
    t=c.attrib.get('t')
    if t=='inlineStr':return ''.join(x.text or '' for x in c.iterfind('.//m:t',NS))
    v=c.find('m:v',NS)
    if v is None or v.text is None:return None
    raw=v.text
    if t=='s':
        try:return ss[int(raw)]
        except:return raw
    try:return int(raw) if '.' not in raw and 'E' not in raw.upper() else float(raw)
    except:return raw


def read_rows(zf,path,ss,width=24):
    root=ET.fromstring(zf.read(path)); sd=root.find('m:sheetData',NS); out=[]
    for row in sd.findall('m:row',NS):
        vals=[None]*width
        for c in row.findall('m:c',NS):
            i=col_index(c.attrib.get('r','A1'))
            if i>=len(vals): vals.extend([None]*(i+1-len(vals)))
            vals[i]=value(c,ss)
        out.append((int(row.attrib.get('r','0')),vals))
    return out


def norm(v):
    if v is None:return ''
    return str(v).strip()


def num(v):
    try:
        x=float(v); return x if math.isfinite(x) else None
    except:return None


def rid(asset_type,name,voltage):return f"{asset_type}|{norm(name).upper()}|{norm(voltage)}"


def main():
    ap=argparse.ArgumentParser(); ap.add_argument('xlsx',type=Path); ap.add_argument('inventory',type=Path); ap.add_argument('output',type=Path); ap.add_argument('reconciliation',type=Path); a=ap.parse_args()
    inv=json.loads(a.inventory.read_text(encoding='utf-8')); expected=set(inv['source_record_ids'])
    with zipfile.ZipFile(a.xlsx) as zf:
        ss=strings(zf); sp=sheets(zf); records=[]; observed=set(); duplicates=[]; join_gaps=[]
        for short,atype in [('ZS','zone_substation'),('STS','subtransmission_substation')]:
            tech={}
            for r,v in read_rows(zf,sp[f'Tech Spec ({short})'],ss,16):
                if r<7 or not norm(v[1]):continue
                key=rid(atype,v[1],v[2])
                rec={
                    'source_record_id':key,'asset_type':atype,'substation_name':norm(v[1]),'voltage_level':norm(v[2]),
                    'summer_total_capacity_mva':num(v[3]),'summer_firm_capacity_mva':num(v[4]),'summer_load_transfer_capacity_mva':num(v[5]),'summer_95pct_peak_exceeded_hours_per_year':num(v[6]),'summer_embedded_solar_pv_mw':num(v[7]),'summer_embedded_other_generation_mw':num(v[8]),
                    'winter_total_capacity_mva':num(v[9]),'winter_firm_capacity_mva':num(v[10]),'winter_load_transfer_capacity_mva':num(v[11]),'winter_95pct_peak_exceeded_hours_per_year':num(v[12]),'winter_embedded_solar_pv_mw':num(v[13]),'winter_embedded_other_generation_mw':num(v[14]),
                }
                if key in observed:duplicates.append(key)
                observed.add(key);tech[norm(v[1]).upper()]=rec;records.append(rec)
            actual={}
            for r,v in read_rows(zf,sp[f'Actual Demand ({short})'],ss,15):
                if r<7 or not norm(v[1]):continue
                actual[norm(v[1]).upper()]={
                    'summer_actual_2022_23_mva':num(v[2]),'summer_actual_2022_23_pf':num(v[3]),'summer_actual_2023_24_mva':num(v[4]),'summer_actual_2023_24_pf':num(v[5]),'summer_actual_2024_25_mva':num(v[6]),'summer_actual_2024_25_pf':num(v[7]),
                    'winter_actual_2022_mva':num(v[8]),'winter_actual_2022_pf':num(v[9]),'winter_actual_2023_mva':num(v[10]),'winter_actual_2023_pf':num(v[11]),'winter_actual_2024_mva':num(v[12]),'winter_actual_2024_pf':num(v[13])}
            forecast={}
            for r,v in read_rows(zf,sp[f'Demand Forecast ({short})'],ss,23):
                if r<7 or not norm(v[1]):continue
                d={}
                summer=['2025_26','2026_27','2027_28','2028_29','2029_30']
                winter=['2025','2026','2027','2028','2029']
                for j,y in enumerate(summer):d[f'summer_forecast_{y}_mva']=num(v[2+j*2]);d[f'summer_forecast_{y}_pf']=num(v[3+j*2])
                for j,y in enumerate(winter):d[f'winter_forecast_{y}_mva']=num(v[12+j*2]);d[f'winter_forecast_{y}_pf']=num(v[13+j*2])
                forecast[norm(v[1]).upper()]=d
            for name,rec in tech.items():
                if name not in actual:join_gaps.append(f'{atype}|{name}|actual')
                else:rec.update(actual[name])
                if name not in forecast:join_gaps.append(f'{atype}|{name}|forecast')
                else:rec.update(forecast[name])
                sf=rec.get('summer_firm_capacity_mva');sa=rec.get('summer_actual_2024_25_mva');s29=rec.get('summer_forecast_2029_30_mva')
                wf=rec.get('winter_firm_capacity_mva');wa=rec.get('winter_actual_2024_mva');w29=rec.get('winter_forecast_2029_mva')
                rec['summer_apparent_firm_margin_latest_mva']=round(sf-sa,6) if sf is not None and sa is not None else None
                rec['summer_apparent_firm_margin_2029_30_mva']=round(sf-s29,6) if sf is not None and s29 is not None else None
                rec['winter_apparent_firm_margin_latest_mva']=round(wf-wa,6) if wf is not None and wa is not None else None
                rec['winter_apparent_firm_margin_2029_mva']=round(wf-w29,6) if wf is not None and w29 is not None else None
                rec['capacity_interpretation']='Apparent arithmetic margin only: firm capacity minus reported actual/forecast MVA; not guaranteed connection headroom.'
    missing=sorted(expected-observed);extra=sorted(observed-expected)
    fields=[]
    for r in records:
        for k in r:
            if k not in fields:fields.append(k)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with a.output.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(records)
    negative_latest=sum(1 for r in records if (r.get('summer_apparent_firm_margin_latest_mva') is not None and r['summer_apparent_firm_margin_latest_mva']<0) or (r.get('winter_apparent_firm_margin_latest_mva') is not None and r['winter_apparent_firm_margin_latest_mva']<0))
    negative_2029=sum(1 for r in records if (r.get('summer_apparent_firm_margin_2029_30_mva') is not None and r['summer_apparent_firm_margin_2029_30_mva']<0) or (r.get('winter_apparent_firm_margin_2029_mva') is not None and r['winter_apparent_firm_margin_2029_mva']<0))
    recon={'source':'Ausgrid 2025 Substation Capacity and Demand Forecast','expected_assets':len(expected),'extracted_assets':len(records),'unique_source_record_ids':len(observed),'missing_source_record_ids':missing,'extra_source_record_ids':extra,'duplicate_source_record_ids':sorted(set(duplicates)),'demand_join_gaps':sorted(join_gaps),'exact_identity_match':not missing and not extra and not duplicates and not join_gaps and len(records)==len(expected),'asset_type_counts':{t:sum(r['asset_type']==t for r in records) for t in ('zone_substation','subtransmission_substation')},'assets_with_negative_latest_apparent_firm_margin':negative_latest,'assets_with_negative_2029_apparent_firm_margin':negative_2029}
    a.reconciliation.parent.mkdir(parents=True,exist_ok=True);a.reconciliation.write_text(json.dumps(recon,indent=2)+'\n',encoding='utf-8');print(json.dumps(recon,indent=2))
    return 0 if recon['exact_identity_match'] else 2

if __name__=='__main__':raise SystemExit(main())
