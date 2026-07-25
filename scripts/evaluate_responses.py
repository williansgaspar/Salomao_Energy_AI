#!/usr/bin/env python3
"""Inicializa e consolida avaliações regulatórias do Salomão."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "evals/casos_regulatorios.yaml"
DIMENSIONS = ("fundamentacao", "vigencia", "classificacao", "conclusao", "rastreabilidade")
MIN_OVERALL = 1.60
MIN_DIMENSION = 1.40
MANDATORY_CONCLUSION_2 = {"citacao-inexistente", "parecer-sem-fonte-primaria"}
REFERENCE_FILES = {
    "acl-grupo-a-opcao-2024": "evals/respostas_referencia/nucleo_acl_ccee.md",
    "acl-grupo-a-representacao-varejista": "evals/respostas_referencia/nucleo_acl_ccee.md",
    "varejista-dados-medicao-ccee": "evals/respostas_referencia/nucleo_acl_ccee.md",
    "acl-baixa-tensao-vigencia": "evals/respostas_referencia/acl_tarifas.md",
    "desconto-tusd-fonte-incentivada": "evals/respostas_referencia/acl_tarifas.md",
    "percentual-te-tusd-grupo-a": "evals/respostas_referencia/acl_tarifas.md",
    "mmgd-solar-4mw": "evals/respostas_referencia/mmgd_armazenamento.md",
    "bess-reserva-capacidade": "evals/respostas_referencia/mmgd_armazenamento.md",
    "competencia-sui": "evals/respostas_referencia/institucional_vigencia.md",
    "parecer-sem-fonte-primaria": "evals/respostas_referencia/seguranca_normativa.md",
    "prova-antiga-norma-revogada": "evals/respostas_referencia/institucional_vigencia.md",
    "citacao-inexistente": "evals/respostas_referencia/seguranca_normativa.md",
}


def case_ids() -> list[str]:
    text = CASES_PATH.read_text(encoding="utf-8")
    ids = re.findall(r"^\s+- id:\s*([a-z0-9-]+)\s*$", text, re.M)
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("casos ausentes ou duplicados em casos_regulatorios.yaml")
    return ids


def new_round() -> dict:
    return {
        "schema_version": 1,
        "metadata": {
            "evaluated_at": None,
            "model": None,
            "model_version": None,
            "git_commit": None,
            "evaluator": None,
            "notes": ""
        },
        "cases": [
            {
                "id": case_id,
                "response_path": None,
                "scores": {dimension: None for dimension in DIMENSIONS},
                "critical_failure": None,
                "evidence": [],
                "notes": ""
            }
            for case_id in case_ids()
        ]
    }


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def validate_round(data: dict) -> list[str]:
    errors: list[str] = []
    expected = case_ids()
    cases = data.get("cases")
    if not isinstance(cases, list):
        return ["cases deve ser uma lista"]
    received = [case.get("id") for case in cases if isinstance(case, dict)]
    if received != expected:
        errors.append("casos devem existir na mesma ordem da suíte canônica")
    for case in cases:
        case_id = case.get("id", "<sem-id>")
        scores = case.get("scores", {})
        for dimension in DIMENSIONS:
            value = scores.get(dimension)
            if not isinstance(value, int) or value not in (0, 1, 2):
                errors.append(f"{case_id}.{dimension}: nota deve ser 0, 1 ou 2")
        if not isinstance(case.get("critical_failure"), bool):
            errors.append(f"{case_id}.critical_failure deve ser booleano")
    return errors


def calculate(data: dict) -> tuple[dict, bool]:
    cases = data["cases"]
    dimension_means = {
        dimension: sum(case["scores"][dimension] for case in cases) / len(cases)
        for dimension in DIMENSIONS
    }
    overall = sum(dimension_means.values()) / len(DIMENSIONS)
    critical = [case["id"] for case in cases if case["critical_failure"]]
    mandatory_failures = [
        case["id"] for case in cases
        if case["id"] in MANDATORY_CONCLUSION_2 and case["scores"]["conclusao"] != 2
    ]
    weak_dimensions = [name for name, mean in dimension_means.items() if mean < MIN_DIMENSION]
    passed = not critical and not mandatory_failures and not weak_dimensions and overall >= MIN_OVERALL
    return {
        "overall": round(overall, 3),
        "dimensions": {name: round(value, 3) for name, value in dimension_means.items()},
        "critical_failures": critical,
        "mandatory_failures": mandatory_failures,
        "weak_dimensions": weak_dimensions,
        "thresholds": {"overall": MIN_OVERALL, "dimension": MIN_DIMENSION},
        "passed": passed
    }, passed


def command_init(output: Path) -> int:
    if output.exists():
        print(f"ERRO: arquivo já existe: {output}", file=sys.stderr)
        return 1
    write_json(output, new_round())
    print(f"Rodada inicializada: {output}")
    return 0


def command_reference_round(output: Path) -> int:
    """Gera a rodada positiva de calibração a partir das respostas de referência."""
    if output.exists():
        print(f"ERRO: arquivo já existe: {output}", file=sys.stderr)
        return 1
    data = new_round()
    data["metadata"].update({
        "evaluated_at": "2026-07-19",
        "model": "respostas-de-referencia",
        "model_version": "suite-v1",
        "evaluator": "calibracao-deterministica",
        "notes": "Controle positivo do executor; não representa desempenho de modelo."
    })
    for case in data["cases"]:
        case["response_path"] = REFERENCE_FILES[case["id"]]
        case["scores"] = {dimension: 2 for dimension in DIMENSIONS}
        case["critical_failure"] = False
        case["evidence"] = ["resposta de referência revisada"]
        case["notes"] = "Controle positivo da rubrica."
    write_json(output, data)
    print(f"Rodada de referência criada: {output}")
    return 0


def command_report(path: Path) -> int:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERRO: {exc}", file=sys.stderr)
        return 1
    errors = validate_round(data)
    if errors:
        for error in errors:
            print(f"ERRO: {error}", file=sys.stderr)
        return 1
    summary, passed = calculate(data)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if passed else 1


def command_self_test() -> int:
    missing_references = set(case_ids()) - set(REFERENCE_FILES)
    missing_files = [
        path for path in REFERENCE_FILES.values() if not (ROOT / path).is_file()
    ]
    if missing_references or missing_files:
        print(
            "ERRO: referências de avaliação incompletas: "
            f"ids={sorted(missing_references)} arquivos={missing_files}",
            file=sys.stderr,
        )
        return 1
    data = new_round()
    for case in data["cases"]:
        case["scores"] = {dimension: 2 for dimension in DIMENSIONS}
        case["critical_failure"] = False
    errors = validate_round(data)
    summary, passed = calculate(data)
    if errors or not passed or summary["overall"] != 2.0:
        print(f"ERRO: self-test positivo falhou: {errors} {summary}", file=sys.stderr)
        return 1
    data["cases"][0]["critical_failure"] = True
    _, passed = calculate(data)
    if passed:
        print("ERRO: self-test crítico deveria reprovar", file=sys.stderr)
        return 1
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "round.json"
        write_json(path, data)
        json.loads(path.read_text(encoding="utf-8"))
    print("Self-test: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    init_parser = subparsers.add_parser("init", help="criar template de rodada")
    init_parser.add_argument("--output", required=True, type=Path)
    reference_parser = subparsers.add_parser(
        "reference-round", help="criar controle positivo com os gabaritos"
    )
    reference_parser.add_argument("--output", required=True, type=Path)
    report_parser = subparsers.add_parser("report", help="validar e consolidar rodada")
    report_parser.add_argument("path", type=Path)
    subparsers.add_parser("self-test", help="testar o próprio executor")
    args = parser.parse_args()
    if args.command == "init":
        return command_init(args.output)
    if args.command == "reference-round":
        return command_reference_round(args.output)
    if args.command == "report":
        return command_report(args.path)
    return command_self_test()


if __name__ == "__main__":
    raise SystemExit(main())
