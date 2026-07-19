"""Revisão 4 — consulta, simulação/comparação e histórico de tarifas ANEEL."""

from datetime import date, datetime
from io import BytesIO
from pathlib import Path

import pandas as pd
import streamlit as st

from aneel_api import ano_da_vigencia, converter_valor_brl
from src.aneel import criar_sessao, listar_distribuidoras, obter_tarifas
from src.domain.calculos import calcular_fatura, calcular_por_consumo_total
from src.domain.composicao import chave_versao, rotulo_versao, valores_por_posto, versoes_disponiveis
from src.domain.vigencia import periodo_do_mes, registros_vigentes_no_periodo
from src.exports import gerar_excel, gerar_pdf
from src.ui import aplicar_tema, cabecalho, fmt_brl

BASE_DIR = Path(__file__).resolve().parent
MESES = [(1, "Jan"), (2, "Fev"), (3, "Mar"), (4, "Abr"), (5, "Mai"), (6, "Jun"), (7, "Jul"), (8, "Ago"), (9, "Set"), (10, "Out"), (11, "Nov"), (12, "Dez")]
COLUNAS = {
    "SigAgente": "Distribuidora", "DscREH": "REH", "DatInicioVigencia": "Início vigência",
    "DatFimVigencia": "Fim vigência", "DscBaseTarifaria": "Base tarifária", "DscSubGrupo": "Subgrupo",
    "DscModalidadeTarifaria": "Modalidade", "DscClasse": "Classe", "DscSubClasse": "Subclasse",
    "DscDetalhe": "Detalhe", "NomPostoTarifario": "Posto", "DscUnidadeTerciaria": "Unidade",
    "SigAgenteAcessante": "Acessante", "VlrTUSD": "TUSD", "VlrTE": "TE",
}

st.set_page_config(page_title="Tarifas ANEEL", page_icon="⚡", layout="wide")
aplicar_tema()
cabecalho(BASE_DIR)


@st.cache_resource
def sessao():
    return criar_sessao()


@st.cache_data(ttl=7 * 86400, show_spinner="Atualizando distribuidoras...")
def distribuidoras():
    return listar_distribuidoras(sessao())


@st.cache_data(ttl=86400, show_spinner="Consultando a base da ANEEL...")
def dados_distribuidora(sigla):
    return obter_tarifas(sessao(), sigla)


def opcoes(registros, campo):
    return sorted({r.get(campo) for r in registros if r.get(campo)})


def filtrar(registros, campo, valor, todos):
    return registros if not valor or valor == todos else [r for r in registros if r.get(campo) == valor]


def dataframe_tarifas(registros):
    df = pd.DataFrame(registros)
    if df.empty:
        return df
    for coluna in ("VlrTUSD", "VlrTE"):
        if coluna in df:
            df[coluna] = df[coluna].map(converter_valor_brl)
    existentes = [c for c in COLUNAS if c in df]
    return df[existentes].rename(columns=COLUNAS)


def contexto_consulta(parametros):
    return " | ".join(f"{k}: {v}" for k, v in parametros.items() if v not in (None, "Todos", "Todas", ""))


def carregar_perfil(arquivo):
    if arquivo is None:
        return {}
    df = pd.read_csv(arquivo, sep=None, engine="python") if arquivo.name.lower().endswith(".csv") else pd.read_excel(arquivo)
    normalizadas = {str(c).strip().lower(): c for c in df.columns}
    if {"posto", "consumo_mwh"}.issubset(normalizadas):
        return {
            str(row[normalizadas["posto"]]).strip(): float(row[normalizadas["consumo_mwh"]])
            for _, row in df.iterrows() if pd.notna(row[normalizadas["consumo_mwh"]])
        }
    raise ValueError("O arquivo deve conter as colunas 'posto' e 'consumo_mwh'.")


aba_consulta, aba_simulacao, aba_historico = st.tabs(["1. Consulta", "2. Simulação e comparação", "3. Histórico"])

