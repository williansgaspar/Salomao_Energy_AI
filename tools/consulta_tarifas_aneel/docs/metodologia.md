# Metodologia de cálculo

## Escopo

O aplicativo consulta as tarifas homologadas publicadas na API de Dados Abertos da ANEEL. O `resource_id`, a data/hora da extração, os filtros e a versão do aplicativo acompanham as exportações.

## Consumo por posto

É o modo preferencial quando há medição ou estimativa segregada. Para cada posto tarifário:

`Custo de energia = (TE + TUSD Energia) × consumo do posto`.

O resultado total é a soma dos postos. Não se aplica ponderação por horas quando o usuário já informa a curva por posto.

## Consumo total estimado

Distribui o consumo mensal total por pesos de referência: 66 para Ponta, 44 para Intermediário quando existente e o restante até 720 para Fora Ponta. Trata-se de perfil presumido e não substitui a curva de carga da unidade consumidora.

## Demanda

Para cada posto disponível:

`Custo de demanda = TUSD Demanda (R$/kW) × demanda informada (kW)`.

## Indicadores ponderados ACL × ACR

O app apresenta, separadamente da simulação, TE, TUSD Energia e TUSD Demanda ponderadas para um mês típico de 720 horas. São usados 66 h de Ponta, 44 h de Intermediário quando esse posto existir e o saldo como Fora Ponta. Para estruturas sem diferenciação de posto, a tarifa original recebe peso de 720 h.

Esses valores servem como referência inicial de comparação — em especial entre TE regulada no ACR e ofertas de TE no ACL. Eles não utilizam os consumos informados, não representam a curva de carga e não alimentam os totais da simulação. A TUSD Demanda ponderada em R$/kW é um indicador comparativo construído com os mesmos pesos horários, não um critério de faturamento.

## Vigência

A consulta mensal inclui toda composição cuja vigência alcance pelo menos um dia do mês. Quando houver mais de uma REH no período, ambas permanecem disponíveis e devem ser desambiguadas na simulação. A data exata elimina essa ambiguidade quando aplicável.

## Limitações

- Não contempla tributos, bandeiras, reativos, ultrapassagem, descontos, encargos ou regras particulares da unidade consumidora.
- O resultado é uma estimativa técnica e não substitui o faturamento da distribuidora.
- Séries históricas agregam registros repetidos por média apenas para visualização; a tabela de origem deve ser usada em análises formais.
