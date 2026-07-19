"""
REVISÃO 3 (19/07/2026) — cálculo por posto tarifário, vigência mensal por
intervalo e memória de cálculo auditável. Versões anteriores em revisions/.

Interface web para consulta de tarifas de distribuidoras de energia elétrica
homologadas pela ANEEL (API de Dados Abertos, pública, sem autenticação), com
cálculo de energia (TE+TUSD) e demanda (TUSD) estimadas a partir de consumo e
demanda contratada informados pelo usuário.

Rodar com:
    streamlit run app.py
"""

import base64
import io
from datetime import date
from pathlib import Path

import pandas as pd
import streamlit as st

from aneel_api import (
    ano_da_vigencia,
    converter_valor_brl,
    nova_sessao,
    registros_da_distribuidora,
    valores_distintos,
    vigente_em,
)
from src.domain.calculos import calcular_fatura, calcular_por_consumo_total
from src.domain.vigencia import periodo_do_mes, registros_vigentes_no_periodo

st.set_page_config(page_title="Tarifas ANEEL", page_icon="⚡", layout="wide")

REVISAO_ATUAL = "Revisão 3"

COLUNAS_EXIBICAO = {
    "SigAgente": "Distribuidora",
    "DscREH": "REH",
    "DatInicioVigencia": "Início vigência",
    "DatFimVigencia": "Fim vigência",
    "DscBaseTarifaria": "Base tarifária",
    "DscSubGrupo": "Subgrupo",
    "DscModalidadeTarifaria": "Modalidade",
    "DscClasse": "Classe",
    "DscSubClasse": "Subclasse",
    "DscDetalhe": "Detalhe",
    "NomPostoTarifario": "Posto tarifário",
    "DscUnidadeTerciaria": "Unidade",
    "SigAgenteAcessante": "Acessante",
    "VlrTUSD": "TUSD (R$)",
    "VlrTE": "TE (R$)",
    "EnergiaComposta": "Energia Composta TUSD+TE (R$/MWh)",
}

MESES = [
    (1, "Jan"), (2, "Fev"), (3, "Mar"), (4, "Abr"), (5, "Mai"), (6, "Jun"),
    (7, "Jul"), (8, "Ago"), (9, "Set"), (10, "Out"), (11, "Nov"), (12, "Dez"),
]

POSTOS_PADRAO = {"Ponta", "Fora ponta", "Intermediário", "Não se aplica"}

# Pesos fixos (horas/mês) usados no cálculo ponderado — ver Memória de cálculo
# no output. Ponta = 66h (~3h/dia útil x 22 dias úteis); Intermediário (só
# modalidade Branca) = 44h (1h antes + 1h depois da Ponta x 22 dias úteis);
# Fora Ponta = resto até completar 720h/mês.
HORAS_TOTAL_MES = 720.0
HORAS_PONTA = 66.0
HORAS_INTERMEDIARIO = 44.0

# --------------------------------------------------------------------------
# Tema claro/escuro — paleta inspirada no padrão visual institucional das
# secretarias da Prefeitura do Rio (fazenda.prefeitura.rio: azul #004A80/
# #1863DC, azure #12BBEF, barra utilitária cinza #363636, verde de destaque
# #0BB975 — este último também usado como identidade do Rio de Energia
# Verde, o que casou bem). Fonte institucional (Cera Pro/Museo Sans) é
# proprietária e não fica disponível fora da rede da Prefeitura — nesta
# revisão usa-se 'Inter' como substituta livre (geometria parecida), com
# fallback para fontes do sistema caso a futura hospedagem na intranet não
# tenha saída à internet para o Google Fonts.
# --------------------------------------------------------------------------

