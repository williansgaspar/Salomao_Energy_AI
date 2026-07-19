"""
Cliente da API BBCE Connect (Portal do Desenvolvedor BBCE) para consulta da
BBCE Curva Forward -- a referencia de precos futuros de energia eletrica do
mercado livre brasileiro, calculada diariamente pela BBCE a partir de negocios
reais na plataforma EHUB.

Requer credenciais proprias de assinante do plano BBCE Connect (Essentials):
apiKey, e-mail, senha e codigo externo da empresa (companyExternalCode). Ver
README.md e .env.example.

Compartilhado entre o script de linha de comando (consulta_curva_forward.py)
e o aplicativo web (app.py).
"""

import json
import os
import time
from pathlib import Path

import requests

BASE_URL = os.environ.get("BBCE_BASE_URL", "https://api-beta.qa.bbce.tech/bus")

SCRIPT_DIR = Path(__file__).resolve().parent
CACHE_DIR = SCRIPT_DIR / "cache"
SESSION_CACHE_FILE = CACHE_DIR / "session.json"

TIMEOUT = 30
MAX_TENTATIVAS = 3

FONTES_ENERGIA = ["CON", "I0", "I5", "I1", "CQ5"]
SUBMERCADOS = ["SE", "SU", "NE", "NO"]
TIPOS_CURVA_PRODUTO = ["PrecoFixo", "SWAP"]


class BBCEAuthError(RuntimeError):
    """Credenciais ausentes ou rejeitadas pela API BBCE."""


class BBCECredenciais:
    """
    Credenciais de acesso ao BBCE Connect. Qualquer valor nao informado
    explicitamente cai para a variavel de ambiente equivalente (tipicamente
    vinda de um .env) -- permite tanto configuracao via .env (CLI) quanto
    valores digitados na interface (app.py).
    """

    def __init__(self, api_key=None, email=None, password=None, company_external_code=None):
        self.api_key = api_key or os.environ.get("BBCE_API_KEY", "")
        self.email = email or os.environ.get("BBCE_EMAIL", "")
        self.password = password or os.environ.get("BBCE_PASSWORD", "")
        codigo = str(company_external_code or os.environ.get("BBCE_COMPANY_EXTERNAL_CODE", "")).strip()
        if codigo:
            try:
                self.company_external_code = int(codigo)
            except ValueError:
                raise BBCEAuthError(f"Codigo da empresa invalido: '{codigo}' (deve ser numerico).")
        else:
            self.company_external_code = None

    def validar(self):
        faltando = [
            nome
            for nome, valor in [
                ("BBCE_API_KEY", self.api_key),
                ("BBCE_EMAIL", self.email),
                ("BBCE_PASSWORD", self.password),
                ("BBCE_COMPANY_EXTERNAL_CODE", self.company_external_code),
            ]
            if not valor
        ]
        if faltando:
            raise BBCEAuthError(
                "Credenciais BBCE Connect ausentes: " + ", ".join(faltando)
                + ". Configure um arquivo .env na pasta do tool (veja .env.example)."
            )


def nova_sessao():
    session = requests.Session()
    session.headers.update({"User-Agent": "consulta-curva-forward-bbce/1.0 (script Python simples)"})
    return session


