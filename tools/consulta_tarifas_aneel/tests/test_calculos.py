import pytest

from src.domain.calculos import calcular_fatura, calcular_por_consumo_total, comparar_acr_acl, comparar_acr_scee_bt, simular_scee_bt
from src.domain.scee import parametros_regulatorios_scee


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


def test_comparacao_acl_altera_somente_te():
    resultado = comparar_acr_acl(30_000, 20_000, 10_000, 100, 200)
    assert resultado["te_acr_efetiva"] == 300
    assert resultado["custo_te_acl"] == 20_000
    assert resultado["total_acr"] == 60_000
    assert resultado["total_acl"] == 50_000
    assert resultado["economia"] == 10_000
    assert resultado["economia_percentual"] == pytest.approx(16.6667, rel=1e-4)


def test_comparacao_acl_rejeita_tarifa_negativa():
    with pytest.raises(ValueError, match="negativo"):
        comparar_acr_acl(100, 100, 100, 1, -1)


def test_comparacao_acl_adiciona_bandeira_somente_ao_acr():
    resultado = comparar_acr_acl(30_000, 20_000, 10_000, 100, 200, bandeira_r_mwh=18.85)
    assert resultado["custo_bandeira_acr"] == 1_885
    assert resultado["total_acr"] == 61_885
    assert resultado["total_acl"] == 50_000
    assert resultado["economia"] == 11_885


def test_comparacao_acr_scee_bt_aplica_desconto_sobre_conta_acr_com_bandeira():
    resultado = comparar_acr_scee_bt(10_000, 100, 20, bandeira_r_mwh=18.85)
    assert resultado["custo_bandeira_acr"] == 1_885
    assert resultado["conta_acr"] == 11_885
    assert resultado["conta_scee_com_desconto"] == 9_508
    assert resultado["economia"] == 2_377
    assert resultado["economia_percentual"] == 20


def test_comparacao_acr_scee_bt_rejeita_desconto_acima_de_cem_por_cento():
    with pytest.raises(ValueError, match="superior a 100%"):
        comparar_acr_scee_bt(10_000, 100, 100.01)


def test_scee_gd_i_compensa_te_tusd_e_aplica_desconto_comercial_ao_credito():
    resultado = simular_scee_bt(100_000, 100, 100, 12.51, "GD I", custo_disponibilidade_kwh=0)

    assert resultado["residual_scee_r_mwh"] == 0
    assert resultado["fatura_light"] == 0
    assert resultado["pagamento_fornecedor"] == pytest.approx(87_490)
    assert resultado["economia_percentual"] == pytest.approx(12.51)


def test_scee_aplica_desconto_linear_sobre_tarifa_com_bandeira_vigente():
    resultado = simular_scee_bt(
        100_000, 100, 100, 10, "GD I", custo_disponibilidade_kwh=0,
        bandeira_r_mwh=20,
    )

    assert resultado["tarifa_comercial_r_mwh"] == 1_020
    assert resultado["pagamento_fornecedor"] == 91_800
    assert resultado["conta_acr"] == 102_000
    assert resultado["economia"] == 10_200
    assert resultado["economia_percentual"] == pytest.approx(10)


def test_scee_apura_resultado_financeiro_com_ajustes_de_cada_cenario():
    resultado = simular_scee_bt(
        1_000, 1, 100, 10, "GD I", custo_disponibilidade_kwh=0,
        ajustes_financeiros_acr=120, ajustes_financeiros_scee=20,
    )

    assert resultado["conta_acr_financeira"] == 1_120
    assert resultado["conta_scee_financeira"] == 920
    assert resultado["economia"] == 200


def test_scee_gd_ii_aplica_sessenta_por_cento_do_fio_b_em_2026():
    resultado = simular_scee_bt(100_000, 100, 100, 12.51, "GD II", custo_disponibilidade_kwh=0, fio_b_r_mwh=100)

    assert resultado["residual_scee_r_mwh"] == 60
    assert resultado["fatura_light"] == 6_000
    assert resultado["conta_scee"] == pytest.approx(93_490)


def test_scee_gd_ii_aplica_progressao_anual_do_fio_b():
    assert parametros_regulatorios_scee("GD II", 2023)["fio_b"] == 0.15
    assert parametros_regulatorios_scee("GD II", 2028)["fio_b"] == 0.90


def test_scee_gd_iii_aplica_fatores_do_artigo_27_paragrafo_primeiro():
    resultado = simular_scee_bt(
        100_000, 100, 100, 0, "GD III", custo_disponibilidade_kwh=0,
        fio_b_r_mwh=100, fio_a_conexao_r_mwh=50, pde_ee_tfsee_r_mwh=10,
    )

    assert resultado["residual_scee_r_mwh"] == 130


def test_scee_restringe_estimativa_a_periodo_explicito_de_transicao():
    with pytest.raises(ValueError, match="2023 a 2028"):
        simular_scee_bt(100_000, 100, 100, 0, "GD II", ano_referencia=2029)


def test_scee_gd_iii_soma_fio_b_e_componentes_adicionais_informados():
    resultado = simular_scee_bt(
        100_000, 100, 100, 12.51, "GD III", custo_disponibilidade_kwh=0,
        fio_b_r_mwh=100, componentes_adicionais_gdiii_r_mwh=35,
    )

    assert resultado["residual_scee_r_mwh"] == 135
    assert resultado["fatura_light"] == 13_500


def test_scee_aplica_piso_do_custo_de_disponibilidade_na_fatura_light():
    resultado = simular_scee_bt(10_000, 10, 100, 10, "GD I", custo_disponibilidade_kwh=100)

    assert resultado["piso_disponibilidade"] == 100
    assert resultado["fatura_light"] == 100
