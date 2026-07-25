#!/usr/bin/env python3
"""Extrai links do boletim para fila de triagem sem promover conhecimento."""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


ROOT = Path(__file__).resolve().parents[1]
OFFICIAL_DOMAINS = ("gov.br", "aneel.gov.br", "ccee.org.br", "ons.org.br", "epe.gov.br", "in.gov.br")


def is_official(url: str) -> bool:
    host = (urlparse(url).hostname or "").lower()
    return any(host == domain or host.endswith("." + domain) for domain in OFFICIAL_DOMAINS)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bulletin", type=Path, default=ROOT / "Atualizacoes_Mercado/Boletim_Atualizacoes_SEB.html")
    parser.add_argument("--output", type=Path, default=ROOT / "knowledge_base/triagem/fila_boletim.json")
    args = parser.parse_args()
    text = args.bulletin.read_text(encoding="utf-8", errors="replace")
    urls = sorted(set(html.unescape(value) for value in re.findall(r'href=["\'](https?://[^"\']+)', text)), key=str.casefold)
    catalog = json.loads((ROOT / "knowledge_base/catalogo_normativo/catalogo.json").read_text(encoding="utf-8"))
    known = {item.get("official_url") for item in catalog["instruments"]}
    previous = {}
    if args.output.exists():
        previous_data = json.loads(args.output.read_text(encoding="utf-8"))
        previous = {item["url"]: item for item in previous_data.get("items", [])}
    items = []
    for url in urls:
        old = previous.get(url, {})
        items.append({
            "url": url,
            "source_class": "official" if is_official(url) else "secondary",
            "catalogued": url in known,
            "review_status": old.get("review_status", "pending"),
            "decision": old.get("decision"),
            "notes": old.get("notes", "Descoberta não constitui evidência normativa final.")
        })
    official_pending = sum(
        item["source_class"] == "official" and item["review_status"] == "pending"
        for item in items
    )
    data = {
        "schema_version": 2,
        "generated_at": dt.date.today().isoformat(),
        "source": args.bulletin.relative_to(ROOT).as_posix(),
        "source_last_modified_at": dt.datetime.fromtimestamp(
            args.bulletin.stat().st_mtime, tz=dt.timezone.utc
        ).date().isoformat(),
        "policy": "Descoberta e triagem não constituem promoção normativa.",
        "summary": {
            "total_links": len(items),
            "official_links": sum(item["source_class"] == "official" for item in items),
            "official_pending_review": official_pending,
        },
        "items": items,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(
        f"Fila atualizada: {len(items)} links; "
        f"{data['summary']['official_links']} oficiais; "
        f"{official_pending} oficiais pendentes"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
