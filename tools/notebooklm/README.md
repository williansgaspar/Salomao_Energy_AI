# NotebookLM / Gemini Notebook no SalomãoAI

Este diretório padroniza o uso do NotebookLM no projeto. O Google passou a entregar a interface deste ambiente em `https://notebook.google.com`; versões atuais do `notebooklm-py` ainda restringem a configuração aos hosts históricos `notebooklm.google.com` e `notebooklm.cloud.google.com`.

`Salomao-NotebookLM.ps1` resolve esse descompasso de forma idempotente:

1. localiza o ambiente isolado instalado pelo `uv`;
2. aplica uma compatibilidade estrita, limitada a `notebook.google.com` e aos cookies desse domínio;
3. usa o executável isolado, evitando outro `notebooklm.exe` que possa existir no `PATH`;
4. configura `NOTEBOOKLM_BASE_URL` apenas para o processo chamado.

## Pré-requisito único

Instale a ferramenta isolada com o Python local autorizado pelo Windows:

```powershell
uv tool install --force --python "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" "notebooklm-py[browser]"
```

O script cria uma cópia de segurança única dos arquivos alterados do pacote em `*.salomaoai-backup`, dentro do ambiente do `uv` (nunca no repositório).

## Operação

```powershell
# Validação de rede e credencial (comando padrão)
.\tools\notebooklm\Salomao-NotebookLM.ps1 check

# Login interativo; conclua na janela Chromium aberta e mantenha-a aberta
# até o terminal informar que a autenticação foi salva.
.\tools\notebooklm\Salomao-NotebookLM.ps1 login

# Inventário de notebooks
.\tools\notebooklm\Salomao-NotebookLM.ps1 list

# Qualquer comando da CLI. Use IDs completos em automações.
.\tools\notebooklm\Salomao-NotebookLM.ps1 run source list -n <notebook-id>
```

## Segurança e operação

- As credenciais ficam em `C:\Users\willi\.notebooklm\profiles\default\storage_state.json`; são credenciais portadoras e não devem ser copiadas para o projeto, commits, logs ou mensagens.
- O wrapper não persiste variáveis de ambiente no Windows. Ele só define a URL base dentro do processo da chamada.
- Antes de rotinas automatizadas, execute `check`; só prossiga quando o JSON retornar `status: "ok"` e `checks.token_fetch: true`.
- Para fluxos concorrentes, passe sempre `-n <UUID completo>` aos comandos do NotebookLM e não dependa de `notebooklm use`.
