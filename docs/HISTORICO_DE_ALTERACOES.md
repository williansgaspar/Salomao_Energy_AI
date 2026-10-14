# Histórico de Alterações — Salomão

Registro cronológico (mais recente no topo) de **achados, alterações, correções de bug,
edições, exclusões e adições** relevantes deste projeto, para fins de auditoria e
rastreabilidade — mesmo padrão adotado em `16_Plataforma_App` e `18_Consulta_Fotos_ARP2026`.

Cada entrada traz **o que, por quê, quando e quem**.

**Não substitui** a documentação de governança já existente — é o ponto de entrada único que
amarra tudo numa linha do tempo, com link para o detalhe:

| Já existe | Serve para |
|---|---|
| `docs/ADR-00N-*.md` | Decisões de arquitetura, com alternativas consideradas e motivação completa. |
| `docs/AUDITORIA_*.md`, `docs/RELATORIO_IMPLEMENTACAO_*.md` | Relatórios de auditoria/implementação de um marco específico, na íntegra. |
| `docs/STATUS_OPERACIONAL_SALOMAO_AI.md` | Estado operacional atual + atualizações datadas recentes. |
| `git log` | Detalhe técnico linha a linha de cada commit. |

**Regra:** toda mudança não trivial (decisão de arquitetura, segurança, dado sensível,
comportamento em produção, achado relevante de auditoria) ganha uma entrada aqui na mesma
tarefa em que acontece — mesmo que o detalhe completo more num ADR/relatório à parte; aqui fica
pelo menos o resumo com quem/por quê/quando e o link para o documento completo.

| Campo | Conteúdo |
|---|---|
| Tipo | Achado / Alteração / Correção / Edição / Exclusão / Adição |
| O que | Descrição objetiva e verificável |
| Por quê | Motivação, decisão ou causa raiz |
| Quando | Data |
| Quem | Quem decidiu/autorizou + quem executou (ex.: "Willians Gaspar, via Claude Code") |
| Referência | Commit, ADR, relatório ou arquivo relacionado |

---

## 2026-10-03

### Adição — Padrão geral do VS Code (`docs/PADRAO_VSCODE.md`) e `.vscode/extensions.json`

| Campo | Conteúdo |
|---|---|
| Tipo | Adição / Exclusão (ambiente de desenvolvimento; sem efeito nos dados do Salomão) |
| O que | Criado `docs/PADRAO_VSCODE.md` (extensões essenciais e removidas, ferramentas de sistema, configurações globais, manutenção) e `.vscode/extensions.json`. Removidas 27 extensões sem uso (Oracle, Fabric/Power BI, SQL Server, C/C++, temas redundantes); instaladas 16 (Ruff, PostgreSQL, GitLens, Jupyter [depois desinstalado no mesmo dia; ver entrada de 2026-10-03 abaixo], markdownlint, cSpell pt-BR, ESLint, Prettier, Tailwind, Playwright etc.). `settings.json` do usuário ajustado (UTF-8/LF, formatação só das linhas modificadas, cSpell com glossário do setor). Instalados no sistema: ruff, pre-commit, ipykernel, pandoc, uv, DBeaver. |
| Por quê | Pedido do Willians: padronizar o ambiente entre máquinas e projetos. `psql` 17 (winget) foi bloqueado pelo Smart App Control (binário sem assinatura); a política não foi contornada. Depois o Willians baixou o instalador oficial 18.6: `psql` e `pg_dump` rodam, `pg_restore` segue bloqueado (usar via container). Correção posterior (registrada em 2026-10-14): o laptop é de propriedade particular do Willians, não equipamento público; o texto original dizia o contrário. |
| Quando | 2026-10-03 |
| Quem | Willians Gaspar (autorizou), via Claude Code (execução) |
| Referência | `docs/PADRAO_VSCODE.md`; `16_Plataforma_App/HISTORICO_DE_ALTERACOES.md` (entrada de mesma data) |

### Alteração — Ajustes posteriores do padrão do VS Code (commits `593bc08`, `077d3af`, `31da97d`, `c66c1f4`)

