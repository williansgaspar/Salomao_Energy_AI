from src.domain.historico import filtros_da_familia, ordenar_registros_historicos, registros_historicos


def registro(**sobrescritas):
    base = {
        "SigAgente": "LIGHT SESA", "DscSubGrupo": "A4", "DscModalidadeTarifaria": "Verde",
        "DscBaseTarifaria": "Tarifa de Aplicação", "DscClasse": "Poder Público",
        "DscSubClasse": "Poder Público Federal", "DscDetalhe": "Não se aplica",
        "SigAgenteAcessante": None, "NomPostoTarifario": "Fora ponta",
        "DscREH": "REH 1", "DatInicioVigencia": "2025-01-01", "DscUnidadeTerciaria": "MWh",
    }
    return {**base, **sobrescritas}


def test_historico_mantem_filtros_tecnicos_e_libera_reh_vigencia():
    parametros = {
        "SigAgente": "LIGHT SESA", "DscSubGrupo": "A4", "DscModalidadeTarifaria": "Verde",
        "DscBaseTarifaria": "Tarifa de Aplicação", "DscClasse": "Poder Público",
        "DscSubClasse": "Poder Público Federal", "DscDetalhe": "Não se aplica",
        "SigAgenteAcessante": "Todos", "NomPostoTarifario": "Todos",
    }
    filtros = filtros_da_familia(parametros)
    registros = [
        registro(DscREH="REH 1", DatInicioVigencia="2025-01-01"),
        registro(DscREH="REH 2", DatInicioVigencia="2026-01-01"),
        registro(DscBaseTarifaria="Tarifa de Distribuição"),
        registro(DscClasse="Industrial"),
    ]
    assert registros_historicos(registros, filtros) == registros[:2]


def test_historico_nao_consolida_rehs_com_mesma_data():
    registros = [
        registro(DscREH="REH 2", DatInicioVigencia="2025-01-01"),
        registro(DscREH="REH 1", DatInicioVigencia="2025-01-01"),
    ]
    ordenados = ordenar_registros_historicos(registros)
    assert [r["DscREH"] for r in ordenados] == ["REH 1", "REH 2"]