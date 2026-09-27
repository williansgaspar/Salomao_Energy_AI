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
