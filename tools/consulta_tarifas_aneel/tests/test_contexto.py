from src.domain.contexto import fingerprint_simulacao


def test_fingerprint_independe_da_ordem_das_chaves():
    assert fingerprint_simulacao({"a": 1, "b": 2}) == fingerprint_simulacao({"b": 2, "a": 1})


def test_fingerprint_muda_quando_parametro_muda():
    anterior = fingerprint_simulacao({"consumo": 18, "composicao": "A"})
    atual = fingerprint_simulacao({"consumo": 19, "composicao": "A"})
    assert anterior != atual