| Campo | Conteúdo |
|---|---|
| Tipo | Alteração / Exclusão (ambiente de desenvolvimento) |
| O que | `.editorconfig` (UTF-8, LF, indentação) sem alterar as regras de fim de linha dos textos normativos; 3 extensões novas recomendadas (`pretty-ts-errors`, `gc-excelviewer`, `git-graph`); Jupyter (e associadas), Live Server, `openai.chatgpt`, `openai.codex-audio` e `graphify-vscode` movidos para `unwantedRecommendations` e desinstalados. `docs/PADRAO_VSCODE.md` alinhado ao `extensions.json` em 2026-10-14. |
| Por quê | Enxugar o ambiente depois da primeira rodada; o Jupyter e o Codex no VS Code não eram usados. Entrada criada com atraso (revisão de 2026-10-14 apontou a lacuna). |
| Quando | 2026-10-03 (commits); 2026-10-14 (registro e ajuste do PADRAO) |
| Quem | Willians Gaspar (decidiu), via Claude Code (execução) |
| Referência | Commits `593bc08`, `077d3af`, `31da97d`, `c66c1f4`; `.vscode/extensions.json`; `docs/PADRAO_VSCODE.md` |

### Adição — Fluxograma do processo DEVEC/ICMS da energia no ACL (`docs/diagramas/fluxo-devec-icms-acl.html`)

| Campo | Conteúdo |
|---|---|
| Tipo | Adição (material de apoio; não é fonte normativa final) |
| O que | Fluxograma interativo (skill `fluxograma`) do processo DEVEC da SEFAZ-RJ. Partiu de um rascunho em Mermaid gerado pelo Gemini e foi revisado contra o Manual DEVEC v1.1 (jan/2018) e as Res. SEFAZ 177/2017, 19/2019 e 62/2019, que alteram o Anexo XV da Res. SEFAZ 720/2014, e a Res. CGM 2082/2025 (prazos da PCRJ) (texto lido em republicações, não no DOE). Correções principais: janela do consumidor (o rascunho dizia dias 01–14; o diagrama usa o prazo de dia 14, que consta no manual v1.1, na Res. CGM 2082/2025 e na cartilha da CCEE, mas **não está confirmado em norma**: o art. 16 na redação da Res. SEFAZ 177/2017 diz dia 10 e o ato que mudou o prazo não foi localizado); status I/C/N do arquivo de preço médio; dispensa anual; retificação (art. 17-A) e extemporânea (art. 17-B) separadas; análise pela AFE 03. |
| Por quê | Pedido do Willians (A/NMI) para entender o processo e, depois, confrontar o rascunho com fonte oficial. |
| Quando | 2026-10-03 |
| Quem | Willians Gaspar (pedido), via Claude Code (execução) |
| Ajuste de layout (campo extra, não previsto na tabela de campos) | Fluxo dobrado em duas camadas (linha de cima da esquerda para a direita, a de baixo de volta) e retificação no canto esquerdo: largura de 4.884 px para 2.552 px (22 para 11 colunas). No arquivo do diagrama, o motor ganhou coluna fixa por caixa (`col`), lado de saída/entrada nas setas do `DADOS` e numeração das etapas na ordem narrativa; as chaves de armazenamento do navegador foram renovadas, então posições arrastadas antes não valem mais. |
| Referência | `docs/diagramas/fluxo-devec-icms-acl.html` (commit desta entrada). Pontos em aberto no próprio diagrama ("Pontos a confirmar"): ato que mudou o prazo de dia 10 para 14, manual vigente (v1.8B citado pela Consulta 54/2021), recolhimento (DARJ/GNRE) e desfecho do indeferimento. |

---

## 2026-09-27

