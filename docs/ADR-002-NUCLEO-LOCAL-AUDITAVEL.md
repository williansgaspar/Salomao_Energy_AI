# ADR-002: Núcleo local auditável como caminho crítico de consulta

**Status:** Aceito  
**Data:** 22/07/2026  
**Decisor:** Willians

## Contexto

O fluxo SharePoint → Copilot Notebook introduziu dependência de indexação opaca,
interfaces múltiplas e validações manuais repetitivas. Os testes mostraram que uma
fonte pode ser recuperada em uma conversa e falhar nas seguintes, sem evidência
operacional suficiente para diagnosticar a causa ou reproduzir o resultado.

O projeto já possui catálogo normativo, matriz de compatibilização, textos canônicos
e controles de qualidade locais. Faltava uma camada única que consumisse esses ativos
antes de qualquer geração de resposta.

## Decisão

Adotar `tools/salomao_core/` como núcleo de recuperação local e determinística.
Ele recupera somente fontes primárias verificadas que existam localmente, prioriza o
caminho canônico definido na matriz de compatibilização e devolve um pacote de
evidências rastreável. Ausência de evidência bloqueia conclusão normativa.

O SharePoint e o Copilot Notebook continuam como publicação e consulta complementar,
mas não integram o caminho crítico de fundamentação.

## Alternativas consideradas

| Alternativa | Decisão |
|---|---|
| Continuar ajustando o Copilot Notebook | Rejeitada: baixa reprodutibilidade e alto custo manual. |
| Migrar diretamente para vetor/LLM/serviço externo | Adiada: adiciona custo e opacidade antes de estabilizar a base. |
| Recuperador lexical local com contrato auditável | Aceita: simples, explicável, testável e compatível com o acervo atual. |

## Consequências

- Toda futura camada gerativa deverá receber o pacote de evidências do Core.
- Um resultado de recuperação não confirma, sozinho, a aplicabilidade jurídica do
  dispositivo; a resposta final continua sujeita ao protocolo de vigência.
- A busca lexical é o primeiro estágio. Busca semântica só será adicionada depois de
  avaliar ganhos sobre os casos em `evals/`.

## Ações seguintes

1. Integrar os casos prioritários do ACL e da comercialização varejista ao Core. **Concluído em 22/07/2026.**
2. Converter a interface Streamlit em porta única de consulta local. **Concluído para o MVP em 22/07/2026.**
3. Adicionar redação controlada com citações validadas. **Concluído sem camada gerativa; ver ADR-003.**
