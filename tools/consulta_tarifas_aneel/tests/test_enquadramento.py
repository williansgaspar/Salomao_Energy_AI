import pytest

from src.domain.enquadramento import detalhe_tarifario_padrao, grupo_tarifario


@pytest.mark.parametrize(("subgrupo", "esperado"), [
    ("A4", "A"),
    ("AS", "A"),
    ("B1", "B"),
    ("B3", "B"),
    (" b2 ", "B"),
    (None, None),
    ("Não informado", None),
])
def test_grupo_tarifario_classifica_subgrupos(subgrupo, esperado):
    assert grupo_tarifario(subgrupo) == esperado


@pytest.mark.parametrize(("detalhes", "detalhe_documento", "esperado"), [
    (["APE", "Não se aplica", "SCEE"], None, "Não se aplica"),
    (["APE", "Não se aplica", "SCEE"], "SCEE", "SCEE"),
    (["APE", "Não se aplica"], "SCEE", "Não se aplica"),
    (["SCEE"], None, "SCEE"),
    ([], None, None),
])
def test_detalhe_tarifario_padrao_prioriza_documento_e_nao_se_aplica(detalhes, detalhe_documento, esperado):
    assert detalhe_tarifario_padrao(detalhes, detalhe_documento) == esperado
