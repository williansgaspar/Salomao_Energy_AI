#!/usr/bin/env python3
"""Executa o gate local reproduzível do projeto."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMANDS = [
    [sys.executable, "scripts/validate_project.py"],
    [sys.executable, "scripts/monitor_verification.py"],
    [sys.executable, "scripts/evaluate_responses.py", "self-test"],
    [sys.executable, "tools/salomao_core/consulta.py", "self-test"],
    [sys.executable, "-m", "unittest", "discover", "-s", "tools/salomao_core/tests"],
    [sys.executable, "-m", "json.tool", "evals/golden/manifest.json"],
    [sys.executable, "-m", "json.tool", "knowledge_base/catalogo_normativo/inventario_entrada.json"],
]


def main() -> int:
    for command in COMMANDS:
        print("+", " ".join(command))
        completed = subprocess.run(command, cwd=ROOT)
        if completed.returncode:
            return completed.returncode
    print("Quality gate: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
