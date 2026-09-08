#!/usr/bin/env python3
"""Materialise VECA's QLD/NSW/ACT/VIC SA2 population layer from ABS 2024-25 cubes."""
from __future__ import annotations

import io
import re
from pathlib import Path

import pandas as pd
import requests

BASE = "https://www.abs.gov.au/statistics/people/population/regional-population/2024-25"
LONG_URL = f"{BASE}/32180DS0003_2001-25.xlsx"
CURRENT_URL = f"{BASE}/32180DS0001_2024-25.xlsx"
OUT = Path("data/derived/population_sa2_east.csv")
VALIDATION_CSV = Path("data/derived/population_state_validation.csv")
VALIDATION_MD = Path("research/population/population_validation.md")
STATE_MAP = {"1": "NSW", "2": "VIC", "3": "QLD", "8": "ACT"}
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


def locate_sa2_table(book: bytes) -> tuple[str, pd.DataFrame, int]:
    xls = pd.ExcelFile(io.BytesIO(book))
    for sheet in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet, header=None)
        for idx, row in raw.iloc[:60, :].iterrows():
            text = " | ".join(norm(v) for v in row.tolist())
            if "sa2" in text and "code" in text and "name" in text:
                return sheet, raw, int(idx)
    raise RuntimeError(f"Could not locate SA2 table; sheets={xls.sheet_names}")


def header_block(raw: pd.DataFrame, anchor: int, before: int = 5, after: int = 4) -> list[str]:
    start, end = max(0, anchor - before), min(len(raw) - 1, anchor + after)
    headers: list[str] = []
    for c in range(raw.shape[1]):
        bits: list[str] = []
        for r in range(start, end + 1):
            s = norm(raw.iat[r, c])
            if s and s not in bits:
                bits.append(s)
        headers.append(" | ".join(bits))
    return headers


def find_col(headers: list[str], *needles: str) -> int:
    n = tuple(x.lower() for x in needles)
    hits = [i for i, h in enumerate(headers) if all(x in h for x in n)]
    if not hits:
        raise RuntimeError(f"Missing column containing {n}; headers={headers[:30]}")
    return hits[-1]


def find_year_col(headers: list[str], year: int) -> int:
    hits = [i for i, h in enumerate(headers) if re.search(rf"(^|\D){year}(\D|$)", h)]
    if not hits:
        raise RuntimeError(f"Missing ERP year {year}; headers={headers[:35]}")
    return hits[-1]


def first_data_row(raw: pd.DataFrame, code_col: int, after: int) -> int:
    for r in range(after + 1, len(raw)):
        s = re.sub(r"\.0$", "", str(raw.iat[r, code_col]).strip())
        if re.match(r"^[1-8]\d{8}$", s):
            return r
    raise RuntimeError("Could not locate first 9-digit SA2 data row")


def clean_code(s: pd.Series) -> pd.Series:
    return s.astype(str).str.replace(r"\.0$", "", regex=True).str.strip()


def num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s, errors="coerce")


def extract_long(book: bytes) -> pd.DataFrame:
    sheet, raw, anchor = locate_sa2_table(book)
    headers = header_block(raw, anchor)
    code_i, name_i = find_col(headers, "sa2", "code"), find_col(headers, "sa2", "name")
    year_i = {y: find_year_col(headers, y) for y in [2001, 2010, 2015, 2020, 2024, 2025]}
    start = first_data_row(raw, code_i, anchor)
    data = raw.iloc[start:].copy()
    out = pd.DataFrame({"sa2_code": clean_code(data.iloc[:, code_i]), "sa2_name": data.iloc[:, name_i].astype(str).str.strip()})
    for y, i in year_i.items():
        out[f"erp_{y}"] = num(data.iloc[:, i])
    out = out[out.sa2_code.str.match(r"^[1-8]\d{8}$", na=False)].copy()
    out["state_code"] = out.sa2_code.str[0]
    out = out[out.state_code.isin(STATE_MAP)].copy()
    out["state"] = out.state_code.map(STATE_MAP)
    print(f"Long cube: {sheet}, header anchor row {anchor}, {len(out)} target SA2 rows")
    return out


def component_col(headers: list[str], tokens: tuple[str, ...]) -> int:
    hits = [i for i, h in enumerate(headers) if all(t in h for t in tokens)]
    if not hits:
        raise RuntimeError(f"Missing component column {tokens}; headers={headers[:45]}")
    return hits[-1]


