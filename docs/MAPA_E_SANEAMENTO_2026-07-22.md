# Mapa e saneamento do repositório SalomãoAI

**Leitura realizada em:** 22/07/2026  
**Escopo:** acervo local; sem remoção ou movimentação de fonte normativa.

## Retrato do acervo

| Área | Papel | Estado de saneamento |
|---|---|---|
| `Legislacao/` | textos normativos organizados por espécie | fonte operacional; há classificações históricas a migrar gradualmente |
| `knowledge_base/Legislação/` | PDFs de entrada e downloads originais | preservar origem; PdCs vieram diretamente da CCEE |
| `knowledge_base/normas/` | textos extraídos, índices e futuras coleções | CCEE estruturada; ONS, REH e notas técnicas ainda vazios |
| `knowledge_base/catalogo_normativo/` | autoridade de metadados e caminhos de consulta | ativo; manter datas de atualização coerentes |
| `skills/` | procedimentos temáticos | ativo; fatos voláteis devem permanecer em fontes/referências |
| `tools/` | consultas e Core local | ativo; caches, logs e PID são regeneráveis |
| `docs/` | decisões, status, auditorias e históricos | indexado por `docs/README.md` |
| `evals/` | regressões e controles dourados | ativo; ampliar com casos reais anonimizados |

## Constatações

- Não foram encontradas duplicatas binárias exatas no acervo analisado.
- PDFs, TXT e HTML de um mesmo ato são variantes funcionais: PDF preserva origem,
  TXT atende recuperação local e HTML preserva publicação/navegação. Não devem ser
  eliminados por semelhança de título.
- Os 30 PdCs ordinários estão catalogados como `verified`; quatro procedimentos
  provisórios exigem monitoramento de substituição.
- REN ANEEL nº 1.012/2022 e REN ANEEL nº 1.110/2024 foram migradas para
  `Legislacao/Resolucoes_ANEEL/` em 22/07/2026; catálogo e matriz apontam para esses
  caminhos canônicos.
- Relatórios de 19–21/07 preservam marcos históricos e podem conter contagens já
  superadas. O status corrente é definido pelo catálogo, pelo mapa e pelo status operacional.

## Regras de disposição

| Classe | Tratamento |
|---|---|
| fonte primária verificada | preservar, catalogar e citar pelo caminho canônico |
| PDF oficial de origem | preservar com hash e proveniência |
| texto extraído | preservar como derivado de consulta e vincular ao original/catálogo |
| boletim, notícia, prova e glossário | descoberta, estudo ou triagem; não usar como fundamento final |
| relatório histórico | manter como registro; não usar como status atual sem reconciliação |
| cache, `.pyc`, log e PID | regenerável; pode ser limpo se não houver processo em execução |

## Fila de saneamento segura

1. Atualizar a data de geração do inventário a cada execução. **Concluído.**
2. Consolidar caminhos físicos das RENs em lote próprio, após varredura de referências. **Concluído em 22/07/2026.**
3. Atualizar relatórios históricos que ainda indiquem somente sete PdCs ou 13 instrumentos,
   sem apagar o contexto de sua data-base.
4. Definir rotina de expiração para verificações de fonte, PdCs e boletins.
5. Limpar artefatos efêmeros ignorados somente após encerrar processos Streamlit ativos.
