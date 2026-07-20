"""Revisão 17 — histórico coerente com a família tarifária consultada."""

import hashlib
from datetime import date, datetime
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

from aneel_api import ano_da_vigencia, converter_valor_brl
from src.aneel import criar_sessao, listar_distribuidoras, obter_tarifas
from src.domain.calculos import calcular_fatura, calcular_por_consumo_total, comparar_acr_acl, tarifas_indicativas_ponderadas
from src.domain.composicao import chave_versao, rotulo_versao, valores_por_posto, versoes_disponiveis
from src.domain.contexto import fingerprint_simulacao
from src.domain.historico import filtros_da_familia, ordenar_registros_historicos, registros_historicos
from src.domain.vigencia import periodo_do_mes, registros_vigentes_no_periodo
from src.exports import gerar_excel, gerar_pdf
from src.importers import extrair_fatura, grandezas_ausentes, grandezas_da_fatura, reconciliar_com_aneel, totais_tributos
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
tema_col1, tema_col2 = st.columns([7, 1])
with tema_col2:
    tema_escuro = st.toggle("Tema escuro", value=False, key="tema_escuro")
aplicar_tema(tema_escuro)
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


def chave_input(prefixo, posto):
    posto_normalizado = posto.lower().replace(" ", "_").replace("ã", "a")
    versao = st.session_state.get("perfil_widget_versao", "manual")
    return f"{prefixo}_{posto_normalizado}_{versao}"


def chave_param(nome):
    versao = st.session_state.get("param_widget_versao", "manual")
    return f"{nome}_{versao}"


def fmt_percentual(valor):
    return "—" if valor is None else f"{valor:.2f}%".replace(".", ",")


def fmt_numero_br(valor, casas):
    return f"{valor:,.{casas}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def validar_estado_select(chave, opcoes_validas, padrao=None):
    """Evita estado inválido quando uma fatura troca as opções em cascata."""
    chave = chave_param(chave)
    if st.session_state.get(chave) is None:
        st.session_state.pop(chave, None)
        return
    if chave in st.session_state and st.session_state[chave] not in opcoes_validas:
        st.session_state[chave] = padrao if padrao in opcoes_validas else (opcoes_validas[0] if opcoes_validas else None)


def validar_estado_historico(chave, opcoes_validas, padrao=None):
    """Evita que a aba 3 mantenha seleção de uma consulta anterior."""
    if chave in st.session_state and st.session_state[chave] not in opcoes_validas:
        st.session_state[chave] = padrao if padrao in opcoes_validas else (opcoes_validas[0] if opcoes_validas else None)


def carregar_documento_tabular(arquivo):
    if arquivo.name.lower().endswith(".csv"):
        texto = arquivo.getvalue().decode("utf-8-sig")
        candidatos = [pd.read_csv(StringIO(texto), sep=separador) for separador in (";", ",", "\t")]
        df = next((c for c in candidatos if "posto" in {str(col).strip().lower() for col in c.columns}), candidatos[0])
    else:
        df = pd.read_excel(arquivo)
    normalizadas = {str(c).strip().lower(): c for c in df.columns}
    if "posto" not in normalizadas or not ({"consumo_mwh", "demanda_kw"} & set(normalizadas)):
        raise ValueError("CSV/XLSX deve conter 'posto' e ao menos uma coluna entre 'consumo_mwh' e 'demanda_kw'.")

    def primeiro(campo):
        if campo not in normalizadas:
            return None
        valores = df[normalizadas[campo]].dropna()
        return str(valores.iloc[0]).strip() if not valores.empty else None

    def posto_padrao(valor):
        normal = str(valor).strip().lower()
        if normal in {"hfp", "fora ponta", "fora de ponta"}:
            return "Fora ponta"
        if normal in {"hp", "hpt", "ponta"}:
            return "Ponta"
        return str(valor).strip()

    def numero(valor):
        convertido = converter_valor_brl(valor) if isinstance(valor, str) else float(valor)
        if convertido is None:
            raise ValueError(f"Valor numérico inválido: {valor}")
        return float(convertido)

    itens = []
    for _, linha in df.iterrows():
        posto = posto_padrao(linha[normalizadas["posto"]])
        if "consumo_mwh" in normalizadas and pd.notna(linha[normalizadas["consumo_mwh"]]):
            quantidade = numero(linha[normalizadas["consumo_mwh"]]) * 1000
            itens.append({"tipo": "Energia", "posto": posto, "unidade": "kWh", "quantidade": quantidade,
                          "consumo_mwh": quantidade / 1000, "valor_com_tributos": None, "pis_cofins": None,
                          "icms": None, "tarifa_liquida": None, "aliquota_icms": None})
        if "demanda_kw" in normalizadas and pd.notna(linha[normalizadas["demanda_kw"]]):
            quantidade = numero(linha[normalizadas["demanda_kw"]])
            itens.append({"tipo": "Demanda", "posto": posto, "unidade": "kW", "quantidade": quantidade,
                          "consumo_mwh": None, "valor_com_tributos": None, "pis_cofins": None,
                          "icms": None, "tarifa_liquida": None, "aliquota_icms": None})
    if not itens:
        raise ValueError("O arquivo não contém valores numéricos válidos de consumo ou demanda.")
    return {
        "origem": "tabular", "metodo": "arquivo tabular", "itens": itens, "avisos": [],
        "distribuidora": primeiro("distribuidora"), "competencia": primeiro("competencia"),
        "subgrupo": primeiro("subgrupo"), "modalidade": primeiro("modalidade"),
        "classe": primeiro("classe"), "subclasse": primeiro("subclasse"),
        "pis_percentual": None, "cofins_percentual": None, "icms_percentual": None,
    }


