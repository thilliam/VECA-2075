#!/usr/bin/env python3
"""Extract VECA's QLD/NSW/ACT/VIC SA2 population layer from ABS Regional Population 2024-25.

Outputs:
- data/derived/population_sa2_east.csv
- data/derived/population_state_validation.csv
- research/population/population_validation.md

The script intentionally uses the ABS-published XLSX cubes because ABS itself recommends
Excel cubes over Data Explorer for large SA2 datasets. It preserves ASGS Edition 3 SA2 codes.
"""
from __future__ import annotations

import io
import re
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

BASE = "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25"
LONG_URL = f"{BASE}/32180DS0003_2001-25.xlsx"
CURRENT_URL = f"{BASE}/32180DS0001_2024-25.xlsx"
OUT = Path("data/derived/population_sa2_east.csv")
VALIDATION_CSV = Path("data/derived/population_state_validation.csv")
VALIDATION_MD = Path("research/population/population_validation.md")
STATE_MAP = {"1": "NSW", "2": "VIC", "3": "QLD", "8": "ACT"}
TARGET_STATE_CODES = set(STATE_MAP)
SOURCE_ID = "SRC-ABS-SA2-ERP-2025"
GEOGRAPHY_VERSION = "ASGS Edition 3 (2021)"


def download(url: str) -> bytes:
    r = requests.get(url, timeout=90)
    r.raise_for_status()
    if len(r.content) < 50_000:
        raise RuntimeError(f"ABS download unexpectedly small: {url} ({len(r.content)} bytes)")
    return r.content


def norm(v: object) -> str:
    if pd.isna(v):
        return ""
    return re.sub(r"\s+", " ", str(v).strip()).lower()


def find_sa2_sheet(book: bytes, required_tokens: Iterable[str]) -> tuple[str, pd.DataFrame, int]:
    xls = pd.ExcelFile(io.BytesIO(book))
    wanted = [t.lower() for t in required_tokens]
    diagnostics = []
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None)
        probe = raw.iloc[:40, :].copy()
        for idx, row in probe.iterrows():
            text = " | ".join(norm(v) for v in row.tolist())
            if "sa2" in text and "code" in text and all(t in text for t in wanted):
                return sheet, raw, int(idx)
        diagnostics.append(sheet)
    raise RuntimeError(f"Could not locate SA2 worksheet/header. Sheets inspected: {diagnostics}")


def flatten_headers(raw: pd.DataFrame, header_row: int, depth: int = 4) -> list[str]:
    start = max(0, header_row - depth + 1)
    headers = []
    for c in range(raw.shape[1]):
        bits = []
        for r in range(start, header_row + 1):
            s = norm(raw.iat[r, c])
            if s and s not in bits:
                bits.append(s)
        headers.append(" | ".join(bits))
    return headers


def find_col(headers: list[str], *needles: str, exclude: tuple[str, ...] = ()) -> int:
    needles = tuple(n.lower() for n in needles)
    exclude = tuple(e.lower() for e in exclude)
    matches = []
    for i, h in enumerate(headers):
        if all(n in h for n in needles) and not any(e in h for e in exclude):
            matches.append(i)
    if not matches:
        raise RuntimeError(f"Missing column containing {needles}; header sample={headers[:15]}")
    return matches[-1]


def clean_code(series: pd.Series) -> pd.Series:
    return series.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series, errors="coerce")


def extract_long(book: bytes) -> pd.DataFrame:
    sheet, raw, hrow = find_sa2_sheet(book, ["2025"])
    headers = flatten_headers(raw, hrow)
    code_i = find_col(headers, "sa2", "code")
    name_i = find_col(headers, "sa2", "name")

    year_cols = {}
    for year in [2001, 2010, 2015, 2020, 2024, 2025]:
        candidates = [i for i, h in enumerate(headers) if re.search(rf"(^|\D){year}(\D|$)", h)]
        if not candidates:
            raise RuntimeError(f"Could not find ERP {year} column on {sheet}")
        year_cols[year] = candidates[-1]

    data = raw.iloc[hrow + 1 :].copy()
    out = pd.DataFrame({
        "sa2_code": clean_code(data.iloc[:, code_i]),
        "sa2_name": data.iloc[:, name_i].astype(str).str.strip(),
    })
    for year, idx in year_cols.items():
        out[f"erp_{year}"] = numeric(data.iloc[:, idx])

    out = out[out["sa2_code"].str.match(r"^[1-8]\d{8}$", na=False)].copy()
    out["state_code"] = out["sa2_code"].str[0]
    out = out[out["state_code"].isin(TARGET_STATE_CODES)].copy()
    out["state"] = out["state_code"].map(STATE_MAP)
    return out


