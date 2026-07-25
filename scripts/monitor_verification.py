#!/usr/bin/env python3
"""Reporta expiração de verificações e atraso da fila do boletim sem alterar fontes."""

from __future__ import annotations

import argparse
import datetime as dt
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "knowledge_base/catalogo_normativo/catalogo.json"
QUEUE_PATH = ROOT / "knowledge_base/triagem/fila_boletim.json"
FAST_SUBJECTS = {
    "abertura-acl", "armazenamento", "ccee", "mmgd", "pld", "tarifas", "tusd", "tust",
}


def parse_date(value: str | None) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value or "")
    except ValueError:
        return None


def business_days_since(start: dt.date, end: dt.date) -> int:
    if start >= end:
        return 0
    return sum(
        1 for offset in range(1, (end - start).days + 1)
        if (start + dt.timedelta(days=offset)).weekday() < 5
    )


def build_report(as_of: dt.date) -> dict:
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    queue = json.loads(QUEUE_PATH.read_text(encoding="utf-8")) if QUEUE_PATH.exists() else None
    due, invalid = [], []
    for item in catalog.get("instruments", []):
        verification = item.get("verification", {})
        if verification.get("status") != "verified":
            continue
        checked_at = parse_date(verification.get("checked_at"))
        if not checked_at:
            invalid.append(item.get("id"))
            continue
        subjects = set(item.get("subjects", []))
        max_age = 30 if subjects & FAST_SUBJECTS else 90
        age = (as_of - checked_at).days
        if age > max_age:
            due.append({
                "id": item["id"], "checked_at": checked_at.isoformat(), "age_days": age,
                "max_age_days": max_age, "subjects": item.get("subjects", []),
            })
    queue_status = {"state": "missing"}
    if queue:
        generated_at = parse_date(queue.get("generated_at"))
        source_modified_at = parse_date(queue.get("source_last_modified_at"))
        if not generated_at or not source_modified_at:
            queue_status = {"state": "invalid_generated_at"}
        else:
            age = business_days_since(generated_at, as_of)
            source_age = business_days_since(source_modified_at, as_of)
            items = queue.get("items", [])
            queue_status = {
                "state": (
                    "current" if age <= 1 and source_age <= 1
                    else "queue_overdue" if age > 1 else "source_stale"
                ),
                "generated_at": generated_at.isoformat(),
                "business_days_old": age,
                "max_business_days": 1,
                "source_last_modified_at": source_modified_at.isoformat(),
                "source_business_days_old": source_age,
                "source_max_business_days": 1,
                "official_pending_review": sum(
                    row.get("source_class") == "official" and row.get("review_status") == "pending"
                    for row in items
                ),
            }
    return {
        "schema_version": 1,
        "as_of": as_of.isoformat(),
        "policy": {
            "fast_subjects_max_age_days": 30,
            "standard_subjects_max_age_days": 90,
            "bulletin_queue_max_business_days": 1,
        },
        "catalog": {
            "verified_count": sum(
                item.get("verification", {}).get("status") == "verified"
                for item in catalog.get("instruments", [])
            ),
            "overdue": due,
            "invalid_checked_at": invalid,
        },
        "bulletin_queue": queue_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", type=parse_date, default=dt.date.today())
    parser.add_argument("--strict", action="store_true", help="retorna erro se houver controle vencido")
    args = parser.parse_args()
    if args.as_of is None:
        parser.error("--as-of deve usar AAAA-MM-DD")
    report = build_report(args.as_of)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    blocked = (
        report["catalog"]["overdue"]
        or report["catalog"]["invalid_checked_at"]
        or report["bulletin_queue"]["state"] != "current"
    )
    return 1 if args.strict and blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