def montar_sincronizacao(documento, identificador):
    competencia = documento.get("competencia")
    ano_doc, mes_doc = (competencia.split("-") if competencia and "-" in competencia else (None, None))
    subgrupo = documento.get("subgrupo")
    grandezas = grandezas_da_fatura(documento)
    # Na modalidade Verde, a Light apresenta a demanda como HFP/Único,
    # enquanto a base tarifária da ANEEL usa o posto "Não se aplica".
    if documento.get("modalidade") == "Verde" and "Fora ponta" in grandezas["demandas_kw"]:
        grandezas["demandas_kw"]["Não se aplica"] = grandezas["demandas_kw"]["Fora ponta"]
    distribuidora_documento = documento.get("distribuidora") or (
        "LIGHT SESA" if documento.get("origem") == "fatura" else st.session_state.get(chave_param("consulta_distribuidora"))
    )
    return {
        "id": identificador,
        "widgets": {
            "consulta_distribuidora": distribuidora_documento,
            "consulta_ano": int(ano_doc) if ano_doc else st.session_state.get(chave_param("consulta_ano")),
            "consulta_mes": dict(MESES).get(int(mes_doc)) if mes_doc else st.session_state.get(chave_param("consulta_mes")),
            "consulta_data_ref": None,
            "consulta_subgrupo": subgrupo or st.session_state.get(chave_param("consulta_subgrupo"), "Todos"),
            "consulta_modalidade": documento.get("modalidade") or st.session_state.get(chave_param("consulta_modalidade"), "Todas"),
            "consulta_base": "Tarifa de Aplicação", "consulta_reh": "Todas",
            "consulta_classe": documento.get("classe") or "Todas",
            "consulta_subclasse": documento.get("subclasse") or "Todas",
            "consulta_detalhe": "Não se aplica", "consulta_acessante": "Todos", "consulta_posto": "Todos",
        },
        "grandezas": grandezas,
        "resumo": (
            f"Documento válido {competencia or 'sem competência'}: {distribuidora_documento or 'distribuidora não informada'}, "
            f"Grupo {(subgrupo or '—')[:1]} / Subgrupo {subgrupo or 'não informado'}, "
            f"modalidade {documento.get('modalidade') or 'não informada'}. "
            "Dados documentais prevalecem; campos ausentes permanecem para preenchimento manual."
        ),
    }


@st.cache_data(show_spinner="Lendo fatura e executando OCR local...")
def extrair_fatura_cache(conteudo, nome):
    return {**extrair_fatura(conteudo, nome), "origem": "fatura"}


# Descarte precisa ocorrer antes da recriação do file_uploader; caso contrário,
# o frontend restaura o arquivo e ele é processado novamente no mesmo rerun.
if st.session_state.pop("descartar_documento_pendente", False):
    for chave in ("arquivo_parametrizacao", "documento_ativo", "fatura_sync_id", "fatura_sync_resumo",
                  "fatura_grandezas_aplicadas", "consulta_registros", "consulta_brutos", "consulta_contexto",
                  "consulta_filtros_historico"):
        st.session_state.pop(chave, None)
    for chave in [k for k in st.session_state if k.startswith("consulta_")]:
        st.session_state.pop(chave, None)
    st.session_state["perfil_widget_versao"] = "manual"
    st.session_state["param_widget_versao"] = f"manual_{st.session_state.get('manual_widget_ciclo', 0) + 1}"
    st.session_state["manual_widget_ciclo"] = st.session_state.get("manual_widget_ciclo", 0) + 1


# A sincronização é aplicada antes de os widgets serem instanciados. Isso é
# necessário porque o Streamlit não permite alterar o estado de um widget já
# renderizado no mesmo ciclo em que a fatura foi processada na segunda aba.
if "fatura_sync_pendente" in st.session_state:
    sincronizacao = st.session_state.pop("fatura_sync_pendente")
    st.session_state["perfil_widget_versao"] = sincronizacao["id"][:12]
    st.session_state["param_widget_versao"] = sincronizacao["id"][:12]
    for chave, valor in sincronizacao["widgets"].items():
        st.session_state[chave_param(chave)] = valor
    for posto, valor in sincronizacao["grandezas"]["consumos_mwh"].items():
        st.session_state[chave_input("consumo", posto)] = valor
    for posto, valor in sincronizacao["grandezas"]["demandas_kw"].items():
        st.session_state[chave_input("demanda", posto)] = valor
    st.session_state["modo_calculo"] = "Consumo por posto"
    essenciais = sincronizacao["widgets"]
    st.session_state["consulta_auto_executar"] = all([
        essenciais.get("consulta_distribuidora"), essenciais.get("consulta_ano"),
        essenciais.get("consulta_subgrupo") not in (None, "Todos"),
        essenciais.get("consulta_modalidade") not in (None, "Todas"),
    ])
    st.session_state["fatura_sync_id"] = sincronizacao["id"]
    st.session_state["fatura_sync_resumo"] = sincronizacao["resumo"]
    st.session_state["fatura_grandezas_aplicadas"] = sincronizacao["grandezas"]
    st.session_state["fatura_sync_aplicando"] = True
    st.session_state.pop("sim_composicoes", None)


