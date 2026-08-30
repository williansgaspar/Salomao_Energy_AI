---
target: Consulta de Tarifas ANEEL
total_score: 24
max_score: 40
na_heuristics: 
p0_count: 0
p1_count: 3
timestamp: 2026-07-25T22-34-15Z
slug: tools-consulta-tarifas-aneel-app-py
---
## Avaliação Impeccable — Consulta de Tarifas ANEEL

### Método

Avaliação dual: revisão independente de design/UX e verificação técnica independente. O detector encontrou zero achados. A inspeção visual em navegador não esteve disponível neste ambiente.

### Saúde de design

| Heurística | Pontuação | Observação-chave |
|---|---:|---|
| Visibilidade do status | 3/4 | Bons estados de carregamento e resultado; falta checklist local de requisitos. |
| Correspondência com o mundo real | 3/4 | Linguagem setorial correta, mas termos pouco frequentes carecem de orientação. |
| Controle e liberdade | 2/4 | Falta reset, histórico e resumo persistente de filtros. |
| Consistência | 3/4 | Tema, cards e ações são coerentes. |
| Prevenção de erros | 3/4 | Filtros dependentes e restrições ajudam; recuperação pode ser mais local. |
| Reconhecimento | 2/4 | Filtros avançados relevantes ficam ocultos fora da Aba 1. |
| Flexibilidade | 2/4 | Sem perfis salvos, cenários reutilizáveis ou atalho de especialista. |
| Estética e minimalismo | 2/4 | Resultado executivo compete com métricas, tabelas e auditoria. |
| Recuperação de erros | 2/4 | Mensagens são geralmente úteis, mas podem expor exceções técnicas. |
| Ajuda e documentação | 2/4 | Há tooltips, mas não glossário/contexto de tarefa. |
| **Total** | **24/40** | **Aceitável — melhorias significativas recomendadas** |

### Veredito de especificidade

O cabeçalho, a identidade municipal, a rastreabilidade ANEEL e a memória de cálculo são próprios do produto. A superfície operacional ainda é predominantemente Streamlit genérica: subcabeçalhos, alertas, métricas e dataframes empilhados. A maior oportunidade é transformar a consulta em um caso tarifário persistente e o resultado em uma conclusão decisória, deixando a auditoria como evidência secundária.

### Pontos fortes

- Credibilidade institucional: marcas, dados oficiais, rastreabilidade e linguagem adequada ao contexto regulatório.
- Fluxo setorial consistente: OCR, filtros em cascata, separação A/B, bandeiras e memória auditável.
- Bons guardrails: validações, avisos de desatualização e pré-requisitos reduzem risco de interpretação indevida.

### Prioridades

#### P1 — Tornar a entrada decisiva

Upload de fatura/planilha e configuração manual competem no mesmo início. Criar dois cartões de entrada mutuamente exclusivos e um progresso visível: Fonte → Enquadramento → Consulta.

#### P1 — Preservar o contexto tarifário

Adicionar uma faixa persistente nas abas de Simulação e Histórico com distribuidora, competência/vigência, subgrupo, modalidade, REH e detalhe. Incluir ação “Editar consulta”.

#### P1 — Criar um resumo executivo dominante

Antes das tabelas, mostrar uma conclusão: custo ACR, custo comparado, economia, premissas e pendência de verificação. Recolher memória de cálculo e linhas tarifárias por padrão.

#### P2 — Explicar termos que mudam a família tarifária

Oferecer microajuda para REH, Base tarifária, Detalhe tarifário e Acessante, explicando quando cada campo muda o resultado.

#### P2 — Assumir acessibilidade como parte do sistema visual

Adicionar foco visível de alto contraste, estados textuais para cor, regiões de status anunciáveis e teste de reflow/zoom para grids e tabelas.

### Personas

**Especialista recorrente:** precisa de perfis salvos, presets e cenários reutilizáveis; hoje reconstrói filtros e premissas a cada análise.

**Usuário ocasional:** precisa escolher entre importar e configurar manualmente sem ter de inferir qual caminho é correto; termos avançados requerem contexto.

**Usuário dependente de acessibilidade:** precisa de foco visível, reflow confiável e anúncios de mudança de status em uma interface de alta densidade.

### Questões estratégicas

- O app deve se comportar como uma tabela tarifária ou como um dossiê de decisão com evidências?
- Qual informação um gestor precisa entender em 15 segundos e qual um analista precisa auditar em 15 minutos?
- Quais presets profissionais podem eliminar filtros repetitivos sem perder rigor?
