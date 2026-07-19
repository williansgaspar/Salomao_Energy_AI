import pytest

from src.importers.fatura_light import Token, _extrair_itens, reconciliar_com_aneel


def linha(y, rotulo, quantidade, bruto, valor, pis, icms, liquida):
    return [
        Token(.10, y, rotulo), Token(.34, y, quantidade), Token(.40, y, bruto),
        Token(.48, y, valor), Token(.575, y, pis), Token(.65, y, "24,000"),
        Token(.69, y, icms), Token(.735, y, liquida),
    ]


def test_extrai_e_remove_tributos_por_item():
    tokens = linha(.10, "Energia Ativa kWh HFP/Único", "672.242", "0,63962757", "429.984,51", "16.077,98", "103.196,28", "0,46220")
    item = _extrair_itens(tokens)[0]
    assert item["quantidade"] == 672_242
    assert item["consumo_mwh"] == 672.242
    assert item["tarifa_liquida"] == pytest.approx((429_984.51 - 16_077.98 - 103_196.28) / 672_242, abs=1e-5)


def test_reconciliacao_converte_tarifa_energia_para_mwh():
    fatura = {"itens": [{
        "tipo": "Energia", "posto": "Fora ponta", "unidade": "kWh", "quantidade": 1000,
        "consumo_mwh": 1, "tarifa_liquida": .4622, "valor_com_tributos": 0,
        "pis_cofins": 0, "icms": 0,
    }]}
    linha = reconciliar_com_aneel(fatura, {"Fora ponta": (200, 262.2)}, {})[0]
    assert linha["tarifa_liquida_comparavel"] == 462.2
    assert linha["soma_aneel"] == 462.2
    assert linha["diferenca_tarifa"] == pytest.approx(0)


def test_reconciliacao_demanda_usa_r_kw_sem_conversao():
    fatura = {"itens": [{
        "tipo": "Demanda", "posto": "Ponta", "unidade": "kW", "quantidade": 200,
        "consumo_mwh": None, "tarifa_liquida": 29.95, "valor_com_tributos": 0,
        "pis_cofins": 0, "icms": 0,
    }]}
    linha = reconciliar_com_aneel(fatura, {}, {"Ponta": (29.95, 0)})[0]
    assert linha["tarifa_liquida_comparavel"] == 29.95
    assert linha["diferenca_tarifa"] == pytest.approx(0)
