"""Bancada operacional local do SalomãoAI.

Execução: python -m streamlit run tools/salomao_core/app.py

A interface não promove documentos ao catálogo. Ela organiza a rotina diária,
recupera evidências verificadas e só aciona um modelo externo mediante ação
expressa do usuário e chave fornecida na sessão.
"""

from __future__ import annotations

import datetime as dt
import json
import re
import sys
import urllib.error
import urllib.request
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import streamlit as st

APP_DIR = Path(__file__).resolve().parent
ROOT = APP_DIR.parents[1]
sys.path.insert(0, str(APP_DIR))

from redacao import compose_auditable_draft  # noqa: E402
from salomao_core import LocalRetriever  # noqa: E402


QUEUE_PATH = ROOT / "knowledge_base/triagem/fila_boletim.json"
CATALOG_PATH = ROOT / "knowledge_base/catalogo_normativo/catalogo.json"
BULLETIN_PATH = ROOT / "Atualizacoes_Mercado/Boletim_Atualizacoes_SEB.html"
DEFAULT_MODEL = "gpt-5.6-sol"


st.set_page_config(
    page_title="SalomãoAI | Bancada regulatória",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .stApp { background: #f7f8f5; }
      [data-testid="stSidebar"] { background: #102a28; }
      [data-testid="stSidebar"] * { color: #f2f4ef; }
      .salomao-kicker { color: #5a765f; font-size: 0.78rem; font-weight: 700;
        letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.35rem; }
      .salomao-title { color: #12251f; font-family: Georgia, 'Times New Roman', serif;
        font-size: 2.45rem; line-height: 1.08; margin: 0; }
      .salomao-subtitle { color: #54615b; font-size: 1rem; max-width: 810px;
        margin-top: 0.55rem; }
      .evidence-label { color: #5a765f; font-size: 0.75rem; font-weight: 700;
        letter-spacing: 0.08em; text-transform: uppercase; }
      .source-card { background: #ffffff; border-left: 4px solid #5c8065;
        padding: 0.75rem 1rem; margin: 0.45rem 0; }
      .routine-card { background: #ffffff; border: 1px solid #d8dfd6;
        padding: 0.9rem 1rem; margin: 0.55rem 0; }
      .muted-note { color: #66726d; font-size: 0.88rem; }
      .stButton > button[kind="primary"] { background: #174f45; border-color: #174f45; }
      .stButton > button[kind="primary"]:hover { background: #0d3d35; border-color: #0d3d35; }
    </style>
    """,
    unsafe_allow_html=True,
)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def parse_date(value: str | None) -> dt.date | None:
    try:
        return dt.date.fromisoformat(value or "")
    except ValueError:
        return None


@st.cache_data(ttl=60)
def monitoring_snapshot() -> dict[str, Any]:
    """Lê o estado local sem alterar catálogo, boletim ou fila."""

    queue = read_json(QUEUE_PATH) or {}
    catalog = read_json(CATALOG_PATH) or {}
    today = dt.date.today()
    source_date = queue.get("source_last_modified_at")
    source_day = parse_date(source_date)
    source_age = (today - source_day).days if source_day else None
    instruments = catalog.get("instruments", [])
    verified = sum(
        item.get("verification", {}).get("status") == "verified" for item in instruments
    )
    pending_official = [
        item
        for item in queue.get("items", [])
        if item.get("source_class") == "official" and item.get("review_status") == "pending"
    ]
    return {
        "generated_at": queue.get("generated_at"),
        "source_date": source_date,
        "source_age": source_age,
        "verified": verified,
        "pending_official": pending_official,
        "queue_items": queue.get("items", []),
        "bulletin_exists": BULLETIN_PATH.is_file(),
    }


class LatestEditionParser(HTMLParser):
    """Extrai somente os títulos da edição mais recente do boletim local."""

    def __init__(self) -> None:
        super().__init__()
        self.in_latest_edition = False
        self.finished = False
        self.capture_heading = False
        self.current_heading: list[str] = []
        self.edition = ""
        self.headlines: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "h2":
            if self.in_latest_edition:
                self.finished = True
                self.in_latest_edition = False
            elif not self.finished:
                self.in_latest_edition = True
                self.capture_heading = True
                self.current_heading = []
        elif tag == "h4" and self.in_latest_edition and not self.finished:
            self.capture_heading = True
            self.current_heading = []

    def handle_data(self, data: str) -> None:
        if self.capture_heading:
            self.current_heading.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag not in {"h2", "h4"} or not self.capture_heading:
            return
        text = " ".join(" ".join(self.current_heading).split())
        if tag == "h2" and not self.edition:
            self.edition = text
        elif tag == "h4" and text:
            self.headlines.append(text)
        self.capture_heading = False


@st.cache_data(ttl=60)
def latest_bulletin_edition() -> dict[str, Any]:
    if not BULLETIN_PATH.is_file():
        return {"edition": "Boletim indisponível", "headlines": []}
    parser = LatestEditionParser()
    parser.feed(BULLETIN_PATH.read_text(encoding="utf-8", errors="replace"))
    return {"edition": unescape(parser.edition), "headlines": [unescape(item) for item in parser.headlines]}


def status_text(snapshot: dict[str, Any]) -> tuple[str, str]:
    age = snapshot["source_age"]
    if not snapshot["bulletin_exists"] or age is None:
        return "Estado indisponível", "⚪"
    if age <= 1:
        return "Monitoramento em dia", "🟢"
    return "Revisão necessária", "🟠"


def url_publisher(url: str) -> str:
    host = urlparse(url).netloc.lower().removeprefix("www.")
    if "aneel" in host:
        return "ANEEL"
    if "ccee" in host:
        return "CCEE"
    if "gov.br" in host and "mme" in url.lower():
        return "MME"
    if "epe.gov.br" in host:
        return "EPE"
    if "ons.org.br" in host:
        return "ONS"
    return host or "Fonte oficial"


def triage_priority(url: str) -> tuple[int, str, str]:
    """Prioriza por tema operacional, sem atribuir efeito jurídico ao link."""

    value = url.lower()
    topic_rules = (
        (("armazen", "bateria", "lrcap", "sae"), "Armazenamento / LRCAP", 1),
        (("mercado", "comercial", "pld", "mve"), "ACL / comercialização", 2),
        (("tarifa", "reajuste", "bandeira"), "Tarifas", 2),
        (("mmgd", "geracao-distribuida", "gd-"), "MMGD", 2),
        (("leilao", "transmissao", "edital"), "Leilões / expansão", 3),
    )
    for terms, topic, priority in topic_rules:
        if any(term in value for term in terms):
            return priority, topic, "Tema com impacto recorrente na carteira SEB."
    return 4, "Regulação / institucional", "Fonte oficial nova a classificar."


def daily_agenda(items: list[dict[str, Any]], limit: int = 8) -> list[dict[str, Any]]:
    agenda = []
    for item in items:
        url = item.get("url", "")
        priority, topic, reason = triage_priority(url)
        agenda.append(
            {
                "url": url,
                "publisher": url_publisher(url),
                "topic": topic,
                "priority": priority,
                "reason": reason,
                "next_step": "Ler a publicação e localizar o ato, processo ou documento primário correspondente.",
            }
        )
    return sorted(agenda, key=lambda row: (row["priority"], row["publisher"], row["url"]))[:limit]


def agenda_markdown(agenda: list[dict[str, Any]], edition: str) -> str:
    lines = ["# Caderno diário — SalomãoAI", "", f"Base: {edition}", ""]
    for index, item in enumerate(agenda, start=1):
        lines.extend(
            [
                f"## {index}. {item['publisher']} — {item['topic']}",
                f"- Prioridade: P{item['priority']}",
                f"- Link: {item['url']}",
                f"- Próximo passo: {item['next_step']}",
                "- Decisão humana: pendente.",
                "",
            ]
        )
    lines.append("O caderno é de triagem; não constitui fundamentação normativa.")
    return "\n".join(lines)


def evidence_context(pack: dict[str, Any]) -> str:
    blocks = []
    for index, item in enumerate(pack.get("evidence", []), start=1):
        source = item["source"]
        blocks.append(
            "\n".join(
                [
                    f"FONTE {index}: {source['type'].upper()} nº {source['number']}, de {source['date']}",
                    f"Dispositivo: {item.get('provision') or 'não identificado'}",
                    f"Verificação local: {source.get('checked_at') or 'data não registrada'}",
                    f"URL oficial: {source.get('official_url') or 'não registrada'}",
                    f"Trecho: {item['excerpt']}",
                ]
            )
        )
    return "\n\n".join(blocks)


def call_openai_response(
    *, api_key: str, model: str, question: str, facts: str, deliverable: str, pack: dict[str, Any]
) -> dict[str, str]:
    """Chama Responses API apenas após clique explícito no fluxo de caso."""

    if pack.get("status") != "evidence_ready":
        return {"status": "refused", "message": "Não há evidência local suficiente para enviar uma consulta ao modelo."}

    instructions = """Você é Salomão, assistente sênior do Setor Elétrico Brasileiro.
Responda somente em português e somente com base nas fontes fornecidas. Não complemente com memória,
notícias ou inferências sobre vigência. Para cada afirmação, cite instrumento, data e dispositivo.
Se as fontes não resolverem a pergunta, declare a lacuna e indique o documento primário a obter.
Estruture a saída em: Questão; fundamentos recuperados; análise condicionada; lacunas e verificações;
próximo passo. Não apresente a resposta como parecer conclusivo."""
    user_input = "\n\n".join(
        [
            f"QUESTÃO: {question}",
            f"FATOS DO CASO: {facts or 'não informados'}",
            f"ENTREGA DESEJADA: {deliverable or 'nota técnica de trabalho'}",
            "FONTES VERIFICADAS LOCALMENTE:",
            evidence_context(pack),
        ]
    )
    payload = json.dumps(
        {
            "model": model,
            "instructions": instructions,
            "input": [{"role": "user", "content": [{"type": "input_text", "text": user_input}]}],
        }
    ).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", errors="replace")[:500]
        return {"status": "error", "message": f"A API respondeu {error.code}: {detail}"}
    except (urllib.error.URLError, TimeoutError) as error:
        return {"status": "error", "message": f"Não foi possível consultar a API: {error}"}

    output_text = data.get("output_text", "")
    if not output_text:
        chunks = []
        for output in data.get("output", []):
            for content in output.get("content", []):
                if content.get("type") == "output_text":
                    chunks.append(content.get("text", ""))
        output_text = "\n".join(chunks)
    if not output_text:
        return {"status": "error", "message": "A API não retornou texto utilizável."}
    return {"status": "ready", "text": output_text}


def show_evidence(pack: dict[str, Any]) -> None:
    if pack["status"] == "insufficient_evidence":
        st.error("Evidência insuficiente para uma conclusão normativa.")
        st.info(pack["generation_policy"])
        return

    st.success("Evidências primárias verificadas foram localizadas.")
    st.info(pack["generation_policy"])
    st.caption("Campos exigidos na análise: " + " · ".join(pack["required_response_fields"]))
    for index, item in enumerate(pack["evidence"], start=1):
        source = item["source"]
        provision = item["provision"] or "Dispositivo não identificado"
        st.markdown(
            f"<div class='source-card'><span class='evidence-label'>Fundamento {index}</span><br>"
            f"<strong>{source['type'].upper()} nº {source['number']}</strong> — {source['title']}<br>"
            f"<span class='muted-note'>{provision} · verificado em {source['checked_at']} · aderência {item['score']}</span></div>",
            unsafe_allow_html=True,
        )
        with st.expander("Ver trecho e metadados", expanded=index == 1):
            st.code(item["excerpt"], language=None)
            st.caption(f"Arquivo canônico: {source['local_path']}")
            st.caption(f"Status: {source['verification_status']} · Fonte: {source['source_kind']}")
            if source["official_url"]:
                st.link_button("Abrir publicação oficial", source["official_url"], key=f"official-{index}")


def initialize_state() -> None:
    defaults = {
        "case_question": "",
        "case_facts": "",
        "case_deliverable": "Nota técnica de trabalho",
        "evidence_pack": None,
        "model_analysis": None,
        "api_key": "",
        "model_name": DEFAULT_MODEL,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


initialize_state()
snapshot = monitoring_snapshot()
edition = latest_bulletin_edition()
system_status, system_icon = status_text(snapshot)
agenda = daily_agenda(snapshot["pending_official"])

with st.sidebar:
    st.markdown("## SalomãoAI")
    st.caption("Bancada técnico-regulatória local")
    st.divider()
    st.markdown(f"### {system_icon} {system_status}")
    st.metric("Fontes verificadas", snapshot["verified"])
    st.metric("Fontes oficiais na fila", len(snapshot["pending_official"]))
    st.caption(f"Boletim-fonte: {snapshot['source_date'] or 'não identificado'}")
    st.caption(f"Fila gerada: {snapshot['generated_at'] or 'não identificada'}")
    if st.button("Atualizar dados locais", use_container_width=True):
        monitoring_snapshot.clear()
        latest_bulletin_edition.clear()
        st.rerun()
    st.divider()
    st.markdown("**Copiloto por API (opcional)**")
    st.text_input("Chave da API", type="password", key="api_key", help="Fica apenas nesta sessão do navegador.")
    st.text_input("Modelo", key="model_name", help="Altere se sua conta não tiver acesso ao modelo padrão.")
    st.caption("A API só é chamada ao selecionar “Gerar análise controlada”. A pergunta, os fatos informados e os trechos recuperados serão enviados ao provedor.")
    st.divider()
    st.markdown("**Contrato de segurança**")
    st.caption("O boletim gera triagem. Só fontes primárias verificadas podem compor a análise ou a minuta.")

st.markdown("<div class='salomao-kicker'>Rotina, evidência e análise controlada</div>", unsafe_allow_html=True)
st.markdown("<h1 class='salomao-title'>Bancada regulatória SalomãoAI</h1>", unsafe_allow_html=True)
st.markdown(
    "<p class='salomao-subtitle'>Comece pela rotina do dia, transforme um item em caso e só então produza uma análise com cadeia de prova.</p>",
    unsafe_allow_html=True,
)

tab_today, tab_case, tab_output, tab_monitor = st.tabs(["Rotina de hoje", "Abrir caso", "Análise e minuta", "Monitoramento"])

with tab_today:
    left, right = st.columns([3, 2])
    with left:
        st.subheader("Fila de trabalho do dia")
        st.caption(f"{edition['edition'] or 'Edição mais recente do boletim'} · ordenação operacional, não classificação jurídica.")
        if agenda:
            for index, item in enumerate(agenda, start=1):
                st.markdown(
                    f"<div class='routine-card'><span class='evidence-label'>P{item['priority']} · {item['publisher']}</span><br>"
                    f"<strong>{item['topic']}</strong><br><span class='muted-note'>{item['reason']}<br>"
                    f"Próximo passo: {item['next_step']}</span></div>",
                    unsafe_allow_html=True,
                )
                action, link = st.columns([1, 4])
                with action:
                    if st.button("Selecionar", key=f"select-{index}"):
                        st.session_state["case_question"] = f"Verificar implicações regulatórias da fonte {item['publisher']} sobre {item['topic']}."
                        st.session_state["case_facts"] = f"Origem da demanda: boletim diário. Link em triagem: {item['url']}"
                        st.session_state["model_analysis"] = None
                        st.toast("Item levado para “Abrir caso”.")
                with link:
                    st.link_button("Abrir fonte em triagem", item["url"], key=f"queue-link-{index}")
        else:
            st.info("Não há fontes oficiais pendentes na fila local.")
    with right:
        st.subheader("O que mudou no boletim")
        if edition["headlines"]:
            for headline in edition["headlines"]:
                st.write(f"• {headline}")
        else:
            st.info("Não foi possível extrair títulos da edição atual.")
        st.download_button(
            "Baixar caderno diário (.md)",
            data=agenda_markdown(agenda, edition["edition"]),
            file_name=f"caderno_diario_{snapshot['generated_at'] or 'sem_data'}.md",
            mime="text/markdown",
            use_container_width=True,
        )
        st.caption("O caderno gera uma pauta de curadoria para o dia; ele não altera a fila nem promove documentos.")

with tab_case:
    st.subheader("Abrir caso técnico-regulatório")
    st.caption("O caso só avança para análise após recuperar fonte primária verificada. A descrição dos fatos fica sob seu controle.")
    with st.form("case_intake", clear_on_submit=False):
        question = st.text_area(
            "Questão regulatória",
            key="case_question",
            placeholder="Ex.: Quais providências de representação e comercialização se aplicam a este consumidor do Grupo A?",
            height=100,
        )
        facts = st.text_area(
            "Fatos e premissas do caso", key="case_facts", placeholder="Agente, perfil de carga, cronograma, documentos disponíveis e hipótese a verificar.", height=120
        )
        deliverable = st.selectbox(
            "Entrega de trabalho", ["Nota técnica de trabalho", "Roteiro de diligências", "Estrutura de parecer", "Resposta executiva para cliente"], key="case_deliverable"
        )
        time_sensitive = st.checkbox("Há tarifa, prazo, cronograma ou regra sensível ao tempo neste caso?", value=True)
        retrieve_clicked = st.form_submit_button("1. Recuperar evidências", type="primary")

    if retrieve_clicked:
        normalized_question = question.strip()
        if not normalized_question:
            st.warning("Informe uma questão antes de recuperar evidências.")
        else:
            st.session_state["evidence_pack"] = LocalRetriever().evidence_pack(normalized_question)
            st.session_state["model_analysis"] = None
            if time_sensitive:
                st.session_state["time_sensitive"] = True
            else:
                st.session_state["time_sensitive"] = False

    pack = st.session_state.get("evidence_pack")
    if pack:
        st.divider()
        st.markdown("### 2. Checagem de prova")
        if st.session_state.get("time_sensitive"):
            st.warning("Caso sensível ao tempo: confirme vigência, valor e cronograma no texto oficial atualizado antes de usar a análise externamente.")
        show_evidence(pack)

with tab_output:
    st.subheader("Análise e minuta controladas")
    pack = st.session_state.get("evidence_pack")
    if not pack:
        st.info("Abra um caso e recupere evidências para habilitar esta etapa.")
    elif pack["status"] != "evidence_ready":
        st.warning("Sem evidência primária recuperada, não há análise nem minuta a produzir.")
    else:
        st.caption("A minuta local organiza os trechos recuperados. O copiloto por API é opcional e não substitui a sua revisão técnica.")
        draft = compose_auditable_draft(pack)
        if draft["status"] == "draft_ready":
            with st.expander("Minuta local auditável", expanded=True):
                st.text_area("Texto de trabalho", value=draft["text"], height=340, disabled=True)
                st.download_button("Baixar minuta local (.md)", data=draft["text"], file_name="minuta_auditavel_salomao.md", mime="text/markdown")
        else:
            st.warning(draft["reason"])

        st.divider()
        st.markdown("### Copiloto de análise")
        if not st.session_state["api_key"]:
            st.info("Para habilitar o copiloto, informe uma chave de API na barra lateral. Sem chave, a bancada continua operando em modo local e auditável.")
        elif st.button("3. Gerar análise controlada", type="primary"):
            with st.spinner("Gerando análise somente a partir do pacote de evidências..."):
                st.session_state["model_analysis"] = call_openai_response(
                    api_key=st.session_state["api_key"],
                    model=st.session_state["model_name"],
                    question=st.session_state["case_question"],
                    facts=st.session_state["case_facts"],
                    deliverable=st.session_state["case_deliverable"],
                    pack=pack,
                )
        analysis = st.session_state.get("model_analysis")
        if analysis:
            if analysis["status"] == "ready":
                st.success("Análise gerada. Revise pertinência fática e vigência antes de qualquer uso externo.")
                st.markdown(analysis["text"])
                st.download_button("Baixar análise (.md)", data=analysis["text"], file_name="analise_controlada_salomao.md", mime="text/markdown")
            else:
                st.error(analysis["message"])

with tab_monitor:
    st.subheader("Monitoramento de vigência e curadoria")
    monitor_cols = st.columns(4)
    monitor_cols[0].metric("Estado", system_status)
    monitor_cols[1].metric("Fontes verificadas", snapshot["verified"])
    monitor_cols[2].metric("Pendências oficiais", len(snapshot["pending_official"]))
    monitor_cols[3].metric("Idade do boletim", "—" if snapshot["source_age"] is None else f"{snapshot['source_age']} dia(s)")
    if snapshot["source_age"] is not None and snapshot["source_age"] > 1:
        st.warning("O boletim-fonte requer atualização antes de sustentar afirmações sensíveis ao tempo.")
    else:
        st.success("Boletim e fila estão dentro da janela operacional configurada.")

    rows = [
        {
            "Prioridade": f"P{priority}",
            "Órgão": url_publisher(item.get("url", "")),
            "Tema": topic,
            "URL": item.get("url"),
        }
        for item in snapshot["pending_official"]
        for priority, topic, _ in [triage_priority(item.get("url", ""))]
    ]
    st.markdown("### Fontes oficiais pendentes")
    if rows:
        st.dataframe(rows, use_container_width=True, hide_index=True, height=360)
    else:
        st.info("Não há links oficiais pendentes na fila.")
    st.caption("A promoção documental permanece fora desta tela: exige conferência, hash, vigência e decisão humana registrada no catálogo.")

st.divider()
st.caption("SalomãoAI · núcleo local auditável · a interface não substitui parecer técnico-regulatório.")
