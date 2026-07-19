"""
Cliente da API de Dados Abertos da ANEEL (CKAN, pública, sem autenticação) para o
dataset "Tarifas de aplicação das distribuidoras de energia elétrica".

Compartilhado entre o script de linha de comando (consulta_tarifas_aneel.py) e o
aplicativo web (app.py).
"""

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import requests

BASE_URL = "https://dadosabertos.aneel.gov.br/api/3/action/datastore_search"
RESOURCE_ID = "fcf2906c-7c32-4b9b-a637-054e7a5234f4"  # tarifas-homologadas-distribuidoras-energia-eletrica.csv

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPT_DIR / "cache"
CACHE_MAX_AGE_DIAS = 7

PAGE_SIZE = 5000  # tamanho de página por requisição (máx. aceito pela API: 32000)
TIMEOUT = 30
MAX_TENTATIVAS = 3

CAMPOS = [
    "DatGeracaoConjuntoDados", "DscREH", "SigAgente", "NumCNPJDistribuidora",
    "DatInicioVigencia", "DatFimVigencia", "DscBaseTarifaria", "DscSubGrupo",
    "DscModalidadeTarifaria", "DscClasse", "DscSubClasse", "DscDetalhe",
    "NomPostoTarifario", "DscUnidadeTerciaria", "SigAgenteAcessante",
    "VlrTUSD", "VlrTE",
]


def nova_sessao():
    session = requests.Session()
    session.headers.update({"User-Agent": "consulta-tarifas-aneel/1.0 (script Python simples)"})
    return session


def _get(session, params):
    """GET com retentativa simples em caso de falha de rede/HTTP."""
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = session.get(BASE_URL, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            dados = resp.json()
            if not dados.get("success"):
                raise RuntimeError(f"API retornou success=false: {dados.get('error')}")
            return dados["result"]
        except (requests.RequestException, RuntimeError, ValueError) as erro:
            ultimo_erro = erro
            if tentativa < MAX_TENTATIVAS:
                time.sleep(1.5 * tentativa)
    raise RuntimeError(f"Falha ao consultar a API da ANEEL após {MAX_TENTATIVAS} tentativas: {ultimo_erro}")


def buscar_paginado(session, filters=None, q=None, fields=None, limit_total=None):
    """Percorre datastore_search com paginação e devolve todos os registros."""
    registros = []
    offset = 0
    total = None

    while True:
        params = {
            "resource_id": RESOURCE_ID,
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        if filters:
            params["filters"] = json.dumps(filters, ensure_ascii=False)
        if q:
            params["q"] = q
        if fields:
            params["fields"] = ",".join(fields)

        resultado = _get(session, params)
        total = resultado["total"]
        pagina = resultado["records"]
        registros.extend(pagina)

        if limit_total and len(registros) >= limit_total:
            registros = registros[:limit_total]
            break
        if not pagina or offset + len(pagina) >= total:
            break
        offset += len(pagina)

    return registros, total


def _cache_valido(caminho):
    if not caminho.exists():
        return False
    idade_dias = (time.time() - caminho.stat().st_mtime) / 86400
    return idade_dias < CACHE_MAX_AGE_DIAS


def valores_distintos(session, campo, forcar_atualizacao=False, avisar=lambda msg: print(msg, file=sys.stderr)):
    """Lista valores distintos de um campo (ex.: SigAgente), com cache local em disco."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    caminho_cache = CACHE_DIR / f"distintos_{campo}.json"

    if not forcar_atualizacao and _cache_valido(caminho_cache):
        return json.loads(caminho_cache.read_text(encoding="utf-8"))

    avisar(f"Consultando valores distintos de '{campo}' na API da ANEEL (pode levar ~1 min)...")
    valores = set()
    offset = 0
    while True:
        params = {
            "resource_id": RESOURCE_ID,
            "limit": PAGE_SIZE,
            "offset": offset,
            "fields": campo,
        }
        resultado = _get(session, params)
        pagina = resultado["records"]
        valores.update(r[campo] for r in pagina if r.get(campo))
        total = resultado["total"]
        if not pagina or offset + len(pagina) >= total:
            break
        offset += len(pagina)

    lista_ordenada = sorted(valores)
    caminho_cache.write_text(json.dumps(lista_ordenada, ensure_ascii=False, indent=2), encoding="utf-8")
    return lista_ordenada


def registros_da_distribuidora(session, sig_agente, fields=None):
    """Busca todos os registros de uma distribuidora (geralmente cabe em 1-2 páginas)."""
    registros, _ = buscar_paginado(session, filters={"SigAgente": sig_agente}, fields=fields)
    return registros


class DistribuidoraAmbigua(Exception):
    """Termo de busca corresponde a mais de uma distribuidora."""

    def __init__(self, termo, candidatas):
        self.termo = termo
        self.candidatas = candidatas
        super().__init__(f"'{termo}' é ambíguo: {len(candidatas)} distribuidoras encontradas")


class DistribuidoraNaoEncontrada(Exception):
    """Termo de busca não corresponde a nenhuma distribuidora."""

    def __init__(self, termo):
        self.termo = termo
        super().__init__(f"Nenhuma distribuidora encontrada para '{termo}'")


def resolver_distribuidora(session, termo, forcar_atualizacao=False):
    """Resolve um termo de busca (parcial ou exato) para o SigAgente exato na base.

    Levanta DistribuidoraAmbigua ou DistribuidoraNaoEncontrada quando não há um
    único resultado; chamadores (CLI, web) decidem como reagir a cada caso.
    """
    termo_upper = termo.strip().upper()

    # Tentativa 1: match exato direto (evita baixar a lista completa de agentes)
    resultado = _get(session, {
        "resource_id": RESOURCE_ID,
        "filters": json.dumps({"SigAgente": termo_upper}, ensure_ascii=False),
        "limit": 1,
    })
    if resultado["total"] > 0:
        return termo_upper

    # Tentativa 2: match parcial contra a lista de distribuidoras (com cache)
    distribuidoras = valores_distintos(session, "SigAgente", forcar_atualizacao=forcar_atualizacao)
    candidatas = [d for d in distribuidoras if termo_upper in d]

    if len(candidatas) == 1:
        return candidatas[0]
    if len(candidatas) > 1:
        raise DistribuidoraAmbigua(termo, candidatas)
    raise DistribuidoraNaoEncontrada(termo)


def ano_da_vigencia(registro):
    """Extrai o ano de início de vigência (int) de um registro, ou None se mal formatado."""
    try:
        return datetime.strptime(registro["DatInicioVigencia"], "%Y-%m-%d").year
    except (ValueError, KeyError, TypeError):
        return None


def _data(texto):
    try:
        return datetime.strptime(texto, "%Y-%m-%d").date()
    except (ValueError, KeyError, TypeError):
        return None


def vigente_em(registro, data_referencia):
    """True se o registro está vigente na data de referência (mês de referência).

    DatFimVigencia em branco é tratada como vigência em aberto (sem data de fim).
    """
    inicio = _data(registro.get("DatInicioVigencia"))
    if inicio is None or inicio > data_referencia:
        return False
    fim = _data(registro.get("DatFimVigencia"))
    return fim is None or data_referencia <= fim


def converter_valor_brl(valor_texto):
    """Converte string no formato brasileiro ('1,85' / ',00') para float."""
    if valor_texto is None or valor_texto == "":
        return None
    try:
        return float(valor_texto.replace(".", "").replace(",", "."))
    except ValueError:
        return None
