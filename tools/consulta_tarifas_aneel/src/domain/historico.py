"""Historical tariff-family selection without implicit aggregation."""

from datetime import date

from .vigencia import parse_data


CAMPOS_FAMILIA_TARIFARIA = (
    "SigAgente",
    "DscSubGrupo",
    "DscModalidadeTarifaria",
    "DscBaseTarifaria",
    "DscClasse",
    "DscSubClasse",
    "DscDetalhe",
    "SigAgenteAcessante",
    "NomPostoTarifario",
)
VALORES_TODOS = {None, "", "Todos", "Todas"}


def filtros_da_familia(parametros):
    """Keep technical filters and release only REH and validity dates."""
    return {
        campo: parametros.get(campo)
        for campo in CAMPOS_FAMILIA_TARIFARIA
        if parametros.get(campo) not in VALORES_TODOS
    }


def registros_historicos(registros, filtros):
    """Return every REH and validity interval from the selected tariff family."""
    return [
        registro for registro in registros
        if all(registro.get(campo) == valor for campo, valor in filtros.items())
    ]


def ordenar_registros_historicos(registros):
    """Order observations without averaging or consolidating REHs."""
    data_maxima = date.max
    return sorted(
        registros,
        key=lambda r: (
            parse_data(r.get("DatInicioVigencia")) or data_maxima,
            r.get("DscREH") or "",
            r.get("NomPostoTarifario") or "",
            r.get("DscUnidadeTerciaria") or "",
        ),
    )