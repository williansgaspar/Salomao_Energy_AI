# SalomãoAI

Assistente técnico-regulatório para o Setor Elétrico Brasileiro, com fundamentação
auditável em fonte primária.

## Começar aqui

1. [Mapa e saneamento do repositório](docs/MAPA_E_SANEAMENTO_2026-07-22.md)
2. [Arquitetura e roadmap](docs/ARQUITETURA_E_ROADMAP_SALOMAO.md)
3. [Status operacional](docs/STATUS_OPERACIONAL_SALOMAO_AI.md)
4. [Índice da documentação](docs/README.md)

## Estrutura canônica

| Área | Função |
|---|---|
| `AGENTS.md` | instruções canônicas, tom e protocolo de vigência |
| `skills/` | procedimentos de trabalho por tema |
| `Legislacao/` | textos normativos locais organizados por espécie |
| `knowledge_base/catalogo_normativo/` | catálogo, inventário e matriz de compatibilização |
| `knowledge_base/normas/` | textos e índices operacionais, especialmente CCEE |
| `Atualizacoes_Mercado/` | descoberta e triagem; não substitui fonte primária |
| `tools/salomao_core/` | recuperação local e minuta auditável |
| `evals/` | casos de regressão e controles de qualidade |

## Regras de operação

- O catálogo e a matriz de compatibilização definem o caminho de consumo; a localização
  física histórica de um arquivo não é, sozinha, prova de classificação correta.
- Não excluir, mover ou promover uma fonte normativa sem varredura de referências,
  atualização do catálogo e validação do projeto.
- PDFs baixados da CCEE são fonte de origem; textos extraídos são derivados de consulta.
  A versão aplicável deve ser conferida no catálogo e na página oficial vigente.
- Execute `python scripts/run_quality_gate.py` antes de entregar alteração estrutural.

## Consulta local

```powershell
python tools/salomao_core/consulta.py query "consumidores Grupo A carga individual inferior a 500 kW" --minuta
python -m streamlit run tools/salomao_core/app.py
```
