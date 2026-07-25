#!/usr/bin/env python3
"""CLI do núcleo local auditável do Salomão."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from redacao import compose_auditable_draft  # noqa: E402
from salomao_core import LocalRetriever, self_test  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    query = commands.add_parser("query", help="recuperar pacote auditável de evidências")
    query.add_argument("question")
    query.add_argument("--limit", type=int, default=5)
    query.add_argument("--json", action="store_true", help="emitir JSON completo")
    query.add_argument("--minuta", action="store_true", help="emitir minuta auditável")
    commands.add_parser("self-test", help="executar controles internos")
    args = parser.parse_args()

    if args.command == "self-test":
        self_test()
        print("Salomão Core self-test: OK")
        return 0

    pack = LocalRetriever().evidence_pack(args.question, args.limit)
    if args.minuta:
        draft = compose_auditable_draft(pack)
        if args.json:
            print(json.dumps({"evidence_pack": pack, "draft": draft}, ensure_ascii=False, indent=2))
        else:
            print(f"Status: {draft['status']}")
            print(draft["text"])
        return 0 if draft["status"] == "draft_ready" else 2
    if args.json:
        print(json.dumps(pack, ensure_ascii=False, indent=2))
    else:
        print(f"Status: {pack['status']}")
        print(pack["generation_policy"])
        for item in pack["evidence"]:
            source = item["source"]
            print(f"\n[{item['score']}] {source['type'].upper()} nº {source['number']} — {source['title']}")
            print(f"Arquivo: {source['local_path']} | verificado em {source['checked_at']}")
            print(item["excerpt"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
