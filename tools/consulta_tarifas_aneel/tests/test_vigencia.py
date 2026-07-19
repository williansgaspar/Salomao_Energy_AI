from datetime import date

from src.domain.vigencia import periodo_do_mes, registros_vigentes_no_periodo


def test_periodo_do_mes_respeita_ano_bissexto():
    assert periodo_do_mes(2024, 2) == (date(2024, 2, 1), date(2024, 2, 29))


def test_reh_que_comeca_no_meio_do_mes_e_incluida():
    registros = [{"DatInicioVigencia": "2026-07-15", "DatFimVigencia": "2027-07-14"}]
    assert registros_vigentes_no_periodo(registros, date(2026, 7, 1), date(2026, 7, 31)) == registros


def test_vigencia_aberta_e_incluida():
    registros = [{"DatInicioVigencia": "2025-01-01", "DatFimVigencia": ""}]
    assert registros_vigentes_no_periodo(registros, date(2026, 1, 1), date(2026, 1, 31)) == registros
