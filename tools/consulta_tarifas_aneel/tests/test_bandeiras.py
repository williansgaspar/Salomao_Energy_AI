from src.aneel.bandeiras import bandeira_da_competencia, competencia_texto, opcoes_manuais


ACIO = [
    {"DatCompetencia": "2026-07-01", "NomBandeiraAcionada": "Amarela", "VlrAdicionalBandeira": "18,85"},
    {"DatCompetencia": "2026-06-01", "NomBandeiraAcionada": "Vermelha P1", "VlrAdicionalBandeira": "44,63"},
]


def test_resolve_bandeira_da_competencia():
    bandeira = bandeira_da_competencia(ACIO, "2026-07")
    assert bandeira["nome"] == "Amarela"
    assert bandeira["adicional_r_mwh"] == 18.85


def test_competencia_invalida_nao_e_resolvida():
    assert competencia_texto("jul/2026") is None


def test_opcoes_manuais_preservam_ultimo_valor_por_bandeira():
    opcoes = opcoes_manuais(ACIO)
    assert {opcao["nome"] for opcao in opcoes} == {"Amarela", "Vermelha P1"}
