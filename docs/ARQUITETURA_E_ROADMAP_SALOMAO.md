# Arquitetura e roadmap do Salomão

**Status:** diagnóstico inicial  
**Data:** 19/07/2026  
**Objetivo:** transformar o acervo atual em um agente técnico-regulatório rastreável, atualizável e testável.

## 1. Diagnóstico executivo

O projeto já tem três ativos importantes: uma identidade bem delimitada, cinco skills temáticas coerentes e uma base local que combina legislação, índices operacionais da CCEE, boletim de atualizações e ferramentas de consulta.

A lacuna principal não é quantidade de conteúdo. É governança do conhecimento. Hoje, alegações normativas, observações de mercado e inferências aparecem juntas em arquivos Markdown. A data de coleta é registrada, mas não há um mecanismo uniforme para ligar cada alegação ao texto primário, ao dispositivo, à vigência temporal e a um teste que detecte regressões.

Também há riscos operacionais imediatos: o repositório ainda não possui commit inicial; artefatos locais e um arquivo de chave de API estavam preparados para versionamento; não existe suíte de avaliações; e parte relevante da base contém índices/metadados, não os textos integrais das fontes primárias.

## 2. Decisão arquitetural proposta

Adotar quatro camadas separadas:

1. **Instruções globais** — `AGENTS.md` e `CLAUDE.md`: identidade, tom, política de fontes, protocolo de vigência e regras de segurança epistemológica.
2. **Skills procedurais** — `skills/`: como executar uma classe de trabalho. Devem conter fluxo, critérios de decisão e rotas para referências; fatos voláteis devem ficar fora do corpo principal.
3. **Base de evidências** — `Legislacao/` e `knowledge_base/`: textos primários, metadados normalizados e cadeia de vigência. Índices e boletins são instrumentos de descoberta, não prova jurídica final.
4. **Avaliações** — `evals/`: casos com critérios verificáveis para citações, vigência, distinção entre regra e proposta, cálculos e recusa calibrada.

Essa separação reduz três falhas comuns: conhecimento volátil embutido na skill, citação circular de resumos internos e respostas persuasivas sem prova normativa suficiente.

## 3. Achados prioritários

### P0 — antes do primeiro commit

- Remover do índice Git qualquer segredo, log, PID, bytecode e arquivo de sistema.
- Rotacionar a chave existente em `tools/brightdata - API Key.txt` se ela já tiver sido compartilhada fora da máquina, mesmo que ainda não exista commit.
- Criar o commit-base somente depois de revisar os arquivos atualmente staged.

### P1 — confiabilidade regulatória

- Criar um catálogo estruturado de normas com, no mínimo: tipo, número, data, órgão, assunto, URI oficial, caminho local, status, início/fim de vigência, alterações, dispositivos relevantes, data e método da última verificação.
- Distinguir em toda resposta: **texto normativo**, **interpretação**, **informação de processo regulatório** e **inferência**.
- Proibir que índice, boletim, prova ou glossário seja citado como fonte final quando a afirmação depender do texto de uma norma.
- Revisar afirmações temporais inseridas diretamente nas skills, especialmente abertura do ACL, MMGD, descontos TUSD/TUST, armazenamento, CDE e versões de Regras/Procedimentos CCEE.

### P1 — qualidade das skills

- Manter o corpo de cada `SKILL.md` procedural e mover fatos detalhados/voláteis para referências versionadas.
- Adicionar roteamento explícito de fontes por tema e condição de parada: se não houver texto primário confirmado, declarar a limitação em vez de completar por memória.
- Evitar duplicação entre `AGENTS.md` e `CLAUDE.md`; eleger uma fonte canônica e gerar/sincronizar a outra quando necessário.
- Adicionar validação automática de frontmatter, links locais, referências inexistentes e datas de verificação vencidas.

### P2 — cobertura funcional

- Criar skills específicas apenas quando houver workflow distinto e recorrente. Candidatas: operação/Procedimentos de Rede ONS; tarifas e PRORET; migração e representação varejista; contratação pública municipal de energia; análise de risco contratual ACL.
- Não criar uma skill por sigla ou instituição. Estrutura institucional é referência transversal; os workflows devem refletir entregáveis reais.

## 4. Plano de execução em quatro ciclos

### Ciclo 1 — saneamento e baseline

- Proteger segredos e artefatos locais.
- Inventariar fontes e gerar relatório de integridade.
- Rodar os casos em `evals/casos_regulatorios.yaml` contra a versão atual e guardar os resultados.
- Selecionar 10 a 20 respostas reais de alta importância como conjunto dourado, após anonimização.

### Ciclo 2 — registro normativo e vigência

- Definir o schema do catálogo de normas.
- Importar primeiro os instrumentos estruturantes já existentes em `Legislacao/`.
- Implementar verificação de duplicidade, URI oficial, hash do arquivo, data de verificação e cadeia `altera/revoga/regulamenta`.
- Marcar documentos derivados: índice, boletim, prova, glossário e parecer anterior.

### Ciclo 3 — refatoração das skills

- Refatorar uma skill por vez, começando por `seb-arcabouco-legal` e `geracao-pareceres-seb`.
- Executar avaliações antes e depois de cada mudança.
- Só então revisar `comercializacao-acr-acl`, `mmgd-novas-tecnologias` e `estrutura-institucional-seb`.

### Ciclo 4 — automação contínua

- Integrar o boletim diário a uma fila de triagem: descoberta não altera automaticamente o conhecimento canônico.
- Exigir revisão para promover uma notícia ou ato novo ao catálogo normativo.
- Rodar periodicamente testes de links, vigência, versões CCEE e regressões de respostas.

## 5. Critérios de sucesso

- Toda afirmação normativa material aponta para instrumento, dispositivo e fonte primária.
- Toda afirmação sensível ao tempo informa a data da verificação.
- O agente separa regra vigente, transição, proposta em consulta e inferência.
- Uma atualização normativa altera o catálogo/referência correspondente, não exige reescrever várias skills.
- Casos críticos possuem avaliação reproduzível e resultado comparável entre versões.
- Nenhum segredo ou artefato local entra no histórico Git.

## 6. Próxima decisão recomendada

Executar primeiro o Ciclo 1 e, em seguida, modelar o catálogo normativo com um pequeno conjunto piloto (Lei nº 14.300/2022, Lei nº 15.269/2025, REN ANEEL nº 1.000/2021 e normas diretamente ligadas à abertura do ACL). Esse piloto permitirá validar o schema antes de tentar catalogar todo o SEB.

