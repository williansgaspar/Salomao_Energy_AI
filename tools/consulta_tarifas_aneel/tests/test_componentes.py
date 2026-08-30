import pandas as pd
import pytest

from src.aneel.componentes import apurar_componentes_scee


def _linha(componente, valor):
    return {
        "SigNomeAgente": "LIGHT SESA", "DscResolucaoHomologatoria": "REH Nº 3.571",
        "DatInicioVigencia": "2026-03-15", "DscBaseTarifaria": "Tarifa de Aplicação",
        "DscSubGrupoTarifario": "B3", "DscModalidadeTarifaria": "Convencional",
        "DscDetalheConsumidor": "SCEE", "DscPostoTarifario": "Não se aplica",
        "DscUnidade": "R$/MWh", "DscComponenteTarifario": componente,
        "VlrComponenteTarifario": valor,
    }


def test_apura_componentes_scee_da_mesma_composicao():
    registros = pd.DataFrame([
        _linha("TUSD_FioB", 225.345641), _linha("TUSD_CCT", 3.539455),
        _linha("TUSD_PeD", 4.191344), _linha("TUSD_TFSEE", 0.689028),
        {**_linha("TUSD_FioB", 999), "DscBaseTarifaria": "CVA"},
    ])
    versao = ("REH Nº 3.571", "Tarifa de Aplicação", "B3", "Convencional", "Não se aplica", "Não se aplica", "Não se aplica", "2026-03-15", "2027-03-14")

    resultado = apurar_componentes_scee(registros, "LIGHT SESA", versao)

    assert resultado["fio_b_r_mwh"] == 225.345641
    assert resultado["fio_a_conexao_r_mwh"] == 3.539455
    assert resultado["pde_ee_tfsee_r_mwh"] == pytest.approx(4.880372)


def test_nao_retorna_valor_quando_nao_ha_mesma_composicao():
    registros = pd.DataFrame([_linha("TUSD_FioB", 225)])
    versao = ("REH Nº 3.571", "Tarifa de Aplicação", "B2", "Convencional", None, None, None, "2026-03-15", None)
    assert apurar_componentes_scee(registros, "LIGHT SESA", versao) is None
