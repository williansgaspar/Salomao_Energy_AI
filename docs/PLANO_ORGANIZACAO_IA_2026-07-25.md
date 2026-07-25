# Plano de organização de projetos de IA

**Data-base:** 25/07/2026  
**Estado:** fase 1 concluída — inventário e desenho-alvo; nenhuma fonte, aplicação ou histórico foi movido.

## 1. Inventário confirmado

No diretório imediato `Projects/` foi identificado um único projeto de IA local:

| Projeto | Situação | Papel |
|---|---|---|
| `Salomao_Energy_AI` | ativo | agente técnico-regulatório do Setor Elétrico Brasileiro, base de evidências, ferramentas de consulta e avaliações |

O projeto contém aproximadamente 756 arquivos (cerca de 112 MB). A sua divisão funcional já é adequada:

| Área | Manter como |
|---|---|
| `Legislacao/`, `knowledge_base/` | evidência e acervo controlado |
| `skills/`, `AGENTS.md` | instruções e métodos de trabalho |
| `tools/`, `scripts/` | software e automações locais |
| `evals/` | avaliações e regressões |
| `docs/` | governança, decisões, status e histórico |
| `Atualizacoes_Mercado/` | descoberta e triagem, sem valor de fonte final |

### Candidatos encontrados no OneDrive

| Localização | Classificação inicial | Decisão recomendada |
|---|---|---|
| `Claude AI/` | projeto separado de dados/Power BI do Programa Rio de Energia Verde; contém pipeline e um projeto MMGD/SCEE ainda aguardando dados | manter separado do Salomão; inicializar Git corretamente e realocar para a categoria de projetos ativos ou incubação |
| `SalomãoAi_NotebookLM e Claude/` | pasta de trabalho com notas e utilitário de consulta | vincular ao Salomão como área operacional temporária ou absorver os itens úteis em `tools/notebooklm/` |
| `Documentos/Repositorio Salomao AI/` | pasta vazia | transformar em atalho/documentação de acesso ou remover após confirmar que não é destino de integração |
| `01_Trabalho/Clientes-Projetos/Salomao Energy AI/` | contém um relatório PMO | manter como entrega/projeto de cliente, não como cópia do repositório |
| `.../SME/Estudo_GPT/` | quatro imagens de estudo, sem código ou instruções | reclassificar como material de análise/dado de projeto, não como projeto de IA |
| `.../Legislação ACL e ACR - ANEEL - ONS - CCEE - Agentes/` | acervo normativo legado, inclusive versões históricas de PdCs | preservar como entrada histórica; incorporar ao catálogo do Salomão apenas após verificação de vigência e duplicidade |

O diretório `Claude AI/` possui uma pasta `.git`, mas ela não constitui atualmente um repositório Git válido nem tem histórico ou remoto configurados.

## 2. Decisões de organização

1. Não mover fontes normativas, a base de conhecimento ou qualquer item de trabalho antes de reconciliar as alterações locais pendentes.
2. Tratar `tools/consulta_tarifas_aneel/` como candidata a fonte única da aplicação tarifária. A pasta `API Forward/tarifas-aneel-acl/` contém uma cópia de publicação quase integral e não deve receber evoluções manuais em paralelo.
3. Separar documentação corrente de registros históricos. Até a migração física, documentos históricos continuam válidos apenas para o seu contexto temporal.
4. Manter segredos fora do Git **e** fora de pastas sincronizadas. O arquivo local de chave existente está ignorado pelo Git, mas é replicado pelo OneDrive.

## 3. Arquitetura-alvo

```text
C:\Projetos\IA\repos\
  Salomao_Energy_AI\              # código, skills, testes, acervo controlado e Git

OneDrive - OnEnergy\IA\
  00_portfolio\                   # inventário de projetos, responsáveis e decisões
  01_ativos\Salomao_Energy_AI\    # entregas compartilháveis e insumos colaborativos
  02_incubacao\                   # protótipos com prazo de revisão
  90_arquivo\                     # projetos encerrados, somente leitura
```

O repositório Git deve permanecer em disco local fora do OneDrive. O Git remoto mantém o histórico do código; o OneDrive fica restrito a documentos de trabalho, entregas e materiais que exigem sincronização institucional.

## 4. Fila de migração segura

| Prioridade | Ação | Condição de execução |
|---|---|---|
| P0 | Revisar e registrar as alterações locais do Salomão | antes de mover o repositório |
| P0 | Retirar segredos de área sincronizada e validar rotação, se aplicável | sem expor o valor da credencial |
| P1 | Definir a relação fonte/publicação da aplicação tarifária | antes de remover qualquer cópia |
| P1 | Criar a pasta de portfólio e cadastrar os candidatos já identificados | após confirmar o destino institucional do portfólio |
| P2 | Transferir uma cópia validada do repositório para fora do OneDrive | com Git limpo, testes aprovados e rollback disponível |
| P2 | Reorganizar `docs/` em corrente, decisões e histórico | após atualizar os links internos |
| P3 | Arquivar ou encerrar projetos sem objetivo, responsável e próxima revisão | somente após aprovação explícita |

## 5. Critério de classificação do portfólio

- **Ativo:** tem objetivo atual, responsável e próxima entrega em até 90 dias.
- **Incubação:** hipótese ou protótipo com data explícita de revisão.
- **Arquivado:** preservado para consulta, sem trabalho previsto.
- **Encerrado:** sem valor operacional, legal, técnico ou histórico; elegível para eliminação somente com autorização específica.

## 6. Próxima informação necessária

O inventário local contém somente o Salomão. Para consolidar os demais projetos de IA, registrar para cada um: nome, localização, objetivo, última atividade, responsável, dados sensíveis e decisão pretendida (manter, incubar, arquivar ou encerrar).
