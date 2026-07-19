"""
Interface web (Streamlit) para consultar a BBCE Curva Forward via API do
BBCE Connect (Portal do Desenvolvedor BBCE). Requer credenciais proprias
(plano Essentials) -- ver README.md e .env.example.
"""

from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv

import bbce_api as api

SCRIPT_DIR = Path(__file__).resolve().parent
load_dotenv(SCRIPT_DIR / ".env")

# Paleta categorica validada (ver skill dataviz/references/palette.md)
CORES_SERIES = ["#2a78d6", "#008300", "#e87ba4", "#eda100", "#1baf7a", "#eb6834", "#4a3aa7", "#e34948"]
COR_GRADE = "#e1e0d9"
COR_EIXO = "#c3c2b7"
COR_TEXTO_MUTED = "#898781"
COR_TEXTO_SECUNDARIO = "#52514e"

st.set_page_config(page_title="BBCE Curva Forward", layout="wide")
st.title("BBCE Curva Forward")
st.caption(
    "Consulta a BBCE Curva Forward -- referencia de precos futuros de energia eletrica do mercado livre "
    "brasileiro, calculada diariamente pela BBCE a partir de negocios reais na plataforma EHUB. "
    "Fonte: BBCE Connect (Portal do Desenvolvedor BBCE), plano Essentials."
)

# Pre-preenche o formulario com o que estiver no .env (se houver), mas os
# valores digitados na interface ficam so em st.session_state -- em memoria
# da sessao do navegador, nunca gravados em disco.
if "bbce_email" not in st.session_state:
    _padrao = api.BBCECredenciais()
    st.session_state["bbce_api_key"] = _padrao.api_key
    st.session_state["bbce_email"] = _padrao.email
    st.session_state["bbce_password"] = _padrao.password
    st.session_state["bbce_company_code"] = str(_padrao.company_external_code or "")
    st.session_state["bbce_autenticado"] = False

with st.sidebar:
    st.header("Login BBCE Connect")
    with st.form("login_form"):
        api_key_input = st.text_input("API Key", type="password", value=st.session_state["bbce_api_key"])
        empresa_input = st.text_input("Código da Empresa", value=st.session_state["bbce_company_code"])
        usuario_input = st.text_input("Usuário (e-mail)", value=st.session_state["bbce_email"])
        senha_input = st.text_input("Senha", type="password", value=st.session_state["bbce_password"])
        entrar = st.form_submit_button("Entrar")

    if entrar:
        st.session_state["bbce_api_key"] = api_key_input
        st.session_state["bbce_company_code"] = empresa_input
        st.session_state["bbce_email"] = usuario_input
        st.session_state["bbce_password"] = senha_input
        try:
            credenciais = api.BBCECredenciais(
                api_key=api_key_input, email=usuario_input,
                password=senha_input, company_external_code=empresa_input,
            )
            credenciais.validar()
            api.login(api.nova_sessao(), credenciais)
            st.session_state["bbce_autenticado"] = True
            st.success("Login realizado com sucesso.")
        except api.BBCEAuthError as erro:
            st.session_state["bbce_autenticado"] = False
            st.error(str(erro))
        except requests.RequestException as erro:
            st.session_state["bbce_autenticado"] = False
            st.error(f"Falha ao conectar a API da BBCE: {erro}")

    if st.session_state["bbce_autenticado"]:
        st.caption("Sessão ativa.")


def credenciais_atuais():
    return api.BBCECredenciais(
        api_key=st.session_state["bbce_api_key"],
        email=st.session_state["bbce_email"],
        password=st.session_state["bbce_password"],
        company_external_code=st.session_state["bbce_company_code"],
    )


def _credenciais_ok():
    try:
        credenciais_atuais().validar()
        return True, None
    except api.BBCEAuthError as erro:
        return False, str(erro)


def _layout_grafico(fig, titulo_y):
    fig.update_layout(
        template="plotly_white",
        hovermode="x unified",
        margin=dict(l=10, r=10, t=10, b=10),
        plot_bgcolor="#fcfcfb",
        paper_bgcolor="#fcfcfb",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        font=dict(color="#0b0b0b"),
    )
    fig.update_xaxes(showgrid=False, linecolor=COR_EIXO, tickfont=dict(color=COR_TEXTO_MUTED))
    fig.update_yaxes(
        title=titulo_y, gridcolor=COR_GRADE, zeroline=False,
        linecolor=COR_EIXO, tickfont=dict(color=COR_TEXTO_MUTED),
        title_font=dict(color=COR_TEXTO_SECUNDARIO),
    )
    return fig


@st.cache_data(ttl=600, show_spinner="Consultando curva forward...")
def consultar_curva_geral(data_referencia, fonte, regiao, api_key, email, password, company_code):
    session = api.nova_sessao()
    credenciais = api.BBCECredenciais(api_key=api_key, email=email, password=password, company_external_code=company_code)
    return api.curva_forward(session, credenciais, data_referencia, fonte=fonte or None, regiao=regiao or None)


