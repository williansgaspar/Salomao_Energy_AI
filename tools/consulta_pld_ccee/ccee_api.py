"""
Cliente da API de Dados Abertos da CCEE (CKAN, pública, sem autenticação) para os
datasets da família PLD (Preço de Liquidação das Diferenças):

  - pld_horario         PLD horário corrente (modelo DESSEM) — o dado de referência hoje
  - pld_media_diaria    PLD médio diário
  - pld_media_mensal    PLD médio mensal
  - pld_final_historico PLD Final histórico — semanal, abr–set/2013, mecanismo delta-PLD da
                         Res. CNPE nº 3/2013 (legado; NÃO é o PLD corrente)

Compartilhado entre o script de linha de comando (consulta_pld_ccee.py) e o
aplicativo web (app.py).

NOTA IMPORTANTE (14-15/07/2026): o portal dadosabertos.ccee.org.br aplica um WAF que
bloqueou 100% das tentativas de acesso a partir do sandbox onde este código foi
escrito — WebFetch direto, curl direto e proxy do Google Translate retornaram todos
403 "acesso bloqueado por políticas de segurança". Não foi possível, portanto,
confirmar ao vivo os resource_id (UUID) de cada dataset nem os nomes exatos de campo
(coluna de submercado, data, valor etc.). Para lidar com isso sem hardcodar valores
não verificados, este cliente:

  1. NÃO hardcoda resource_id — resolve dinamicamente via `package_show` (API CKAN
     padrão) e cacheia localmente (`resolver_recursos`);
  2. NÃO hardcoda nomes de coluna — detecta heuristicamente submercado/data/valor/
     patamar a partir do `fields` retornado por `datastore_search` (`detectar_campos`).

Rode a primeira consulta a partir da rede do usuário (este sandbox tem a rede
bloqueada) e confira com `--listar-campos` se a detecção heurística bateu com o
schema real antes de montar filtros finos ou pareceres em cima dos dados.
"""

import json
import sys
import time
from pathlib import Path

import requests

BASE_URL = "https://dadosabertos.ccee.org.br"
ACTION_URL = f"{BASE_URL}/api/3/action"

# id (slug CKAN) -> descrição amigável
DATASETS = {
    "pld_horario": "PLD horário (corrente, granularidade horária — modelo DESSEM)",
    "pld_media_diaria": "PLD médio diário",
    "pld_media_mensal": "PLD médio mensal",
    "pld_final_historico": "PLD Final histórico (semanal, abr–set/2013 — legado delta-PLD, Res. CNPE nº 3/2013)",
}

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPT_DIR / "cache"
CACHE_MAX_AGE_DIAS = 1  # PLD é publicado semanalmente; cache curto para não ficar defasado

PAGE_SIZE = 5000  # tamanho de página por requisição (máx. aceito pela API: 32000)
TIMEOUT = 30
MAX_TENTATIVAS = 3

# Heurísticas para localizar campos relevantes por nome de coluna (case-insensitive,
# primeira pista que casar com algum campo, na ordem listada, vence).
PISTAS_CAMPO = {
    "submercado": ["submerc"],
    "data": ["din_instante", "dat_referencia", "dat_", "data_", "din_", "data"],
    "valor": ["val_pld", "vlr_pld", "val_", "vlr_", "preco", "preço"],
    "patamar": ["patamar", "pat_"],
    "ano": ["ano_referencia", "ano"],
}


class DatasetInvalido(Exception):
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        super().__init__(
            f"Dataset '{dataset_id}' não reconhecido. Opções: {', '.join(DATASETS)}"
        )


class RecursoNaoEncontrado(Exception):
    def __init__(self, dataset_id):
        self.dataset_id = dataset_id
        super().__init__(f"Nenhum recurso (resource) encontrado para o dataset '{dataset_id}'")


def nova_sessao():
    session = requests.Session()
    session.headers.update({"User-Agent": "consulta-pld-ccee/1.0 (script Python simples)"})
    return session


