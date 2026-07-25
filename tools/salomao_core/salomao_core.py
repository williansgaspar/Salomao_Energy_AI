"""Recuperação local, determinística e rastreável de fontes normativas.

Este módulo não gera pareceres. Ele entrega somente o pacote de evidências
que deve anteceder uma resposta do Salomão: fontes canônicas localizadas,
trechos recuperados e metadados de verificação.
"""

from __future__ import annotations

import html
import json
import re
import unicodedata
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / "knowledge_base/catalogo_normativo/catalogo.json"
COMPATIBILITY_PATH = (
    ROOT / "knowledge_base/catalogo_normativo/ajustes_compatibilizacao_2026-07-21_v2.json"
)
TOKEN_PATTERN = re.compile(r"[a-zA-ZÀ-ÿ0-9]+")
TAG_PATTERN = re.compile(r"<[^>]+>")
REN_NUMBER_PATTERN = re.compile(r"\bren\s+(?:aneel\s+)?n?[ºo.]?\s*(\d{1,3}(?:[.,]\d{3})?)")
# Os textos são compactados na leitura; o "Art." com inicial maiúscula distingue a
# estrutura do ato das referências internas usuais ("art. 15 da Lei...").
ARTICLE_PATTERN = re.compile(r"\bArt\.\s*\d+[\w-]*[º°]?")
# Após a compactação do texto, o parágrafo estrutural sucede início ou ponto;
# isso evita confundir menções internas como "consumidores de que trata o § 1º".
PARAGRAPH_PATTERN = re.compile(r"(?:(?<=\.)|^)\s*(§\s*\d+[º°]?)")


@dataclass(frozen=True)
class Source:
    """Registro canônico apto à recuperação."""

    id: str
    type: str
    number: str
    date: str
    issuer: str
    title: str
    subjects: tuple[str, ...]
    official_url: str | None
    local_path: str
    verification_status: str
    checked_at: str | None
    source_kind: str

    @property
    def citation(self) -> str:
        return f"{self.type.upper()} nº {self.number}, de {self.date}"


@dataclass(frozen=True)
class Evidence:
    """Trecho recuperado com pontuação e rastreabilidade de origem."""

    source: Source
    score: int
    excerpt: str
    provision: str | None

    def as_dict(self) -> dict[str, Any]:
        return {
            "score": self.score,
            "excerpt": self.excerpt,
            "provision": self.provision,
            "source": asdict(self.source),
        }


def normalize(value: str) -> str:
    """Normaliza texto para busca sem alterar a evidência exibida."""

    decomposed = unicodedata.normalize("NFKD", value.lower())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def tokens(value: str) -> set[str]:
    return {token for token in TOKEN_PATTERN.findall(normalize(value)) if len(token) > 1}


