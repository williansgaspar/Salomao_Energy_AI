#!/usr/bin/env python3
"""Inventaria deterministicamente a área de entrada sem promover documentos."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = ROOT / "knowledge_base/Legislação"
DEFAULT_OUTPUT = ROOT / "knowledge_base/catalogo_normativo/inventario_entrada.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def classify(path: Path) -> tuple[str, str]:
    name = path.name.lower()
    if re.search(r"\blei\b", name):
        return "lei", "pending_official_check"
    if "portaria" in name:
        return "portaria", "pending_official_check"
    if "ren aneel" in name:
        return "ren", "pending_official_check"
    if "pdc" in name or "procedimento" in str(path.parent).lower():
        return "procedimento_ccee", "pending_version_check"
    return "outro", "pending_classification"


def build(source: Path) -> dict:
    files = []
    for path in sorted((item for item in source.rglob("*") if item.is_file()), key=lambda p: str(p).casefold()):
        kind, status = classify(path)
        files.append({
            "path": path.relative_to(ROOT).as_posix(),
            "size_bytes": path.stat().st_size,
            "sha256": sha256(path),
            "classification": kind,
            "triage_status": status,
            "canonical": False,
            "notes": "Área de entrada; conferir fonte oficial, versão e vigência antes da promoção."
        })
    return {
        "schema_version": 1,
        "generated_at": "2026-07-19",
        "source": source.relative_to(ROOT).as_posix(),
        "policy": "Inventário não promove nem confirma vigência.",
        "count": len(files),
        "files": files
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    source = args.source.resolve()
    output = args.output.resolve()
    if not source.is_dir():
        raise SystemExit(f"Área de entrada ausente: {source}")
    data = build(source)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventariados {data['count']} arquivos em {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
