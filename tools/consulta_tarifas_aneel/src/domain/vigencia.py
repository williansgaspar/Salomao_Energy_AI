"""Seleção de tarifas por data ou período de faturamento."""

from calendar import monthrange
from datetime import date, datetime


def parse_data(valor):
    if isinstance(valor, date):
        return valor
    if not valor:
        return None
    try:
        return datetime.strptime(str(valor), "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None


def periodo_do_mes(ano: int, mes: int):
    return date(ano, mes, 1), date(ano, mes, monthrange(ano, mes)[1])


def sobrepoe_periodo(registro, inicio: date, fim: date) -> bool:
    vigencia_inicio = parse_data(registro.get("DatInicioVigencia"))
    vigencia_fim = parse_data(registro.get("DatFimVigencia"))
    if vigencia_inicio is None:
        return False
    return vigencia_inicio <= fim and (vigencia_fim is None or vigencia_fim >= inicio)


def registros_vigentes_no_periodo(registros, inicio: date, fim: date):
    """Retorna registros cuja vigência alcança pelo menos um dia do período."""
    if inicio > fim:
        raise ValueError("O início do período não pode ser posterior ao fim.")
    return [r for r in registros if sobrepoe_periodo(r, inicio, fim)]
