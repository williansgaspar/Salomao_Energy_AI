"""
REVISÃO 1 (congelada em 16/07/2026) — mantida só para referência histórica.
A versão em uso é ../app.py (Revisão 2 em diante). Ver ../REVISIONS.md.

Interface web para consulta de tarifas de distribuidoras de energia elétrica
homologadas pela ANEEL (API de Dados Abertos, pública, sem autenticação).

Rodar com (a partir desta pasta revisions/, copiando aneel_api.py para cá,
ou ajustando o import):
    streamlit run app_v1.py
"""

import io

import pandas as pd
import streamlit as st

from aneel_api import (
    ano_da_vigencia,
    converter_valor_brl,
    nova_sessao,
    registros_da_distribuidora,
    valores_distintos,
)

st.set_page_config(page_title="Tarifas ANEEL", page_icon="⚡", layout="wide")

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
    "VlrTUSD": "TUSD (R$)",
    "VlrTE": "TE (R$)",
    "EnergiaComposta": "Energia Composta TUSD+TE (R$/MWh)",
}


@st.cache_resource
def sessao():
    return nova_sessao()


@st.cache_data(ttl=7 * 24 * 3600, show_spinner=False)
def lista_distribuidoras():
    return valores_distintos(sessao(), "SigAgente")


@st.cache_data(ttl=24 * 3600, show_spinner="Buscando REH e anos disponíveis para a distribuidora...")
def registros_brutos_da_distribuidora(sig_agente):
    """Todos os registros de uma distribuidora (usados para popular Ano/REH e como base de filtro)."""
    return registros_da_distribuidora(sessao(), sig_agente)


def campo_distintos(registros, campo):
    return sorted({r[campo] for r in registros if r.get(campo)})


def filtrar_por_campo(registros, campo, valor, opcao_todos):
    if valor and valor != opcao_todos:
        return [r for r in registros if r.get(campo) == valor]
    return registros


def elegivel_para_composicao(registro):
    """Só linhas de energia (R$/MWh) compõem TUSD+TE.

    Linhas de demanda (R$/kW) ficam de fora: somar TUSD (kW) com TE (R$/MWh) não
    faz sentido dimensional. Tarifa de Aplicação e Base Econômica são ambas
    elegíveis — se as duas aparecerem juntas para a mesma composição, isso vira
    ambiguidade (ver chave_versao) e é resolvido no popup, não aqui.
    """
    return registro.get("DscUnidadeTerciaria") == "MWh"


def chave_versao(registro):
    """Identifica uma 'versão' de tarifa: mesma REH/base tarifária/subgrupo/
    modalidade/classe/subclasse/detalhe/vigência. Postos tarifários diferentes
    (Ponta/Fora Ponta/Intermediário) da mesma versão não geram ambiguidade — só
    versões diferentes (inclusive Tarifa de Aplicação vs. Base Econômica)
    coexistindo no resultado filtrado geram.
    """
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
        "tarifária, subgrupo/modalidade, classe ou detalhe elegível para compor "
        "TUSD + TE. Escolha qual delas usar no cálculo — as demais linhas "
        "continuam visíveis na tabela, só não entram na coluna de energia composta."
    )
    rotulos = {rotulo_versao(v): v for v in versoes}
    escolha_rotulo = st.radio("Composição", list(rotulos.keys()), label_visibility="collapsed")
    if st.button("Calcular esta composição", type="primary"):
        st.session_state["versao_escolhida"] = rotulos[escolha_rotulo]
        st.session_state["versao_escolhida_contexto"] = contexto_hash
        st.rerun()


POSTOS_PADRAO = {"Ponta", "Fora ponta", "Intermediário", "Não se aplica"}


def valores_por_posto(registros, versao_escolhida):
    """TUSD e TE (separados) por posto tarifário dentro da versão escolhida.

    Retorna (valores, postos_ambiguos): valores[posto] = (tusd, te);
    postos_ambiguos lista postos em que a própria versão escolhida ainda tem
    mais de um valor distinto (não deveria acontecer, mas protege contra dados
    inesperados).
    """
    valores = {}
    ambiguos = set()
    for r in registros:
        if versao_escolhida is None or not elegivel_para_composicao(r) or chave_versao(r) != versao_escolhida:
            continue
        posto = r.get("NomPostoTarifario")
        tusd, te = converter_valor_brl(r.get("VlrTUSD")), converter_valor_brl(r.get("VlrTE"))
        if tusd is None or te is None:
            continue
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


st.title("⚡ Consulta de Tarifas ANEEL")
st.caption(
    "Fonte: API de Dados Abertos da ANEEL (CKAN, pública, sem autenticação) — dataset "
    "[Tarifas de aplicação das distribuidoras de energia elétrica]"
    "(https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica)."
)

