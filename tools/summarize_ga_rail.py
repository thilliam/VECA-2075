#!/usr/bin/env python3
"""Summarise the committed GA rail foundation layer using meaningful network measures.

Reads the already-materialised GeoJSON. Does not re-download source data.
Outputs replace the original feature-count-only summary with counts AND summed source
length_km by operational status, feature subtype, gauge and source jurisdiction.
"""
from __future__ import annotations

import csv
import json
from collections import Counter, defaultdict
from pathlib import Path

SRC = Path("data/derived/transport/ga_rail_east.geojson")
OUT = Path("data/derived/transport/ga_rail_east_summary.csv")
VALIDATION = Path("research/transport/rail_foundation_validation.md")
SUBTYPE = {90015: "Railway", 90016: "Rail Siding", 90017: "Tramline"}


def val(p: dict, *names: str):
    lower = {str(k).lower(): v for k, v in p.items()}
    for n in names:
        if n.lower() in lower and lower[n.lower()] not in (None, ""):
            return lower[n.lower()]
    return None


def clean_label(v) -> str:
    return str(v).strip() if v not in (None, "") else "UNKNOWN"


def main() -> None:
    data = json.loads(SRC.read_text(encoding="utf-8"))
    features = data.get("features", [])
    if not features:
        raise RuntimeError("Committed rail GeoJSON has no features")

    counts: dict[str, Counter] = defaultdict(Counter)
    kms: dict[str, defaultdict[str, float]] = defaultdict(lambda: defaultdict(float))
    missing_length = 0

    for f in features:
        p = f.get("properties", {})
        status = clean_label(val(p, "operational_status", "oper_status", "status"))
        raw_sub = val(p, "featuresubtype", "feature_subtype", "subtype")
        try:
            sub = SUBTYPE.get(int(raw_sub), clean_label(raw_sub))
        except (TypeError, ValueError):
            sub = clean_label(raw_sub)
        gauge = clean_label(val(p, "track_gauge", "gauge"))
        jurisdiction = clean_label(val(p, "source_jurisdiction", "jurisdiction"))
        owner = clean_label(val(p, "owner"))
        length = val(p, "length_km", "lengthkm")
        try:
            length_km = float(length)
        except (TypeError, ValueError):
            length_km = 0.0
            missing_length += 1

        for dimension, label in [
            ("operational_status", status),
            ("feature_subtype", sub),
            ("track_gauge", gauge),
            ("source_jurisdiction", jurisdiction),
            ("owner", owner),
        ]:
            counts[dimension][label] += 1
            kms[dimension][label] += length_km

    rows = []
    for dimension in ["operational_status", "feature_subtype", "track_gauge", "source_jurisdiction"]:
        for label, count in counts[dimension].most_common():
            rows.append((dimension, label, count, round(kms[dimension][label], 3)))
    for label, count in counts["owner"].most_common(30):
        rows.append(("owner_top30", label, count, round(kms["owner"][label], 3)))

    with OUT.open("w", newline="", encoding="utf-8") as fp:
        w = csv.writer(fp)
        w.writerow(["dimension", "value", "feature_count", "source_length_km_sum"])
        w.writerows(rows)

    total_km = sum(kms["operational_status"].values())
    operational_km = sum(
        km for label, km in kms["operational_status"].items()
        if label.lower() in {"operational", "fully capable of operation."}
    )
    railway_km = kms["feature_subtype"].get("Railway", 0.0)
    siding_km = kms["feature_subtype"].get("Rail Siding", 0.0)
    tram_km = kms["feature_subtype"].get("Tramline", 0.0)

    VALIDATION.write_text(
        "# Rail foundation extraction validation\n\n"
        "Source: Geoscience Australia Foundation Rail Infrastructure, Railway_Lines layer.\n\n"
        f"Extracted **{len(features):,} line features** intersecting the broad EXP-001 envelope "
        "(138.5E–154.2E, 39.8S–25.0S). The envelope is an extraction convenience, not a VECA preferred corridor.\n\n"
        "## Network-length QA\n\n"
        f"Summing the source `length_km` attribute gives **{total_km:,.1f} km of source line-segments** across all statuses/types, of which approximately **{operational_km:,.1f} km** are labelled Operational or Fully capable of operation.\n\n"
        f"By feature subtype the source contains approximately **{railway_km:,.1f} km Railway**, **{siding_km:,.1f} km Rail Siding** and **{tram_km:,.1f} km Tramline** within the extraction envelope (all operational statuses combined).\n\n"
        f"`length_km` was missing/unparseable on {missing_length:,} of {len(features):,} features.\n\n"
        "These kilometre sums are more meaningful than feature counts but are still source-segment lengths, not unique corridor-km or track-km. Parallel tracks, sidings and overlapping source records can increase totals.\n\n"
        "## Important limitations\n\n"
        "- Foundation geometry does not measure service frequency, capacity, axle load, speed, ownership quality or freight importance.\n"
        "- Usage/intensity must be layered separately from BITRE/NFDH/state/operator evidence.\n"
        "- Historical/disused/dismantled records remain deliberately present and distinguishable; they may reveal corridor inheritance/option value.\n"
        "- Gauge, subtype, jurisdiction and top-owner summaries are in `ga_rail_east_summary.csv`.\n",
        encoding="utf-8",
    )
    print(f"Summarised {len(features):,} rail features; source length {total_km:,.1f} km")


if __name__ == "__main__":
    main()