with aba_consulta:
    st.subheader("Parâmetros da consulta")
    st.caption("Selecione a referência principal. Filtros técnicos menos frequentes ficam em Consulta avançada.")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    distribuidora = c1.selectbox("Distribuidora", distribuidoras(), index=None, placeholder="Digite para buscar...")
    brutos = dados_distribuidora(distribuidora) if distribuidora else []
    anos = sorted({ano_da_vigencia(r) for r in brutos if ano_da_vigencia(r)}, reverse=True)
    ano = c2.selectbox("Ano", anos, index=0 if anos else None, disabled=not anos)
    mes_nome = c3.selectbox("Mês", [nome for _, nome in MESES], index=date.today().month - 1, disabled=not anos)
    data_exata = c4.date_input("Data de referência", value=None, help="Se preenchida, prevalece sobre Ano/Mês.")

    periodo = brutos
    if brutos and data_exata:
        periodo = registros_vigentes_no_periodo(brutos, data_exata, data_exata)
    elif brutos and ano:
        mes = dict((nome, numero) for numero, nome in MESES)[mes_nome]
        inicio, fim = periodo_do_mes(int(ano), mes)
        periodo = registros_vigentes_no_periodo(brutos, inicio, fim)

    c5, c6 = st.columns(2)
    subgrupo = c5.selectbox("Subgrupo", ["Todos"] + opcoes(periodo, "DscSubGrupo"), disabled=not periodo)
    por_subgrupo = filtrar(periodo, "DscSubGrupo", subgrupo, "Todos")
    modalidade = c6.selectbox("Modalidade", ["Todas"] + opcoes(por_subgrupo, "DscModalidadeTarifaria"), disabled=not por_subgrupo)
    filtrados = filtrar(por_subgrupo, "DscModalidadeTarifaria", modalidade, "Todas")

    with st.expander("Consulta avançada"):
        a1, a2, a3 = st.columns(3)
        bases_disponiveis = opcoes(filtrados, "DscBaseTarifaria")
        bases_ordenadas = (["Tarifa de Aplicação"] if "Tarifa de Aplicação" in bases_disponiveis else []) + [v for v in bases_disponiveis if v != "Tarifa de Aplicação"]
        base = a1.selectbox("Base tarifária", bases_ordenadas, index=0 if bases_ordenadas else None, disabled=not bases_ordenadas)
        filtrados = filtrar(filtrados, "DscBaseTarifaria", base, "Todas")
        reh = a2.selectbox("REH", ["Todas"] + opcoes(filtrados, "DscREH"), disabled=not filtrados)
        filtrados = filtrar(filtrados, "DscREH", reh, "Todas")
        classe = a3.selectbox("Classe", ["Todas"] + opcoes(filtrados, "DscClasse"), disabled=not filtrados)
        filtrados = filtrar(filtrados, "DscClasse", classe, "Todas")
        a4, a5, a6 = st.columns(3)
        detalhe = a4.selectbox("Detalhe", ["Todas"] + opcoes(filtrados, "DscDetalhe"), disabled=not filtrados)
        filtrados = filtrar(filtrados, "DscDetalhe", detalhe, "Todas")
        acessante = a5.selectbox("Acessante", ["Todos"] + opcoes(filtrados, "SigAgenteAcessante"), disabled=not filtrados)
        filtrados = filtrar(filtrados, "SigAgenteAcessante", acessante, "Todos")
        posto = a6.selectbox("Posto", ["Todos"] + opcoes(filtrados, "NomPostoTarifario"), disabled=not filtrados)
        filtrados = filtrar(filtrados, "NomPostoTarifario", posto, "Todos")

    parametros = {"Distribuidora": distribuidora, "Referência": str(data_exata or f"{mes_nome}/{ano}"), "Subgrupo": subgrupo, "Modalidade": modalidade, "Base": base if periodo else None, "REH": reh if periodo else None}
    if st.button("Consultar tarifas", type="primary", disabled=not distribuidora):
        st.session_state["consulta_registros"] = filtrados
        st.session_state["consulta_brutos"] = brutos
        st.session_state["consulta_contexto"] = contexto_consulta(parametros)

    consulta = st.session_state.get("consulta_registros", [])
    if consulta:
        st.success(f"{len(consulta)} registros encontrados. A simulação foi habilitada na aba seguinte.")
        tabela = dataframe_tarifas(consulta)
        st.dataframe(tabela, hide_index=True, width="stretch", height=360)
        st.download_button("Baixar dados em CSV", tabela.to_csv(index=False, sep=";").encode("utf-8-sig"), "tarifas_aneel.csv", "text/csv")
        with st.expander("Qualidade e rastreabilidade dos dados"):
            ausentes_tusd = sum(not r.get("VlrTUSD") for r in consulta)
            ausentes_te = sum(not r.get("VlrTE") for r in consulta)
            datas = [r.get("DatInicioVigencia") for r in consulta if r.get("DatInicioVigencia")]
            st.write({
                "resource_id": "fcf2906c-7c32-4b9b-a637-054e7a5234f4",
                "consultado_em": datetime.now().astimezone().isoformat(timespec="seconds"),
                "registros": len(consulta),
                "maior_inicio_vigencia": max(datas) if datas else None,
                "TUSD ausente": ausentes_tusd,
                "TE ausente": ausentes_te,
            })
    elif distribuidora:
        st.info("Ajuste os filtros e clique em Consultar tarifas.")
    else:
        st.info("Comece selecionando uma distribuidora.")

