#!/usr/bin/env python3
"""Extract scoped AEMO NEM Generation Information rows using stdlib XLSX parsing.

The independent expected-ID inventory is supplied separately (built with openpyxl in
CI). This extractor deliberately uses a different implementation path and reconciles
exact Gen Info Unit IDs before succeeding.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "pkg": "http://schemas.openxmlformats.org/package/2006/relationships",
}
CELL_RE = re.compile(r"([A-Z]+)(\d+)")
TARGET_REGIONS = {"QLD1", "NSW1", "VIC1"}


def col_index(ref: str) -> int:
    m = CELL_RE.match(ref)
    if not m:
        return 0
    n = 0
    for ch in m.group(1):
        n = n * 26 + ord(ch) - 64
    return n - 1


def shared_strings(zf: zipfile.ZipFile) -> list[str]:
    try:
        root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
    except KeyError:
        return []
    return ["".join(t.text or "" for t in si.iterfind(".//main:t", NS)) for si in root.findall("main:si", NS)]


def sheet_path(zf: zipfile.ZipFile, wanted: str) -> str:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("pkg:Relationship", NS)}
    for s in wb.find("main:sheets", NS):
        if s.attrib.get("name") != wanted:
            continue
        rid = s.attrib[f"{{{NS['rel']}}}id"]
        target = targets[rid]
        return target.lstrip("/") if target.startswith("/") else "xl/" + target.lstrip("/")
    raise KeyError(f"sheet not found: {wanted}")


def cell_value(cell: ET.Element, strings: list[str]) -> object:
    t = cell.attrib.get("t")
    if t == "inlineStr":
        return "".join(x.text or "" for x in cell.iterfind(".//main:t", NS))
    v = cell.find("main:v", NS)
    if v is None or v.text is None:
        return None
    raw = v.text
    if t == "s":
        try:
            return strings[int(raw)]
        except (ValueError, IndexError):
            return raw
    if t == "b":
        return raw == "1"
    try:
        return int(raw) if "." not in raw and "E" not in raw.upper() else float(raw)
    except ValueError:
        return raw


def row_values(row: ET.Element, strings: list[str], width: int) -> list[object]:
    out: list[object] = [None] * width
    for cell in row.findall("main:c", NS):
        idx = col_index(cell.attrib.get("r", "A1"))
        if idx >= len(out):
            out.extend([None] * (idx + 1 - len(out)))
        out[idx] = cell_value(cell, strings)
    return out


def clean_header(value: object, idx: int) -> str:
    text = str(value or "").strip().lower()
    text = text.replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "_", text).strip("_")
    return text or f"column_{idx + 1}"


def unique_headers(values: list[object]) -> list[str]:
    seen: dict[str, int] = {}
    out = []
    for i, value in enumerate(values):
        base = clean_header(value, i)
        seen[base] = seen.get(base, 0) + 1
        out.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return out


def norm_id(value: object) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("xlsx", type=Path)
    ap.add_argument("inventory", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("reconciliation", type=Path)
    args = ap.parse_args()

    inventory = json.loads(args.inventory.read_text(encoding="utf-8"))
    expected = set(inventory["gen_info_unit_ids"])
    extracted_rows: list[dict[str, object]] = []
    observed: set[str] = set()
    duplicate_ids: list[str] = []

    with zipfile.ZipFile(args.xlsx) as zf:
        strings = shared_strings(zf)
        root = ET.fromstring(zf.read(sheet_path(zf, "Generator Information")))
        rows = root.find("main:sheetData", NS).findall("main:row", NS)
        header_row = next(r for r in rows if int(r.attrib.get("r", 0)) == 4)
        raw_headers = row_values(header_row, strings, 165)
        headers = unique_headers(raw_headers)
        region_idx = headers.index("region")
        unit_id_idx = headers.index("gen_info_unit_id")

        for row in rows:
            rnum = int(row.attrib.get("r", 0))
            if rnum <= 4:
                continue
            vals = row_values(row, strings, len(headers))
            region = str(vals[region_idx] or "").strip()
            if region not in TARGET_REGIONS:
                continue
            uid = norm_id(vals[unit_id_idx])
            if not uid:
                continue
            if uid in observed:
                duplicate_ids.append(uid)
            observed.add(uid)
            record = {headers[i]: vals[i] if i < len(vals) else None for i in range(len(headers))}
            record["gen_info_unit_id"] = uid
            record["source_record_id"] = uid
            extracted_rows.append(record)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["source_record_id"] + [h for h in headers if h != "source_record_id"]
    with args.output.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(extracted_rows)

    missing = sorted(expected - observed)
    extra = sorted(observed - expected)
    by_region: dict[str, int] = {}
    by_status: dict[str, int] = {}
    by_technology: dict[str, int] = {}
    for r in extracted_rows:
        for key, target in (("region", by_region), ("commitment_status", by_status), ("technology_type", by_technology)):
            v = str(r.get(key) or "").strip() or "(blank)"
            target[v] = target.get(v, 0) + 1

    recon = {
        "source": "AEMO NEM Generation Information July 2026",
        "scope_regions": sorted(TARGET_REGIONS),
        "expected_unit_ids": len(expected),
        "extracted_unit_ids": len(observed),
        "extracted_rows": len(extracted_rows),
        "missing_source_record_ids": missing,
        "extra_source_record_ids": extra,
        "duplicate_gen_info_unit_ids": sorted(set(duplicate_ids)),
        "exact_identity_match": not missing and not extra and not duplicate_ids and len(extracted_rows) == len(expected),
        "counts_by_region": dict(sorted(by_region.items())),
        "counts_by_commitment_status": dict(sorted(by_status.items())),
        "counts_by_technology_type": dict(sorted(by_technology.items())),
        "source_column_count": len(headers),
    }
    args.reconciliation.parent.mkdir(parents=True, exist_ok=True)
    args.reconciliation.write_text(json.dumps(recon, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(recon, indent=2))
    return 0 if recon["exact_identity_match"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
