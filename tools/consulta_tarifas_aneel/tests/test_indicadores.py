import pytest

from src.domain.calculos import pesos_horarios_indicativos, tarifas_indicativas_ponderadas


def test_pesos_verde_somam_720_horas():
    pesos = pesos_horarios_indicativos({"Ponta", "Fora ponta"})
    assert pesos == {"Ponta": 66.0, "Fora ponta": 654.0}
    assert sum(pesos.values()) == 720


def test_pesos_branca_incluem_intermediario():
    assert pesos_horarios_indicativos({"Ponta", "Intermediário", "Fora ponta"}) == {
        "Ponta": 66.0, "Intermediário": 44.0, "Fora ponta": 610.0,
    }


def test_tarifas_ponderadas_nao_dependem_de_consumo():
    energia = {"Ponta": (1000, 500), "Fora ponta": (200, 300)}
    demanda = {"Ponta": (50, 0), "Fora ponta": (20, 0)}
    r = tarifas_indicativas_ponderadas(energia, demanda)
    assert r["te_ponderada"] == pytest.approx((500 * 66 + 300 * 654) / 720)
    assert r["tusd_energia_ponderada"] == pytest.approx((1000 * 66 + 200 * 654) / 720)
    assert r["tusd_demanda_ponderada"] == pytest.approx((50 * 66 + 20 * 654) / 720)


def test_posto_nao_se_aplica_mantem_tarifa_original():
    r = tarifas_indicativas_ponderadas({"Não se aplica": (321, 456)}, {"Não se aplica": (78, 0)})
    assert r["te_ponderada"] == 456
    assert r["tusd_energia_ponderada"] == 321
    assert r["tusd_demanda_ponderada"] == 78
