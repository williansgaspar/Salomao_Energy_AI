#!/bin/sh
set -eu

if [ "${SALOMAO_REQUIRE_LOGIN:-false}" = "true" ]; then
    : "${SALOMAO_AUTH_REDIRECT_URI:?Defina SALOMAO_AUTH_REDIRECT_URI}"
    : "${SALOMAO_AUTH_COOKIE_SECRET:?Defina SALOMAO_AUTH_COOKIE_SECRET}"
    : "${SALOMAO_AUTH_CLIENT_ID:?Defina SALOMAO_AUTH_CLIENT_ID}"
    : "${SALOMAO_AUTH_CLIENT_SECRET:?Defina SALOMAO_AUTH_CLIENT_SECRET}"
    : "${SALOMAO_AUTH_TENANT_ID:?Defina SALOMAO_AUTH_TENANT_ID}"

    python - <<'PY'
import json
import os
from pathlib import Path

def quoted(name):
    return json.dumps(os.environ[name])

Path(".streamlit").mkdir(exist_ok=True)
Path(".streamlit/secrets.toml").write_text(
    "[auth]\\n"
    f"redirect_uri = {quoted('SALOMAO_AUTH_REDIRECT_URI')}\\n"
    f"cookie_secret = {quoted('SALOMAO_AUTH_COOKIE_SECRET')}\\n\\n"
    "[auth.microsoft]\\n"
    f"client_id = {quoted('SALOMAO_AUTH_CLIENT_ID')}\\n"
    f"client_secret = {quoted('SALOMAO_AUTH_CLIENT_SECRET')}\\n"
    "server_metadata_url = "
    f"{json.dumps('https://login.microsoftonline.com/' + os.environ['SALOMAO_AUTH_TENANT_ID'] + '/v2.0/.well-known/openid-configuration')}\\n",
    encoding="utf-8",
)
PY
fi

exec streamlit run app.py --server.address=0.0.0.0 --server.port="${PORT:-8501}" --server.headless=true
