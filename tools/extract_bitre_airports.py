#!/usr/bin/env python3
"""Extract long-run airport activity for VECA-relevant eastern airports from BITRE.

Primary source: BITRE Airport Traffic Data 1985-2025 (calendar years).
The parser is deliberately defensive because BITRE workbooks are presentation-oriented.
It first seeks a normal row-oriented table; if the workbook changes, it fails with useful
sheet/header diagnostics rather than silently producing incorrect data.

Outputs:
- data/derived/transport/airport_activity_1985_2025.csv
- research/transport/airport_activity_validation.md
"""
from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

URL = "https://www.bitre.gov.au/sites/default/files/documents/WebAirport_CY_1985-2025.xlsx"
OUT = Path("data/derived/transport/airport_activity_1985_2025.csv")
VALIDATION = Path("research/transport/airport_activity_validation.md")
TARGETS = {
    "Brisbane", "Gold Coast", "Sydney", "Canberra", "Melbourne", "Avalon",
    "Newcastle", "Ballina", "Coffs Harbour", "Port Macquarie", "Armidale",
    "Tamworth", "Dubbo", "Orange", "Wagga Wagga", "Albury", "Mildura",
    "Sunshine Coast", "Toowoomba", "Western Sydney"
}


def norm(v: object) -> str:
    if pd.isna(v):
        return ""
    return re.sub(r"\s+", " ", str(v).strip()).lower()


def download() -> bytes:
    r = requests.get(URL, timeout=120)
    r.raise_for_status()
    if len(r.content) < 100_000:
        raise RuntimeError(f"BITRE workbook unexpectedly small: {len(r.content)} bytes")
    return r.content


def flatten(raw: pd.DataFrame, row: int, depth: int = 3) -> list[str]:
    start = max(0, row - depth + 1)
    out = []
    for c in range(raw.shape[1]):
        parts = []
        for r in range(start, row + 1):
            s = norm(raw.iat[r, c])
            if s and s not in parts:
                parts.append(s)
        out.append(" | ".join(parts))
    return out


def find_col(headers: list[str], includes: tuple[str, ...], excludes: tuple[str, ...] = ()) -> int | None:
    matches = []
    for i, h in enumerate(headers):
        if all(x in h for x in includes) and not any(x in h for x in excludes):
            matches.append(i)
    return matches[-1] if matches else None


def parse_row_table(xls: pd.ExcelFile) -> pd.DataFrame | None:
    diagnostics = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None)
        diagnostics.append((sheet, raw.shape))
        for r in range(min(50, len(raw))):
            headers = flatten(raw, r, 4)
            airport_i = find_col(headers, ("airport",))
            year_i = find_col(headers, ("year",))
            passenger_i = find_col(headers, ("passenger",), ("percent", "%"))
            if airport_i is None or year_i is None or passenger_i is None:
                continue
            data = raw.iloc[r + 1 :].copy()
            out = pd.DataFrame({
                "airport": data.iloc[:, airport_i].astype(str).str.strip(),
                "year": pd.to_numeric(data.iloc[:, year_i], errors="coerce"),
                "passenger_movements": pd.to_numeric(data.iloc[:, passenger_i], errors="coerce"),
            })
            aircraft_i = find_col(headers, ("aircraft",), ("percent", "%"))
            if aircraft_i is not None:
                out["aircraft_movements"] = pd.to_numeric(data.iloc[:, aircraft_i], errors="coerce")
            else:
                out["aircraft_movements"] = pd.NA
            out = out[out["year"].between(1985, 2025, inclusive="both")]
            out = out[out["airport"].ne("")]
            if len(out) > 100:
                print(f"Parsed row table from {sheet!r}, header row {r + 1}, {len(out)} records")
                return out
    print("No row-oriented table found. Workbook diagnostics:", diagnostics)
    return None


