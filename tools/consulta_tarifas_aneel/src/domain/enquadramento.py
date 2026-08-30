"""Classificação de interface a partir do subgrupo tarifário consultado."""


def grupo_tarifario(subgrupo):
    """Retorna ``A`` ou ``B`` quando o subgrupo informado permitir classificação.

    A classificação apenas seleciona o simulador compatível na interface. Ela não
    atesta a adesão da unidade consumidora ao ACL nem sua participação no SCEE.
    """
    valor = str(subgrupo or "").strip().upper()
    if valor.startswith("A"):
        return "A"
    if valor.startswith("B"):
        return "B"
    return None


def detalhe_tarifario_padrao(detalhes_disponiveis, detalhe_documento=None):
    """Define o detalhe inicial sem substituir escolha manual válida.

    Uma informação explícita do documento prevalece quando estiver disponível na
    composição. Sem essa informação, ``Não se aplica`` é o padrão preferencial.
    """
    detalhes = list(detalhes_disponiveis)
    if detalhe_documento in detalhes:
        return detalhe_documento
    if "Não se aplica" in detalhes:
        return "Não se aplica"
    return detalhes[0] if detalhes else None
