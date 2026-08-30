"""Leitura das componentes tarifárias homologadas publicadas pela ANEEL."""

import io
import re
import unicodedata

import pandas as pd
import requests


_BASE_URL = "https://dadosabertos.aneel.gov.br/dataset/613e6b74-1a4b-4c48-a231-096815e96bd5/resource/{resource}/download/componentes-tarifarias-{ano}.parquet"
_RECURSOS = {
    2023: "8db8b51d-e0ae-4789-aa1e-23425944c0ea",
    2024: "5a29d53f-b7a6-4436-8497-7de00214d8fb",
    2025: "2a7a5364-8bd7-4464-9c56-587d77329447",
    2026: "59c32c89-8e86-4122-a7cf-a0d5fa9d0ff5",
}


def _normalizar(valor):
    texto = unicodedata.normalize("NFKD", str(valor or "")).encode("ascii", "ignore").decode().lower()
    return "".join(caractere for caractere in texto if caractere.isalnum())


def _filtrar_texto(df, coluna, valor):
    if coluna not in df or valor is None:
        return df
    normalizado = _normalizar(valor)
    return df[df[coluna].map(_normalizar) == normalizado]


def carregar_componentes_ano(ano):
    """Baixa o Parquet anual oficial de componentes tarifárias da ANEEL."""
    recurso = _RECURSOS.get(int(ano))
    if not recurso:
        raise ValueError(f"A base de componentes ANEEL ainda não possui arquivo publicado para {ano}.")
    url = _BASE_URL.format(resource=recurso, ano=int(ano))
    resposta = requests.get(url, timeout=90)
    resposta.raise_for_status()
    return pd.read_parquet(io.BytesIO(resposta.content)), url


def apurar_componentes_scee(registros, distribuidora, versao):
    """Obtém bases SCEE da mesma composição tarifária da simulação.

    ``versao`` segue a chave de composição do app. A base de componentes usa
    explicitamente o detalhe SCEE, mesmo quando a consulta de tarifa de
    aplicação estava em ``Não se aplica``.
    """
    reh, base, subgrupo, modalidade, _classe, _subclasse, _detalhe, inicio, _fim = versao
    if not inicio:
        return None
    df = registros.copy()
    for coluna, valor in (
        ("SigNomeAgente", distribuidora),
        ("DscBaseTarifaria", base),
        ("DscSubGrupoTarifario", subgrupo),
        ("DscModalidadeTarifaria", modalidade),
        ("DscDetalheConsumidor", "SCEE"),
        ("DscPostoTarifario", "Não se aplica"),
        ("DscUnidade", "R$/MWh"),
    ):
        df = _filtrar_texto(df, coluna, valor)
    if "DatInicioVigencia" in df:
        df = df[df["DatInicioVigencia"].astype(str).str[:10] == str(inicio)[:10]]
    if df.empty:
        return None

    # A data de início já individualiza a REH. A conferência pelo número é
    # apenas uma proteção adicional quando ambos os textos estão disponíveis.
    if reh and "DscResolucaoHomologatoria" in df:
        numeros_reh = re.findall(r"\d+", str(reh))
        if numeros_reh:
            candidatos = df[df["DscResolucaoHomologatoria"].astype(str).map(lambda item: all(numero in item for numero in numeros_reh[-2:]))]
            if not candidatos.empty:
                df = candidatos

    valores = {
        componente: float(df.loc[df["DscComponenteTarifario"] == componente, "VlrComponenteTarifario"].iloc[0])
        for componente in ("TUSD_FioB", "TUSD_CCT", "TUSD_PeD", "TUSD_TFSEE")
        if not df.loc[df["DscComponenteTarifario"] == componente].empty
    }
    if "TUSD_FioB" not in valores:
        return None
    return {
        "fio_b_r_mwh": valores["TUSD_FioB"],
        "fio_a_conexao_r_mwh": valores.get("TUSD_CCT", 0.0),
        "pde_ee_tfsee_r_mwh": valores.get("TUSD_PeD", 0.0) + valores.get("TUSD_TFSEE", 0.0),
        "componentes": valores,
        "reh": df["DscResolucaoHomologatoria"].iloc[0],
        "inicio_vigencia": str(df["DatInicioVigencia"].iloc[0])[:10],
    }


def componentes_scee_da_versao(distribuidora, versao):
    """Carrega e apura as bases oficiais da versão tarifária selecionada."""
    ano = int(str(versao[7])[:4])
    registros, url = carregar_componentes_ano(ano)
    resultado = apurar_componentes_scee(registros, distribuidora, versao)
    if resultado is not None:
        resultado["fonte_url"] = url
        resultado["ano_arquivo"] = ano
    return resultado