with st.sidebar:
    st.header("Filtros")

    distribuidoras = lista_distribuidoras()
    distribuidora = st.selectbox(
        "Distribuidora",
        options=distribuidoras,
        index=None,
        placeholder="Digite para buscar (ex.: LIGHT, CPFL, ENEL)...",
    )

    ano = None
    reh = None
    base_tarifaria = None
    detalhe = None
    subgrupo = None
    modalidade = None
    classe = None

    if distribuidora:
        registros_dist = registros_brutos_da_distribuidora(distribuidora)

        anos_disponiveis = sorted({ano_da_vigencia(r) for r in registros_dist if ano_da_vigencia(r)}, reverse=True)
        ano = st.selectbox(
            "Ano de início de vigência",
            options=["Todos"] + anos_disponiveis,
            index=0,
        )
        registros_ano = [r for r in registros_dist if ano == "Todos" or ano_da_vigencia(r) == ano]

        rehs_disponiveis = campo_distintos(registros_ano, "DscREH")
        reh = st.selectbox(
            "REH (Resolução Homologatória)",
            options=["Todas"] + rehs_disponiveis,
            index=0,
            placeholder="Digite para buscar...",
        )
        registros_reh = filtrar_por_campo(registros_ano, "DscREH", reh, "Todas")

        bases_disponiveis = campo_distintos(registros_reh, "DscBaseTarifaria")
        base_tarifaria = st.selectbox(
            "Base tarifária",
            options=["Todas"] + bases_disponiveis,
            index=0,
        )
        registros_base = filtrar_por_campo(registros_reh, "DscBaseTarifaria", base_tarifaria, "Todas")

        detalhes_disponiveis = campo_distintos(registros_base, "DscDetalhe")
        detalhe = st.selectbox(
            "Detalhe",
            options=["Todas"] + detalhes_disponiveis,
            index=0,
            placeholder="Digite para buscar...",
        )
        registros_detalhe = filtrar_por_campo(registros_base, "DscDetalhe", detalhe, "Todas")

        with st.expander("Filtros avançados"):
            subgrupos_disponiveis = campo_distintos(registros_detalhe, "DscSubGrupo")
            subgrupo = st.selectbox(
                "Subgrupo",
                options=["Todos"] + subgrupos_disponiveis,
                index=0,
            )
            registros_subgrupo = filtrar_por_campo(registros_detalhe, "DscSubGrupo", subgrupo, "Todos")

            modalidades_disponiveis = campo_distintos(registros_subgrupo, "DscModalidadeTarifaria")
            modalidade = st.selectbox(
                "Modalidade",
                options=["Todas"] + modalidades_disponiveis,
                index=0,
            )
            registros_modalidade = filtrar_por_campo(registros_subgrupo, "DscModalidadeTarifaria", modalidade, "Todas")

            classes_disponiveis = campo_distintos(registros_modalidade, "DscClasse")
            classe = st.selectbox(
                "Classe",
                options=["Todas"] + classes_disponiveis,
                index=0,
            )
    else:
        st.info("Selecione uma distribuidora para habilitar os demais filtros.")

    consultar = st.button("Consultar", type="primary", disabled=not distribuidora)

if not distribuidora:
    st.info("Use a barra lateral para escolher uma distribuidora e consultar as tarifas homologadas.")
    st.stop()

if not consultar and "ultimo_resultado" not in st.session_state:
    st.info("Ajuste os filtros na barra lateral e clique em **Consultar**.")
    st.stop()

if consultar:
    registros_dist = registros_brutos_da_distribuidora(distribuidora)

    registros_filtrados = registros_dist
    if ano and ano != "Todos":
        registros_filtrados = [r for r in registros_filtrados if ano_da_vigencia(r) == ano]
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscREH", reh, "Todas")
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscBaseTarifaria", base_tarifaria, "Todas")
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscDetalhe", detalhe, "Todas")
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscSubGrupo", subgrupo, "Todos")
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscModalidadeTarifaria", modalidade, "Todas")
    registros_filtrados = filtrar_por_campo(registros_filtrados, "DscClasse", classe, "Todas")

    partes_contexto = [distribuidora, f"Ano: {ano or 'Todos'}", f"REH: {reh or 'Todas'}"]
    if base_tarifaria and base_tarifaria != "Todas":
        partes_contexto.append(f"Base: {base_tarifaria}")
    if detalhe and detalhe != "Todas":
        partes_contexto.append(f"Detalhe: {detalhe}")
    if subgrupo and subgrupo != "Todos":
        partes_contexto.append(f"Subgrupo: {subgrupo}")
    if modalidade and modalidade != "Todas":
        partes_contexto.append(f"Modalidade: {modalidade}")
    if classe and classe != "Todas":
        partes_contexto.append(f"Classe: {classe}")

    st.session_state["ultimo_resultado"] = registros_filtrados
    st.session_state["ultimo_contexto"] = " | ".join(partes_contexto)

registros_filtrados = st.session_state.get("ultimo_resultado", [])
contexto = st.session_state.get("ultimo_contexto", "")

st.subheader(f"Resultados — {contexto}")
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
        "Escolha uma no popup para calcular a coluna de energia composta (TUSD+TE)."
    )
    dialog_escolher_versao(versoes, contexto_hash)

