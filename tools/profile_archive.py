#!/usr/bin/env python3
"""Profile a ZIP archive without extracting it into the repository.

Produces a deterministic JSON inventory of members plus lightweight previews for
CSV/text files and workbook metadata for XLSX members. Intended for source
reconnaissance before writing a source-specific extractor.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


def xlsx_profile(data: bytes) -> dict:
    out = {"type": "xlsx", "sheets": []}
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        shared = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            ns = {"x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
            for si in root.findall("x:si", ns):
                shared.append("".join(t.text or "" for t in si.iterfind(".//x:t", ns)))
        wb = ET.fromstring(zf.read("xl/workbook.xml"))
        rels = ET.fromstring(zf.read("xl/_rels/workbook.xml.rels"))
        rns = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
        rel_map = {r.attrib["Id"]: r.attrib["Target"] for r in rels.findall("r:Relationship", rns)}
        ns = {
            "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
            "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
        }
        for s in wb.findall("x:sheets/x:sheet", ns):
            rid = s.attrib.get("{%s}id" % ns["r"])
            target = rel_map.get(rid, "")
            sheet_path = "xl/" + target.lstrip("/") if not target.startswith("xl/") else target
            if sheet_path not in zf.namelist():
                sheet_path = "xl/worksheets/" + Path(target).name
            row_count = 0
            preview = []
            if sheet_path in zf.namelist():
                root = ET.fromstring(zf.read(sheet_path))
                for row in root.findall(".//x:sheetData/x:row", ns):
                    row_count += 1
                    if len(preview) < 8:
                        vals = []
                        for c in row.findall("x:c", ns):
                            v = c.find("x:v", ns)
                            val = "" if v is None or v.text is None else v.text
                            if c.attrib.get("t") == "s" and val.isdigit():
                                idx = int(val)
                                if idx < len(shared):
                                    val = shared[idx]
                            vals.append(val)
                        preview.append(vals)
            out["sheets"].append({"name": s.attrib.get("name"), "rows": row_count, "preview": preview})
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("archive", type=Path)
    ap.add_argument("output", type=Path)
    args = ap.parse_args()

    members = []
    with zipfile.ZipFile(args.archive) as zf:
        for info in sorted(zf.infolist(), key=lambda i: i.filename.lower()):
            if info.is_dir():
                continue
            item = {
                "name": info.filename,
                "size": info.file_size,
                "compressed_size": info.compress_size,
            }
            suffix = Path(info.filename).suffix.lower()
            data = zf.read(info)
            if suffix == ".xlsx":
                try:
                    item["profile"] = xlsx_profile(data)
                except Exception as exc:
                    item["profile_error"] = str(exc)
            elif suffix in {".csv", ".txt"}:
                text = data.decode("utf-8-sig", errors="replace")
                rows = list(csv.reader(io.StringIO(text))) if suffix == ".csv" else [[line] for line in text.splitlines()]
                item["row_count"] = len(rows)
                item["preview"] = rows[:12]
            members.append(item)

    payload = {
        "archive": str(args.archive).replace("\\", "/"),
        "member_count": len(members),
        "members": members,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"profiled {len(members)} archive members -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
