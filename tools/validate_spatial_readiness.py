#!/usr/bin/env python3
"""Validate assurance/spatial_readiness.json against repo files and map catalogue."""
from __future__ import annotations
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
READINESS=ROOT/'assurance'/'spatial_readiness.json'
CATALOGUE=ROOT/'maps'/'layers'/'catalogue.json'
MAPPED={'mapped_authoritative','mapped_representative'}
READY={'map_ready_authoritative','map_ready_representative'}
BLOCKED='blocked_spatial_join'
VALID=MAPPED|READY|{BLOCKED,'not_spatial'}

def main():
    errors=[]
    r=json.loads(READINESS.read_text(encoding='utf-8'))
    c=json.loads(CATALOGUE.read_text(encoding='utf-8'))
    layers={x['layer_id'] for x in c.get('layers',[])}
    seen=set()
    for i,row in enumerate(r.get('datasets',[]),1):
        path=row.get('dataset_path');state=row.get('spatial_state');layer=row.get('map_layer_id')
        label=path or f'row {i}'
        if not path:errors.append(f'{label}: missing dataset_path');continue
        if path in seen:errors.append(f'{label}: duplicate readiness record')
        seen.add(path)
        if not (ROOT/path).exists():errors.append(f'{label}: dataset path does not exist')
        if state not in VALID:errors.append(f'{label}: invalid spatial_state {state!r}')
        if state in MAPPED:
            if not layer:errors.append(f'{label}: mapped state requires map_layer_id')
            elif layer not in layers:errors.append(f'{label}: map_layer_id {layer!r} missing from catalogue')
            if not row.get('mapped_poc'):errors.append(f'{label}: mapped state requires mapped_poc')
        if state==BLOCKED:
            if layer:errors.append(f'{label}: blocked spatial join must not claim map_layer_id')
            if not row.get('join_or_blocker'):errors.append(f'{label}: blocked spatial join requires blocker explanation')
    if errors:
        print('Spatial readiness validation FAILED')
        for e in errors:print(f' - {e}')
        raise SystemExit(1)
    print(f'Spatial readiness validation OK: {len(seen)} datasets, {len(layers)} catalogue layers')

if __name__=='__main__':main()