### Alteração (infraestrutura) — Repositório sai do OneDrive e passa a morar em `C:\dev\Salomao_Energy_AI`
- **O que:** cópia integral da pasta (incluindo `.git`, `secrets.toml` do app de tarifas,
  `.claude/`, `.codex/`, `evals/resultados/` e `tmp/`; sem `__pycache__`, logs e `.pid`) de
  `OneDrive - OnEnergy\0 PCRJ_PEE\Meta_2026_...\Projects\Salomao_Energy_AI` para
  `C:\dev\Salomao_Energy_AI`, fora de qualquer pasta sincronizada. Validação: `git fsck` sem
  erro, mesmo HEAD (`5a859c0`) e mesma `main` local (`557ee05`, que não existe no GitHub),
  `git fetch` funcionando e 81 testes aprovados no novo local. O `CLAUDE.md` da pasta
  `Meta_2026_...` foi copiado para `C:\dev\CLAUDE.md` para continuar sendo carregado.
- **Por quê:** problema de armazenamento no OneDrive (tenant x2p34) levou à migração dos
  arquivos para o Google Drive desktop (streaming); repositório git dentro de pasta
  sincronizada arrisca conflito e corrupção do `.git`. Executa a ação P2 de
  `docs/PLANO_ORGANIZACAO_IA_2026-07-25.md`.
- **Quando:** 2026-09-27.
- **Quem:** Willians Gaspar (decisão), via Claude Code (execução).
- **Referência:** este commit. A cópia antiga no OneDrive e a cópia em
  `G:\Meu Drive\OnEnergy\...` ficam congeladas como rollback; ambas ainda contêm o
  `secrets.toml` (pendência P0 do plano: retirar segredos de área sincronizada).

## 2026-09-26

### Alteração (segurança) — Credenciais no cofre Bitwarden; assinatura de commits fica desligada neste repositório
- **O que:** o Willians passou a usar o cofre **Bitwarden** (2FA duplo) para chaves SSH e
  senhas, e os commits feitos no XPS passaram a ser **assinados** (`commit.gpgsign=true`
  global, chave SSH do cofre, e-mail privado do GitHub). **Neste repositório** a assinatura
  ficou **desligada** (`commit.gpgsign=false` e `tag.gpgsign=false` na config local), para
  preservar a identidade própria "Salomao Energy AI" (`salomao-energy-ai@local.invalid`), que
  não é conta do GitHub e apareceria como "não verificada". O fluxo de commits daqui não muda.
- **Por quê:** auditoria de autoria no ecossistema (sistema de órgão público); aqui a identidade
  do agente é deliberada.
- **Quando:** 2026-09-26.
- **Quem:** Willians Gaspar (decisão), via Claude Code.
- **Referência:** `16_Plataforma_App/SEGURANCA_CREDENCIAIS.md` (inventário completo de
  credenciais, cofre e procedimento de emergência) e `16_Plataforma_App/HISTORICO_DE_ALTERACOES.md`
  (26/09/2026). Contexto do mesmo dia: a produção do 16_Plataforma_App migrou da AWS para a
  Oracle Cloud (`DEPLOY_VPS_ORACLE.md` daquele repositório).

## 2026-09-05

### Adição — Este arquivo (prática de auditoria)
- **O que:** criação de `docs/HISTORICO_DE_ALTERACOES.md` como ponto de entrada cronológico
  único do projeto, referenciando (sem duplicar) os ADRs, relatórios de auditoria e o
  `STATUS_OPERACIONAL_SALOMAO_AI.md` já existentes.
- **Por quê:** pedido explícito do Willians por rastreabilidade e auditagem de todo achado,
  alteração, correção, edição, exclusão e adição em seus projetos ativos — mesmo padrão
  replicado em `16_Plataforma_App` e `18_Consulta_Fotos_ARP2026`.
- **Quando:** 2026-09-05.
- **Quem:** Willians Gaspar, via Claude Code.

> **Nota sobre o histórico anterior a esta data:** este projeto já documentava decisões e
> auditorias de forma estruturada antes deste arquivo existir (ver tabela acima) — não foi
> reconstruída aqui uma entrada retroativa para cada uma, para não arriscar atribuir
> motivação/autoria de forma imprecisa a decisões tomadas em sessões anteriores sem revisitar
> cada documento a fundo. Para o histórico completo pré-2026-09-05, consulte os ADRs, os
> relatórios `AUDITORIA_*`/`RELATORIO_IMPLEMENTACAO_*` e `git log`.
