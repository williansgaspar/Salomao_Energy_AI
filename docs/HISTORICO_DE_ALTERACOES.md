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
