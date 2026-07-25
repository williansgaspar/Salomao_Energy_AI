# ADR-004: Saneamento não destrutivo do acervo local

**Status:** Aceito  
**Data:** 22/07/2026  
**Decisor:** Willians

## Contexto

O repositório reúne textos primários, PDFs originais, extrações textuais, HTMLs de
publicação, índices, relatórios de implantação e artefatos operacionais. Parte dos
arquivos permanece em localização histórica que não representa sua classificação ideal.
Movimentação ou exclusão em massa pode quebrar links, automações e referências do
catálogo, além de eliminar evidência de origem.

## Decisão

Preservar os arquivos normativos e organizar o repositório primeiro por metadados,
índices de navegação e regras explícitas de consumo. A matriz de compatibilização e o
catálogo normativo definem o arquivo canônico para consulta, mesmo que exista cópia
histórica em outra pasta.

Só mover ou retirar fonte após varredura de referências, atualização de catálogo e
execução do quality gate. Arquivos derivados efêmeros podem ser limpos quando ignorados
pelo Git e regeneráveis.

## Alternativas consideradas

| Alternativa | Decisão |
|---|---|
| Reorganização física imediata | Rejeitada: risco alto de quebrar referências e perder proveniência. |
| Manter o estado sem mapa | Rejeitada: aumenta ambiguidade e trabalho manual. |
| Organização lógica com migração gradual | Aceita: reduz risco e permite validação por lote. |

## Consequências

- `README.md` e `docs/README.md` tornam explícita a porta de entrada do projeto.
- Documentos históricos permanecem disponíveis, mas não concorrem com referências ativas.
- O inventário passa a registrar os PdCs como downloads oficiais da CCEE, sem confundir
  proveniência com confirmação permanente de vigência.

## Próximas ações

1. Consolidar as referências canônicas das RENs atualmente em pastas históricas. **Concluído em 22/07/2026.**
2. Reconciliar metadados de atualização do catálogo e dos relatórios históricos.
3. Limpar somente artefatos efêmeros ignorados e regeneráveis, após confirmação de uso.
