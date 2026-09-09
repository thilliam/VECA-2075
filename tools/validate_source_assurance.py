#!/usr/bin/env python3
"""Validate VECA source coverage and ingestion assurance records.

Stdlib-only so agents and CI can run it without installing dependencies.

Usage:
    python tools/validate_source_assurance.py
    python tools/validate_source_assurance.py --strict
    python tools/validate_source_assurance.py --write-report
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSURANCE = ROOT / "assurance"
REGISTER = ASSURANCE / "source_register.json"
MANIFEST_DIR = ASSURANCE / "manifests"
REPORT_MD = ASSURANCE / "coverage_report.md"
REPORT_JSON = ASSURANCE / "coverage_report.json"

SOURCE_STATES = {
    "discovered", "triaged", "relevant", "ingestion_planned",
    "ingested", "reconciled", "verified", "stale", "not_relevant"
}
PRIORITIES = {"P0", "P1", "P2", "P3"}
SOURCE_TYPES = {
    "authoritative_reality",
    "government_intent",
    "infrastructure_owner_intent",
    "committed_private_capital",
    "private_development_pipeline",
    "industry_consortium_proposition",
    "market_analysis",
    "veca_inference",
}
COUNT_BASES = {
    "table_rows", "appendix_inventory", "api_count", "gis_feature_count",
    "official_index", "manual_inventory", "not_applicable"
}
VERIFICATION_STATES = {"not_started", "sampled", "passed", "failed", "not_applicable"}


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def add(errors: list[str], where: str, msg: str) -> None:
    errors.append(f"{where}: {msg}")


def validate_register(data: Any) -> tuple[list[str], dict[str, dict[str, Any]]]:
    errors: list[str] = []
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        return ["source_register.json: schema_version must be 1"], {}
    sources = data.get("sources")
    if not isinstance(sources, list):
        return ["source_register.json: sources must be an array"], {}

    by_id: dict[str, dict[str, Any]] = {}
    for i, src in enumerate(sources):
        where = f"source_register.json sources[{i}]"
        if not isinstance(src, dict):
            add(errors, where, "must be an object")
            continue
        sid = src.get("source_id")
        if not isinstance(sid, str) or not sid:
            add(errors, where, "source_id is required")
            continue
        if sid in by_id:
            add(errors, where, f"duplicate source_id {sid}")
        by_id[sid] = src

        for field in ("title", "publisher", "domain", "geography", "source_type", "status", "priority"):
            if not isinstance(src.get(field), str) or not src.get(field):
                add(errors, where, f"{field} is required")
        if src.get("source_type") not in SOURCE_TYPES:
            add(errors, where, f"invalid source_type {src.get('source_type')!r}")
        if src.get("status") not in SOURCE_STATES:
            add(errors, where, f"invalid status {src.get('status')!r}")
        if src.get("priority") not in PRIORITIES:
            add(errors, where, f"invalid priority {src.get('priority')!r}")
        if not isinstance(src.get("map_relevance"), bool):
            add(errors, where, "map_relevance must be boolean")
        if not isinstance(src.get("known_gaps", []), list):
            add(errors, where, "known_gaps must be an array")
    return errors, by_id


def validate_manifest(path: Path, m: Any, register: dict[str, dict[str, Any]]) -> list[str]:
    errors: list[str] = []
    where = path.relative_to(ROOT).as_posix()
    if not isinstance(m, dict):
        return [f"{where}: manifest must be an object"]
    if m.get("schema_version") != 1:
        add(errors, where, "schema_version must be 1")

    sid = m.get("source_id")
    if sid not in register:
        add(errors, where, f"source_id {sid!r} does not exist in source_register.json")

    inv = m.get("inventory")
    if not isinstance(inv, dict):
        add(errors, where, "inventory object is required")
        return errors

    mode = inv.get("mode")
    if mode not in {"entity_count", "not_applicable"}:
        add(errors, where, "inventory.mode must be entity_count or not_applicable")
        return errors

    basis = inv.get("count_basis")
    if basis not in COUNT_BASES:
        add(errors, where, f"invalid inventory.count_basis {basis!r}")

    if mode == "entity_count":
        expected = inv.get("expected_count")
        if not isinstance(expected, int) or expected < 0:
            add(errors, where, "inventory.expected_count must be a non-negative integer")
            expected = None
        if basis == "not_applicable":
            add(errors, where, "entity_count inventory cannot use not_applicable count_basis")
        locator = inv.get("evidence_locator")
        if not isinstance(locator, str) or not locator.strip():
            add(errors, where, "inventory.evidence_locator is required for entity_count")
        if inv.get("independent_from_extraction") is not True:
            add(errors, where, "inventory.independent_from_extraction must be true")

        disp = m.get("disposition")
        if not isinstance(disp, dict):
            add(errors, where, "disposition object is required for entity_count")
        else:
            fields = ("mapped", "dataset_only", "excluded", "duplicate", "unresolved")
            vals: dict[str, int] = {}
            for field in fields:
                val = disp.get(field)
                if not isinstance(val, int) or val < 0:
                    add(errors, where, f"disposition.{field} must be a non-negative integer")
                else:
                    vals[field] = val
            if expected is not None and len(vals) == len(fields):
                accounted = sum(vals.values())
                if accounted != expected:
                    add(errors, where, f"reconciliation FAIL: expected {expected}, accounted {accounted}")
                if m.get("map_required") is True and vals["dataset_only"] != 0:
                    add(errors, where, "map_required source has dataset_only entities; map disposition is incomplete")
                if m.get("verification", {}).get("state") == "passed" and vals["unresolved"] != 0:
                    add(errors, where, "verification cannot pass while unresolved entities remain")
    else:
        if basis != "not_applicable":
            add(errors, where, "not_applicable inventory must use count_basis=not_applicable")

    verification = m.get("verification")
    if not isinstance(verification, dict):
        add(errors, where, "verification object is required")
    else:
        state = verification.get("state")
        if state not in VERIFICATION_STATES:
            add(errors, where, f"invalid verification.state {state!r}")
        if state in {"sampled", "passed", "failed"}:
            checks = verification.get("checks")
            if not isinstance(checks, list) or not checks:
                add(errors, where, "verification.checks must contain evidence-backed checks")
            else:
                for j, check in enumerate(checks):
                    cwhere = f"{where} verification.checks[{j}]"
                    if not isinstance(check, dict):
                        add(errors, cwhere, "must be an object")
                        continue
                    for field in ("field", "method", "evidence_locator", "result"):
                        if not isinstance(check.get(field), str) or not check.get(field):
                            add(errors, cwhere, f"{field} is required")

    if m.get("map_required") is not None and not isinstance(m.get("map_required"), bool):
        add(errors, where, "map_required must be boolean")

    return errors


def build_report(register: dict[str, dict[str, Any]], manifests: dict[str, dict[str, Any]]) -> dict[str, Any]:
    by_domain: dict[str, Counter] = defaultdict(Counter)
    by_source_type: dict[str, Counter] = defaultdict(Counter)
    known_gaps = []
    for sid, src in register.items():
        status = src["status"]
        by_domain[src["domain"]][status] += 1
        by_source_type[src["source_type"]][status] += 1
        for gap in src.get("known_gaps", []):
            known_gaps.append({
                "source_id": sid,
                "domain": src["domain"],
                "priority": src["priority"],
                "gap": gap,
            })

    manifest_summary = []
    for sid, m in manifests.items():
        inv = m.get("inventory", {})
        disp = m.get("disposition", {})
        expected = inv.get("expected_count")
        accounted = None
        completeness = None
        if inv.get("mode") == "entity_count" and isinstance(expected, int):
            vals = [disp.get(k) for k in ("mapped", "dataset_only", "excluded", "duplicate", "unresolved")]
            if all(isinstance(v, int) for v in vals):
                accounted = sum(vals)
                completeness = (accounted / expected) if expected else 1.0
        manifest_summary.append({
            "source_id": sid,
            "expected": expected,
            "accounted": accounted,
            "completeness": completeness,
            "verification": m.get("verification", {}).get("state"),
            "map_required": m.get("map_required"),
            "mapped": disp.get("mapped"),
            "unresolved": disp.get("unresolved"),
        })

    return {
        "generated": date.today().isoformat(),
        "source_count": len(register),
        "manifest_count": len(manifests),
        "by_domain": {k: dict(v) for k, v in sorted(by_domain.items())},
        "by_source_type": {k: dict(v) for k, v in sorted(by_source_type.items())},
        "known_gaps": known_gaps,
        "manifests": sorted(manifest_summary, key=lambda x: x["source_id"]),
    }


def report_markdown(report: dict[str, Any]) -> str:
    lines = [
        "# VECA Source Coverage Report",
        "",
        f"Generated: {report['generated']}",
        "",
        "> Generated by `tools/validate_source_assurance.py --write-report`. Do not hand-edit.",
        "",
        f"- Registered sources: **{report['source_count']}**",
        f"- Sources with ingestion manifests: **{report['manifest_count']}**",
        "",
        "## Coverage by domain",
        "",
        "| Domain | Discovered/other | Ingested | Reconciled | Verified | Stale |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for domain, counts in report["by_domain"].items():
        other = sum(v for k, v in counts.items() if k not in {"ingested", "reconciled", "verified", "stale"})
        lines.append(
            f"| {domain} | {other} | {counts.get('ingested',0)} | "
            f"{counts.get('reconciled',0)} | {counts.get('verified',0)} | {counts.get('stale',0)} |"
        )

    lines += ["", "## Ingestion reconciliation", "",
              "| Source | Expected | Accounted | Mapped | Unresolved | Verification |",
              "|---|---:|---:|---:|---:|---|"]
    if not report["manifests"]:
        lines.append("| _No manifests yet_ |  |  |  |  |  |")
    else:
        for m in report["manifests"]:
            exp = "" if m["expected"] is None else m["expected"]
            acc = "" if m["accounted"] is None else m["accounted"]
            mapped = "" if m["mapped"] is None else m["mapped"]
            unr = "" if m["unresolved"] is None else m["unresolved"]
            lines.append(f"| `{m['source_id']}` | {exp} | {acc} | {mapped} | {unr} | {m['verification']} |")

    lines += ["", "## Known gaps", ""]
    if not report["known_gaps"]:
        lines.append("_No known gaps recorded._")
    else:
        for gap in sorted(report["known_gaps"], key=lambda x: (x["priority"], x["domain"], x["source_id"])):
            lines.append(f"- **{gap['priority']} {gap['domain']}** `{gap['source_id']}` — {gap['gap']}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true",
                        help="also fail if a reconciled/verified source is unresolved, or verified manifest is not passed")
    parser.add_argument("--write-report", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    if not REGISTER.exists():
        print(f"ERROR: missing {REGISTER.relative_to(ROOT)}", file=sys.stderr)
        return 1

    reg_data = load_json(REGISTER)
    reg_errors, register = validate_register(reg_data)
    errors.extend(reg_errors)

    manifests: dict[str, dict[str, Any]] = {}
    if MANIFEST_DIR.exists():
        for path in sorted(MANIFEST_DIR.glob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                m = load_json(path)
            except (json.JSONDecodeError, OSError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: cannot parse JSON: {exc}")
                continue
            sid = m.get("source_id") if isinstance(m, dict) else None
            if isinstance(sid, str):
                if sid in manifests:
                    errors.append(f"{path.relative_to(ROOT)}: duplicate manifest for source_id {sid}")
                manifests[sid] = m
            errors.extend(validate_manifest(path, m, register))

    for sid, src in register.items():
        if src["status"] in {"ingested", "reconciled", "verified"} and sid not in manifests:
            errors.append(f"source_register.json {sid}: status={src['status']} requires an ingestion manifest")
        if args.strict and src["status"] in {"reconciled", "verified"}:
            m = manifests.get(sid)
            if m is None:
                continue
            if src["status"] == "verified" and m.get("verification", {}).get("state") != "passed":
                errors.append(f"source_register.json {sid}: verified source requires verification.state=passed")
            if m.get("inventory", {}).get("mode") == "entity_count":
                if m.get("disposition", {}).get("unresolved", 0) != 0:
                    errors.append(f"source_register.json {sid}: reconciled/verified source has unresolved entities")

    report = build_report(register, manifests)
    if args.write_report:
        REPORT_JSON.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        REPORT_MD.write_text(report_markdown(report), encoding="utf-8")

    if errors:
        print(f"VECA source assurance: FAIL ({len(errors)} issue(s))", file=sys.stderr)
        for err in errors:
            print(f"- {err}", file=sys.stderr)
        return 1

    print(f"VECA source assurance: PASS ({len(register)} sources, {len(manifests)} manifests)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