def extract_current_components(book: bytes) -> pd.DataFrame:
    sheet, raw, hrow = find_sa2_sheet(book, ["2025"])
    headers = flatten_headers(raw, hrow, depth=6)
    code_i = find_col(headers, "sa2", "code")

    # These labels are intentionally semantic rather than positional. If ABS changes the cube,
    # fail loudly rather than silently merging the wrong columns.
    ni_i = find_col(headers, "natural", "increase", "2024", "25")
    nim_i = find_col(headers, "net", "internal", "migration", "2024", "25")
    nom_i = find_col(headers, "net", "overseas", "migration", "2024", "25")

    data = raw.iloc[hrow + 1 :].copy()
    out = pd.DataFrame({
        "sa2_code": clean_code(data.iloc[:, code_i]),
        "natural_increase_2024_25": numeric(data.iloc[:, ni_i]),
        "net_internal_migration_2024_25": numeric(data.iloc[:, nim_i]),
        "net_overseas_migration_2024_25": numeric(data.iloc[:, nom_i]),
    })
    out = out[out["sa2_code"].str.match(r"^[1-8]\d{8}$", na=False)].copy()
    return out.drop_duplicates("sa2_code")


def pct_change(new: pd.Series, old: pd.Series) -> pd.Series:
    return ((new - old) / old.where(old != 0) * 100).round(2)


def main() -> None:
    long = extract_long(download(LONG_URL))
    current = extract_current_components(download(CURRENT_URL))
    df = long.merge(current, on="sa2_code", how="left", validate="one_to_one")

    df["change_2015_25_abs"] = df["erp_2025"] - df["erp_2015"]
    df["change_2015_25_pct"] = pct_change(df["erp_2025"], df["erp_2015"])
    df["change_2020_25_abs"] = df["erp_2025"] - df["erp_2020"]
    df["change_2020_25_pct"] = pct_change(df["erp_2025"], df["erp_2020"])
    df["change_2024_25_abs"] = df["erp_2025"] - df["erp_2024"]
    df["change_2024_25_pct"] = pct_change(df["erp_2025"], df["erp_2024"])
    df["source_id"] = SOURCE_ID
    df["geography_version"] = GEOGRAPHY_VERSION

    cols = [
        "sa2_code", "sa2_name", "state", "state_code",
        "erp_2001", "erp_2010", "erp_2015", "erp_2020", "erp_2024", "erp_2025",
        "change_2015_25_abs", "change_2015_25_pct",
        "change_2020_25_abs", "change_2020_25_pct",
        "change_2024_25_abs", "change_2024_25_pct",
        "natural_increase_2024_25", "net_internal_migration_2024_25", "net_overseas_migration_2024_25",
        "source_id", "geography_version",
    ]
    df = df[cols].sort_values(["state_code", "sa2_code"]).reset_index(drop=True)

    if len(df) < 1_000:
        raise RuntimeError(f"Expected >1000 SA2 rows across QLD/NSW/ACT/VIC; got {len(df)}")
    if df["sa2_code"].duplicated().any():
        raise RuntimeError("Duplicate SA2 codes found")
    if set(df["state"].dropna()) != {"QLD", "NSW", "ACT", "VIC"}:
        raise RuntimeError(f"Unexpected state coverage: {sorted(df['state'].dropna().unique())}")
    if df["erp_2025"].isna().mean() > 0.01:
        raise RuntimeError("More than 1% of ERP 2025 values are missing")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_MD.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    state = (
        df.groupby("state", as_index=False)
        .agg(sa2_rows=("sa2_code", "count"), erp_2024=("erp_2024", "sum"), erp_2025=("erp_2025", "sum"))
    )
    state["change_2024_25_abs"] = state["erp_2025"] - state["erp_2024"]
    state["change_2024_25_pct"] = (state["change_2024_25_abs"] / state["erp_2024"] * 100).round(2)
    state.to_csv(VALIDATION_CSV, index=False)

    top_growth = df.nlargest(15, "change_2024_25_abs")[["state", "sa2_name", "change_2024_25_abs", "change_2024_25_pct"]]
    top_decline = df.nsmallest(15, "change_2024_25_abs")[["state", "sa2_name", "change_2024_25_abs", "change_2024_25_pct"]]
    top_internal = df.nlargest(15, "net_internal_migration_2024_25")[["state", "sa2_name", "net_internal_migration_2024_25", "change_2024_25_abs"]]

    def md_table(x: pd.DataFrame) -> str:
        return x.to_markdown(index=False)

    VALIDATION_MD.write_text(
        "# Population extraction validation\n\n"
        "Source: ABS Regional Population 2024-25. Geography: ASGS Edition 3 (2021).\n\n"
        f"Extracted **{len(df):,} SA2 records** across QLD, NSW, ACT and VIC.\n\n"
        "## State-level sums of extracted SA2 records\n\n"
        + md_table(state)
        + "\n\n## Largest 2024-25 absolute SA2 growth\n\n"
        + md_table(top_growth)
        + "\n\n## Largest 2024-25 absolute SA2 declines\n\n"
        + md_table(top_decline)
        + "\n\n## Largest net internal-migration gains, 2024-25\n\n"
        + md_table(top_internal)
        + "\n\n## Validation notes\n\n"
        "- SA2 codes are retained exactly as supplied under ASGS Edition 3.\n"
        "- State totals here are sums of included SA2 records and are used as extraction QA; they should not be silently substituted for separately published state ERP without checking scope.\n"
        "- Population change is evidence of observed movement, not a causal growth-driver classification.\n"
        "- Region typology and causal-driver attribution remain separate research steps.\n",
        encoding="utf-8",
    )
    print(f"Wrote {OUT} with {len(df):,} rows")
    print(state.to_string(index=False))


if __name__ == "__main__":
    main()