def _carregar_cache_sessao():
    if SESSION_CACHE_FILE.exists():
        try:
            return json.loads(SESSION_CACHE_FILE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _salvar_cache_sessao(dados):
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    SESSION_CACHE_FILE.write_text(json.dumps(dados, ensure_ascii=False), encoding="utf-8")


def login(session, credenciais):
    """POST /v2/login -- autentica e devolve a sessao (idToken/refreshToken/expiraEm)."""
    resp = session.post(
        f"{BASE_URL}/v2/login",
        headers={"apiKey": credenciais.api_key, "Accept": "application/json", "Content-Type": "application/json"},
        json={
            "companyExternalCode": credenciais.company_external_code,
            "email": credenciais.email,
            "password": credenciais.password,
        },
        timeout=TIMEOUT,
    )
    if resp.status_code == 422:
        raise BBCEAuthError("Credenciais BBCE invalidas (e-mail, senha ou companyExternalCode).")
    resp.raise_for_status()
    dados = resp.json()
    sessao = {
        "idToken": dados["idToken"],
        "refreshToken": dados["refreshToken"],
        "companyId": dados.get("companyId"),
        "userId": dados.get("userId"),
        "expiraEm": time.time() + dados.get("expiresIn", 14400) - 60,
        "email": credenciais.email,
        "companyExternalCode": credenciais.company_external_code,
    }
    _salvar_cache_sessao(sessao)
    return sessao


def refresh_token(session, credenciais, sessao):
    """POST /v1/refresh-token -- renova o idToken usando o refreshToken salvo."""
    resp = session.post(
        f"{BASE_URL}/v1/refresh-token",
        headers={
            "apiKey": credenciais.api_key,
            "Authorization": f"Bearer {sessao['idToken']}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        json={"refreshToken": sessao["refreshToken"]},
        timeout=TIMEOUT,
    )
    resp.raise_for_status()
    dados = resp.json()
    nova = dict(sessao)
    nova["idToken"] = dados["idToken"]
    nova["refreshToken"] = dados.get("refreshToken", sessao["refreshToken"])
    nova["expiraEm"] = time.time() + dados.get("expiresIn", 14400) - 60
    _salvar_cache_sessao(nova)
    return nova


def obter_sessao(session, credenciais):
    """Garante um idToken valido: reusa cache, renova via refresh-token, ou faz login novo.

    O cache so e reaproveitado se pertencer a mesma conta (email +
    companyExternalCode) das credenciais atuais -- evita misturar tokens ao
    trocar de usuario/empresa na interface.
    """
    credenciais.validar()
    sessao = _carregar_cache_sessao()
    mesma_conta = bool(sessao) and sessao.get("email") == credenciais.email \
        and sessao.get("companyExternalCode") == credenciais.company_external_code
    if mesma_conta and sessao.get("expiraEm", 0) > time.time():
        return sessao
    if mesma_conta and sessao.get("refreshToken"):
        try:
            return refresh_token(session, credenciais, sessao)
        except requests.RequestException:
            pass
    return login(session, credenciais)


def _headers_autenticados(credenciais, sessao):
    return {
        "apiKey": credenciais.api_key,
        "Authorization": f"Bearer {sessao['idToken']}",
        "Accept": "application/json",
    }


def _get(session, credenciais, path, params=None):
    """GET autenticado, com retentativa e reautenticacao automatica em 401/403."""
    sessao = obter_sessao(session, credenciais)
    params_limpos = {k: v for k, v in (params or {}).items() if v not in (None, "")}
    ultimo_erro = None
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            resp = session.get(
                f"{BASE_URL}{path}",
                headers=_headers_autenticados(credenciais, sessao),
                params=params_limpos,
                timeout=TIMEOUT,
            )
            if resp.status_code in (401, 403) and tentativa == 1:
                sessao = login(session, credenciais)
                continue
            resp.raise_for_status()
            return resp.json()
        except requests.RequestException as erro:
            ultimo_erro = erro
            if tentativa < MAX_TENTATIVAS:
                time.sleep(1.5 * tentativa)
    raise RuntimeError(f"Falha ao consultar {path} apos {MAX_TENTATIVAS} tentativas: {ultimo_erro}")


def curva_forward(session, credenciais, data_referencia, fonte=None, regiao=None):
    """GET /v1/curve/bbce-fwd -- curva forward geral (preco projetado por vertice de data)."""
    return _get(session, credenciais, "/v1/curve/bbce-fwd", {
        "referenceDate": data_referencia,
        "energyType": fonte,
        "region": regiao,
    })


def curva_por_produto(session, credenciais, data_referencia, fonte=None, tipo_curva=None):
    """GET /v1/curve-product/bbce-fwd -- curva forward por ticker/produto negociavel."""
    return _get(session, credenciais, "/v1/curve-product/bbce-fwd", {
        "referenceDate": data_referencia,
        "energyType": fonte,
        "curveType": tipo_curva,
    })


def historico_contribuicoes(session, credenciais, data_inicio, data_fim, ticker_ids=None, user_ids=None):
    """GET /v1/call/report -- historico de contribuicoes ("calls") de preco por periodo."""
    return _get(session, credenciais, "/v1/call/report", {
        "contributionStartDate": data_inicio,
        "contributionEndDate": data_fim,
        "tickerIds": ticker_ids,
        "userIds": user_ids,
    })
