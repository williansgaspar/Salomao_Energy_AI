import pytest

from src.importers.fatura_light import Token, _extrair_itens, _metadados, grandezas_ausentes, grandezas_da_fatura, reconciliar_com_aneel, totais_tributos


def linha(y, rotulo, quantidade, bruto, valor, pis, icms, liquida):
    return [
        Token(.10, y, rotulo), Token(.34, y, quantidade), Token(.452, y, bruto),
        Token(.509, y, valor), Token(.560, y, pis), Token(.66, y, "24,000"),
        Token(.70, y, icms), Token(.74, y, liquida),
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
    tokens[5] = Token(.66, .10, "21108,17")
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


def test_extrai_quantidades_com_coluna_deslocada_e_rotulo_hfp_corrompido():
    tokens = [
        Token(.20, .10, "Itens de fatura"), Token(.392, .10, "Quant."),
        Token(.20, .20, "ooun/dJH Mx eAgy epurweg"), Token(.403, .20, "2.475"),
        Token(.20, .21, "Demanda Ativa kW HP"), Token(.358, .21, "kW"), Token(.403, .21, "2.122"),
        Token(.20, .22, "Energia Ativa kWh HFP/Único"), Token(.358, .22, "kWh"), Token(.400, .22, "672.242"),
        Token(.20, .23, "Energia Ativa kWh HP"), Token(.358, .23, "kWh"), Token(.401, .23, "72.879"),
    ]
    itens = _extrair_itens(tokens)
    assert {(i["tipo"], i["posto"]): i["quantidade"] for i in itens} == {
        ("Demanda", "Fora ponta"): 2475,
        ("Demanda", "Ponta"): 2122,
        ("Energia", "Fora ponta"): 672242,
        ("Energia", "Ponta"): 72879,
    }


def test_modalidade_verde_infere_demanda_unica_e_ignora_tabela_do_medidor():
    tokens = [
        Token(.20, .10, "Itens de fatura"), Token(.392, .10, "Quant."),
        Token(.20, .20, "ooun/dJH Mx eAgy epurweg"), Token(.358, .20, "kW"), Token(.408, .20, "30"),
        Token(.20, .21, "Energia Ativa kWh HFP/Único"), Token(.358, .21, "kWh"), Token(.403, .21, "7.175"),
        Token(.20, .22, "Energia Ativa kWh HP"), Token(.358, .22, "kWh"), Token(.406, .22, "775"),
        Token(.17, .30, "Medidor"), Token(.23, .31, "Demanda Ativa-kW"), Token(.29, .31, "Único"), Token(.343, .31, "57.309"),
    ]
    itens = _extrair_itens(tokens, "Verde")
    assert {(i["tipo"], i["posto"]): i["quantidade"] for i in itens} == {
        ("Demanda", "Fora ponta"): 30,
        ("Energia", "Fora ponta"): 7175,
        ("Energia", "Ponta"): 775,
    }
    fatura = {"modalidade": "Verde", "itens": itens}
    assert grandezas_ausentes(fatura) == []


def test_modalidade_azul_exige_as_duas_demandas_e_descarta_posto_nulo():
    fatura = {"modalidade": "Azul", "itens": [
        {"tipo": "Energia", "posto": "Fora ponta", "quantidade": 1000},
        {"tipo": "Energia", "posto": "Ponta", "quantidade": 1000},
        {"tipo": "Demanda", "posto": "Fora ponta", "quantidade": 100},
        {"tipo": "Demanda", "posto": None, "quantidade": 999},
    ]}
    assert grandezas_da_fatura(fatura)["demandas_kw"] == {"Fora ponta": 100}
    assert grandezas_ausentes(fatura) == ["Demanda HPT"]


def test_metadados_identificam_grupo_b_e_subgrupo_b3():
    metadados = _metadados([Token(.1, .1, "LIGHT Grupo B - B3")])
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] == "B3"


def test_metadados_identificam_grupo_b_mesmo_sem_subgrupo_explicito():
    metadados = _metadados([Token(.1, .1, "LIGHT - GRUPO B")])
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] is None


def test_metadados_reconhecem_competencia_numerica_subgrupo_com_espaco_e_detalhe():
    metadados = _metadados([Token(.1, .1, "LIGHT GRUPO B - B 3 - 07/2026 - Convencional - SCEE")])
    assert metadados["competencia"] == "2026-07"
    assert metadados["subgrupo"] == "B3"
    assert metadados["modalidade"] == "Convencional"
    assert metadados["detalhe"] == "SCEE"


def test_metadados_reconhecem_subgrupo_com_hifen():
    metadados = _metadados([Token(.1, .1, "LIGHT - GRUPO B - SUBGRUPO B-3")])
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] == "B3"


def test_metadados_corrigem_b3_lido_como_83_e_aplicam_modalidade_convencional_no_grupo_b():
    metadados = _metadados([Token(.1, .1, "GRUPO: B  SUBGRUPO: 8:3")])
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] == "B3"
    assert metadados["modalidade"] == "Convencional"


def test_metadados_usam_camada_textual_complementar_para_subgrupo():
    metadados = _metadados([Token(.1, .1, "LIGHT - GRUPO B")], "SUBGRUPO TARIFÁRIO: B3")
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] == "B3"
    assert metadados["modalidade"] == "Convencional"


def test_metadados_usam_texto_do_cabecalho_light_para_classificacao():
    metadados = _metadados([], "Classificação: Grupo B / Subgrupo B3 Poder Público")
    assert metadados["grupo"] == "B"
    assert metadados["subgrupo"] == "B3"
    assert metadados["classe"] == "Poder Público"


def test_grupo_b_exige_apenas_consumo_e_consolida_em_posto_unico():
    fatura = {"grupo": "B", "subgrupo": "B3", "itens": [
        {"tipo": "Energia", "posto": "Fora ponta", "quantidade": 12_345},
    ]}
    assert grandezas_da_fatura(fatura) == {
        "consumos_mwh": {"Não se aplica": 12.345},
        "demandas_kw": {},
    }
    assert grandezas_ausentes(fatura) == []


def test_grupo_b_sem_consumo_informa_apenas_a_grandeza_necessaria():
    assert grandezas_ausentes({"grupo": "B", "itens": []}) == ["Consumo de energia"]


def test_grupo_indeterminado_nao_aplica_exigencias_do_grupo_a():
    fatura = {"itens": [{"tipo": "Energia", "posto": "Não se aplica", "quantidade": 1_000}]}
    assert grandezas_ausentes(fatura) == []