aba_consulta, aba_simulacao, aba_historico = st.tabs(["1. Consulta", "2. Simulação e comparação", "3. Histórico"])

with aba_consulta:
    st.subheader("Origem dos dados")
    st.caption("Envie uma conta ou planilha para parametrização automática. Sem documento válido, preencha manualmente os campos obrigatórios abaixo.")
    arquivo_parametros = st.file_uploader(
        "Conta de energia ou arquivo de parâmetros",
        type=["pdf", "png", "jpg", "jpeg", "webp", "csv", "xlsx"],
        help=("PDF/imagem: fatura Light Grupo A. CSV/XLSX: posto e consumo_mwh e/ou demanda_kw; "
              "opcionalmente distribuidora, competencia, subgrupo, modalidade, classe e subclasse."),
        key="arquivo_parametrizacao",
    )
    if arquivo_parametros is not None:
        conteudo_parametros = arquivo_parametros.getvalue()
        id_documento = hashlib.sha256(conteudo_parametros).hexdigest() + ":v15"
        if st.session_state.get("fatura_sync_id") != id_documento:
            try:
                extensao = arquivo_parametros.name.lower().rsplit(".", 1)[-1]
                if extensao in {"csv", "xlsx"}:
                    documento = carregar_documento_tabular(arquivo_parametros)
                else:
                    documento = extrair_fatura_cache(conteudo_parametros, arquivo_parametros.name)
                grandezas_validadas = grandezas_da_fatura(documento)
                if documento.get("origem") == "fatura":
                    ausentes = grandezas_ausentes(documento)
                    if ausentes:
                        raise ValueError("grandezas obrigatórias não reconhecidas: " + ", ".join(ausentes))
                st.session_state["documento_ativo"] = documento
                st.session_state["fatura_sync_pendente"] = montar_sincronizacao(documento, id_documento)
                st.rerun()
            except Exception as erro:
                st.session_state.pop("documento_ativo", None)
                st.error(f"Documento inválido ou não reconhecido: {erro}. Preencha os parâmetros manualmente.")

    documento_ativo = st.session_state.get("documento_ativo")
    if documento_ativo:
        st.success(f"Documento validado por {documento_ativo['metodo']}. Parâmetros e grandezas disponíveis foram aplicados.")
        grandezas_doc = grandezas_da_fatura(documento_ativo)
        st.info(
            "Perfil documental: "
            f"Consumo HFP {fmt_numero_br(grandezas_doc['consumos_mwh'].get('Fora ponta', 0), 3)} MWh · "
            f"Consumo HPT {fmt_numero_br(grandezas_doc['consumos_mwh'].get('Ponta', 0), 3)} MWh · "
            f"Demanda HFP {fmt_numero_br(grandezas_doc['demandas_kw'].get('Fora ponta', 0), 0)} kW · "
            f"Demanda HPT {fmt_numero_br(grandezas_doc['demandas_kw'].get('Ponta', 0), 0)} kW"
        )
        if st.button("Descartar documento e voltar ao preenchimento manual", type="secondary"):
            st.session_state["descartar_documento_pendente"] = True
            st.rerun()

    st.divider()
    st.subheader("Parâmetros da consulta")
    st.caption("Selecione a referência principal. Filtros técnicos menos frequentes ficam em Consulta avançada.")
    c1, c2, c3, c4 = st.columns([2, 1, 1, 1])
    opcoes_distribuidora = distribuidoras()
    distribuidora_sincronizada = st.session_state.get(chave_param("consulta_distribuidora"))
    if distribuidora_sincronizada not in opcoes_distribuidora and distribuidora_sincronizada:
        correspondencia = next(
            (opcao for opcao in opcoes_distribuidora if "light" in opcao.lower() and "light" in distribuidora_sincronizada.lower()),
            None,
        )
        if correspondencia:
            st.session_state[chave_param("consulta_distribuidora")] = correspondencia
    validar_estado_select("consulta_distribuidora", opcoes_distribuidora)
    distribuidora = c1.selectbox("Distribuidora", opcoes_distribuidora, index=None, placeholder="Digite para buscar...", key=chave_param("consulta_distribuidora"))
    brutos = dados_distribuidora(distribuidora) if distribuidora else []
    anos = sorted({ano_da_vigencia(r) for r in brutos if ano_da_vigencia(r)}, reverse=True)
    validar_estado_select("consulta_ano", anos, anos[0] if anos else None)
    ano = c2.selectbox("Ano", anos, index=0 if anos else None, disabled=not anos, key=chave_param("consulta_ano"))
    meses_nomes = [nome for _, nome in MESES]
    validar_estado_select("consulta_mes", meses_nomes, meses_nomes[date.today().month - 1])
    mes_nome = c3.selectbox("Mês", meses_nomes, index=date.today().month - 1, disabled=not anos, key=chave_param("consulta_mes"))
    data_exata = c4.date_input("Data de referência", value=None, help="Se preenchida, prevalece sobre Ano/Mês.", key=chave_param("consulta_data_ref"))

    periodo = brutos
    if brutos and data_exata:
        periodo = registros_vigentes_no_periodo(brutos, data_exata, data_exata)
    elif brutos and ano:
        mes = dict((nome, numero) for numero, nome in MESES)[mes_nome]
        inicio, fim = periodo_do_mes(int(ano), mes)
        periodo = registros_vigentes_no_periodo(brutos, inicio, fim)

    c5, c6 = st.columns(2)
    opcoes_subgrupo = ["Todos"] + opcoes(periodo, "DscSubGrupo")
    validar_estado_select("consulta_subgrupo", opcoes_subgrupo, "Todos")
    subgrupo = c5.selectbox("Subgrupo", opcoes_subgrupo, disabled=not periodo, key=chave_param("consulta_subgrupo"))
    por_subgrupo = filtrar(periodo, "DscSubGrupo", subgrupo, "Todos")
    opcoes_modalidade = ["Todas"] + opcoes(por_subgrupo, "DscModalidadeTarifaria")
    validar_estado_select("consulta_modalidade", opcoes_modalidade, "Todas")
    modalidade = c6.selectbox("Modalidade", opcoes_modalidade, disabled=not por_subgrupo, key=chave_param("consulta_modalidade"))
    filtrados = filtrar(por_subgrupo, "DscModalidadeTarifaria", modalidade, "Todas")

    with st.expander("Consulta avançada"):
        a1, a2, a3, a4 = st.columns(4)
        bases_disponiveis = opcoes(filtrados, "DscBaseTarifaria")
        bases_ordenadas = (["Tarifa de Aplicação"] if "Tarifa de Aplicação" in bases_disponiveis else []) + [v for v in bases_disponiveis if v != "Tarifa de Aplicação"]
        validar_estado_select("consulta_base", bases_ordenadas, "Tarifa de Aplicação")
        base = a1.selectbox("Base tarifária", bases_ordenadas, index=0 if bases_ordenadas else None, disabled=not bases_ordenadas, key=chave_param("consulta_base"))
        filtrados = filtrar(filtrados, "DscBaseTarifaria", base, "Todas")
        rehs_disponiveis = opcoes(filtrados, "DscREH")
        opcoes_reh = ["Todas"] + rehs_disponiveis
        if st.session_state.get("fatura_sync_aplicando") and len(rehs_disponiveis) == 1:
            st.session_state[chave_param("consulta_reh")] = rehs_disponiveis[0]
        validar_estado_select("consulta_reh", opcoes_reh, "Todas")
        reh = a2.selectbox("REH", opcoes_reh, disabled=not filtrados, key=chave_param("consulta_reh"))
        filtrados = filtrar(filtrados, "DscREH", reh, "Todas")
        opcoes_classe = ["Todas"] + opcoes(filtrados, "DscClasse")
        validar_estado_select("consulta_classe", opcoes_classe, "Todas")
        classe = a3.selectbox("Classe", opcoes_classe, disabled=not filtrados, key=chave_param("consulta_classe"))
        filtrados = filtrar(filtrados, "DscClasse", classe, "Todas")
        opcoes_subclasse = ["Todas"] + opcoes(filtrados, "DscSubClasse")
        validar_estado_select("consulta_subclasse", opcoes_subclasse, "Todas")
        subclasse = a4.selectbox("Subclasse", opcoes_subclasse, disabled=not filtrados, key=chave_param("consulta_subclasse"))
        filtrados = filtrar(filtrados, "DscSubClasse", subclasse, "Todas")
        a5, a6, a7 = st.columns(3)
        detalhes_disponiveis = opcoes(filtrados, "DscDetalhe")
        if documento_ativo:
            detalhe = "Não se aplica"
            st.session_state[chave_param("consulta_detalhe")] = detalhe
            a5.selectbox(
                "Detalhe documental",
                [detalhe], disabled=True, key=chave_param("consulta_detalhe"),
                help="Com documento válido, o detalhe é fixado automaticamente em 'Não se aplica'.",
            )
        else:
            validar_estado_select("consulta_detalhe", detalhes_disponiveis)
            detalhe = a5.selectbox(
                "Detalhe tarifário (obrigatório)", detalhes_disponiveis, index=None,
                placeholder="Selecione o detalhe", disabled=not detalhes_disponiveis,
                key=chave_param("consulta_detalhe"),
                help="Na entrada manual, selecione explicitamente Não se aplica, APE, SCEE ou outra opção disponível.",
            )
        if detalhe and detalhe in detalhes_disponiveis:
            filtrados = filtrar(filtrados, "DscDetalhe", detalhe, "Todas")
        else:
            filtrados = []
            if documento_ativo:
                a5.caption("Sem registro 'Não se aplica' para a combinação selecionada.")
        opcoes_acessante = ["Todos"] + opcoes(filtrados, "SigAgenteAcessante")
        validar_estado_select("consulta_acessante", opcoes_acessante, "Todos")
        acessante = a6.selectbox("Acessante", opcoes_acessante, disabled=not filtrados, key=chave_param("consulta_acessante"))
        filtrados = filtrar(filtrados, "SigAgenteAcessante", acessante, "Todos")
        opcoes_posto = ["Todos"] + opcoes(filtrados, "NomPostoTarifario")
        validar_estado_select("consulta_posto", opcoes_posto, "Todos")
        posto = a7.selectbox("Posto", opcoes_posto, disabled=not filtrados, key=chave_param("consulta_posto"))
        filtrados = filtrar(filtrados, "NomPostoTarifario", posto, "Todos")

    parametros = {"Distribuidora": distribuidora, "Referência": str(data_exata or f"{mes_nome}/{ano}"), "Subgrupo": subgrupo, "Modalidade": modalidade, "Base": base if periodo else None, "REH": reh if periodo else None, "Classe": classe if periodo else None, "Subclasse": subclasse if periodo else None, "Detalhe": detalhe if periodo else None, "Acessante": acessante if periodo else None, "Posto": posto if periodo else None}
    parametros_historico = {
        "SigAgente": distribuidora, "DscSubGrupo": subgrupo,
        "DscModalidadeTarifaria": modalidade, "DscBaseTarifaria": base,
        "DscClasse": classe, "DscSubClasse": subclasse, "DscDetalhe": detalhe,
        "SigAgenteAcessante": acessante, "NomPostoTarifario": posto,
    }
    parametros_obrigatorios = bool(distribuidora and ano and mes_nome and subgrupo not in (None, "Todos") and modalidade not in (None, "Todas") and base and detalhe and filtrados)
    consulta_manual = st.button("Consultar tarifas", type="primary", disabled=not parametros_obrigatorios)
    consulta_automatica = st.session_state.pop("consulta_auto_executar", False)
    if consulta_manual or consulta_automatica:
        st.session_state["consulta_registros"] = filtrados
        st.session_state["consulta_brutos"] = brutos
        st.session_state["consulta_contexto"] = contexto_consulta(parametros)
        st.session_state["consulta_filtros_historico"] = filtros_da_familia(parametros_historico)
        for chave in ("sim_resultados", "sim_memoria", "sim_fingerprint"):
            st.session_state.pop(chave, None)
        if consulta_automatica:
            st.session_state["sim_reset_composicoes"] = True
            st.session_state.pop("fatura_sync_aplicando", None)
            if reh not in (None, "Todas"):
                st.session_state["fatura_sync_resumo"] += f" REH aplicada automaticamente: {reh}."
            st.toast("Aba 1 atualizada automaticamente com os dados da fatura.", icon="✅")
        else:
            st.session_state.pop("fatura_sync_aplicando", None)

    if st.session_state.get("fatura_sync_resumo"):
        st.info(st.session_state["fatura_sync_resumo"])

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
        st.info("Informe obrigatoriamente Ano, Mês, Subgrupo, Modalidade e Detalhe tarifário; depois clique em Consultar tarifas.")
    else:
        st.info("Sem documento válido, comece selecionando uma distribuidora e preencha os demais parâmetros obrigatórios.")

