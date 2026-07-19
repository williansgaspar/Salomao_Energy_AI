# ADR-001: Catálogo normativo estruturado

**Status:** Aceito  
**Data:** 19/07/2026  
**Decisor:** Willians, com implementação inicial pelo Salomão

## Contexto

As normas e referências do projeto estão distribuídas entre textos integrais, páginas HTML, resumos, índices e materiais didáticos. O agente precisa distinguir existência local, autenticidade, vigência e aptidão de uma fonte para fundamentar uma conclusão.

## Decisão

Manter um catálogo canônico em `knowledge_base/catalogo_normativo/catalogo.json`, validado contra regras documentadas em `schema.json`. Cada registro representa um instrumento, não uma alegação jurídica. A inclusão no catálogo não confirma vigência: o campo `verification.status` controla esse estado explicitamente.

Usar JSON para permitir validação determinística com a biblioteca padrão do Python. Manter textos primários em suas pastas atuais para preservar links e automações existentes.

Tratar `knowledge_base/Legislação/` como área de entrada pendente de classificação. Em
19/07/2026, a pasta continha 41 arquivos e nenhum deles era duplicata binária de outro
arquivo do projeto. Portanto, os documentos não devem ser excluídos nem presumidos
canônicos: cada item deve ser identificado, conferido em fonte oficial e então promovido
ao catálogo e, quando aplicável, à estrutura canônica de `knowledge_base/normas/`.

Tratar `Atualizacoes_Mercado/Boletim_Atualizacoes_SEB_web.html` como variante de
publicação do boletim, não como cópia do arquivo canônico. Sua incorporação ao Git depende
de confirmar qual rotina o gera e se o artefato é fonte, saída reproduzível ou publicação.

## Alternativas consideradas

### Markdown tabular

Mais legível manualmente, porém frágil para validação, relações entre normas e automação.

### Banco de dados relacional

Oferece consultas avançadas, mas adiciona complexidade prematura e dificulta revisão por Git.

### JSON versionado

É menos confortável para edição manual, mas favorece validação, diff, portabilidade e evolução futura para banco ou grafo.

## Consequências

- A base passa a distinguir documento localizado de norma confirmada como vigente.
- Relações como `altera`, `revoga` e `regulamenta` poderão ser representadas sem duplicar texto nas skills.
- A promoção de registros para `verified` exigirá conferência em fonte oficial e data de verificação.
- Alegações por artigo/dispositivo deverão, numa etapa posterior, ter camada própria; não serão indevidamente misturadas ao cadastro do instrumento.
