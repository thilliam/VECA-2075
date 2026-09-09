#!/usr/bin/env python3
"""Summarise Ergon annual zone-substation half-hourly load archive.

The source labels load fields MW/MVA. Values are preserved exactly as reported;
this tool does not rescale suspicious values. Robust percentiles and QA flags are
included so raw SCADA/meter anomalies remain visible instead of being corrected
silently.
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
            p99_mw = pct(mw, 0.99)
            p99_mva = pct(mva, 0.99)
            # QA only: a zone-substation 99th percentile above 500 reported MW/MVA
            # warrants checking source scale/meter quality. No correction is made.
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
                "reported_mean_mw": round(statistics.fmean(mw), 6) if mw else "",
                "reported_p95_mw": round(pct(mw, 0.95), 6) if mw else "",
                "reported_p99_mw": round(p99_mw, 6) if p99_mw is not None else "",
                "reported_peak_mw": round(max(mw), 6) if mw else "",
                "reported_mean_mva": round(statistics.fmean(mva), 6) if mva else "",
                "reported_p95_mva": round(pct(mva, 0.95), 6) if mva else "",
                "reported_p99_mva": round(p99_mva, 6) if p99_mva is not None else "",
                "reported_peak_mva": round(max(mva), 6) if mva else "",
                "possible_scale_or_meter_anomaly": str(scale_flag).lower(),
                "interpretation_note": "Raw Ergon reported MW/MVA; no rescaling or spike correction applied.",
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
    }
    args.reconciliation.parent.mkdir(parents=True, exist_ok=True)
    args.reconciliation.write_text(json.dumps(recon, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(recon, indent=2))
    if not recon["exact_identity_match"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