def read_text(path: Path) -> str:
    """Lê os formatos textuais do acervo com fallback de codificação."""

    raw = path.read_bytes()
    for encoding in ("utf-8", "utf-8-sig", "cp1252", "latin-1"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:  # pragma: no cover - fallback defensivo
        text = raw.decode("utf-8", errors="replace")
    if path.suffix.lower() in {".html", ".htm"}:
        text = html.unescape(TAG_PATTERN.sub(" ", text))
    return re.sub(r"\s+", " ", text).strip()


def load_sources(
    catalog_path: Path = CATALOG_PATH,
    compatibility_path: Path = COMPATIBILITY_PATH,
) -> list[Source]:
    """Carrega apenas fontes verificadas, primárias e presentes localmente."""

    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    overrides: dict[str, str] = {}
    if compatibility_path.is_file():
        matrix = json.loads(compatibility_path.read_text(encoding="utf-8"))
        overrides = {
            item["id"]: item["caminho_local_canonico"]
            for item in matrix.get("overrides", [])
            if item.get("id") and item.get("caminho_local_canonico")
        }

    sources: list[Source] = []
    for item in catalog["instruments"]:
        local_path = overrides.get(item["id"], item.get("local_path"))
        if (
            item.get("verification", {}).get("status") != "verified"
            or item.get("source_kind") != "primary_text"
            or not local_path
            or not (ROOT / local_path).is_file()
        ):
            continue
        sources.append(
            Source(
                id=item["id"],
                type=item["type"],
                number=item["number"],
                date=item["date"],
                issuer=item["issuer"],
                title=item["title"],
                subjects=tuple(item.get("subjects", [])),
                official_url=item.get("official_url"),
                local_path=local_path,
                verification_status=item["verification"]["status"],
                checked_at=item["verification"].get("checked_at"),
                source_kind=item["source_kind"],
            )
        )
    return sources


def _article_sections(text: str) -> list[tuple[int, int]]:
    articles = list(ARTICLE_PATTERN.finditer(text))
    if not articles:
        return [(0, len(text))]
    return [
        (article.start(), articles[index + 1].start() if index + 1 < len(articles) else len(text))
        for index, article in enumerate(articles)
    ]


def _anchor_position(text: str, query_tokens: set[str]) -> int | None:
    """Localiza o termo na seção de artigo com maior aderência à consulta."""

    normalized = normalize(text)
    ranked_tokens = sorted(
        query_tokens,
        key=lambda token: (not any(char.isdigit() for char in token), -len(token), token),
    )
    sections = _article_sections(text)
    scored_sections = []
    for start, end in sections:
        section_tokens = tokens(text[start:end])
        score = len(query_tokens & section_tokens)
        if score:
            scored_sections.append((score, start, end))
    if not scored_sections:
        return None
    _, start, end = max(scored_sections, key=lambda section: (section[0], -section[1]))
    positions = [
        normalized.find(token, start, end)
        for token in ranked_tokens
        if normalized.find(token, start, end) >= 0
    ]
    return positions[0] if positions else None


def _provision(text: str, anchor: int | None) -> str | None:
    """Identifica o artigo e, quando disponível, o parágrafo do trecho recuperado."""

    if anchor is None:
        return None
    articles = [match for match in ARTICLE_PATTERN.finditer(text) if match.start() <= anchor]
    if not articles:
        return None
    article = articles[-1].group(0).replace("Art.", "art.")
    start = articles[-1].start()
    paragraphs = [
        match for match in PARAGRAPH_PATTERN.finditer(text[start:anchor + 1])
    ]
    if paragraphs:
        return f"{article}, {paragraphs[-1].group(1)}"
    return article


def _excerpt(text: str, query_tokens: set[str], width: int = 700) -> str:
    position = _anchor_position(text, query_tokens)
    if position is None:
        return text[:width].strip()
    # Os tokens já foram ordenados por especificidade; priorizar o primeiro evita
    # que um termo amplo (por exemplo, "grupo") esconda um limiar numérico crítico.
    assert position is not None
    start = max(0, position - width // 3)
    end = min(len(text), start + width)
    prefix = "…" if start else ""
    suffix = "…" if end < len(text) else ""
    return f"{prefix}{text[start:end].strip()}{suffix}"


class LocalRetriever:
    """Busca lexical explicável sobre a base canônica já catalogada."""

    def __init__(self, sources: list[Source] | None = None) -> None:
        self.sources = sources if sources is not None else load_sources()

    def search(self, query: str, limit: int = 5) -> list[Evidence]:
        query_tokens = tokens(query)
        if not query_tokens:
            return []
        requested_ren = REN_NUMBER_PATTERN.search(normalize(query))
        requested_ren_number = (
            requested_ren.group(1).replace(",", ".") if requested_ren else None
        )
        evidences: list[Evidence] = []
        for source in self.sources:
            if requested_ren_number and not (
                source.type == "ren" and source.number == requested_ren_number
            ):
                continue
            source_text = read_text(ROOT / source.local_path)
            metadata = " ".join(
                (source.title, source.type, source.number, source.issuer, *source.subjects)
            )
            content_tokens = tokens(source_text)
            metadata_tokens = tokens(metadata)
            content_hits = len(query_tokens & content_tokens)
            metadata_hits = len(query_tokens & metadata_tokens)
            if not content_hits and not metadata_hits:
                continue
            phrase_bonus = 10 if normalize(query) in normalize(source_text) else 0
            score = content_hits * 3 + metadata_hits * 5 + phrase_bonus
            evidences.append(
                Evidence(
                    source=source,
                    score=score,
                    excerpt=_excerpt(source_text, query_tokens),
                    provision=_provision(source_text, _anchor_position(source_text, query_tokens)),
                )
            )
        return sorted(evidences, key=lambda item: (-item.score, item.source.id))[:limit]

    def evidence_pack(self, query: str, limit: int = 5) -> dict[str, Any]:
        evidences = self.search(query, limit)
        return {
            "query": query,
            "status": "evidence_ready" if evidences else "insufficient_evidence",
            "generation_policy": (
                "A resposta substantiva só pode ser gerada com base nas fontes abaixo; "
                "deve citar instrumento, data, dispositivo e arquivo local."
                if evidences
                else "Não gerar conclusão normativa. Solicitar ou localizar fonte primária aplicável."
            ),
            "required_response_fields": [
                "instrumento",
                "data",
                "dispositivo",
                "arquivo_fonte",
                "status_de_verificacao",
                "nivel_de_confianca",
            ],
            "evidence": [evidence.as_dict() for evidence in evidences],
        }


def self_test() -> None:
    """Controles mínimos contra regressão de recuperação e rastreabilidade."""

    retriever = LocalRetriever()
    assert retriever.sources, "nenhuma fonte canônica recuperável foi carregada"
    group_a = retriever.search("consumidores Grupo A carga individual inferior a 500 kW")
    assert group_a and group_a[0].source.id == "portaria-mme-50-2022"
    varejista = retriever.search("gestora de informações comercialização varejista CCEE")
    assert any(item.source.id == "ren-aneel-1011-2022" for item in varejista)
    missing = retriever.evidence_pack("REN ANEEL 9.999 tarifa municipal inexistente")
    assert missing["status"] == "insufficient_evidence"