with aba_simulacao:
    consulta = st.session_state.get("consulta_registros", [])
    contexto = st.session_state.get("consulta_contexto", "Consulta não identificada")
    if not consulta:
        st.info("Faça uma consulta na primeira aba para habilitar a simulação.")
    else:
        versoes = versoes_disponiveis(consulta)
        rotulos = {rotulo_versao(v): v for v in versoes}
        st.subheader("Composição tarifária")
        escolhas = st.multiselect("Composições para simular e comparar", list(rotulos), default=list(rotulos)[:1], max_selections=2)
        st.caption("Selecione uma composição para simular ou duas para comparar com o mesmo perfil.")
        if escolhas:
            principal = rotulos[escolhas[0]]
            tarifas_mwh = valores_por_posto(consulta, principal, "MWh")
            tarifas_kw = valores_por_posto(consulta, principal, "kW")
            postos_energia = list(tarifas_mwh)
            postos_demanda = list(tarifas_kw)
            modo = st.radio("Forma de cálculo", ["Consumo por posto", "Consumo total estimado"], horizontal=True)
            arquivo = st.file_uploader("Importar perfil CSV/XLSX (opcional)", type=["csv", "xlsx"], help="Colunas esperadas: posto, consumo_mwh")
            try:
                perfil = carregar_perfil(arquivo)
            except ValueError as erro:
                st.error(str(erro)); perfil = {}

            consumos = {}
            demandas = {}
            if modo == "Consumo por posto":
                colunas = st.columns(max(1, len(postos_energia)))
                for i, posto_nome in enumerate(postos_energia):
                    consumos[posto_nome] = colunas[i].number_input(f"Consumo {posto_nome} (MWh)", min_value=0.0, value=float(perfil.get(posto_nome, 0.0)), step=0.1)
            else:
                consumo_total = st.number_input("Consumo mensal total (MWh)", min_value=0.0, step=0.1)
                st.caption("Distribuição padrão: 66 horas de ponta, 44 horas intermediárias quando existentes e horas restantes fora de ponta.")
            if postos_demanda:
                cols_demanda = st.columns(len(postos_demanda))
                for i, posto_nome in enumerate(postos_demanda):
                    demandas[posto_nome] = cols_demanda[i].number_input(f"Demanda {posto_nome} (kW)", min_value=0.0, step=1.0)

            if st.button("Calcular estimativa", type="primary"):
                resultados = []
                memorias = []
                try:
                    for escolha in escolhas:
                        versao = rotulos[escolha]
                        tmwh = valores_por_posto(consulta, versao, "MWh")
                        tkw = valores_por_posto(consulta, versao, "kW")
                        if set(tmwh) != set(tarifas_mwh):
                            raise ValueError("As composições comparadas possuem postos de energia diferentes e não admitem o mesmo perfil.")
                        if modo == "Consumo por posto":
                            calculo = calcular_fatura(tmwh, consumos, tkw, demandas)
                        else:
                            pesos = {p: (66 if p == "Ponta" else 44 if p == "Intermediário" else 720) for p in tmwh}
                            if "Fora ponta" in pesos:
                                pesos["Fora ponta"] = 720 - sum(v for p, v in pesos.items() if p != "Fora ponta")
                            energia = calcular_por_consumo_total(tmwh, consumo_total, pesos)
                            demanda = calcular_fatura(tmwh, {}, tkw, demandas)["demanda"]
                            calculo = {"energia": energia, "demanda": demanda, "linhas": energia["linhas"] + demanda["linhas"], "total": energia["total"] + demanda["total"]}
                        resultados.append({"Composição": escolha, "Energia (R$)": calculo["energia"]["total"], "Demanda (R$)": calculo["demanda"]["total"], "Total (R$)": calculo["total"]})
                        for linha in calculo["linhas"]:
                            memorias.append({"Composição": escolha, **linha})
                    st.session_state["sim_resultados"] = pd.DataFrame(resultados)
                    st.session_state["sim_memoria"] = pd.DataFrame(memorias)
                except ValueError as erro:
                    st.error(f"Cálculo não realizado: {erro}")

            resultados_df = st.session_state.get("sim_resultados", pd.DataFrame())
            memoria_df = st.session_state.get("sim_memoria", pd.DataFrame())
            if not resultados_df.empty:
                st.markdown(f'<div class="total-card">Total da composição principal<br><strong>{fmt_brl(resultados_df.iloc[0]["Total (R$)"])}</strong></div>', unsafe_allow_html=True)
                st.dataframe(resultados_df, hide_index=True, width="stretch")
                with st.expander("Memória de cálculo auditável", expanded=True):
                    st.dataframe(memoria_df, hide_index=True, width="stretch")
                dados_df = dataframe_tarifas(consulta)
                e1, e2 = st.columns(2)
                e1.download_button("Exportar XLSX completo", gerar_excel(dados_df, memoria_df, contexto), "simulacao_tarifas_aneel.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                e2.download_button("Exportar PDF executivo", gerar_pdf(memoria_df, contexto, float(resultados_df.iloc[0]["Total (R$)"])), "simulacao_tarifas_aneel.pdf", "application/pdf")

with aba_historico:
    brutos = st.session_state.get("consulta_brutos", [])
    if not brutos:
        st.info("Faça uma consulta para carregar o histórico da distribuidora.")
    else:
        st.subheader("Evolução das tarifas homologadas")
        h1, h2, h3 = st.columns(3)
        sub = h1.selectbox("Subgrupo histórico", opcoes(brutos, "DscSubGrupo"), key="hist_sub")
        base_hist = filtrar(brutos, "DscSubGrupo", sub, "Todos")
        mod = h2.selectbox("Modalidade histórica", opcoes(base_hist, "DscModalidadeTarifaria"), key="hist_mod")
        base_hist = filtrar(base_hist, "DscModalidadeTarifaria", mod, "Todas")
        unidade = h3.selectbox("Unidade", opcoes(base_hist, "DscUnidadeTerciaria"), key="hist_un")
        base_hist = filtrar(base_hist, "DscUnidadeTerciaria", unidade, "Todas")
        hist = pd.DataFrame(base_hist)
        if not hist.empty:
            hist["Data"] = pd.to_datetime(hist["DatInicioVigencia"], errors="coerce")
            hist["TUSD"] = hist["VlrTUSD"].map(converter_valor_brl)
            hist["TE"] = hist["VlrTE"].map(converter_valor_brl)
            hist["Posto"] = hist["NomPostoTarifario"]
            agrupado = hist.groupby(["Data", "Posto"], as_index=False)[["TUSD", "TE"]].mean().sort_values("Data")
            metrica = st.radio("Componente", ["TUSD", "TE"], horizontal=True)
            grafico = agrupado.pivot(index="Data", columns="Posto", values=metrica)
            st.line_chart(grafico)
            st.dataframe(agrupado, hide_index=True, width="stretch")
        else:
            st.warning("Não há série para os filtros selecionados.")

st.caption("Fonte: API pública de Dados Abertos da ANEEL. A simulação é estimativa técnica e não substitui a fatura da distribuidora.")
