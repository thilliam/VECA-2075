#!/usr/bin/env python3
"""Build POC-004 integrated system derivatives on top of POC-003.

The POC distinguishes exact/source geometry from representative anchors.
No invented transmission alignments, REZ polygons, water networks or planning-area
boundaries are created here.
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
WATER = ROOT / "domains" / "water" / "data" / "derived" / "water_systems_seed.csv"
PLANNING = ROOT / "domains" / "government-intent" / "data" / "derived" / "land_zoning_optionality_seed.csv"
GOV_LAND = ROOT / "domains" / "government-intent" / "data" / "derived" / "government_land_education_seed.csv"

WATER_ANCHORS = {
    "WAT-SEQ": (152.80, -27.55), "WAT-SYD": (150.90, -33.85),
    "WAT-CBR": (149.10, -35.30), "WAT-MELB": (144.90, -37.85),
    "WAT-WAGGA": (147.37, -35.12), "WAT-ALBURY": (146.92, -36.08),
    "WAT-GOULBURN": (149.72, -34.75),
}
PLANNING_ANCHORS = {
    "GI-LAND-SEQ-PFGA": (152.65, -27.62),
    "GI-LAND-TOOWOOMBA-PFGA": (151.95, -27.58),
    "GI-LAND-CC-SCP": (151.33, -33.28),
}
GOV_LAND_ANCHORS = {
    "GLE-CC-003": (151.38, -33.30),
    "GLE-NE-001": (150.94, -31.08),
    "GLE-ACT-001": (149.09, -35.34),
    "GLE-SEQ-001": (153.05, -27.60),
    "GLE-SEQ-002": (152.76, -27.66),
    "GLE-SEQ-003": (151.95, -27.60),
}


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
    out.update({"entity_id": entity_id, "name": name, "domain": domain,
                "geometry_quality": r["geometry_quality"], "geometry_note": r["geometry_note"]})
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [float(r["longitude"]), float(r["latitude"])]}, "properties": out}


def anchored_feature(entity_id: str, name: str, domain: str, props: dict, lon: float, lat: float, quality: str, note: str):
    out = dict(props)
    out.update({"entity_id": entity_id, "name": name, "domain": domain,
                "geometry_quality": quality, "geometry_note": note})
    return {"type": "Feature", "geometry": {"type": "Point", "coordinates": [lon, lat]}, "properties": out}


def transmission_status(raw: str):
    s = (raw or "").lower()
    if "committed" in s: return "committed"
    if "actionable" in s: return "actionable"
    if "future" in s: return "future"
    return "planned"


def build_transmission(reg):
    out, missing = [], []
    for row in read_csv(TRANSMISSION):
        eid = row["project_id"]
        f = feature(eid, row["project_name"], "energy-transmission", {**row, "status": transmission_status(row.get("status_class")), "source_dataset": str(TRANSMISSION.relative_to(ROOT)), "assurance_state": "reconciled_entity_inventory"}, reg)
        out.append(f) if f else missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_zones(reg):
    out, missing = [], []
    for row in read_csv(ENERGY_ZONES):
        if row.get("state") not in {"NSW", "VIC"}: continue
        eid = row["zone_id"]
        status = "declared" if row.get("zone_type") == "declared_REZ" else "proposed"
        f = feature(eid, row["name"], "energy-zone", {**row, "status": status, "source_dataset": str(ENERGY_ZONES.relative_to(ROOT)), "assurance_state": "provenance_reconciled"}, reg)
        out.append(f) if f else missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_capital(reg):
    out, missing = [], []
    for row in read_csv(CAPITAL):
        eid = row["project_id"]
        f = feature(eid, row["name"], "capital-project", {**row, "status": row.get("status") or "unknown", "source_dataset": str(CAPITAL.relative_to(ROOT)), "assurance_state": "provenance_reconciled"}, reg)
        out.append(f) if f else missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_freight(reg):
    out, missing = [], []
    for row in read_csv(FREIGHT):
        eid = row["terminal_id"]
        f = feature(eid, row["name"], "freight-intermodal", {**row, "status": row.get("status") or "unknown", "source_dataset": str(FREIGHT.relative_to(ROOT)), "assurance_state": "provenance_reconciled"}, reg)
        out.append(f) if f else missing.append(eid)
    return {"type": "FeatureCollection", "features": out}, missing


def build_water():
    out, missing = [], []
    for row in read_csv(WATER):
        eid = row["system_id"]; loc = WATER_ANCHORS.get(eid)
        if not loc: missing.append(eid); continue
        out.append(anchored_feature(eid, row["system_name"], "water-system", {**row, "source_dataset": str(WATER.relative_to(ROOT)), "assurance_state": "structured_research_seed"}, loc[0], loc[1], "representative_system_anchor", "Representative urban water-system anchor; not dam, pipe, catchment or service-area geometry"))
    return {"type": "FeatureCollection", "features": out}, missing


def build_planning_optionality():
    out, missing = [], []
    for row in read_csv(PLANNING):
        eid = row["area_id"]; loc = PLANNING_ANCHORS.get(eid)
        if not loc:
            # Broad statewide/multi-region policies are intentionally not converted to misleading points.
            continue
        out.append(anchored_feature(eid, row["area_or_program"], "planning-optionality", {**row, "source_dataset": str(PLANNING.relative_to(ROOT)), "assurance_state": "provenance_reconciled"}, loc[0], loc[1], "representative_program_anchor", "Representative program/growth-area anchor; not statutory boundary or parcel geometry"))
    for row in read_csv(GOV_LAND):
        if row.get("record_type") not in {"government_land", "growth_land"}: continue
        eid = row["record_id"]; loc = GOV_LAND_ANCHORS.get(eid)
        if not loc:
            missing.append(eid); continue
        out.append(anchored_feature(eid, row["asset_or_area"], "planning-optionality", {**row, "source_dataset": str(GOV_LAND.relative_to(ROOT)), "assurance_state": "provenance_reconciled"}, loc[0], loc[1], "representative_program_anchor", "Representative government/growth-land anchor; not parcel boundary"))
    return {"type": "FeatureCollection", "features": out}, missing


def write(name: str, data: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    p = OUT / name
    p.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
    print(f"{name}: {len(data.get('features', [])):,} features, {p.stat().st_size/1_000_000:.2f} MB")


def main():
    build_poc003(); reg = registry()
    transmission, a = build_transmission(reg); zones, b = build_zones(reg)
    capital, c = build_capital(reg); freight, d = build_freight(reg)
    water, e = build_water(); planning, f = build_planning_optionality()
    write("transmission_projects.geojson", transmission); write("energy_zones.geojson", zones)
    write("capital_projects.geojson", capital); write("freight_intermodal.geojson", freight)
    write("water_systems.geojson", water); write("planning_optionality.geojson", planning)
    gaps = {"transmission": a, "energy_zones": b, "capital": c, "freight": d, "water": e, "planning_optionality": f}
    (OUT / "spatial-gaps.json").write_text(json.dumps(gaps, indent=2), encoding="utf-8")
    manifest = {
        "transmission": {"features": len(transmission["features"]), "geometry_mode": "representative anchors"},
        "energy_zones": {"features": len(zones["features"]), "geometry_mode": "representative anchors"},
        "capital_projects": {"features": len(capital["features"]), "geometry_mode": "representative anchors"},
        "freight_intermodal": {"features": len(freight["features"]), "geometry_mode": "approximate asset points"},
        "water_systems": {"features": len(water["features"]), "geometry_mode": "representative system anchors"},
        "planning_optionality": {"features": len(planning["features"]), "geometry_mode": "representative program anchors"},
        "health": {"mode": "reuse POC-002 corpus derivative"}, "education": {"mode": "reuse POC-002 corpus derivative"}
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    gap_count = sum(len(v) for v in gaps.values())
    print(f"POC-004 spatial gaps: {gap_count} -> maps/poc-004/data/spatial-gaps.json")
    print("POC-004 complete")


if __name__ == "__main__": main()
