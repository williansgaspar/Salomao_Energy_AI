from src.domain.composicao import chave_versao, valores_por_posto, versoes_disponiveis


def registro(unidade="MWh", posto="Ponta", tusd="100,00", te="200,00"):
    return {
        "DscREH": "REH 1", "DscBaseTarifaria": "Tarifa de Aplicação", "DscSubGrupo": "A4",
        "DscModalidadeTarifaria": "Verde", "DscClasse": "Não se aplica", "DscSubClasse": "Não se aplica",
        "DscDetalhe": "Não se aplica", "DatInicioVigencia": "2026-01-01", "DatFimVigencia": "2026-12-31",
        "DscUnidadeTerciaria": unidade, "NomPostoTarifario": posto, "VlrTUSD": tusd, "VlrTE": te,
    }


def test_versao_agrupa_postos_e_unidades():
    registros = [registro(), registro(posto="Fora ponta"), registro(unidade="kW")]
    assert versoes_disponiveis(registros) == [chave_versao(registros[0])]


def test_valores_por_posto_converte_formato_brasileiro():
    r = registro(tusd="1.234,56", te="200,10")
    assert valores_por_posto([r], chave_versao(r), "MWh") == {"Ponta": (1234.56, 200.1)}
