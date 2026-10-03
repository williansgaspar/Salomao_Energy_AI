# Padrão do VS Code — Willians Gaspar / A-NMI

Referência única para montar (ou reconstruir) o ambiente de desenvolvimento em qualquer máquina
(laptop XPS, desktop Windows, mini PC "salomão" via Remote-SSH). Vale para todos os projetos:
`Salomao_Energy_AI`, `16_Plataforma_App`, `18_Consulta_Fotos_ARP2026`.

Última revisão: **2026-10-03**. Responsável: Willians Gaspar (decisão), via Claude Code (execução).

## 1. Extensões

**Essenciais (todos os projetos)**

| Extensão | ID | Para quê |
|---|---|---|
| Claude Code | `anthropic.claude-code` | Assistente principal |
| Codex / ChatGPT | `openai.chatgpt` | Segunda opinião; integração manual Claude↔Codex |
| Python + Pylance + Debugpy | `ms-python.python`, `.vscode-pylance`, `.debugpy` | Backend e scripts |
| Ruff | `charliermarsh.ruff` | Lint/format Python (traz o binário embutido) |
| Jupyter | `ms-toolsai.jupyter` | Análises exploratórias (ONS, Pareto/VRA) |
| Docker | `ms-azuretools.vscode-docker` | Compose do DEV/PROD |
| Remote-SSH / Remote-WSL | `ms-vscode-remote.remote-ssh`, `.remote-wsl` | Mini PC, Oracle A1, WSL2 |
| GitHub PR + Actions | `github.vscode-pull-request-github`, `github.vscode-github-actions` | PRs e CI (`tests.yml`, `deploy.yml`) |
| GitLens | `eamodio.gitlens` | Autoria por linha (apoia o HISTORICO_DE_ALTERACOES) |
| PostgreSQL | `ms-ossdata.vscode-pgsql` | Consulta ao banco DEV/PROD |
| Markdown All in One + markdownlint | `yzhang.markdown-all-in-one`, `davidanson.vscode-markdownlint` | ~70 `.md` que são fonte de verdade |
| YAML / TOML | `redhat.vscode-yaml`, `tamasfe.even-better-toml` | Workflows, compose, `ruff.toml` |
| Error Lens | `usernamehw.errorlens` | Diagnóstico inline |
| Code Spell Checker + pt-BR | `streetsidesoftware.code-spell-checker`, `…-portuguese-brazilian` | Ortografia dos documentos |
| Rainbow CSV, PDF, PowerShell | `mechatroner.rainbow-csv`, `tomoki1207.pdf`, `ms-vscode.powershell` | Dados, PDFs normativos, scripts |

**Só para projetos web (16_Plataforma_App)**: `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`,
`bradlc.vscode-tailwindcss`, `ms-playwright.playwright`.

**Removidas de propósito (não reinstalar sem motivo):** Oracle Cloud toolkits (a VM é gerida por
SSH), Microsoft Fabric/Power BI, SQL Server (`mssql`; o banco é PostgreSQL), C/C++/CMake, vscode-icons
(duplicava o Material Icon Theme), Aura, Edge DevTools, vscode-pets, Codespaces, HTML-CSS Support.

Instalar tudo de uma vez num ambiente novo:

```powershell
Get-Content .vscode\extensions.json | ConvertFrom-Json | Select -Expand recommendations | % { code --install-extension $_ }
```

## 2. Ferramentas de sistema

| Ferramenta | Como instalar | Estado em 2026-10-03 |
|---|---|---|
| ruff, pre-commit, ipykernel | `python -m pip install ruff pre-commit ipykernel` | Instalados (ruff 0.16.10, pre-commit 4.6.2) |
| pandoc | `winget install JohnMacFarlane.Pandoc` | Instalado (3.12): converte os `.md` do treinamento em `.docx` |
| uv | `winget install astral-sh.uv` | Instalado (0.11.32) |
| DBeaver Community | `winget install DBeaver.DBeaver.Community` | Instalado: cliente SQL gráfico de reserva |
| VC++ Redistributable | `winget install Microsoft.VCRedist.2015+.x64` | Instalado |
| PostgreSQL client 18.6 (`psql`, `pg_dump`) | Instalador oficial EDB, só `commandlinetools`, em `%USERPROFILE%\pgclient18` (no PATH do usuário) | Instalado; `pg_restore` bloqueado (ver abaixo) |

### `psql` no Windows e o Smart App Control

Os binários do PostgreSQL para Windows (EDB) **não têm assinatura digital**. O Smart App Control do
Windows 11 decide **arquivo por arquivo**, por reputação na nuvem. Resultado em 2026-10-03, neste laptop
(equipamento particular do Willians):

- Versão 17.11 (winget): `psql.exe` e o desinstalador bloqueados (resta pasta inerte em `C:\Program Files\PostgreSQL`).
- Versão **18.6** (instalador oficial, só cliente, em `%USERPROFILE%\pgclient18`): `psql` e `pg_dump` **rodam**;
  `pg_restore.exe` **bloqueado**. Para restaurar dump use o container: `docker compose exec db pg_restore ...`.
- Não desativar o Smart App Control só por isso (desligar é irreversível sem reinstalar o Windows).

Atalhos: `psql -h localhost -U geo_admin -d governanca_energetica` (DEV, porta 5432 do compose) ou
`docker compose exec db psql -U geo_admin governanca_energetica`. A extensão PostgreSQL do VS Code e o
DBeaver usam driver próprio e não dependem do `psql.exe`.

## 3. Configurações globais (`%APPDATA%\Code\User\settings.json`)

- Tema GitHub Dark Colorblind, fundo `#000000`, densidade compacta.
- UTF-8, fim de linha LF, apara espaços e termina arquivo com nova linha.
- **Formatar ao salvar só as linhas modificadas** (`editor.formatOnSaveMode: modifications`).
  Razão: o legado não segue o estilo do ruff/prettier; reformatar o arquivo inteiro geraria diffs
  gigantes e atrapalharia a auditoria (`git blame`, HISTORICO_DE_ALTERACOES).
- Formatadores: Ruff (Python), Prettier (JS/TS/JSON), redhat.yaml, Even Better TOML. Markdown **não**
  formata ao salvar.
- markdownlint com regras ruidosas desligadas (MD013 largura de linha, MD022, MD024, MD032, MD033, MD034, MD036, MD040, MD041, MD060).
- cSpell em `en,pt-BR` com glossário do setor (ACL, ACR, CCEE, PLD, TUSD, ARP, ANEEL…).
- Interpretador padrão: Python 3.12 do usuário.

## 4. Configuração por projeto

Cada repositório leva o seu `.vscode/extensions.json` (recomendações) e, quando preciso,
`.vscode/settings.json`. Ver a seção de VS Code do `README.md`/`CLAUDE.md` de cada um.

- `Salomao_Energy_AI`: `.vscode/extensions.json` (conjunto essencial).
- `16_Plataforma_App`: `.vscode/extensions.json` (essencial + web), `.vscode/settings.json`,
  `ruff.toml` e `.pre-commit-config.yaml`. Detalhes em `16_Plataforma_App/README.md`, seção
  "Ambiente de desenvolvimento (VS Code)".

## 5. Manutenção

- Ao instalar/remover extensão relevante, atualizar este arquivo **e** o `extensions.json` do projeto,
  na mesma sessão (regra de documentação contextual sempre atualizada).
- Registrar a mudança de padrão no `HISTORICO_DE_ALTERACOES.md` do(s) projeto(s) afetado(s).
