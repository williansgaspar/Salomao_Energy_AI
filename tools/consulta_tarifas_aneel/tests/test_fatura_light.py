import pytest

from src.importers.fatura_light import Token, _extrair_itens, _metadados, grandezas_da_fatura, reconciliar_com_aneel, totais_tributos


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


def test_consolida_tributos_e_grandezas_para_preenchimento():
    fatura = {"itens": [
        {"tipo": "Energia", "posto": "Ponta", "quantidade": 72_879, "pis_cofins": 1_607.50, "icms": 10_319.60},
        {"tipo": "Demanda", "posto": "Fora ponta", "quantidade": 2_475, "pis_cofins": 280.74, "icms": 6_344.06},
    ]}
    assert grandezas_da_fatura(fatura) == {
        "consumos_mwh": {"Ponta": 72.879},
        "demandas_kw": {"Fora ponta": 2475.0},
    }
    assert totais_tributos(fatura) == pytest.approx({"pis_cofins": 1_888.24, "icms": 16_663.66})


def test_rejeita_valor_monetario_lido_como_aliquota_ou_tributo():
    tokens = linha(.10, "Energia Ativa kWh HFP/Único", "672.242", "0,63962757", "429.984,51", "634.200,00", "500.000,00", "0,46220")
    tokens[5] = Token(.65, .10, "21108,17")
    item = _extrair_itens(tokens)[0]
    assert item["aliquota_icms"] is None
    assert item["pis_cofins"] is None
    assert item["icms"] is None


def test_recupera_pis_quando_ocr_concatena_base_e_aliquota():
    metadados = _metadados([
        Token(.1, .1, "492.252,210,88%"),
        Token(.2, .1, "4,04%"),
    ])
    assert metadados["pis_percentual"] == 0.88
    assert metadados["cofins_percentual"] == 4.04
