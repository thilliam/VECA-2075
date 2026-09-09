#!/usr/bin/env python3
"""Extract Essential Energy 2025 DAPR zone-substation capacity/forecast rows.

The source workbook publishes matching ZSSummer/ZSWinter sheets.  This extractor
uses stdlib XLSX/XML parsing and reconciles against an independently generated
openpyxl inventory supplied by CI.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS={
    'main':'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'rel':'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'pkg':'http://schemas.openxmlformats.org/package/2006/relationships',
}
CELL_RE=re.compile(r'([A-Z]+)(\d+)')


def col_index(ref:str)->int:
    m=CELL_RE.match(ref); n=0
    if not m: return 0
    for ch in m.group(1): n=n*26+ord(ch)-64
    return n-1


def shared_strings(zf):
    try: root=ET.fromstring(zf.read('xl/sharedStrings.xml'))
    except KeyError: return []
    return [''.join(t.text or '' for t in si.iterfind('.//main:t',NS)) for si in root.findall('main:si',NS)]


def sheet_path(zf,wanted):
    wb=ET.fromstring(zf.read('xl/workbook.xml'))
    rels=ET.fromstring(zf.read('xl/_rels/workbook.xml.rels'))
    targets={r.attrib['Id']:r.attrib['Target'] for r in rels.findall('pkg:Relationship',NS)}
    for s in wb.find('main:sheets',NS):
        if s.attrib.get('name')==wanted:
            rid=s.attrib[f"{{{NS['rel']}}}id"]
            t=targets[rid]
            return t.lstrip('/') if t.startswith('/') else 'xl/'+t.lstrip('/')
    raise KeyError(wanted)


def cell_value(cell,strings):
    t=cell.attrib.get('t')
    if t=='inlineStr': return ''.join(x.text or '' for x in cell.iterfind('.//main:t',NS))
    v=cell.find('main:v',NS)
    if v is None or v.text is None: return None
    raw=v.text
    if t=='s':
        try: return strings[int(raw)]
        except Exception: return raw
    try: return int(raw) if '.' not in raw and 'E' not in raw.upper() else float(raw)
    except ValueError: return raw


def row_values(row,strings,width=18):
    out=[None]*width
    for c in row.findall('main:c',NS):
        i=col_index(c.attrib.get('r','A1'))
        if i>=len(out): out.extend([None]*(i+1-len(out)))
        out[i]=cell_value(c,strings)
    return out


def norm(v): return '' if v is None else str(v).strip()

def rid(vals): return f"zone_substation|{norm(vals[0])}|{norm(vals[1])}|{norm(vals[2])}"


def read_sheet(zf,strings,name):
    root=ET.fromstring(zf.read(sheet_path(zf,name)))
    rows=root.find('main:sheetData',NS).findall('main:row',NS)
    result={}
    for r in rows:
        if int(r.attrib.get('r',0))<3: continue
        vals=row_values(r,strings,18)
        if not norm(vals[1]): continue
        key=rid(vals)
        if key in result: raise SystemExit(f'duplicate source identity in {name}: {key}')
        result[key]=vals
    return result


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('xlsx',type=Path); ap.add_argument('inventory',type=Path); ap.add_argument('output',type=Path); ap.add_argument('reconciliation',type=Path); a=ap.parse_args()
    inventory=json.loads(a.inventory.read_text(encoding='utf-8')); expected=set(inventory['source_record_ids'])
    with zipfile.ZipFile(a.xlsx) as zf:
        strings=shared_strings(zf); summer=read_sheet(zf,strings,'ZSSummer'); winter=read_sheet(zf,strings,'ZSWinter')
    sk=set(summer); wk=set(winter); observed=sk & wk
    rows=[]
    for key in sorted(observed):
        s=summer[key]; w=winter[key]
        rec={
            'source_record_id':key,'region':norm(s[0]),'substation':norm(s[1]),'kv':norm(s[2]),
            'transformer_rating_tx1':norm(s[3]),'transformer_rating_tx2':norm(s[4]),'transformer_rating_tx3':norm(s[5]),
            'transformer_max_nameplate_tx1_mva':s[6],'transformer_max_nameplate_tx2_mva':s[7],'transformer_max_nameplate_tx3_mva':s[8],
            'summer_firm_normal_cyclic_rating_mva':s[9],'summer_forecast_pf':s[10],
            'summer_forecast_2025_26_mva':s[11],'summer_forecast_2026_27_mva':s[12],'summer_forecast_2027_28_mva':s[13],'summer_forecast_2028_29_mva':s[14],'summer_forecast_2029_30_mva':s[15],
            'summer_embedded_generation_mw':s[16],'summer_95pct_peak_exceeded_hours':s[17],
            'winter_firm_normal_cyclic_rating_mva':w[9],'winter_forecast_pf':w[10],
            'winter_forecast_2026_mva':w[11],'winter_forecast_2027_mva':w[12],'winter_forecast_2028_mva':w[13],'winter_forecast_2029_mva':w[14],'winter_forecast_2030_mva':w[15],
            'winter_embedded_generation_mw':w[16],'winter_95pct_peak_exceeded_hours':w[17],
        }
        sf=rec['summer_firm_normal_cyclic_rating_mva']; wf=rec['winter_firm_normal_cyclic_rating_mva']; s29=rec['summer_forecast_2029_30_mva']; w30=rec['winter_forecast_2030_mva']
        rec['summer_2029_apparent_firm_margin_mva']=sf-s29 if isinstance(sf,(int,float)) and isinstance(s29,(int,float)) else None
        rec['winter_2030_apparent_firm_margin_mva']=wf-w30 if isinstance(wf,(int,float)) and isinstance(w30,(int,float)) else None
        rows.append(rec)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fields=list(rows[0]) if rows else []
    with a.output.open('w',newline='',encoding='utf-8') as f:
        cw=csv.DictWriter(f,fieldnames=fields); cw.writeheader(); cw.writerows(rows)
    missing=sorted(expected-observed); extra=sorted(observed-expected)
    recon={
        'source':'Essential Energy DAPR 2025 BSP, ZS and Lines Extract Summary V2',
        'expected_zone_substations':len(expected),'extracted_zone_substations':len(rows),
        'summer_sheet_records':len(sk),'winter_sheet_records':len(wk),
        'summer_only_source_record_ids':sorted(sk-wk),'winter_only_source_record_ids':sorted(wk-sk),
        'missing_source_record_ids':missing,'extra_source_record_ids':extra,
        'exact_identity_match':not missing and not extra and sk==wk and len(rows)==len(expected),
        'assets_negative_summer_2029_apparent_margin':sum(1 for r in rows if isinstance(r['summer_2029_apparent_firm_margin_mva'],(int,float)) and r['summer_2029_apparent_firm_margin_mva']<0),
        'assets_negative_winter_2030_apparent_margin':sum(1 for r in rows if isinstance(r['winter_2030_apparent_firm_margin_mva'],(int,float)) and r['winter_2030_apparent_firm_margin_mva']<0),
    }
    a.reconciliation.parent.mkdir(parents=True,exist_ok=True); a.reconciliation.write_text(json.dumps(recon,indent=2)+'\n',encoding='utf-8'); print(json.dumps(recon,indent=2))
    return 0 if recon['exact_identity_match'] else 2

if __name__=='__main__': raise SystemExit(main())
