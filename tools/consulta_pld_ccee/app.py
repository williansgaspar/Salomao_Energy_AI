"""
Interface web para consulta do PLD (Preço de Liquidação das Diferenças) na API de
Dados Abertos da CCEE (CKAN, pública, sem autenticação).

Cobre os 4 datasets da família PLD (ver ccee_api.DATASETS): horário, médio diário,
médio mensal e o histórico legado (pld_final_historico, abr–set/2013).

Rodar com:
    streamlit run app.py
"""

import io

import pandas as pd
import streamlit as st

from ccee_api import (
    DATASETS,
    buscar_dataset,
    converter_valor_brl,
    detectar_campos,
    nova_sessao,
    obter_campos,
    resolver_recursos,
    valores_distintos,
)

st.set_page_config(page_title="PLD CCEE", page_icon="📈", layout="wide")


@st.cache_resource
def sessao():
    return nova_sessao()


@st.cache_data(ttl=24 * 3600, show_spinner="Consultando recursos do dataset na CCEE...")
def campos_do_dataset(dataset_id):
    recursos = resolver_recursos(sessao(), dataset_id)
    campos = obter_campos(sessao(), recursos[0]["id"])
    return campos, detectar_campos(campos)


@st.cache_data(ttl=24 * 3600, show_spinner="Buscando submercados disponíveis...")
def submercados_do_dataset(dataset_id, campo_submercado):
    return valores_distintos(sessao(), dataset_id, campo_submercado)


@st.cache_data(ttl=6 * 3600, show_spinner="Consultando PLD na API da CCEE (pode levar alguns segundos)...")
def buscar(dataset_id, submercado, campo_submercado, limite):
    filtros = {campo_submercado: submercado} if (submercado and submercado != "Todos" and campo_submercado) else None
    registros, campos_detectados = buscar_dataset(sessao(), dataset_id, filters=filtros, limit_total=limite or None)
    return registros, campos_detectados


st.title("📈 Consulta de PLD — CCEE")
st.caption(
    "Fonte: API de Dados Abertos da CCEE (CKAN, pública, sem autenticação) — família de datasets "
    "[Preço de Liquidação das Diferenças](https://dadosabertos.ccee.org.br/organization/preco_liquidacao_diferenca)."
)
st.info(
    "⚠️ Os nomes de coluna (submercado/data/valor) usados nos filtros abaixo são detectados "
    "automaticamente a partir do schema retornado pela CCEE, não fixos no código — confira o "
    "aviso de detecção na barra lateral antes de usar os números em um parecer.",
    icon="⚠️",
)

with st.sidebar:
    st.header("Filtros")

    dataset_id = st.selectbox(
        "Dataset",
        options=list(DATASETS),
        format_func=lambda d: DATASETS[d],
        index=0,
    )

    campos, campos_detectados = campos_do_dataset(dataset_id)

    with st.expander("Detecção de campos (schema real)"):
        for chave, valor in campos_detectados.items():
            st.write(f"**{chave}**: `{valor or 'não detectado'}`")
        st.caption("Colunas brutas: " + ", ".join(c["id"] for c in campos))

    campo_submercado = campos_detectados.get("submercado")
    submercado = None
    if campo_submercado:
        submercados = submercados_do_dataset(dataset_id, campo_submercado)
        submercado = st.selectbox("Submercado", options=["Todos"] + submercados, index=0)
    else:
        st.warning("Coluna de submercado não detectada automaticamente para este dataset — resultado virá sem esse filtro.")

    campo_data = campos_detectados.get("data")
    data_ini = data_fim = None
    if campo_data:
        col1, col2 = st.columns(2)
        usar_periodo = st.checkbox("Filtrar por período", value=False)
        if usar_periodo:
            data_ini = col1.date_input("De", value=None, format="YYYY-MM-DD")
            data_fim = col2.date_input("Até", value=None, format="YYYY-MM-DD")

    limite = None
    if not submercado or submercado == "Todos":
        st.caption(
            "⚠️ Sem filtro de submercado, a consulta baixa todos os recursos do dataset "
            "(pode ser lento para pld_horario/pld_media_diaria). Considere limitar:"
        )
        usar_limite = st.checkbox("Limitar número de registros", value=(dataset_id in ("pld_horario", "pld_media_diaria")))
        if usar_limite:
            limite = st.number_input("Limite de registros", min_value=100, value=20000, step=1000)

    consultar = st.button("Consultar", type="primary")

if not consultar and "ultimo_resultado" not in st.session_state:
    st.info("Ajuste os filtros na barra lateral e clique em **Consultar**.")
    st.stop()

if consultar:
    registros, campos_detectados = buscar(dataset_id, submercado, campo_submercado, limite)
    st.session_state["ultimo_resultado"] = registros
    st.session_state["ultimo_campos_detectados"] = campos_detectados
    st.session_state["ultimo_dataset"] = dataset_id
    st.session_state["ultimo_submercado"] = submercado

registros = st.session_state.get("ultimo_resultado", [])
campos_detectados = st.session_state.get("ultimo_campos_detectados", campos_detectados)
dataset_atual = st.session_state.get("ultimo_dataset", dataset_id)

df = pd.DataFrame(registros)
if "_id" in df.columns:
    df = df.drop(columns=["_id"])

campo_data_atual = campos_detectados.get("data")
if campo_data_atual and campo_data_atual in df.columns and (data_ini or data_fim):
    datas = pd.to_datetime(df[campo_data_atual], errors="coerce").dt.date
    if data_ini:
        df = df[datas >= data_ini]
        datas = datas[df.index]
    if data_fim:
        df = df[datas <= data_fim]

campo_valor = campos_detectados.get("valor")
if campo_valor and campo_valor in df.columns:
    df[campo_valor] = df[campo_valor].apply(converter_valor_brl)

st.subheader(f"Resultados — {DATASETS.get(dataset_atual, dataset_atual)}")
st.metric("Registros encontrados", len(df))
st.dataframe(df, use_container_width=True, hide_index=True)

if campo_valor and campo_valor in df.columns and not df[campo_valor].dropna().empty:
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Média ({campo_valor})", f"{df[campo_valor].mean():.2f}")
    col2.metric(f"Mínimo ({campo_valor})", f"{df[campo_valor].min():.2f}")
    col3.metric(f"Máximo ({campo_valor})", f"{df[campo_valor].max():.2f}")

if not df.empty:
    buffer = io.StringIO()
    df.to_csv(buffer, sep=";", index=False, encoding="utf-8-sig")
    st.download_button(
        "Baixar CSV",
        data=buffer.getvalue().encode("utf-8-sig"),
        file_name=f"pld_{dataset_atual}.csv",
        mime="text/csv",
    )