with aba_simulacao:
    consulta = st.session_state.get("consulta_registros", [])
    contexto = st.session_state.get("consulta_contexto", "Consulta não identificada")
    if not consulta:
        st.info("Faça uma consulta na primeira aba para habilitar a simulação.")
    else:
        versoes = versoes_disponiveis(consulta)
        rotulos = {rotulo_versao(v): v for v in versoes}
        st.subheader("Composição tarifária")
        opcoes_composicao = list(rotulos)
        if st.session_state.pop("sim_reset_composicoes", False):
            st.session_state["sim_composicoes"] = opcoes_composicao[:1]
        elif "sim_composicoes" in st.session_state:
            st.session_state["sim_composicoes"] = [v for v in st.session_state["sim_composicoes"] if v in opcoes_composicao][:2]
        escolhas = st.multiselect("Composições para simular e comparar", opcoes_composicao, default=opcoes_composicao[:1], max_selections=2, key="sim_composicoes")
        st.caption("Selecione uma composição para simular ou duas para comparar com o mesmo perfil.")
        if escolhas:
            principal = rotulos[escolhas[0]]
            tarifas_mwh = valores_por_posto(consulta, principal, "MWh")
            tarifas_kw = valores_por_posto(consulta, principal, "kW")
            postos_energia = list(tarifas_mwh)
            postos_demanda = list(tarifas_kw)
            linhas_tarifas = []
            for posto_nome, (tusd, te) in tarifas_mwh.items():
                linhas_tarifas.append({"Posto": posto_nome, "TUSD Energia (R$/MWh)": tusd, "TE (R$/MWh)": te, "TUSD Demanda (R$/kW)": tarifas_kw.get(posto_nome, (None, None))[0]})
            for posto_nome, (tusd, _) in tarifas_kw.items():
                if posto_nome not in tarifas_mwh:
                    linhas_tarifas.append({"Posto": posto_nome, "TUSD Energia (R$/MWh)": None, "TE (R$/MWh)": None, "TUSD Demanda (R$/kW)": tusd})
            with st.expander("Tarifas da composição selecionada", expanded=True):
                st.dataframe(pd.DataFrame(linhas_tarifas), hide_index=True, width="stretch")
            indicadores = tarifas_indicativas_ponderadas(tarifas_mwh, tarifas_kw)
            st.markdown('<div class="section-kicker">Indicadores para comparação ACL × ACR</div>', unsafe_allow_html=True)
            i1, i2, i3 = st.columns(3)
            i1.metric("TE ponderada (R$/MWh)", fmt_brl(indicadores["te_ponderada"]) if indicadores["te_ponderada"] is not None else "—")
            i2.metric("TUSD Energia ponderada (R$/MWh)", fmt_brl(indicadores["tusd_energia_ponderada"]) if indicadores["tusd_energia_ponderada"] is not None else "—")
            i3.metric("TUSD Demanda ponderada (R$/kW)", fmt_brl(indicadores["tusd_demanda_ponderada"]) if indicadores["tusd_demanda_ponderada"] is not None else "—")
            pesos_txt = ", ".join(f"{posto}: {horas:.0f} h" for posto, horas in indicadores["pesos_energia"].items())
            st.caption(
                f"Indicadores horários de um mês típico ({pesos_txt or 'sem postos ponderáveis'}; total de 720 h). "
                "São referências para comparação inicial entre a TE regulada no ACR e ofertas de TE no ACL. "
                "Não representam curva de carga, não alteram os cálculos abaixo e a ponderação da TUSD Demanda não constitui critério de faturamento."
            )
            st.markdown('<div class="section-kicker">Dados documentais recebidos da Aba 1</div>', unsafe_allow_html=True)
            fatura = st.session_state.get("documento_ativo")
            if fatura:
                st.success(f"Fatura processada por {fatura['metodo']}. Os parâmetros e as grandezas reconhecidas já foram aplicados automaticamente.")
                grandezas_aplicadas = st.session_state.get("fatura_grandezas_aplicadas", grandezas_da_fatura(fatura))
                st.info(
                    "Campos preenchidos: "
                    f"Consumo HFP {fmt_numero_br(grandezas_aplicadas['consumos_mwh'].get('Fora ponta', 0), 3)} MWh · "
                    f"Consumo HPT {fmt_numero_br(grandezas_aplicadas['consumos_mwh'].get('Ponta', 0), 3)} MWh · "
                    f"Demanda HFP {fmt_numero_br(grandezas_aplicadas['demandas_kw'].get('Fora ponta', 0), 0)} kW · "
                    f"Demanda HPT {fmt_numero_br(grandezas_aplicadas['demandas_kw'].get('Ponta', 0), 0)} kW"
                )
                tributos = totais_tributos(fatura)
                meta1, meta2, meta3 = st.columns(3)
                meta1.metric("Competência", fatura.get("competencia") or "—")
                meta2.metric("Enquadramento", f"{fatura.get('subgrupo') or '—'} · {fatura.get('modalidade') or '—'}")
                meta3.metric("Alíquota ICMS", fmt_percentual(fatura.get("icms_percentual")))
                trib1, trib2 = st.columns(2)
                trib1.metric("PIS/COFINS retirado", fmt_brl(tributos["pis_cofins"]))
                trib2.metric("ICMS retirado", fmt_brl(tributos["icms"]))
                st.caption(
                    f"PIS identificado: {fmt_percentual(fatura.get('pis_percentual'))} · "
                    f"COFINS identificado: {fmt_percentual(fatura.get('cofins_percentual'))} · "
                    f"Classe identificada: {fatura.get('classe') or '—'} / {fatura.get('subclasse') or '—'}. "
                    "Processamento local: o arquivo não é enviado a serviços externos."
                )
                if fatura.get("subgrupo") and fatura["subgrupo"] != principal[2]:
                    st.warning(f"A fatura indica {fatura['subgrupo']}, mas a composição selecionada é {principal[2]}. Selecione a composição correspondente antes de reconciliar TE/TUSD.")
                if fatura.get("modalidade") and fatura["modalidade"] != principal[3]:
                    st.warning(f"A fatura indica modalidade {fatura['modalidade']}, mas a composição selecionada é {principal[3]}.")
                if fatura.get("competencia"):
                    competencia_data = datetime.strptime(fatura["competencia"] + "-01", "%Y-%m-%d").date()
                    inicio_versao = datetime.strptime(principal[7], "%Y-%m-%d").date() if principal[7] else None
                    fim_versao = datetime.strptime(principal[8], "%Y-%m-%d").date() if principal[8] else None
                    if (inicio_versao and competencia_data < inicio_versao) or (fim_versao and competencia_data > fim_versao):
                        st.warning(
                            f"A competência da fatura é {fatura['competencia']}, fora da vigência da composição selecionada "
                            f"({principal[7]} a {principal[8] or 'aberta'}). Volte à aba Consulta e selecione o mês da fatura."
                        )
                for aviso in fatura.get("avisos", []):
                    st.warning(aviso)
                reconciliados = reconciliar_com_aneel(fatura, tarifas_mwh, tarifas_kw)
                revisao_df = pd.DataFrame([{
                    "Tipo": r["tipo"], "Posto": r["posto"], "Quantidade": r["quantidade"], "Unidade": r["unidade"],
                    "Consumo (MWh)": r["consumo_mwh"], "Valor com tributos (R$)": r["valor_com_tributos"],
                    "PIS/COFINS retirado (R$)": r["pis_cofins"], "ICMS retirado (R$)": r["icms"],
                    "Tarifa líquida fatura": r["tarifa_liquida_comparavel"], "TUSD ANEEL": r["tusd_aneel"],
                    "TE ANEEL": r["te_aneel"], "TE + TUSD ANEEL": r["soma_aneel"], "Diferença": r["diferenca_tarifa"],
                } for r in reconciliados])
                revisao_editada = st.data_editor(
                    revisao_df, hide_index=True, width="stretch", key="revisao_fatura",
                    disabled=[c for c in revisao_df.columns if c not in {"Posto", "Quantidade"}],
                )
                if any(abs(v) > 1 for v in revisao_df["Diferença"].dropna()):
                    st.warning("A tarifa líquida da fatura não reconciliou com TE + TUSD da composição selecionada. Confirme competência, subgrupo, modalidade, classe/detalhe e base tarifária.")
                with st.expander("Como os impostos e TE/TUSD foram tratados"):
                    st.write(
                        "Por item, a tarifa líquida é lida da coluna 'Tarifa Unit.' ou reconstruída por "
                        "(Valor com tributos - PIS/COFINS - ICMS) / Quantidade. Para energia, R$/kWh é convertido "
                        "para R$/MWh. A separação entre TE e TUSD usa a composição ANEEL selecionada e é exibida "
                        "ao lado da tarifa líquida da fatura para reconciliação."
                    )
                if st.button("Reaplicar correções da tabela à simulação", type="secondary"):
                    for _, linha in revisao_editada.iterrows():
                        if pd.isna(linha["Quantidade"]):
                            continue
                        if linha["Tipo"] == "Energia":
                            st.session_state[chave_input("consumo", linha["Posto"])] = float(linha["Quantidade"]) / 1000
                        else:
                            st.session_state[chave_input("demanda", linha["Posto"])] = float(linha["Quantidade"])
                    st.session_state["modo_calculo"] = "Consumo por posto"
                    st.rerun()

            modo = st.radio("Forma de cálculo", ["Consumo por posto", "Consumo total estimado"], horizontal=True, key="modo_calculo")

            consumos = {}
            demandas = {}
            consumo_total = None
            if modo == "Consumo por posto":
                colunas = st.columns(max(1, len(postos_energia)))
                for i, posto_nome in enumerate(postos_energia):
                    consumos[posto_nome] = colunas[i].number_input(
                        f"Consumo {posto_nome} (MWh)", min_value=0.0,
                        value=0.0, step=0.1,
                        key=chave_input("consumo", posto_nome),
                    )
            else:
                consumo_total = st.number_input("Consumo mensal total (MWh)", min_value=0.0, step=0.1)
                st.caption("Distribuição padrão: 66 horas de ponta, 44 horas intermediárias quando existentes e horas restantes fora de ponta.")
            if postos_demanda:
                cols_demanda = st.columns(len(postos_demanda))
                for i, posto_nome in enumerate(postos_demanda):
                    rotulo_demanda = "Demanda única / HFP" if modalidade == "Verde" and posto_nome == "Não se aplica" else f"Demanda {posto_nome}"
                    demandas[posto_nome] = cols_demanda[i].number_input(
                        f"{rotulo_demanda} (kW)", min_value=0.0, step=1.0,
                        key=chave_input("demanda", posto_nome),
                    )

            fingerprint_atual = fingerprint_simulacao({
                "escolhas": escolhas, "modo": modo, "consumos": consumos,
                "consumo_total": consumo_total, "demandas": demandas,
                "consulta": st.session_state.get("consulta_contexto", ""),
            })

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
                        resultados.append({
                            "Composição": escolha,
                            "TE (R$)": calculo["energia"]["te"],
                            "TUSD Energia (R$)": calculo["energia"]["tusd_energia"],
                            "TUSD Demanda (R$)": calculo["demanda"]["total"],
                            "Energia total (R$)": calculo["energia"]["total"],
                            "Total (R$)": calculo["total"],
                        })
                        for linha in calculo["linhas"]:
                            memorias.append({"Composição": escolha, **linha})
                    st.session_state["sim_resultados"] = pd.DataFrame(resultados)
                    st.session_state["sim_memoria"] = pd.DataFrame(memorias)
                    st.session_state["sim_fingerprint"] = fingerprint_atual
                except ValueError as erro:
                    st.error(f"Cálculo não realizado: {erro}")

            resultados_df = st.session_state.get("sim_resultados", pd.DataFrame())
            memoria_df = st.session_state.get("sim_memoria", pd.DataFrame())
            resultado_atual = st.session_state.get("sim_fingerprint") == fingerprint_atual
            if not resultados_df.empty and not resultado_atual:
                st.markdown('<div class="stale-box"><b>Parâmetros alterados.</b> O resultado anterior foi ocultado. Clique em <b>Calcular estimativa</b> para atualizar.</div>', unsafe_allow_html=True)
            if not resultados_df.empty and resultado_atual:
                principal_resultado = resultados_df.iloc[0]
                st.markdown('<div class="section-kicker">Resultado da composição principal</div>', unsafe_allow_html=True)
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("TE", fmt_brl(principal_resultado["TE (R$)"]))
                m2.metric("TUSD Energia", fmt_brl(principal_resultado["TUSD Energia (R$)"]))
                m3.metric("TUSD Demanda", fmt_brl(principal_resultado["TUSD Demanda (R$)"]))
                m4.metric("Energia TE + TUSD", fmt_brl(principal_resultado["Energia total (R$)"]))
                st.markdown(f'<div class="total-card">Total geral estimado<strong>{fmt_brl(principal_resultado["Total (R$)"])}</strong></div>', unsafe_allow_html=True)
                st.markdown('<div class="section-kicker">Simulação ACR × ACL</div>', unsafe_allow_html=True)
                acl_col1, acl_col2 = st.columns([3, 1])
                te_acl_informada = acl_col1.number_input(
                    "Tarifa de Energia no ACL (R$/MWh)", min_value=0.0, step=1.0,
                    help=("Informe somente a TE negociada no ACL. A TUSD Energia e a TUSD Demanda "
                          "permanecem iguais às do cenário ACR calculado acima."),
                    key="te_acl_informada",
                )
                simular_acl = acl_col2.button("Simular ACR vs ACL", type="primary", width="stretch")
                consumo_calculado = float(
                    memoria_df.loc[memoria_df["componente"] == "TE", "quantidade"].sum()
                )
                comparacao_chave = (fingerprint_atual, float(te_acl_informada))
                if simular_acl:
                    try:
                        st.session_state["comparacao_acl"] = comparar_acr_acl(
                            principal_resultado["TE (R$)"], principal_resultado["TUSD Energia (R$)"],
                            principal_resultado["TUSD Demanda (R$)"], consumo_calculado, te_acl_informada,
                        )
                        st.session_state["comparacao_acl_chave"] = comparacao_chave
                    except ValueError as erro:
                        st.error(f"Comparação não realizada: {erro}")
                comparacao = st.session_state.get("comparacao_acl")
                if comparacao and st.session_state.get("comparacao_acl_chave") == comparacao_chave:
                    a1, a2, a3, a4 = st.columns(4)
                    a1.metric("Total ACR", fmt_brl(comparacao["total_acr"]))
                    a2.metric("Total ACL", fmt_brl(comparacao["total_acl"]))
                    a3.metric(
                        "Economia estimada", fmt_brl(comparacao["economia"]),
                        delta=(f'{comparacao["economia_percentual"]:.2f}%'.replace(".", ",")
                               if comparacao["economia_percentual"] is not None else None),
                    )
                    a4.metric(
                        "TE ACR efetiva",
                        (f'{fmt_numero_br(comparacao["te_acr_efetiva"], 2)} R$/MWh'
                         if comparacao["te_acr_efetiva"] is not None else "—"),
                    )
                    st.dataframe(pd.DataFrame([
                        {"Ambiente": "ACR", "TE (R$)": comparacao["custo_te_acr"], "TUSD Energia (R$)": comparacao["tusd_energia"], "TUSD Demanda (R$)": comparacao["tusd_demanda"], "Total (R$)": comparacao["total_acr"]},
                        {"Ambiente": "ACL", "TE (R$)": comparacao["custo_te_acl"], "TUSD Energia (R$)": comparacao["tusd_energia"], "TUSD Demanda (R$)": comparacao["tusd_demanda"], "Total (R$)": comparacao["total_acl"]},
                    ]), hide_index=True, width="stretch")
                    st.caption(
                        f'Memória: TE ACL = {fmt_numero_br(comparacao["te_acl"], 2)} R$/MWh × '
                        f'{fmt_numero_br(comparacao["consumo_total_mwh"], 3)} MWh. '
                        "Premissa: somente a TE varia entre os ambientes; TUSD Energia e TUSD Demanda são mantidas constantes."
                    )
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
        filtros_historico = st.session_state.get("consulta_filtros_historico", {})
        familia = ordenar_registros_historicos(registros_historicos(brutos, filtros_historico))
        st.subheader("Evolução das tarifas homologadas")
        if filtros_historico:
            rastreio = " · ".join(f"{COLUNAS.get(campo, campo)}: {valor}" for campo, valor in filtros_historico.items())
            st.caption(f"Família tarifária preservada da Aba 1: {rastreio}. REH e vigência permanecem livres para formar a série.")
        if not familia:
            st.warning("Não há histórico para a família tarifária consultada. Revise os filtros técnicos da Aba 1.")
        else:
            unidades_historicas = opcoes(familia, "DscUnidadeTerciaria")
            validar_estado_historico("hist_unidade", unidades_historicas)
            h1, h2, h3 = st.columns(3)
            unidade = h1.selectbox("Unidade", unidades_historicas, key="hist_unidade")
            por_unidade = filtrar(familia, "DscUnidadeTerciaria", unidade, "Todas")
            postos_historicos = opcoes(por_unidade, "NomPostoTarifario")
            validar_estado_historico("hist_posto", postos_historicos)
            posto_historico = h2.selectbox("Posto tarifário", postos_historicos, key="hist_posto")
            base_hist = filtrar(por_unidade, "NomPostoTarifario", posto_historico, "Todos")
            hist = pd.DataFrame(base_hist)
            hist["Início da vigência"] = pd.to_datetime(hist["DatInicioVigencia"], errors="coerce")
            hist["Fim da vigência"] = pd.to_datetime(hist["DatFimVigencia"], errors="coerce")
            hist["TUSD"] = hist["VlrTUSD"].map(converter_valor_brl)
            hist["TE"] = hist["VlrTE"].map(converter_valor_brl)
            componentes = [c for c in ("TUSD", "TE") if hist[c].notna().any()]
            validar_estado_historico("hist_componente", componentes)
            componente = h3.selectbox("Componente", componentes, key="hist_componente")
            st.line_chart(hist, x="Início da vigência", y=componente, color="NomPostoTarifario", width="stretch")
            tabela_historica = hist[[
                "Início da vigência", "Fim da vigência", "DscREH", "DscBaseTarifaria",
                "DscSubGrupo", "DscModalidadeTarifaria", "DscClasse", "DscSubClasse",
                "DscDetalhe", "SigAgenteAcessante", "NomPostoTarifario",
                "DscUnidadeTerciaria", "TUSD", "TE",
            ]].rename(columns={
                "DscREH": "REH", "DscBaseTarifaria": "Base tarifária",
                "DscSubGrupo": "Subgrupo", "DscModalidadeTarifaria": "Modalidade",
                "DscClasse": "Classe", "DscSubClasse": "Subclasse", "DscDetalhe": "Detalhe",
                "SigAgenteAcessante": "Acessante", "NomPostoTarifario": "Posto",
                "DscUnidadeTerciaria": "Unidade",
            })
            st.dataframe(tabela_historica, hide_index=True, width="stretch")
            st.caption("Cada linha corresponde a uma observação publicada pela ANEEL. O histórico não realiza média nem consolidação entre REHs.")
st.caption("Fonte: API pública de Dados Abertos da ANEEL. A simulação é estimativa técnica e não substitui a fatura da distribuidora.")
