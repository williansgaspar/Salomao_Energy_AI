import pytest

from src.domain.calculos import calcular_fatura, calcular_por_consumo_total


def test_calculo_direto_respeita_consumo_de_cada_posto():
    tarifas = {"Ponta": (100, 200), "Fora ponta": (50, 150)}
    resultado = calcular_fatura(tarifas, {"Ponta": 10, "Fora ponta": 90})
    assert resultado["energia"]["te"] == 15_500
    assert resultado["energia"]["tusd_energia"] == 5_500
    assert resultado["total"] == 21_000


def test_calculo_inclui_demanda_por_posto():
    resultado = calcular_fatura(
        {"Não se aplica": (60, 180)}, {"Não se aplica": 100},
        {"Não se aplica": (40, 0)}, {"Não se aplica": 500},
    )
    assert resultado["energia"]["total"] == 24_000
    assert resultado["demanda"]["total"] == 20_000
    assert resultado["total"] == 44_000


def test_consumo_total_e_distribuido_pelos_pesos():
    tarifas = {"Ponta": (100, 200), "Fora ponta": (50, 150)}
    resultado = calcular_por_consumo_total(tarifas, 100, {"Ponta": 1, "Fora ponta": 3})
    assert resultado["consumos_estimados"] == {"Ponta": 25, "Fora ponta": 75}
    assert resultado["total"] == 22_500


def test_tarifa_ausente_nao_e_convertida_em_zero():
    with pytest.raises(ValueError, match="ausente"):
        calcular_fatura({"Ponta": (100, 200)}, {"Fora ponta": 10})


def test_valores_negativos_sao_rejeitados():
    with pytest.raises(ValueError, match="negativo"):
        calcular_fatura({"Não se aplica": (10, 20)}, {"Não se aplica": -1})
