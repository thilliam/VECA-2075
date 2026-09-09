#!/usr/bin/env python3
"""Build POC-004 energy/capital/freight derivatives on top of POC-003.

This POC intentionally distinguishes exact/source geometry from representative anchors.
No invented transmission alignments or REZ polygons are created here.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

from build_map_poc003 import main as build_poc003

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "maps" / "poc-004" / "data"
REGISTRY = ROOT / "maps" / "poc-004" / "spatial_overrides.csv"
TRANSMISSION = ROOT / "domains" / "energy" / "data" / "derived" / "transmission_projects_seed.csv"
ENERGY_ZONES = ROOT / "data" / "derived" / "energy_zones_seed.csv"
CAPITAL = ROOT / "data" / "derived" / "infrastructure_projects_seed.csv"
FREIGHT = ROOT / "data" / "derived" / "transport" / "intermodal_terminals_seed.csv"


def read_csv(path: Path):
    with path.open(newline="", encoding="utf-8-sig") as fp:
        return list(csv.DictReader(fp))


def registry():
    return {r["entity_id"]: r for r in read_csv(REGISTRY)}


def feature(entity_id: str, name: str, domain: str, props: dict, reg: dict):
    r = reg.get(entity_id)
    if not r:
        return None
    out = dict(props)
    out.update({
        "entity_id": entity_id,
        "name": name,
        "domain": domain,
        "geometry_quality": r["geometry_quality"],
        "geometry_note": r["geometry_note"],
    })
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(r["longitude"]), float(r["latitude"])]},
        "properties": out,
    }


def transmission_status(raw: str):
    s = (raw or "").lower()
    if "committed" in s:
        return "committed"
    if "actionable" in s:
        return "actionable"
    if "future" in s:
        return "future"
    return "planned"


def build_transmission(reg):
    out = []
    missing = []
    for row in read_csv(TRANSMISSION):
        eid = row["project_id"]
        f = feature(eid, row["project_name"], "energy-transmission", {
            **row,
            "status": transmission_status(row.get("status_class")),
            "source_dataset": str(TRANSMISSION.relative_to(ROOT)),
            "assurance_state": "reconciled_entity_inventory",
        }, reg)
        if f: out.append(f)
        else: missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_zones(reg):
    out = []
    missing = []
    for row in read_csv(ENERGY_ZONES):
        # POC-004 maps current NSW and proposed VIC zones. Historical QLD potential-REZ
        # geography remains available in the dataset but is not on by default.
        if row.get("state") not in {"NSW", "VIC"}:
            continue
        eid = row["zone_id"]
        status = "declared" if row.get("zone_type") == "declared_REZ" else "proposed"
        f = feature(eid, row["name"], "energy-zone", {
            **row,
            "status": status,
            "source_dataset": str(ENERGY_ZONES.relative_to(ROOT)),
            "assurance_state": "provenance_reconciled",
        }, reg)
        if f: out.append(f)
        else: missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_capital(reg):
    out = []
    missing = []
    for row in read_csv(CAPITAL):
        eid = row["project_id"]
        f = feature(eid, row["name"], "capital-project", {
            **row,
            "status": row.get("status") or "unknown",
            "source_dataset": str(CAPITAL.relative_to(ROOT)),
            "assurance_state": "provenance_reconciled",
        }, reg)
        if f: out.append(f)
        else: missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_freight(reg):
    out = []
    missing = []
    for row in read_csv(FREIGHT):
        eid = row["terminal_id"]
        f = feature(eid, row["name"], "freight-intermodal", {
            **row,
            "status": row.get("status") or "unknown",
            "source_dataset": str(FREIGHT.relative_to(ROOT)),
            "assurance_state": "provenance_reconciled",
        }, reg)
        if f: out.append(f)
        else: missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def write(name: str, data: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    p.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"{name}: {len(data.get('features', [])):,} features, {p.stat().st_size/1_000_000:.2f} MB")


def main():
    build_poc003()
    reg = registry()
    transmission, a = build_transmission(reg)
    zones, b = build_zones(reg)
    capital, c = build_capital(reg)
    freight, d = build_freight(reg)
    write("transmission_projects.geojson", transmission)
    write("energy_zones.geojson", zones)
    write("capital_projects.geojson", capital)
    write("freight_intermodal.geojson", freight)
    gaps = {"transmission": a, "energy_zones": b, "capital": c, "freight": d}
    (OUT / "spatial-gaps.json").write_text(json.dumps(gaps, indent=2), encoding="utf-8")
    manifest = {
        "transmission": {"features": len(transmission["features"]), "geometry_mode": "representative anchors"},
        "energy_zones": {"features": len(zones["features"]), "geometry_mode": "representative anchors"},
        "capital_projects": {"features": len(capital["features"]), "geometry_mode": "representative anchors"},
        "freight_intermodal": {"features": len(freight["features"]), "geometry_mode": "approximate asset points"},
        "health": {"mode": "reuse POC-002 corpus derivative"},
        "education": {"mode": "reuse POC-002 corpus derivative"},
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    gap_count = sum(len(v) for v in gaps.values())
    print(f"POC-004 spatial gaps: {gap_count} -> maps/poc-004/data/spatial-gaps.json")
    print("POC-004 complete")


if __name__ == "__main__":
    main()
