from src.domain.preenchimento import grandezas_para_composicao


def test_mapeia_grandezas_com_posto_igual_ao_da_composicao():
    resultado = grandezas_para_composicao(
        {"consumos_mwh": {"Ponta": 10, "Fora ponta": 20}, "demandas_kw": {"Ponta": 30}},
        ["Ponta", "Fora ponta"], ["Ponta", "Fora ponta"],
    )
    assert resultado == {"consumos_mwh": {"Ponta": 10.0, "Fora ponta": 20.0}, "demandas_kw": {"Ponta": 30.0}}


def test_mapeia_valor_documental_unico_para_posto_unico_da_composicao():
    resultado = grandezas_para_composicao(
        {"consumos_mwh": {"Não se aplica": 12.345}, "demandas_kw": {"Fora ponta": 50}},
        ["Fora ponta"], ["Não se aplica"],
    )
    assert resultado == {"consumos_mwh": {"Fora ponta": 12.345}, "demandas_kw": {"Não se aplica": 50.0}}


def test_nao_inventa_mapeamento_quando_ha_mais_de_um_posto_tarifario():
    resultado = grandezas_para_composicao(
        {"consumos_mwh": {"Não se aplica": 12.345}, "demandas_kw": {}}, ["Ponta", "Fora ponta"], [],
    )
    assert resultado["consumos_mwh"] == {}
