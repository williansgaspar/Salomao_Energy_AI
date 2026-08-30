"""Consulta e resolução mensal das bandeiras tarifárias da ANEEL."""

from datetime import date, datetime

from aneel_api import BASE_URL, TIMEOUT, converter_valor_brl


RECURSO_ACIONAMENTO = "0591b8f6-fe54-437b-b72b-1aa2efd46e42"


def listar_acionamentos(session):
    """Obtém o histórico mensal oficial de acionamento das bandeiras."""
    resposta = session.get(
        BASE_URL,
        params={
            "resource_id": RECURSO_ACIONAMENTO,
            "limit": 5000,
            "sort": "DatCompetencia desc",
        },
        timeout=TIMEOUT,
    )
    resposta.raise_for_status()
    dados = resposta.json()
    if not dados.get("success"):
        raise RuntimeError(f"API ANEEL retornou success=false: {dados.get('error')}")
    return dados["result"]["records"]


def competencia_texto(valor):
    """Normaliza data/competência para AAAA-MM."""
    if isinstance(valor, date):
        return valor.strftime("%Y-%m")
    texto = str(valor or "").strip()
    if len(texto) >= 7:
        try:
            return datetime.strptime(texto[:7], "%Y-%m").strftime("%Y-%m")
        except ValueError:
            return None
    return None


def bandeira_da_competencia(acionamentos, competencia):
    """Retorna nome, adicional R$/MWh e competência do acionamento oficial."""
    competencia = competencia_texto(competencia)
    if not competencia:
        return None
    for registro in acionamentos:
        if competencia_texto(registro.get("DatCompetencia")) == competencia:
            adicional = converter_valor_brl(registro.get("VlrAdicionalBandeira"))
            if adicional is None:
                return None
            return {
                "competencia": competencia,
                "nome": registro.get("NomBandeiraAcionada") or "Não informada",
                "adicional_r_mwh": adicional,
                "fonte": "ANEEL — Bandeira Tarifária - Acionamento",
            }
    return None


def opcoes_manuais(acionamentos):
    """Último adicional publicado por bandeira, para seleção manual auditável."""
    por_nome = {}
    for registro in acionamentos:
        nome = registro.get("NomBandeiraAcionada")
        adicional = converter_valor_brl(registro.get("VlrAdicionalBandeira"))
        competencia = competencia_texto(registro.get("DatCompetencia"))
        if not nome or adicional is None or not competencia:
            continue
        atual = por_nome.get(nome)
        if atual is None or competencia > atual["competencia"]:
            por_nome[nome] = {"competencia": competencia, "nome": nome, "adicional_r_mwh": adicional}
    return [por_nome[nome] for nome in sorted(por_nome)]
