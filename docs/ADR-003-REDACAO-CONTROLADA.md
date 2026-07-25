# ADR-003: Redação controlada, sem inferência autônoma

**Status:** Aceito  
**Data:** 22/07/2026  
**Decisor:** Willians

## Contexto

O núcleo local já recupera fontes canônicas, mas a consulta ainda exigia montar
manualmente uma redação com citação, dispositivo e limites de confiança. Uma camada
gerativa irrestrita neste momento voltaria a introduzir opacidade justamente no ponto
em que se pretende ganhar controle.

## Decisão

Adicionar `tools/salomao_core/redacao.py` como compositor determinístico de minuta.
Ele só aceita pacote com evidências primárias verificadas e com dispositivo identificado.
Sua saída registra pergunta, fundamento, trecho, arquivo, data de verificação e nível de
confiança. Se uma dessas condições falhar, a minuta é recusada.

O compositor não conclui além do texto recuperado e não utiliza LLM, API externa ou
copilot. A análise jurídico-regulatória do caso concreto continua humana e deve verificar
vigência e fatos antes de encaminhamento externo.

## Alternativas consideradas

| Alternativa | Decisão |
|---|---|
| LLM com prompt de citações | Adiada: mantém risco de extrapolação e torna a execução menos reprodutível. |
| Formulário manual sem verificação | Rejeitada: preserva a falha de trabalho repetitivo e omissão de campos. |
| Compositor determinístico com recusa | Aceita: mantém a rastreabilidade e reduz o esforço operacional. |

## Consequências

- A interface local passa a oferecer uma minuta auditável e exportável.
- A qualidade da minuta depende da recuperação e da identificação do dispositivo; ambas
  ficam sujeitas a testes de regressão.
- Uma camada de síntese mais fluida somente poderá ser avaliada depois de demonstrar,
  nos casos de avaliação, que não reduz fundamentação, vigência ou rastreabilidade.

## Ações seguintes

1. Aplicar a minuta aos casos prioritários de ACL/CCEE e revisar a utilidade prática.
2. Medir precisão de recuperação e de dispositivo antes de ampliar para temas tarifários
   e MMGD.
3. Avaliar síntese assistida apenas como camada opcional, nunca como fonte de verdade.