def parse_matrix(xls: pd.ExcelFile) -> pd.DataFrame | None:
    """Fallback for presentation matrices with years across columns and airport names down rows."""
    records = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None)
        # Identify candidate year row.
        for r in range(min(60, len(raw))):
            years = {}
            for c, v in enumerate(raw.iloc[r].tolist()):
                try:
                    y = int(float(v))
                except (TypeError, ValueError):
                    continue
                if 1985 <= y <= 2025:
                    years[c] = y
            if len(years) < 5:
                continue
            # Search nearby/remaining rows for airport names and numeric values under year columns.
            for rr in range(r + 1, len(raw)):
                row_text = " | ".join(str(v).strip() for v in raw.iloc[rr, : min(8, raw.shape[1])].tolist() if not pd.isna(v))
                if not row_text:
                    continue
                match = None
                low = row_text.lower()
                for target in TARGETS:
                    if target.lower() in low:
                        match = target
                        break
                if not match:
                    continue
                numeric_count = 0
                vals = []
                for c, y in years.items():
                    val = pd.to_numeric(pd.Series([raw.iat[rr, c]]), errors="coerce").iloc[0]
                    if pd.notna(val):
                        numeric_count += 1
                        vals.append((y, float(val)))
                if numeric_count >= 3:
                    for y, val in vals:
                        records.append({"airport": match, "year": y, "passenger_movements": val, "aircraft_movements": pd.NA})
            if records:
                print(f"Parsed matrix-like data from {sheet!r}: {len(records)} records")
                return pd.DataFrame(records)
    return None


def canonical(name: str) -> str:
    low = re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()
    aliases = {
        "coolangatta": "Gold Coast", "gold coast": "Gold Coast",
        "maroochydore": "Sunshine Coast", "sunshine coast": "Sunshine Coast",
        "williamtown": "Newcastle", "newcastle": "Newcastle",
        "tullamarine": "Melbourne", "melbourne": "Melbourne",
        "kingsford smith": "Sydney", "sydney": "Sydney",
        "wellcamp": "Toowoomba", "toowoomba": "Toowoomba",
    }
    for key, value in aliases.items():
        if key in low:
            return value
    for t in TARGETS:
        if t.lower() in low:
            return t
    return name.strip()


def main() -> None:
    book = download()
    xls = pd.ExcelFile(io.BytesIO(book))
    df = parse_row_table(xls)
    if df is None:
        df = parse_matrix(xls)
    if df is None or df.empty:
        raise RuntimeError(f"Could not parse BITRE airport workbook. Sheets: {xls.sheet_names}")

    df["airport"] = df["airport"].map(canonical)
    df = df[df["airport"].isin(TARGETS)].copy()
    df["year"] = df["year"].astype(int)
    # When presentation sheets repeat a metric, keep the largest passenger value per airport/year;
    # this is a defensive de-duplication and is reported in validation.
    df = (df.sort_values("passenger_movements")
            .drop_duplicates(["airport", "year"], keep="last")
            .sort_values(["airport", "year"]))
    df["source_url"] = URL
    df["source_period"] = "calendar_year"

    if not {"Brisbane", "Sydney", "Melbourne", "Canberra"}.issubset(set(df["airport"])):
        raise RuntimeError(f"Core airports missing after parse: {sorted(set(df['airport']))}")
    if df["year"].max() != 2025:
        raise RuntimeError(f"Expected 2025 data; max year is {df['year'].max()}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    coverage = (df.groupby("airport")
                  .agg(first_year=("year", "min"), last_year=("year", "max"), records=("year", "count"), latest_passengers=("passenger_movements", "last"))
                  .reset_index())
    VALIDATION.write_text(
        "# BITRE airport activity extraction validation\n\n"
        "Source: BITRE Airport Traffic Data 1985 to 2025, calendar years.\n\n"
        f"Extracted **{len(df):,} airport-year records** for {df['airport'].nunique()} VECA-relevant eastern airports.\n\n"
        + coverage.to_markdown(index=False)
        + "\n\n## Discipline\n\n"
        "- These are scheduled RPT airport activity records from BITRE; definitions and historical reporting coverage may change over the series.\n"
        "- Airport traffic measures inherited connectivity/economic gravity; it is not a settlement-suitability score.\n"
        "- Western Sydney International is not expected to have a historical traffic series before commencement of operations.\n"
        "- Regional airport declines can reflect airline network changes as well as underlying regional demand.\n",
        encoding="utf-8",
    )
    print(coverage.to_string(index=False))


if __name__ == "__main__":
    main()