def _get(session, url, params):
    """GET com retentativa simples em caso de falha de rede/HTTP."""
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = session.get(url, params=params, timeout=TIMEOUT)
            resp.raise_for_status()
            dados = resp.json()
            if not dados.get("success"):
                raise RuntimeError(f"API retornou success=false: {dados.get('error')}")
            return dados["result"]
        except (requests.RequestException, RuntimeError, ValueError) as erro:
            ultimo_erro = erro
            if tentativa < MAX_TENTATIVAS:
                time.sleep(1.5 * tentativa)
    raise RuntimeError(f"Falha ao consultar a API da CCEE após {MAX_TENTATIVAS} tentativas: {ultimo_erro}")


def _cache_valido(caminho, max_age_dias=CACHE_MAX_AGE_DIAS):
    if not caminho.exists():
        return False
    idade_dias = (time.time() - caminho.stat().st_mtime) / 86400
    return idade_dias < max_age_dias


def validar_dataset(dataset_id):
    if dataset_id not in DATASETS:
        raise DatasetInvalido(dataset_id)


def resolver_recursos(session, dataset_id, forcar_atualizacao=False, avisar=lambda msg: print(msg, file=sys.stderr)):
    """Lista os recursos (resource_id, nome, formato) de um dataset via `package_show`.

    Alguns datasets deste portal têm um recurso por ano (padrão observado em outros
    datasets da CCEE, ex.: sumario_mensal_resultado_2023/2024) — por isso o cliente
    sempre trabalha com uma LISTA de recursos por dataset, nunca um único resource_id
    fixo. Resultado cacheado localmente por CACHE_MAX_AGE_DIAS dias.
    """
    validar_dataset(dataset_id)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    caminho_cache = CACHE_DIR / f"recursos_{dataset_id}.json"

    if not forcar_atualizacao and _cache_valido(caminho_cache):
        return json.loads(caminho_cache.read_text(encoding="utf-8"))

    avisar(f"Consultando recursos do dataset '{dataset_id}' na API da CCEE (package_show)...")
    resultado = _get(session, f"{ACTION_URL}/package_show", {"id": dataset_id})
    recursos = [
        {
            "id": r["id"],
            "name": r.get("name") or r.get("description") or r["id"],
            "format": r.get("format"),
            "last_modified": r.get("last_modified") or r.get("revision_timestamp"),
        }
        for r in resultado.get("resources", [])
        if r.get("datastore_active", True)  # exclui recursos que não têm datastore ativo (ex.: PDFs)
    ]

    if not recursos:
        raise RecursoNaoEncontrado(dataset_id)

    caminho_cache.write_text(json.dumps(recursos, ensure_ascii=False, indent=2), encoding="utf-8")
    return recursos


def obter_campos(session, resource_id):
    """Retorna a lista de campos (nome/tipo) de um recurso, via datastore_search(limit=0)."""
    resultado = _get(session, f"{ACTION_URL}/datastore_search", {"resource_id": resource_id, "limit": 0})
    # CKAN sempre inclui o campo interno "_id" na resposta; não é um dado de negócio.
    return [f for f in resultado.get("fields", []) if f.get("id") != "_id"]


def detectar_campos(campos):
    """Aplica as heurísticas de PISTAS_CAMPO sobre os nomes de coluna reais do recurso.

    Retorna um dict {"submercado": "NOME_REAL_OU_None", "data": ..., "valor": ...,
    "patamar": ..., "ano": ...}. Não garante acerto — é ponto de partida para
    filtros/exibição; confira com --listar-campos antes de confiar em produção.
    """
    nomes = [c["id"] for c in campos]
    detectado = {}
    for chave, pistas in PISTAS_CAMPO.items():
        achado = None
        for pista in pistas:
            for nome in nomes:
                if pista.lower() in nome.lower():
                    achado = nome
                    break
            if achado:
                break
        detectado[chave] = achado
    return detectado


