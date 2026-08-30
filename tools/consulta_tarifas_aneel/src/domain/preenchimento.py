"""Mapeia grandezas extraídas da fatura para os postos da composição ANEEL."""


def _valores_para_postos(valores_documentais, postos_da_composicao):
    """Preserva correspondência direta e cobre equivalências tarifárias seguras."""
    valores_documentais = valores_documentais or {}
    postos_da_composicao = list(postos_da_composicao or [])
    resultado = {
        posto: float(valores_documentais[posto])
        for posto in postos_da_composicao if posto in valores_documentais
    }
    if len(postos_da_composicao) != 1 or resultado:
        return resultado

    # Grupo B e a demanda Verde podem ser registrados na fatura em um posto e
    # disponibilizados pela composição ANEEL em outro. Com apenas um posto
    # tarifário, a equivalência é inequívoca; em qualquer outro caso, o valor
    # fica para confirmação manual.
    unico_posto = postos_da_composicao[0]
    if len(valores_documentais) == 1:
        resultado[unico_posto] = float(next(iter(valores_documentais.values())))
    return resultado


def grandezas_para_composicao(grandezas_documentais, postos_energia, postos_demanda):
    """Entrega somente valores que podem preencher a composição selecionada."""
    grandezas_documentais = grandezas_documentais or {}
    return {
        "consumos_mwh": _valores_para_postos(grandezas_documentais.get("consumos_mwh"), postos_energia),
        "demandas_kw": _valores_para_postos(grandezas_documentais.get("demandas_kw"), postos_demanda),
    }
