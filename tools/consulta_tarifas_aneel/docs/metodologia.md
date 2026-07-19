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

## Vigência

A consulta mensal inclui toda composição cuja vigência alcance pelo menos um dia do mês. Quando houver mais de uma REH no período, ambas permanecem disponíveis e devem ser desambiguadas na simulação. A data exata elimina essa ambiguidade quando aplicável.

## Limitações

- Não contempla tributos, bandeiras, reativos, ultrapassagem, descontos, encargos ou regras particulares da unidade consumidora.
- O resultado é uma estimativa técnica e não substitui o faturamento da distribuidora.
- Séries históricas agregam registros repetidos por média apenas para visualização; a tabela de origem deve ser usada em análises formais.