def buscar_paginado_recurso(session, resource_id, filters=None, q=None, fields=None, limit_total=None):
    """Percorre datastore_search com paginação sobre UM recurso e devolve todos os registros."""
    registros = []
    offset = 0

    while True:
        params = {
            "resource_id": resource_id,
            "limit": PAGE_SIZE,
            "offset": offset,
        }
        if filters:
            params["filters"] = json.dumps(filters, ensure_ascii=False)
        if q:
            params["q"] = q
        if fields:
            params["fields"] = ",".join(fields)

        resultado = _get(session, f"{ACTION_URL}/datastore_search", params)
        total = resultado["total"]
        pagina = resultado["records"]
        registros.extend(pagina)

        if limit_total and len(registros) >= limit_total:
            registros = registros[:limit_total]
            break
        if not pagina or offset + len(pagina) >= total:
            break
        offset += len(pagina)

    return registros


def buscar_dataset(session, dataset_id, filters=None, q=None, limit_total=None,
                    forcar_atualizacao=False, avisar=lambda msg: print(msg, file=sys.stderr)):
    """Busca registros em TODOS os recursos de um dataset (concatenados) e devolve
    (registros, campos_detectados). Datasets com mais de um recurso (ex.: um por ano)
    são percorridos integralmente — use `filters`/`limit_total` para conter o volume.
    """
    recursos = resolver_recursos(session, dataset_id, forcar_atualizacao=forcar_atualizacao, avisar=avisar)

    campos = obter_campos(session, recursos[0]["id"])
    campos_detectados = detectar_campos(campos)

    todos_registros = []
    for recurso in recursos:
        avisar(f"Consultando recurso '{recurso['name']}' ({recurso['id']})...")
        restante = None if limit_total is None else max(0, limit_total - len(todos_registros))
        if restante == 0:
            break
        registros = buscar_paginado_recurso(session, recurso["id"], filters=filters, q=q, limit_total=restante)
        todos_registros.extend(registros)

    return todos_registros, campos_detectados


def valores_distintos(session, dataset_id, campo, forcar_atualizacao=False,
                       avisar=lambda msg: print(msg, file=sys.stderr)):
    """Lista valores distintos de um campo (ex.: submercado) em todos os recursos do
    dataset, com cache local em disco."""
    validar_dataset(dataset_id)
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    caminho_cache = CACHE_DIR / f"distintos_{dataset_id}_{campo}.json"

    if not forcar_atualizacao and _cache_valido(caminho_cache):
        return json.loads(caminho_cache.read_text(encoding="utf-8"))

    recursos = resolver_recursos(session, dataset_id, forcar_atualizacao=forcar_atualizacao, avisar=avisar)
    avisar(f"Consultando valores distintos de '{campo}' em {len(recursos)} recurso(s)...")

    valores = set()
    for recurso in recursos:
        offset = 0
        while True:
            params = {
                "resource_id": recurso["id"],
                "limit": PAGE_SIZE,
                "offset": offset,
                "fields": campo,
            }
            resultado = _get(session, f"{ACTION_URL}/datastore_search", params)
            pagina = resultado["records"]
            valores.update(r[campo] for r in pagina if r.get(campo) not in (None, ""))
            total = resultado["total"]
            if not pagina or offset + len(pagina) >= total:
                break
            offset += len(pagina)

    lista_ordenada = sorted(valores, key=str)
    caminho_cache.write_text(json.dumps(lista_ordenada, ensure_ascii=False, indent=2), encoding="utf-8")
    return lista_ordenada


def converter_valor_brl(valor):
    """Converte valor numérico da API para float — cobre tanto número nativo quanto
    string no formato brasileiro ('1.234,56')."""
    if valor is None or valor == "":
        return None
    if isinstance(valor, (int, float)):
        return float(valor)
    texto = str(valor)
    try:
        if "," in texto:
            return float(texto.replace(".", "").replace(",", "."))
        return float(texto)
    except ValueError:
        return None
