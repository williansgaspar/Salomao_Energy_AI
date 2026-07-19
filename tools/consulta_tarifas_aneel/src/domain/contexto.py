"""Assinatura estável dos parâmetros usados em uma simulação."""

import hashlib
import json


def fingerprint_simulacao(payload):
    serializado = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(serializado.encode("utf-8")).hexdigest()
