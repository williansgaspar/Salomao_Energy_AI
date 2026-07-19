# Parâmetros de Mercado — ACR/ACL/PLD (2026)

> **QUARENTENA — NÃO CITAR COMO FONTE.** Estudo de trabalho com parâmetros voláteis e cronogramas ainda não integralmente reconfirmados. Consultar fontes oficiais e registrar data-base antes de reutilizar qualquer valor.

> Consolidado em 13/07/2026 via busca web. Estes são exatamente os parâmetros que mudam ano a ano (PLD) ou que estão em regulamentação ativa (cronograma ACL) — confirme na fonte oficial antes de usar em um parecer ou repasse a um cliente.

## Modalidades de leilão ACR

| Modalidade | Objeto | Observação |
|---|---|---|
| A-3, A-4, A-5, A-6 | Energia nova (empreendimentos ainda não construídos) | Número = anos de antecedência entre o leilão e o início do suprimento |
| A-1 | Energia existente (usinas já em operação) | Ajusta o mercado de curto prazo das distribuidoras |
| Ajuste | Pequenos ajustes de montante contratado | Prazo mais curto, volumes menores |
| Reserva | Energia/potência de reserva, incluindo BESS desde a Lei 15.269/2025 | Fora do lastro normal; 1º LRCAP de armazenamento (MME Portaria Normativa nº 136/2026) programado para dezembro/2026 — ver skill `mmgd-novas-tecnologias` para detalhes |
| Fontes alternativas | Eólica, PCH, biomassa, etc. | Leilões específicos por fonte |

## CCEAR — modalidades

- **Quantidade**: vendedor assume o risco hidrológico/de geração; comprador paga por MWh entregue.
- **Disponibilidade**: comprador assume o risco; paga por disponibilidade de capacidade (comum em usinas térmicas).

## Cronograma de abertura do ACL (baixa tensão)

- **Cronograma legal vigente:** o art. 15, § 17, I, da Lei nº 9.074/1995, incluído
  pelo art. 2º da Lei nº 15.269/2025, determina a redução dos limites em até 24 meses
  para consumidores industriais e comerciais e em até 36 meses para os demais,
  contados da entrada em vigor do dispositivo em 25/11/2025. Os marcos-limite são,
  portanto, **25/11/2027** e **25/11/2028**, respectivamente.
- **Datas de agosto/2026 e dezembro/2027:** pertenciam à proposta da MP nº 1.300/2025
  e à Consulta Pública MME nº 196/2025. Não devem ser apresentadas como cronograma
  vigente após a conversão legislativa.
- Mecanismo-chave: **portabilidade da conta de luz** — troca de fornecedor de energia mantendo a mesma distribuidora local para o serviço de rede (TUSD).
- Tratamento regulatório dos custos irrecuperáveis (*stranded costs*) das distribuidoras ainda em definição pela ANEEL.
- **Status de confirmação:** na data da coleta, a regulamentação detalhada da ANEEL sobre portabilidade ainda estava em andamento — reconfirme o cronograma antes de repassar uma data específica a um cliente.

**Verificação de 19/07/2026:** o MME informa oficialmente abertura de comerciais e
industriais até novembro de 2027 e dos demais consumidores até novembro de 2028. Não foi
localizado ato posterior que fixe datas operacionais anteriores aos limites legais.

## PLD — limites vigentes em 2026

| Parâmetro | Valor (R$/MWh) |
|---|---|
| PLD mínimo | 57,31 |
| PLD máximo estrutural | 785,27 |
| PLD máximo horário | 1.611,04 |

**Verificado em 19/07/2026:** valores confirmados no 121º Encontro do PLD da CCEE
(janeiro de 2026) e na Regra de Comercialização **Preço de Liquidação das Diferenças**,
versão 2026.1.0. Registrar sempre `R$/MWh` e ano de apuração ao reutilizá-los.

- Calculado por submercado (SE/CO, S, NE, N), em base horária, desde 01/01/2021 (Portaria MME nº 301/2019).
- Cadeia de modelos: NEWAVE (longo prazo) → DECOMP (médio prazo) → DESSEM (curtíssimo prazo/despacho horário) para estimar o Custo Marginal de Operação (CMO), que fundamenta o PLD.
- A CCEE promove "Encontros do PLD" ao longo do ano para debater a metodologia com os agentes — a métrica segue em aprimoramento (ex: estudos para aprimorar o modelo de cálculo do PLD horário reportados em 2026).
- Estes limites são redefinidos todo ano — sempre confirme o valor vigente antes de usar em cálculo ou parecer.

## Submercados

SE/CO (Sudeste/Centro-Oeste), S (Sul), NE (Nordeste) e N (Norte). O PLD é
determinado por submercado e por hora, observados os limites vigentes.

## Fontes oficiais verificadas

- Lei nº 15.269/2025: <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15269.htm>
- MME, cronograma legal da abertura da baixa tensão:
  <https://www.gov.br/mme/pt-br/assuntos/noticias/mercado-livre-de-energia-avanca-e-amplia-liberdade-de-escolha-para-o-consumidor-brasileiro>
- CCEE, 121º Encontro do PLD — janeiro de 2026:
  <https://www.ccee.org.br/documents/80415/30980462/121o._Encontro_do_PLD_-_Janeiro_de_2026.pdf/0ed6b60f-637f-2f1f-b908-d18b9f64d4d4>
- CCEE, Regra **Preço de Liquidação das Diferenças**, versão 2026.1.0:
  <https://www.ccee.org.br/documents/80415/31001809/00%20-%20Pre%C3%A7o%20de%20Liquida%C3%A7%C3%A3o%20das%20Diferen%C3%A7as_2026.1.0_JAN.pdf/f5c5a604-2eab-2062-3fc9-c3b9d47eecfb>
