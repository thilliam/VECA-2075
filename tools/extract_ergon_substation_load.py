#!/usr/bin/env python3
"""Summarise Ergon annual zone-substation half-hourly load archive.

The source labels load fields MW/MVA. Values are preserved exactly as reported.
A separate interpreted /1000 view is emitted because cross-checks against other
Ergon/Powerlink planning evidence show the archive values are systematically
three orders of magnitude larger than plausible zone-substation MW/MVA loads.
The interpreted fields are explicitly marked as an empirical scale interpretation,
not an Ergon-published correction. Raw fields remain authoritative source evidence.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import re
import statistics
import zipfile
from pathlib import Path

SCALE_INTERPRETATION_FACTOR = 0.001
SCALE_INTERPRETATION = "empirical_divide_by_1000_crosschecked_against_ergon_powerlink_planning_evidence"


def pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    xs = sorted(values)
    if len(xs) == 1:
        return xs[0]
    pos = (len(xs) - 1) * p
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi:
        return xs[lo]
    frac = pos - lo
    return xs[lo] * (1 - frac) + xs[hi] * frac


def fnum(value: str) -> float | None:
    try:
        v = float(value)
        return v if math.isfinite(v) else None
    except Exception:
        return None


def base_name(member: str) -> str:
    name = Path(member).stem
    return re.sub(r"_EECL_20252026$", "", name, flags=re.I).strip()


def scaled(value: float | None) -> float | str:
    return round(value * SCALE_INTERPRETATION_FACTOR, 6) if value is not None else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("reconciliation", type=Path)
    ap.add_argument("--inventory-profile", type=Path, required=True)
    args = ap.parse_args()

    inventory = json.loads(args.inventory_profile.read_text(encoding="utf-8"))
    expected = {m["name"] for m in inventory["members"] if m["name"].lower().endswith(".csv")}
    rows_out = []
    observed = set()

    with zipfile.ZipFile(args.archive) as zf:
        for member in sorted(n for n in zf.namelist() if n.lower().endswith(".csv")):
            observed.add(member)
            text = zf.read(member).decode("utf-8-sig", errors="replace")
            reader = csv.DictReader(io.StringIO(text))
            mw: list[float] = []
            mva: list[float] = []
            dates: list[str] = []
            invalid = negative = 0
            for r in reader:
                d = (r.get("Date") or "").strip()
                if d:
                    dates.append(d)
                a = fnum((r.get("MW") or "").strip())
                b = fnum((r.get("MVA") or "").strip())
                if a is None or b is None:
                    invalid += 1
                    continue
                mw.append(a); mva.append(b)
                if a < 0 or b < 0:
                    negative += 1

            mean_mw = statistics.fmean(mw) if mw else None
            p95_mw = pct(mw, 0.95)
            p99_mw = pct(mw, 0.99)
            peak_mw = max(mw) if mw else None
            mean_mva = statistics.fmean(mva) if mva else None
            p95_mva = pct(mva, 0.95)
            p99_mva = pct(mva, 0.99)
            peak_mva = max(mva) if mva else None

            scale_flag = bool((p99_mw is not None and abs(p99_mw) > 500) or (p99_mva is not None and abs(p99_mva) > 500))
            rows_out.append({
                "source_record_id": member,
                "substation_name": base_name(member),
                "source_file": member,
                "period_start": min(dates) if dates else "",
                "period_end": max(dates) if dates else "",
                "observation_count_valid": len(mw),
                "invalid_or_missing_rows": invalid,
                "negative_rows": negative,
                "reported_units": "MW/MVA",
                "reported_mean_mw": round(mean_mw, 6) if mean_mw is not None else "",
                "reported_p95_mw": round(p95_mw, 6) if p95_mw is not None else "",
                "reported_p99_mw": round(p99_mw, 6) if p99_mw is not None else "",
                "reported_peak_mw": round(peak_mw, 6) if peak_mw is not None else "",
                "reported_mean_mva": round(mean_mva, 6) if mean_mva is not None else "",
                "reported_p95_mva": round(p95_mva, 6) if p95_mva is not None else "",
                "reported_p99_mva": round(p99_mva, 6) if p99_mva is not None else "",
                "reported_peak_mva": round(peak_mva, 6) if peak_mva is not None else "",
                "possible_scale_or_meter_anomaly": str(scale_flag).lower(),
                "source_scale_interpretation": SCALE_INTERPRETATION,
                "interpretation_factor": SCALE_INTERPRETATION_FACTOR,
                "interpreted_mean_mw": scaled(mean_mw),
                "interpreted_p95_mw": scaled(p95_mw),
                "interpreted_p99_mw": scaled(p99_mw),
                "interpreted_peak_mw": scaled(peak_mw),
                "interpreted_mean_mva": scaled(mean_mva),
                "interpreted_p95_mva": scaled(p95_mva),
                "interpreted_p99_mva": scaled(p99_mva),
                "interpreted_peak_mva": scaled(peak_mva),
                "interpretation_note": "Raw source values retained. Interpreted fields divide by 1000 based on cross-source scale validation; Ergon has not been found to publish an explicit correction notice.",
            })

    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fields = list(rows_out[0].keys()) if rows_out else []
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows_out)

    recon = {
        "source": "Ergon Network Zone Substation Load Data 2025-26 archive",
        "expected_csv_members": len(expected),
        "extracted_records": len(rows_out),
        "missing_source_record_ids": missing,
        "extra_source_record_ids": extra,
        "exact_identity_match": not missing and not extra and len(rows_out) == len(expected),
        "flagged_possible_scale_or_meter_anomaly": sum(r["possible_scale_or_meter_anomaly"] == "true" for r in rows_out),
        "source_scale_interpretation": SCALE_INTERPRETATION,
        "interpretation_factor": SCALE_INTERPRETATION_FACTOR,
        "interpretation_is_source_published_correction": False,
    }
    args.reconciliation.parent.mkdir(parents=True, exist_ok=True)
    args.reconciliation.write_text(json.dumps(recon, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(recon, indent=2))
    if not recon["exact_identity_match"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
