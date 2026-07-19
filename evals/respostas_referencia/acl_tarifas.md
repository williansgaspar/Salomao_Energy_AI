# Respostas de referência — ACL e tarifas

**Data-base:** 19/07/2026

**Finalidade:** calibrar avaliação; não reutilizar como parecer sem atualizar fatos e fontes.

## `acl-baixa-tensao-vigencia`

Não há, na data-base, abertura geral já operacional do ACL para unidades atendidas em
tensão inferior a 2,3 kV. O art. 15, § 17, da Lei nº 9.074/1995, incluído pelo art. 2º
da Lei nº 15.269/2025 e eficaz desde 25/11/2025 por força do art. 24, IV, desta última,
estabelece prazos máximos: até 24 meses para consumidores industriais e comerciais e até
36 meses para os demais. Isso leva aos marcos-limite de 25/11/2027 e 25/11/2028.

A abertura depende ainda dos requisitos do § 17, II, entre eles comunicação, segregação
tarifária, regulamentação do SUI, produto padrão, regras de sobrecontratação/exposição e
tratamento de dados. Datas da MP nº 1.300/2025 ou da Consulta Pública MME nº 196/2025
não devem ser apresentadas como cronograma vigente da lei convertida. Conclusão: eventual
migração de consumidor de baixa tensão exige identificar sua classe e confirmar ato
operacional posterior que implemente a abertura.

## `desconto-tusd-fonte-incentivada`

Não. A TUSD de consumidor livre não é sempre menor que a de consumidor cativo. A
comparação depende da tarifa homologada, subgrupo, modalidade, posto, demanda, consumo,
benefícios e demais condições aplicáveis.

O desconto associado à energia incentivada tem fundamento no art. 26 da Lei
nº 9.427/1996 e é apurado segundo a outorga, os atos ANEEL pertinentes e a Regra CCEE
**Cálculo do Desconto Aplicado à TUSD/TUST** vigente. Desde 25/11/2025, o § 14 do art. 26
veda a redução incidente na parcela consumo para novas migrações. Para consumidor já
livre naquela data, a ampliação posterior do MUSD/MUST não recebe a redução, preservada
a possibilidade de desconto sobre o montante já contratado. Portanto, não se presume
percentual nem benefício sem examinar data de migração, montante contratado, outorga e
matriz de comercialização.

## `percentual-te-tusd-grupo-a`

Não. Um percentual fixo de TE e TUSD não é tecnicamente defensável para qualquer
consumidor A4 verde. A cobrança combina grandezas e bases distintas: consumo por posto,
em R$/MWh, e demanda, em R$/kW, além de itens da fatura que não se confundem com TE e
TUSD. O resultado varia com distribuidora, REH e vigência, modalidade, classe, detalhe,
posto, demanda contratada/medida e perfil de consumo.

Para estimar a conta, deve-se extrair a **Tarifa de Aplicação** da base oficial da ANEEL,
registrando todos os filtros. A Base Econômica serve ao cálculo tarifário e não deve ser
substituída silenciosamente pela tarifa faturada. A composição interna deve seguir os
Submódulos 7.1 e 7.3 do PRORET vigentes e o conjunto **Componentes Tarifárias**. Tributos,
CIP, bandeira, ultrapassagem, reativos e benefícios devem ser tratados separadamente.
Conclusão: o percentual só pode ser resultado de uma simulação explicitamente
parametrizada, nunca premissa genérica.

## Fontes controladoras

- Lei nº 9.074/1995, texto compilado:
  <https://www.planalto.gov.br/ccivil_03/leis/l9074cons.htm>
- Lei nº 9.427/1996, texto compilado:
  <https://www.planalto.gov.br/ccivil_03/leis/l9427compilada.htm>
- Lei nº 15.269/2025:
  <https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15269.htm>
- ANEEL, PRORET:
  <https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret>
- ANEEL, Componentes Tarifárias:
  <https://dadosabertos.aneel.gov.br/dataset/componentes-tarifarias>
- CCEE, Regra de desconto TUSD/TUST, versão 2026.1.0:
  <https://www.ccee.org.br/documents/80415/31001809/15%20-%20C%C3%A1lculo%20do%20Desconto%20Aplicado%20%C3%A0%20TUSDTUST_2026.1.0_JAN.pdf/ddb627e1-56c5-795a-c678-c11572464e2d>
