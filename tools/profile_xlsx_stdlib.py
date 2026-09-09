#!/usr/bin/env python3
"""Profile an XLSX source using only Python stdlib.

This is intentionally a source-ingestion utility rather than a workbook editor.
It records workbook sheets, dimensions and representative non-empty rows so a
source-specific extractor can be written without relying on opaque/manual Excel use.
"""
from __future__ import annotations

import argparse
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
    out = []
    for si in root.findall("main:si", NS):
        out.append("".join(t.text or "" for t in si.iterfind(".//main:t", NS)))
    return out


def workbook_sheets(zf: zipfile.ZipFile) -> list[tuple[str, str]]:
    wb = ET.fromstring(zf.read("xl/workbook.xml"))
    rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
    targets = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("pkg:Relationship", NS)}
    result = []
    for s in wb.find("main:sheets", NS):
        rid = s.attrib[f"{{{NS['rel']}}}id"]
        target = targets[rid]
        if target.startswith("/"):
            path = target.lstrip("/")
        else:
            path = "xl/" + target.lstrip("/")
        result.append((s.attrib["name"], path))
    return result


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


def profile_sheet(zf: zipfile.ZipFile, path: str, strings: list[str], max_rows: int) -> dict:
    root = ET.fromstring(zf.read(path))
    dim = root.find("main:dimension", NS)
    sheet_data = root.find("main:sheetData", NS)
    rows_out = []
    max_col = 0
    row_count = 0
    if sheet_data is not None:
        for row in sheet_data.findall("main:row", NS):
            row_count += 1
            vals: dict[int, object] = {}
            for cell in row.findall("main:c", NS):
                idx = col_index(cell.attrib.get("r", "A1"))
                max_col = max(max_col, idx + 1)
                value = cell_value(cell, strings)
                if value not in (None, ""):
                    vals[idx] = value
            if vals and len(rows_out) < max_rows:
                width = max(vals) + 1
                arr = [None] * width
                for i, value in vals.items():
                    arr[i] = value
                rows_out.append({"row": int(row.attrib.get("r", row_count)), "values": arr})
    return {
        "dimension": dim.attrib.get("ref") if dim is not None else None,
        "xml_row_count": row_count,
        "max_observed_columns": max_col,
        "sample_nonempty_rows": rows_out,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("xlsx", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--max-rows", type=int, default=25)
    args = p.parse_args()
    with zipfile.ZipFile(args.xlsx) as zf:
        strings = shared_strings(zf)
        sheets = []
        for name, path in workbook_sheets(zf):
            sheets.append({"name": name, "path": path, **profile_sheet(zf, path, strings, args.max_rows)})
    payload = {"source_file": args.xlsx.name, "sheets": sheets}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"profiled {len(sheets)} sheet(s) -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
