"""Identificação e leitura de composições tarifárias da base ANEEL."""

from aneel_api import converter_valor_brl


def chave_versao(registro):
    return tuple(registro.get(campo) for campo in (
        "DscREH", "DscBaseTarifaria", "DscSubGrupo", "DscModalidadeTarifaria",
        "DscClasse", "DscSubClasse", "DscDetalhe", "DatInicioVigencia", "DatFimVigencia",
    ))


def rotulo_versao(chave):
    reh, base, subgrupo, modalidade, classe, subclasse, detalhe, inicio, fim = chave
    partes = [reh or "REH não informada", base or "Base não informada", f"{subgrupo or '—'} / {modalidade or '—'}"]
    for valor in (classe, subclasse, detalhe):
        if valor and valor != "Não se aplica":
            partes.append(valor)
    partes.append(f"{inicio or '—'} a {fim or 'aberta'}")
    return " | ".join(partes)


def versoes_disponiveis(registros):
    return sorted({chave_versao(r) for r in registros if r.get("DscUnidadeTerciaria") == "MWh"})


def valores_por_posto(registros, versao, unidade):
    valores = {}
    ambiguos = set()
    for registro in registros:
        if chave_versao(registro) != versao or registro.get("DscUnidadeTerciaria") != unidade:
            continue
        posto = registro.get("NomPostoTarifario")
        par = (converter_valor_brl(registro.get("VlrTUSD")), converter_valor_brl(registro.get("VlrTE")) or 0.0)
        if par[0] is None:
            continue
        if posto in valores and valores[posto] != par:
            ambiguos.add(posto)
        valores[posto] = par
    if ambiguos:
        raise ValueError("Valores divergentes no mesmo posto: " + ", ".join(sorted(ambiguos)))
    return valores
