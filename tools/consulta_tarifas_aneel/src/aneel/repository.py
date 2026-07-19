"""Fachada de acesso à fonte ANEEL, desacoplando a UI do cliente CKAN legado."""

from aneel_api import nova_sessao, registros_da_distribuidora, valores_distintos


def criar_sessao():
    return nova_sessao()


def listar_distribuidoras(session):
    return valores_distintos(session, "SigAgente")


def obter_tarifas(session, distribuidora):
    return registros_da_distribuidora(session, distribuidora)
