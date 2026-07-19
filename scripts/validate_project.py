#!/usr/bin/env python3
"""Valida invariantes locais do projeto Salomão sem dependências externas."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_TRACKED = (
    re.compile(r"(^|/)__pycache__(/|$)"),
    re.compile(r"\.py[co]$"),
    re.compile(r"\.log$"),
    re.compile(r"\.pid$"),
    re.compile(r"(^|/)desktop\.ini$", re.I),
    re.compile(r"api[ _-]?key.*\.txt$", re.I),
    re.compile(r"(^|/)\.env($|\.)"),
)
REQUIRED_INSTRUMENT_FIELDS = {
    "id", "type", "number", "date", "issuer", "title", "subjects",
    "official_url", "local_path", "source_kind", "verification", "relations",
}
VALID_VERIFICATION = {"pending", "verified", "superseded", "revoked", "unknown"}
VERIFICATION_MAX_AGE_DAYS = 180


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def parse_date(value: str, label: str, report: Report) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value)
    except (TypeError, ValueError):
        report.error(f"{label}: data inválida {value!r}; use AAAA-MM-DD")
        return None


def validate_catalog(report: Report) -> None:
    path = ROOT / "knowledge_base/catalogo_normativo/catalogo.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"catálogo: não foi possível ler JSON: {exc}")
        return

    if data.get("schema_version") != 1:
        report.error("catálogo: schema_version deve ser 1")
    parse_date(data.get("updated_at"), "catálogo.updated_at", report)
    instruments = data.get("instruments")
    if not isinstance(instruments, list):
        report.error("catálogo.instruments deve ser uma lista")
        return

    ids: set[str] = set()
    relations: list[tuple[str, int, dict]] = []
    today = dt.date.today()
    for index, item in enumerate(instruments):
        label = f"catálogo.instruments[{index}]"
        if not isinstance(item, dict):
            report.error(f"{label}: registro deve ser objeto")
            continue
        missing = REQUIRED_INSTRUMENT_FIELDS - item.keys()
        if missing:
            report.error(f"{label}: campos ausentes: {', '.join(sorted(missing))}")
            continue
        instrument_id = item["id"]
        if instrument_id in ids:
            report.error(f"catálogo: id duplicado {instrument_id}")
        ids.add(instrument_id)
        if not re.fullmatch(r"[a-z0-9-]+", instrument_id):
            report.error(f"{label}.id: formato inválido")
        instrument_date = parse_date(item["date"], f"{label}.date", report)
        if instrument_date and instrument_date > today:
            report.error(f"{label}.date está no futuro: {instrument_date}")
        local_path = item["local_path"]
        if local_path and not (ROOT / local_path).is_file():
            report.error(f"{label}.local_path não existe: {local_path}")
        verification = item["verification"]
        if verification.get("status") not in VALID_VERIFICATION:
            report.error(f"{label}.verification.status inválido")
        if verification.get("status") == "verified":
            if not verification.get("checked_at") or not verification.get("method"):
                report.error(f"{label}: verified exige checked_at e method")
            if not item.get("official_url"):
                report.error(f"{label}: verified exige official_url")
            checked_at = parse_date(
                verification.get("checked_at"), f"{label}.verification.checked_at", report
            )
            if checked_at and checked_at > today:
                report.error(f"{label}.verification.checked_at está no futuro")
            if checked_at and (today - checked_at).days > VERIFICATION_MAX_AGE_DAYS:
                report.warn(
                    f"{label}: verificação tem mais de {VERIFICATION_MAX_AGE_DAYS} dias"
                )
        item_relations = item.get("relations")
        if not isinstance(item_relations, list):
            report.error(f"{label}.relations deve ser uma lista")
        else:
            relations.extend(
                (instrument_id, rel_index, relation)
                for rel_index, relation in enumerate(item_relations)
            )

    for source_id, rel_index, relation in relations:
        label = f"catálogo.{source_id}.relations[{rel_index}]"
        if not isinstance(relation, dict):
            report.error(f"{label}: relação deve ser objeto")
            continue
        target_id = relation.get("target_id")
        if target_id not in ids:
            report.error(f"{label}: target_id inexistente: {target_id!r}")
        if target_id == source_id:
            report.error(f"{label}: autorrelação não permitida")
        if not relation.get("kind") or not relation.get("evidence"):
            report.error(f"{label}: kind e evidence são obrigatórios")


def validate_skills(report: Report) -> None:
    skill_dirs = sorted(path for path in (ROOT / "skills").iterdir() if path.is_dir())
    if not skill_dirs:
        report.error("skills: nenhuma skill encontrada")
        return
    for folder in skill_dirs:
        path = folder / "SKILL.md"
        if not path.is_file():
            report.error(f"skill {folder.name}: SKILL.md ausente")
            continue
        text = path.read_text(encoding="utf-8")
        match = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.S)
        if not match:
            report.error(f"skill {folder.name}: frontmatter inválido")
            continue
        frontmatter = match.group(1)
        name = re.search(r"^name:\s*(.+?)\s*$", frontmatter, re.M)
        description = re.search(r"^description:\s*(.+?)\s*$", frontmatter, re.M)
        if not name or name.group(1) != folder.name:
            report.error(f"skill {folder.name}: name deve coincidir com a pasta")
        if not description or len(description.group(1)) < 40:
            report.error(f"skill {folder.name}: description ausente ou insuficiente")
        if "TODO" in text or "FIXME" in text:
            report.warn(f"skill {folder.name}: contém TODO/FIXME")


def validate_evals(report: Report) -> None:
    path = ROOT / "evals/casos_regulatorios.yaml"
    if not path.is_file():
        report.error("evals: casos_regulatorios.yaml ausente")
        return
    text = path.read_text(encoding="utf-8")
    ids = re.findall(r"^\s+- id:\s*([a-z0-9-]+)\s*$", text, re.M)
    if len(ids) < 5:
        report.error("evals: são necessários ao menos 5 casos")
    if len(ids) != len(set(ids)):
        report.error("evals: há ids duplicados")
    failures = re.findall(r"^\s+critical_failure:\s*$", text, re.M)
    if len(failures) != len(ids):
        report.error("evals: todo caso deve definir critical_failure")

    reference_dir = ROOT / "evals/respostas_referencia"
    if reference_dir.is_dir():
        for reference in sorted(reference_dir.glob("*.md")):
            reference_text = reference.read_text(encoding="utf-8")
            referenced_ids = re.findall(r"^## `([a-z0-9-]+)`\s*$", reference_text, re.M)
            if not referenced_ids:
                report.warn(f"evals: {reference.name} não contém ids de casos")
            for referenced_id in referenced_ids:
                if referenced_id not in ids:
                    report.error(
                        f"evals: {reference.name} referencia caso inexistente {referenced_id}"
                    )


def validate_git(report: Report) -> None:
    try:
        output = subprocess.run(
            ["git", "ls-files"], cwd=ROOT, check=True, capture_output=True, text=True
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        report.warn(f"git: não foi possível listar arquivos rastreados: {exc}")
        return
    for tracked in output.splitlines():
        normalized = tracked.replace("\\", "/")
        if normalized.endswith("/.env.example"):
            continue
        if any(pattern.search(normalized) for pattern in FORBIDDEN_TRACKED):
            report.error(f"git: artefato sensível/efêmero rastreado: {tracked}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-git", action="store_true", help="não validar arquivos rastreados")
    args = parser.parse_args()
    report = Report()
    validate_catalog(report)
    validate_skills(report)
    validate_evals(report)
    if not args.skip_git:
        validate_git(report)

    for warning in report.warnings:
        print(f"AVISO: {warning}")
    for error in report.errors:
        print(f"ERRO: {error}")
    print(
        f"Resultado: {len(report.errors)} erro(s), {len(report.warnings)} aviso(s).",
        file=sys.stderr if report.errors else sys.stdout,
    )
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