def extract_components(book: bytes) -> pd.DataFrame:
    sheet, raw, anchor = locate_sa2_table(book)
    headers = header_block(raw, anchor, before=7, after=7)
    code_i = find_col(headers, "sa2", "code")
    # Current cube contains only 2024 and 2025, so semantic labels are sufficient here.
    ni_i = component_col(headers, ("natural", "increase"))
    nim_i = component_col(headers, ("net", "internal", "migration"))
    nom_i = component_col(headers, ("net", "overseas", "migration"))
    start = first_data_row(raw, code_i, anchor)
    data = raw.iloc[start:].copy()
    out = pd.DataFrame({
        "sa2_code": clean_code(data.iloc[:, code_i]),
        "natural_increase_2024_25": num(data.iloc[:, ni_i]),
        "net_internal_migration_2024_25": num(data.iloc[:, nim_i]),
        "net_overseas_migration_2024_25": num(data.iloc[:, nom_i]),
    })
    out = out[out.sa2_code.str.match(r"^[1-8]\d{8}$", na=False)].drop_duplicates("sa2_code")
    print(f"Current cube: {sheet}, header anchor row {anchor}, {len(out)} SA2 component rows")
    return out


def pct(new: pd.Series, old: pd.Series) -> pd.Series:
    return ((new - old) / old.where(old != 0) * 100).round(2)


def main() -> None:
    df = extract_long(download(LONG_URL)).merge(extract_components(download(CURRENT_URL)), on="sa2_code", how="left", validate="one_to_one")
    for y in [2015, 2020, 2024]:
        df[f"change_{y}_25_abs"] = df.erp_2025 - df[f"erp_{y}"]
        df[f"change_{y}_25_pct"] = pct(df.erp_2025, df[f"erp_{y}"])
    df["source_id"] = SOURCE_ID
    df["geography_version"] = GEOGRAPHY_VERSION

    cols = ["sa2_code","sa2_name","state","state_code","erp_2001","erp_2010","erp_2015","erp_2020","erp_2024","erp_2025",
            "change_2015_25_abs","change_2015_25_pct","change_2020_25_abs","change_2020_25_pct","change_2024_25_abs","change_2024_25_pct",
            "natural_increase_2024_25","net_internal_migration_2024_25","net_overseas_migration_2024_25","source_id","geography_version"]
    df = df[cols].sort_values(["state_code","sa2_code"]).reset_index(drop=True)

    if len(df) < 1000:
        raise RuntimeError(f"Expected >1000 target SA2 rows; got {len(df)}")
    if df.sa2_code.duplicated().any():
        raise RuntimeError("Duplicate SA2 codes")
    if set(df.state.dropna()) != {"QLD","NSW","ACT","VIC"}:
        raise RuntimeError(f"Unexpected states: {sorted(df.state.dropna().unique())}")
    if df.erp_2025.isna().mean() > 0.01:
        raise RuntimeError("Too many missing ERP 2025 values")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_MD.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)

    state = df.groupby("state", as_index=False).agg(sa2_rows=("sa2_code","count"), erp_2024=("erp_2024","sum"), erp_2025=("erp_2025","sum"))
    state["change_2024_25_abs"] = state.erp_2025 - state.erp_2024
    state["change_2024_25_pct"] = (state.change_2024_25_abs / state.erp_2024 * 100).round(2)
    state.to_csv(VALIDATION_CSV, index=False)

    growth = df.nlargest(15,"change_2024_25_abs")[["state","sa2_name","change_2024_25_abs","change_2024_25_pct"]]
    decline = df.nsmallest(15,"change_2024_25_abs")[["state","sa2_name","change_2024_25_abs","change_2024_25_pct"]]
    internal = df.nlargest(15,"net_internal_migration_2024_25")[["state","sa2_name","net_internal_migration_2024_25","change_2024_25_abs"]]
    VALIDATION_MD.write_text(
        "# Population extraction validation\n\n"
        f"Extracted **{len(df):,} SA2 records** across QLD, NSW, ACT and VIC from ABS Regional Population 2024-25 using ASGS Edition 3 geography.\n\n"
        "## State-level sums\n\n" + state.to_markdown(index=False) +
        "\n\n## Largest 2024-25 absolute SA2 growth\n\n" + growth.to_markdown(index=False) +
        "\n\n## Largest 2024-25 absolute SA2 declines\n\n" + decline.to_markdown(index=False) +
        "\n\n## Largest net internal-migration gains, 2024-25\n\n" + internal.to_markdown(index=False) +
        "\n\n## Discipline\n\nPopulation change and migration components are observed evidence. They are not, by themselves, causal region-type or growth-driver classifications.\n",
        encoding="utf-8")
    print(f"Wrote {OUT} with {len(df):,} rows")
    print(state.to_string(index=False))


if __name__ == "__main__":
    main()