df = montar_dataframe(registros_filtrados, versao_escolhida)
st.dataframe(df, use_container_width=True, hide_index=True)

if versao_escolhida is not None:
    valores_posto, postos_ambiguos = valores_por_posto(registros_filtrados, versao_escolhida)
    postos_presentes = set(valores_posto.keys())

    if postos_ambiguos:
        st.info(
            "Há mais de um valor de TUSD+TE para o mesmo posto tarifário dentro da "
            "composição escolhida — média ponderada não calculada. Refine os filtros."
        )
    elif not postos_presentes.issubset(POSTOS_PADRAO):
        st.info(
            "Essa composição usa postos sazonais (seca/úmida) — a média ponderada por "
            "horas não é calculada automaticamente para essa estrutura."
        )
    elif postos_presentes == {"Não se aplica"}:
        tusd_unico, te_unico = valores_posto["Não se aplica"]
        col1, col2, col3 = st.columns(3)
        col1.metric("TUSD (posto único, R$/MWh)", f"R$ {tusd_unico:.2f}")
        col2.metric("TE (posto único, R$/MWh)", f"R$ {te_unico:.2f}")
        col3.metric("Total TUSD+TE (R$/MWh)", f"R$ {tusd_unico + te_unico:.2f}")
    elif postos_presentes:
        with st.expander("📊 Tarifa média ponderada por horas do mês", expanded=True):
            tem_ponta = "Ponta" in postos_presentes
            tem_intermediario = "Intermediário" in postos_presentes

            col1, col2, col3 = st.columns(3)
            total_horas = col1.number_input("Total de horas no mês", min_value=1.0, value=720.0, step=1.0, key="horas_total")
            horas_ponta = col2.number_input("Horas em Ponta", min_value=0.0, value=66.0, step=1.0, key="horas_ponta") if tem_ponta else 0.0
            horas_intermediario = col3.number_input("Horas em Intermediário", min_value=0.0, value=22.0, step=1.0, key="horas_intermediario") if tem_intermediario else 0.0
            horas_fora_ponta = total_horas - horas_ponta - horas_intermediario

            if horas_fora_ponta < 0:
                st.error("Horas de Ponta + Intermediário excedem o total de horas do mês informado.")
            else:
                tusd_ponta, te_ponta = valores_posto.get("Ponta", (0.0, 0.0))
                tusd_intermediario, te_intermediario = valores_posto.get("Intermediário", (0.0, 0.0))
                tusd_fora_ponta, te_fora_ponta = valores_posto.get("Fora ponta", (0.0, 0.0))

                def media_ponderada(v_ponta, v_intermediario, v_fora_ponta):
                    return (
                        v_ponta * horas_ponta
                        + v_intermediario * horas_intermediario
                        + v_fora_ponta * horas_fora_ponta
                    ) / total_horas

                media_tusd = media_ponderada(tusd_ponta, tusd_intermediario, tusd_fora_ponta)
                media_te = media_ponderada(te_ponta, te_intermediario, te_fora_ponta)
                media_total = media_tusd + media_te

                colm1, colm2, colm3 = st.columns(3)
                colm1.metric("TUSD Média Ponderada (R$/MWh)", f"R$ {media_tusd:.2f}")
                colm2.metric("TE Média Ponderada (R$/MWh)", f"R$ {media_te:.2f}")
                colm3.metric("Total Médio Ponderado (R$/MWh)", f"R$ {media_total:.2f}")

                # "$" escapado (\$) porque st.caption renderiza markdown, que trata $..$ como LaTeX
                def linha_posto(nome, tusd, te):
                    return f"{nome}: TUSD R\\$ {tusd:.2f} + TE R\\$ {te:.2f} = R\\$ {tusd + te:.2f}"

                partes_calculo = []
                if tem_ponta:
                    partes_calculo.append(f"{linha_posto('Ponta', tusd_ponta, te_ponta)} × {horas_ponta:.0f}h")
                if tem_intermediario:
                    partes_calculo.append(f"{linha_posto('Intermediário', tusd_intermediario, te_intermediario)} × {horas_intermediario:.0f}h")
                partes_calculo.append(f"{linha_posto('Fora Ponta', tusd_fora_ponta, te_fora_ponta)} × {horas_fora_ponta:.0f}h")
                for parte in partes_calculo:
                    st.caption(parte)
                st.caption(f"Total de horas consideradas: {total_horas:.0f}h")
                st.caption(
                    "Aproximação assumindo consumo constante ao longo do mês (peso só por "
                    "horas-relógio) — não reflete a curva de carga real da unidade consumidora."
                )

if not df.empty:
    buffer = io.StringIO()
    df.to_csv(buffer, sep=";", index=False, encoding="utf-8-sig")
    st.download_button(
        "Baixar CSV",
        data=buffer.getvalue().encode("utf-8-sig"),
        file_name=f"tarifas_{distribuidora.replace(' ', '_')}.csv",
        mime="text/csv",
    )