PALETAS = {
    "claro": {
        "bg": "#F5F5F5", "card_bg": "#FFFFFF", "text": "#212121",
        "text_muted": "#757373", "border": "#E1DFDF", "accent": "#1863DC",
        "accent_contrast": "#FFFFFF", "highlight": "#0BB975",
        "shadow": "rgba(0,0,0,0.15)", "utility_bg": "#363636",
        "utility_azure": "#12BBEF", "band_bg": "#004A80", "band_text": "#FFFFFF",
    },
    "escuro": {
        "bg": "#12161B", "card_bg": "#1B2128", "text": "#E8ECEF",
        "text_muted": "#9AA4AD", "border": "#2B333B", "accent": "#4C9CFF",
        "accent_contrast": "#0B1520", "highlight": "#2FE39A",
        "shadow": "rgba(0,0,0,0.5)", "utility_bg": "#1B1B1B",
        "utility_azure": "#4FD6FF", "band_bg": "#0B2E4D", "band_text": "#FFFFFF",
    },
}


def aplicar_tema(tema):
    p = PALETAS[tema]
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');

        [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background: {p['bg']};
        }}
        html, body, [class*="css"] {{
            font-family: 'Inter', -apple-system, 'Segoe UI', Roboto, sans-serif;
            color: {p['text']};
        }}
        .st-key-card_inputs, .st-key-card_outputs {{
            background: {p['card_bg']} !important;
            border: 1px solid {p['border']} !important;
            border-radius: 10px !important;
            box-shadow: 0 1px 4px {p['shadow']};
            padding: 0.5rem 0.75rem;
        }}
        h1, h2, h3, h4, h5, h6, .stMarkdown p strong {{
            color: {p['text']} !important;
        }}
        [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] label {{
            color: {p['text']} !important;
        }}
        [data-testid="stCaptionContainer"], .stCaption {{
            color: {p['text_muted']} !important;
        }}
        [data-testid="stMetricValue"] {{
            color: {p['accent']};
            font-weight: 700;
        }}
        [data-testid="stMetricLabel"] {{
            color: {p['text_muted']};
        }}
        .stButton>button[kind="primary"], .stDownloadButton>button {{
            background: {p['accent']};
            color: {p['accent_contrast']};
            border: none;
            border-radius: 6px;
            font-weight: 600;
        }}
        [data-testid="stExpander"] {{
            border: 1px solid {p['border']};
            border-radius: 8px;
        }}
        hr {{ border-color: {p['border']}; }}

        .pref-topbar {{
            background: {p['utility_bg']};
            color: #FFFFFF;
            padding: 0.4rem 1rem;
            border-radius: 6px 6px 0 0;
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            letter-spacing: 0.4px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.85rem;
        }}
        .pref-topbar .marca {{ color: {p['utility_azure']}; }}
        .pref-topbar .marca .rio {{ color: #FFFFFF; }}
        .pref-topbar .orgao {{
            color: #D8D8D8;
            font-weight: 400;
            letter-spacing: 0;
        }}
        .pref-band {{
            background: {p['band_bg']};
            color: {p['band_text']};
            padding: 0.7rem 1.25rem;
            border-radius: 0 0 10px 10px;
            margin-bottom: 1rem;
            display: flex;
            align-items: center;
            gap: 1rem;
        }}
        .pref-band h1 {{
            color: {p['band_text']} !important;
            font-size: 1.5rem;
            margin: 0;
        }}
        .pref-band .subtitulo {{
            color: rgba(255,255,255,0.85);
            font-size: 0.85rem;
        }}
        .pref-logo-badge {{
            background: #FFFFFF;
            border-radius: 8px;
            padding: 0.35rem 0.6rem;
            box-shadow: 0 1px 4px rgba(0,0,0,0.25);
            flex-shrink: 0;
            display: flex;
            align-items: center;
        }}
        .pref-logo-badge img {{
            height: 46px;
            display: block;
        }}
        .hero-total {{
            background: {p['card_bg']};
            border: 1px solid {p['border']};
            border-left: 5px solid {p['highlight']};
            border-radius: 8px;
            padding: 0.75rem 1rem;
            margin-top: 0.5rem;
        }}
        .hero-total .rotulo {{
            color: {p['text_muted']};
            font-size: 0.85rem;
        }}
        .hero-total .valor {{
            color: {p['highlight']};
            font-size: 1.8rem;
            font-weight: 800;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def fmt_brl(valor):
    return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


LOGO_PATH = Path(__file__).resolve().parent / "assets" / "logo_rio_energia_verde.png"


@st.cache_data(show_spinner=False)
def logo_data_uri():
    """Logo embutida como data URI (base64) — não depende de servir arquivo
    estático à parte, o que facilita a futura hospedagem na intranet."""
    if not LOGO_PATH.exists():
        return None
    b64 = base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{b64}"


# --------------------------------------------------------------------------
# Dados (cache)
# --------------------------------------------------------------------------

@st.cache_resource
def sessao():
    return nova_sessao()


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def lista_distribuidoras():
    return valores_distintos(sessao(), "SigAgente")


@st.cache_data(ttl=24 * 3600, show_spinner="Buscando registros da distribuidora...")
def registros_brutos_da_distribuidora(sig_agente):
    return registros_da_distribuidora(sessao(), sig_agente)


# --------------------------------------------------------------------------
# Helpers de filtro/composição
# --------------------------------------------------------------------------

def campo_distintos(registros, campo):
    return sorted({r[campo] for r in registros if r.get(campo)})


def filtrar_por_campo(registros, campo, valor, opcao_todos):
    if valor and valor != opcao_todos:
        return [r for r in registros if r.get(campo) == valor]
    return registros


def elegivel_para_composicao(registro):
    """Linhas de energia (R$/MWh) — compõem TE+TUSD energia."""
    return registro.get("DscUnidadeTerciaria") == "MWh"


def elegivel_demanda(registro):
    """Linhas de demanda contratada (R$/kW) — só TUSD, sem TE."""
    return registro.get("DscUnidadeTerciaria") == "kW"


def chave_versao(registro):
    """Identifica uma 'versão' de tarifa (REH/base/subgrupo/modalidade/classe/
    subclasse/detalhe/vigência); postos e unidades diferentes da mesma versão
    não geram ambiguidade — só versões diferentes coexistindo geram."""
    return (
        registro.get("DscREH"),
        registro.get("DscBaseTarifaria"),
        registro.get("DscSubGrupo"),
        registro.get("DscModalidadeTarifaria"),
        registro.get("DscClasse"),
        registro.get("DscSubClasse"),
        registro.get("DscDetalhe"),
        registro.get("DatInicioVigencia"),
        registro.get("DatFimVigencia"),
    )


def rotulo_versao(chave):
    reh, base_tarifaria, subgrupo, modalidade, classe, subclasse, detalhe, ini, fim = chave
    partes = [reh or "REH não informada", base_tarifaria or "Base não informada", f"{subgrupo}/{modalidade}"]
    if classe and classe != "Não se aplica":
        partes.append(classe)
    if subclasse and subclasse != "Não se aplica":
        partes.append(subclasse)
    if detalhe and detalhe != "Não se aplica":
        partes.append(detalhe)
    partes.append(f"vigência {ini} a {fim}")
    return " | ".join(partes)


@st.dialog("Mais de uma composição possível")
def dialog_escolher_versao(versoes, contexto_hash):
    st.write(
        "Os filtros atuais ainda deixam mais de uma combinação de REH, base "
        "tarifária, subgrupo/modalidade, classe ou detalhe elegível. Escolha "
        "qual delas usar no cálculo — as demais linhas continuam visíveis na "
        "tabela, só não entram nos totais calculados."
    )
    rotulos = {rotulo_versao(v): v for v in versoes}
    escolha_rotulo = st.radio("Composição", list(rotulos.keys()), label_visibility="collapsed")
    if st.button("Calcular esta composição", type="primary"):
        st.session_state["versao_escolhida"] = rotulos[escolha_rotulo]
        st.session_state["versao_escolhida_contexto"] = contexto_hash
        st.rerun()


def valores_por_posto(registros, versao_escolhida, elegivel_fn):
    """(tusd, te) por posto tarifário, dentro da versão escolhida, para as
    linhas que satisfazem elegivel_fn (energia MWh ou demanda kW)."""
    valores = {}
    ambiguos = set()
    for r in registros:
        if versao_escolhida is None or not elegivel_fn(r) or chave_versao(r) != versao_escolhida:
            continue
        posto = r.get("NomPostoTarifario")
        tusd = converter_valor_brl(r.get("VlrTUSD"))
        te = converter_valor_brl(r.get("VlrTE"))
        if tusd is None:
            continue
        te = te if te is not None else 0.0
        par = (round(tusd, 4), round(te, 4))
        if posto in valores and valores[posto] != par:
            ambiguos.add(posto)
        valores[posto] = par
    return valores, ambiguos


def montar_dataframe(registros, versao_escolhida):
    df = pd.DataFrame(registros)
    if df.empty:
        return df
    df["VlrTUSD"] = df["VlrTUSD"].apply(converter_valor_brl)
    df["VlrTE"] = df["VlrTE"].apply(converter_valor_brl)

    def energia_composta(registro):
        if versao_escolhida is not None and elegivel_para_composicao(registro) and chave_versao(registro) == versao_escolhida:
            tusd, te = converter_valor_brl(registro.get("VlrTUSD")), converter_valor_brl(registro.get("VlrTE"))
            if tusd is not None and te is not None:
                return round(tusd + te, 4)
        return None

    df["EnergiaComposta"] = [energia_composta(r) for r in registros]

    colunas = [c for c in COLUNAS_EXIBICAO if c in df.columns]
    df = df[colunas].rename(columns=COLUNAS_EXIBICAO)
    return df


# --------------------------------------------------------------------------
# Helpers de grupo/modalidade e congelamento de campos livres
# --------------------------------------------------------------------------

def grupo_tensao(subgrupo):
    if not subgrupo:
        return None
    s = subgrupo.strip().upper()
    if s.startswith("B"):
        return "B"
    if s.startswith("A"):
        return "A"
    return None


def modalidade_tem_ponta(modalidade):
    if not modalidade:
        return False
    return modalidade.startswith("Azul") or modalidade.startswith("Verde") or modalidade == "Branca"


def modalidade_tem_intermediario(modalidade):
    return modalidade == "Branca"


def calcular_congelamento(subgrupo, modalidade):
    """Decide quais dos 4 campos livres (Demanda HPT/HFP, Consumo HPT/HFP)
    ficam desabilitados, com base no Subgrupo e na Modalidade selecionados.

    Grupo B (baixa tensão) não fatura demanda contratada e, por simplicidade,
    só usa o campo Consumo HFP (mesmo para Branca). Grupo A sem posto Ponta
    (ex.: Convencional) não tem HPT, só HFP. Grupo A com Ponta (Azul/Verde/
    Branca) libera os 4 campos.
    """
    conhecido = subgrupo not in (None, "Todos") and modalidade not in (None, "Todas")
    if not conhecido:
        return dict(demanda_hpt=True, demanda_hfp=True, consumo_hpt=True, consumo_hfp=True)

    grupo = grupo_tensao(subgrupo)
    if grupo == "B":
        return dict(demanda_hpt=True, demanda_hfp=True, consumo_hpt=True, consumo_hfp=False)

    if modalidade_tem_ponta(modalidade):
        return dict(demanda_hpt=False, demanda_hfp=False, consumo_hpt=False, consumo_hfp=False)

    return dict(demanda_hpt=True, demanda_hfp=False, consumo_hpt=True, consumo_hfp=False)


def horas_padrao_mes(tem_ponta, tem_intermediario):
    if not tem_ponta:
        return {"Não se aplica": HORAS_TOTAL_MES}
    horas = {"Ponta": HORAS_PONTA}
    restante = HORAS_TOTAL_MES - HORAS_PONTA
    if tem_intermediario:
        horas["Intermediário"] = HORAS_INTERMEDIARIO
        restante -= HORAS_INTERMEDIARIO
    horas["Fora ponta"] = restante
    return horas


def rate_ponderada(valores, horas):
    """(tusd, te) ponderados pelas horas fixas; None se faltar posto necessário."""
    if not set(horas).issubset(valores):
        return None
    tusd = sum(valores[p][0] * h for p, h in horas.items()) / HORAS_TOTAL_MES
    te = sum(valores[p][1] * h for p, h in horas.items()) / HORAS_TOTAL_MES
    return round(tusd, 4), round(te, 4)


def taxa_kw(valores_kw, *nomes_postos):
    for nome in nomes_postos:
        if nome in valores_kw:
            return valores_kw[nome][0]
    return 0.0


def seletor_cascata(coluna, rotulo, registros_base, campo, opcao_todos, key):
    opcoes = campo_distintos(registros_base, campo) if registros_base else []
    return coluna.selectbox(
        rotulo, options=[opcao_todos] + opcoes, index=0,
        disabled=not registros_base, key=key,
    )


# --------------------------------------------------------------------------
# Cabeçalho + tema
# --------------------------------------------------------------------------

tema_opcoes = ["☀️ Claro", "🌙 Escuro"]
tema_escolha = st.session_state.get("tema_toggle", tema_opcoes[0])
tema = "escuro" if tema_escolha == tema_opcoes[1] else "claro"
aplicar_tema(tema)

_logo_uri = logo_data_uri()
_logo_html = f'<div class="pref-logo-badge"><img src="{_logo_uri}" alt="Projeto Rio de Energia Verde"></div>' if _logo_uri else ""

st.markdown(
    f"""
    <div class="pref-topbar">
        <span class="marca">PREFEITURA<span class="rio">.RIO</span></span>
        <span class="orgao">Secretaria Municipal de Administração · Núcleo de Monitoramento e Indicadores (A/NMI)</span>
    </div>
    <div class="pref-band">
        {_logo_html}
        <div>
            <h1>⚡ Consulta de Tarifas ANEEL</h1>
            <div class="subtitulo">Programa de Eficiência, Transição e Governança Energética</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_espaco, col_tema = st.columns([6, 1])
with col_tema:
    st.segmented_control(
        "Tema", options=tema_opcoes, default=tema_opcoes[0],
        key="tema_toggle", label_visibility="collapsed",
    )

st.caption(
    "Fonte: API de Dados Abertos da ANEEL (CKAN, pública, sem autenticação) — dataset "
    "[Tarifas de aplicação das distribuidoras de energia elétrica]"
    "(https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica). "
    f"{REVISAO_ATUAL} — ver REVISIONS.md."
)

# --------------------------------------------------------------------------
# INPUTS
# --------------------------------------------------------------------------

with st.container(border=True, key="card_inputs"):
    st.markdown("#### 📥 Inputs")

    c1, c2, c3, c4 = st.columns(4)

    distribuidoras = lista_distribuidoras()
    distribuidora = c1.selectbox(
        "Concessionária/Distribuidora", options=distribuidoras, index=None,
        placeholder="Digite para buscar (ex.: LIGHT, CPFL, ENEL)...", key="filtro_distribuidora",
    )
    registros_dist = registros_brutos_da_distribuidora(distribuidora) if distribuidora else []

    with c2:
        st.markdown("**Ano/Mês**")
        ca, cm = st.columns(2)
        anos_disponiveis = sorted({ano_da_vigencia(r) for r in registros_dist if ano_da_vigencia(r)}, reverse=True)
        ano = ca.selectbox(
            "Ano", options=["Todos"] + anos_disponiveis, index=0,
            disabled=not registros_dist, label_visibility="collapsed", key="filtro_ano",
        )
        mes_nome = cm.selectbox(
            "Mês", options=["Todos"] + [nome for _, nome in MESES], index=0,
            disabled=(not registros_dist or ano == "Todos"),
            label_visibility="collapsed", key="filtro_mes",
        )

    if registros_dist and ano != "Todos" and mes_nome != "Todos":
        mes_num = {nome: num for num, nome in MESES}[mes_nome]
        periodo_inicio, periodo_fim = periodo_do_mes(int(ano), mes_num)
        registros_anomes = registros_vigentes_no_periodo(registros_dist, periodo_inicio, periodo_fim)
    elif registros_dist and ano != "Todos":
        registros_anomes = [r for r in registros_dist if ano_da_vigencia(r) == ano]
    else:
        registros_anomes = registros_dist

    reh = seletor_cascata(c3, "REH", registros_anomes, "DscREH", "Todas", key="filtro_reh")
    registros_reh = filtrar_por_campo(registros_anomes, "DscREH", reh, "Todas")

    base_tarifaria = seletor_cascata(c4, "Base tarifária", registros_reh, "DscBaseTarifaria", "Todas", key="filtro_base")
    registros_base = filtrar_por_campo(registros_reh, "DscBaseTarifaria", base_tarifaria, "Todas")

    c5, c6, c7, c8 = st.columns(4)

    subgrupo = seletor_cascata(c5, "Subgrupo", registros_base, "DscSubGrupo", "Todos", key="filtro_subgrupo")
    registros_subgrupo = filtrar_por_campo(registros_base, "DscSubGrupo", subgrupo, "Todos")

    modalidade = seletor_cascata(c6, "Modalidade", registros_subgrupo, "DscModalidadeTarifaria", "Todas", key="filtro_modalidade")
    registros_modalidade = filtrar_por_campo(registros_subgrupo, "DscModalidadeTarifaria", modalidade, "Todas")

    detalhe = seletor_cascata(c7, "Detalhe", registros_modalidade, "DscDetalhe", "Todas", key="filtro_detalhe")
    registros_detalhe = filtrar_por_campo(registros_modalidade, "DscDetalhe", detalhe, "Todas")

    posto = seletor_cascata(c8, "Posto", registros_detalhe, "NomPostoTarifario", "Todos", key="filtro_posto")
    registros_posto = filtrar_por_campo(registros_detalhe, "NomPostoTarifario", posto, "Todos")

    c9, c10 = st.columns(2)
    classe = seletor_cascata(c9, "Classe", registros_posto, "DscClasse", "Todas", key="filtro_classe")
    registros_classe = filtrar_por_campo(registros_posto, "DscClasse", classe, "Todas")

    acessante = seletor_cascata(c10, "Acessante", registros_classe, "SigAgenteAcessante", "Todos", key="filtro_acessante")
    registros_filtrados_atual = filtrar_por_campo(registros_classe, "SigAgenteAcessante", acessante, "Todos")

    st.markdown("**Demanda e consumo informados**")
    modo_calculo = st.radio(
        "Forma de cálculo da energia",
        ["Consumo por posto", "Consumo total estimado"],
        horizontal=True,
        help="Por posto usa diretamente a curva informada. Consumo total distribui o volume pelos pesos horários exibidos na memória.",
    )
    congel = calcular_congelamento(subgrupo, modalidade)
    d1, d2, d3, d4, d5 = st.columns(5)
    demanda_hpt = d1.number_input("Demanda HPT (kW)", min_value=0.0, step=1.0, value=0.0, disabled=congel["demanda_hpt"], key="in_demanda_hpt")
    demanda_hfp = d2.number_input("Demanda HFP (kW)", min_value=0.0, step=1.0, value=0.0, disabled=congel["demanda_hfp"], key="in_demanda_hfp")
    consumo_hpt = d3.number_input("Consumo HPT (MWh)", min_value=0.0, step=0.1, value=0.0, disabled=modo_calculo != "Consumo por posto" or congel["consumo_hpt"], key="in_consumo_hpt")
    consumo_intermediario = d4.number_input("Consumo intermediário (MWh)", min_value=0.0, step=0.1, value=0.0, disabled=modo_calculo != "Consumo por posto" or modalidade != "Branca", key="in_consumo_intermediario")
    consumo_hfp = d5.number_input("Consumo HFP/total (MWh)", min_value=0.0, step=0.1, value=0.0, disabled=modo_calculo == "Consumo por posto" and congel["consumo_hfp"], key="in_consumo_hfp")
    st.caption(
        "No modo por posto, cada consumo é multiplicado pela tarifa correspondente. No modo estimado, "
        "o campo HFP/total representa o consumo mensal total, distribuído pelos pesos horários do mês."
    )

    partes_contexto = [distribuidora or "—", f"Ano/Mês: {ano}" + (f"/{mes_nome}" if mes_nome != "Todos" else ""), f"REH: {reh}"]
    for rotulo, valor, padrao in [
        ("Base", base_tarifaria, "Todas"), ("Subgrupo", subgrupo, "Todos"),
        ("Modalidade", modalidade, "Todas"), ("Detalhe", detalhe, "Todas"),
        ("Posto", posto, "Todos"), ("Classe", classe, "Todas"), ("Acessante", acessante, "Todos"),
    ]:
        if valor and valor != padrao:
            partes_contexto.append(f"{rotulo}: {valor}")

    consultar = st.button("Consultar", type="primary", disabled=not distribuidora)

if not distribuidora:
    st.info("Use os Inputs acima para escolher uma distribuidora e consultar as tarifas homologadas.")
    st.stop()

if consultar:
    st.session_state["ultimo_resultado"] = registros_filtrados_atual
    st.session_state["ultimo_contexto"] = " | ".join(partes_contexto)

if "ultimo_resultado" not in st.session_state:
    st.info("Ajuste os filtros acima e clique em **Consultar**.")
    st.stop()

registros_filtrados = st.session_state.get("ultimo_resultado", [])
contexto = st.session_state.get("ultimo_contexto", "")

# --------------------------------------------------------------------------
# OUTPUTS
# --------------------------------------------------------------------------

with st.container(border=True, key="card_outputs"):
    st.markdown("#### 📤 Outputs")
    st.caption(f"Resultados — {contexto}")
    st.metric("Registros encontrados", len(registros_filtrados))

    elegiveis = [r for r in registros_filtrados if elegivel_para_composicao(r)]
    versoes = sorted(set(chave_versao(r) for r in elegiveis))
    contexto_hash = hash(tuple(sorted(r.get("_id") for r in registros_filtrados)))

    versao_escolhida = None
    if len(versoes) <= 1:
        versao_escolhida = versoes[0] if versoes else None
    elif (
        st.session_state.get("versao_escolhida_contexto") == contexto_hash
        and st.session_state.get("versao_escolhida") in versoes
    ):
        versao_escolhida = st.session_state["versao_escolhida"]
    else:
        st.warning(
            f"Há {len(versoes)} composições de tarifa possíveis com os filtros atuais. "
            "Escolha uma no popup para calcular os totais."
        )
        dialog_escolher_versao(versoes, contexto_hash)

    df = montar_dataframe(registros_filtrados, versao_escolhida)
    st.dataframe(df, width="stretch", hide_index=True)

    if versao_escolhida is None and registros_filtrados and not versoes:
        st.info(
            "Nenhuma linha de energia (R$/MWh) elegível para compor TE+TUSD com os filtros "
            "atuais — só há linhas de demanda (R$/kW) ou nenhuma linha. Totais não calculados."
        )

    if versao_escolhida is not None:
        valores_mwh, amb_mwh = valores_por_posto(registros_filtrados, versao_escolhida, elegivel_para_composicao)
        valores_kw, amb_kw = valores_por_posto(registros_filtrados, versao_escolhida, elegivel_demanda)
        postos_mwh = set(valores_mwh)

        if amb_mwh or amb_kw:
            st.info(
                "Há mais de um valor de tarifa para o mesmo posto tarifário dentro da composição "
                "escolhida — totais não calculados. Refine os filtros."
            )
        elif not postos_mwh.issubset(POSTOS_PADRAO):
            st.info(
                "Essa composição usa postos sazonais (seca/úmida) — o cálculo automático de "
                "energia/demanda não é aplicado para essa estrutura."
            )
        else:
            tem_ponta_real = "Ponta" in postos_mwh
            tem_intermediario_real = "Intermediário" in postos_mwh
            horas = horas_padrao_mes(tem_ponta_real, tem_intermediario_real)
            tusd_te = rate_ponderada(valores_mwh, horas)

            if tusd_te is None:
                st.info("Não foi possível calcular a tarifa ponderada — faltam valores para algum posto da composição.")
            else:
                tusd_pond, te_pond = tusd_te
                posto_hfp = "Fora ponta" if tem_ponta_real else "Não se aplica"
                consumos = {
                    "Ponta": consumo_hpt,
                    "Intermediário": consumo_intermediario,
                    posto_hfp: consumo_hfp,
                }
                demandas = {"Ponta": demanda_hpt, posto_hfp: demanda_hfp}
                try:
                    if modo_calculo == "Consumo total estimado":
                        energia = calcular_por_consumo_total(valores_mwh, consumo_hfp, horas)
                        demanda = calcular_fatura(valores_mwh, {}, valores_kw, demandas)["demanda"]
                        calculo = {
                            "energia": energia,
                            "demanda": demanda,
                            "linhas": energia["linhas"] + demanda["linhas"],
                            "total": energia["total"] + demanda["total"],
                        }
                    else:
                        calculo = calcular_fatura(valores_mwh, consumos, valores_kw, demandas)
                except ValueError as erro:
                    st.error(f"Cálculo não realizado: {erro}")
                    st.stop()

                total_te = calculo["energia"]["te"]
                total_tusd_energia = calculo["energia"]["tusd_energia"]
                total_energia = calculo["energia"]["total"]

                st.markdown("##### Energia (TE + TUSD)")
                e1, e2, e3 = st.columns(3)
                e1.metric("TE ponderada (R$/MWh)", fmt_brl(te_pond))
                e2.metric("TUSD ponderada (R$/MWh)", fmt_brl(tusd_pond))
                e3.metric("Total energia (R$)", fmt_brl(total_energia))

                grupo = grupo_tensao(versao_escolhida[2])
                total_demanda = calculo["demanda"]["total"]
                tusd_demanda_ponta = tusd_demanda_hfp = 0.0
                if valores_kw and grupo != "B":
                    tusd_demanda_ponta = taxa_kw(valores_kw, "Ponta")
                    tusd_demanda_hfp = taxa_kw(valores_kw, "Fora ponta", "Não se aplica")
                    st.markdown("##### Demanda (TUSD)")
                    d_1, d_2, d_3 = st.columns(3)
                    d_1.metric("TUSD Demanda Ponta (R$/kW)", fmt_brl(tusd_demanda_ponta))
                    d_2.metric("TUSD Demanda Fora Ponta (R$/kW)", fmt_brl(tusd_demanda_hfp))
                    d_3.metric("Total demanda (R$)", fmt_brl(total_demanda))
                elif grupo == "B":
                    st.caption("Grupo B (baixa tensão) não fatura demanda contratada — total de demanda não calculado.")

                st.markdown(
                    f"""
                    <div class="hero-total">
                        <div class="rotulo">💰 Total geral estimado (R$/mês)</div>
                        <div class="valor">{fmt_brl(calculo['total'])}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander("Memória de cálculo"):
                    memoria_df = pd.DataFrame(calculo["linhas"])
                    if not memoria_df.empty:
                        memoria_df = memoria_df.rename(columns={
                            "componente": "Componente", "posto": "Posto", "tarifa": "Tarifa",
                            "quantidade": "Quantidade", "unidade": "Unidade", "subtotal": "Subtotal (R$)",
                        })
                        st.dataframe(memoria_df, hide_index=True, width="stretch")
                    st.caption(
                        ("O consumo total foi distribuído pelos pesos: " + ", ".join(f"{p} ({h:.0f})" for p, h in horas.items()))
                        if modo_calculo == "Consumo total estimado" else
                        "Cálculo direto: tarifa de cada posto × consumo informado no mesmo posto."
                    )
                    if valores_kw and grupo != "B":
                        st.caption(
                            f"Total demanda (R$) = TUSD Demanda Ponta × Demanda HPT + TUSD Demanda Fora Ponta × Demanda HFP "
                            f"= {fmt_brl(tusd_demanda_ponta)}/kW × {demanda_hpt:.2f} kW + {fmt_brl(tusd_demanda_hfp)}/kW × {demanda_hfp:.2f} kW"
                        )
                    if modo_calculo == "Consumo total estimado":
                        st.caption("Estimativa por perfil horário padrão; não substitui a curva de carga da unidade consumidora.")

    if not df.empty:
        buffer = io.StringIO()
        df.to_csv(buffer, sep=";", index=False, encoding="utf-8-sig")
        st.download_button(
            "Baixar CSV",
            data=buffer.getvalue().encode("utf-8-sig"),
            file_name=f"tarifas_{distribuidora.replace(' ', '_')}.csv",
            mime="text/csv",
        )
