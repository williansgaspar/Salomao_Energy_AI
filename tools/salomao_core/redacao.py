"""Redação controlada a partir do pacote de evidências do Salomão Core.

Não há inferência normativa neste módulo. A saída organiza somente o que foi
recuperado, identifica o dispositivo e explicita os limites de uso da minuta.
"""

from __future__ import annotations

from typing import Any


REQUIRED_SOURCE_FIELDS = {
    "type", "number", "date", "local_path", "verification_status", "source_kind"
}


def compose_auditable_draft(pack: dict[str, Any]) -> dict[str, Any]:
    """Produz minuta rastreável ou recusa quando o contrato de prova falhar."""

    evidence = pack.get("evidence", [])
    if pack.get("status") != "evidence_ready" or not evidence:
        return {
            "status": "refused",
            "reason": "Não há evidência primária suficiente para redigir conclusão normativa.",
            "text": "Não foi gerada minuta. Localize ou atualize a fonte primária aplicável.",
        }

    invalid = []
    for item in evidence:
        source = item.get("source", {})
        missing = REQUIRED_SOURCE_FIELDS - set(source)
        if (
            missing
            or source.get("verification_status") != "verified"
            or source.get("source_kind") != "primary_text"
            or not item.get("provision")
        ):
            invalid.append(source.get("id", "<fonte sem identificação>"))
    if invalid:
        return {
            "status": "refused",
            "reason": "O pacote não contém dispositivo identificável e fonte primária verificada para todas as evidências.",
            "text": "Não foi gerada minuta. Revise a recuperação e o dispositivo aplicável.",
            "invalid_sources": invalid,
        }

    lines = [
        "## Questão",
        pack["query"],
        "",
        "## Fundamentação recuperada",
    ]
    citations = []
    for index, item in enumerate(evidence, start=1):
        source = item["source"]
        citation = (
            f"{source['type'].upper()} nº {source['number']}, de {source['date']}, "
            f"{item['provision']}"
        )
        citations.append(citation)
        lines.extend(
            [
                f"{index}. **{citation}.**",
                f"   Trecho recuperado: {item['excerpt']}",
                f"   Arquivo: `{source['local_path']}`; verificação: {source['checked_at']}.",
            ]
        )
    lines.extend(
        [
            "",
            "## Conclusão controlada",
            "A minuta limita-se aos comandos expressos nos trechos acima. A conclusão "
            "técnico-regulatória final deve verificar pertinência fática, vigência e eventuais "
            "atos posteriores antes de ser emitida ou encaminhada ao cliente.",
            "",
            "**Nível de confiança:** confirmado na base local quanto à existência, natureza "
            "primária e verificação das fontes recuperadas; aplicabilidade ao caso concreto "
            "requer revisão técnica.",
        ]
    )
    return {
        "status": "draft_ready",
        "text": "\n".join(lines),
        "citations": citations,
        "confidence": "confirmed_local_sources_case_review_required",
    }