@st.cache_data(ttl=600, show_spinner="Consultando curva por produto...")
def consultar_curva_produto(data_referencia, fonte, tipo_curva, api_key, email, password, company_code):
    session = api.nova_sessao()
    credenciais = api.BBCECredenciais(api_key=api_key, email=email, password=password, company_external_code=company_code)
    return api.curva_por_produto(session, credenciais, data_referencia, fonte=fonte or None, tipo_curva=tipo_curva or None)


ok, erro_credenciais = _credenciais_ok()
if not ok:
    st.warning(
        f"{erro_credenciais}\n\n"
        "Preencha o formulário de login na barra lateral (ou crie um arquivo `.env` nesta pasta -- "
        "veja `.env.example`)."
    )

aba_geral, aba_produto = st.tabs(["Curva Forward (geral)", "Curva por Produto"])

with aba_geral:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        data_ref = st.date_input("Data de referencia", key="data_geral")
    with col2:
        fonte = st.selectbox("Fonte de energia", ["Todas"] + api.FONTES_ENERGIA, key="fonte_geral")
    with col3:
        regiao = st.selectbox("Submercado", ["Todos"] + api.SUBMERCADOS, key="regiao_geral")
    with col4:
        st.write("")
        st.write("")
        consultar = st.button("Consultar", key="btn_geral", disabled=not ok)

    if consultar:
        credenciais = credenciais_atuais()
        registros = consultar_curva_geral(
            data_ref.isoformat(),
            None if fonte == "Todas" else fonte,
            None if regiao == "Todos" else regiao,
            credenciais.api_key, credenciais.email, credenciais.password, credenciais.company_external_code,
        )
        if not registros:
            st.info("Nenhum registro retornado para os filtros informados.")
        else:
            df = pd.DataFrame(registros)
            df["vertexDate"] = pd.to_datetime(df["vertexDate"]).dt.date
            df = df.sort_values("vertexDate")

            fig = go.Figure()
            series = df["name"].unique() if "name" in df.columns else [None]
            for i, nome_serie in enumerate(series):
                dados_serie = df[df["name"] == nome_serie] if nome_serie is not None else df
                fig.add_trace(go.Scatter(
                    x=dados_serie["vertexDate"], y=dados_serie["vertexValue"],
                    mode="lines+markers", name=nome_serie or "Curva",
                    line=dict(width=2, color=CORES_SERIES[i % len(CORES_SERIES)]),
                    marker=dict(size=7),
                ))
            if len(series) <= 1:
                fig.update_layout(showlegend=False)
            _layout_grafico(fig, "R$/MWh")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Baixar CSV", df.to_csv(index=False, sep=";").encode("utf-8-sig"),
                file_name=f"curva_forward_{data_ref.isoformat()}.csv", mime="text/csv",
            )

with aba_produto:
    col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
    with col1:
        data_ref_p = st.date_input("Data de referencia", key="data_produto")
    with col2:
        fonte_p = st.selectbox("Fonte de energia", ["Todas"] + api.FONTES_ENERGIA, key="fonte_produto")
    with col3:
        tipo_curva_p = st.selectbox("Tipo de preco", ["Todos"] + api.TIPOS_CURVA_PRODUTO, key="tipo_produto")
    with col4:
        st.write("")
        st.write("")
        consultar_p = st.button("Consultar", key="btn_produto", disabled=not ok)

    if consultar_p:
        credenciais = credenciais_atuais()
        registros = consultar_curva_produto(
            data_ref_p.isoformat(),
            None if fonte_p == "Todas" else fonte_p,
            None if tipo_curva_p == "Todos" else tipo_curva_p,
            credenciais.api_key, credenciais.email, credenciais.password, credenciais.company_external_code,
        )
        if not registros:
            st.info("Nenhum registro retornado para os filtros informados.")
        else:
            df = pd.DataFrame(registros)
            df["dateStartTicker"] = pd.to_datetime(df["dateStartTicker"]).dt.date
            df = df.sort_values("dateStartTicker")
            df["tipoPreco"] = df["ticker"].str.extract(r"- (Preço Fixo|SWAP)$").fillna("Nao identificado")

            fig = go.Figure()
            tipos = df["tipoPreco"].unique()
            for i, tipo in enumerate(tipos):
                dados_tipo = df[df["tipoPreco"] == tipo]
                fig.add_trace(go.Scatter(
                    x=dados_tipo["dateStartTicker"], y=dados_tipo["tickerValue"],
                    mode="lines+markers", name=tipo,
                    line=dict(width=2, color=CORES_SERIES[i % len(CORES_SERIES)]),
                    marker=dict(size=7),
                    text=dados_tipo["ticker"], hovertemplate="%{text}<br>R$ %{y}<extra></extra>",
                ))
            if len(tipos) <= 1:
                fig.update_layout(showlegend=False)
            _layout_grafico(fig, "R$/MWh")
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df, use_container_width=True)
            st.download_button(
                "Baixar CSV", df.to_csv(index=False, sep=";").encode("utf-8-sig"),
                file_name=f"curva_por_produto_{data_ref_p.isoformat()}.csv", mime="text/csv",
                key="download_produto",
            )
