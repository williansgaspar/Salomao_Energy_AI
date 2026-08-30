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

## Bandeira tarifária na comparação ACR × ACL

Na simulação ACR × ACL, o adicional de bandeira é apurado para a competência escolhida na Aba 1; se houver fatura importada, a competência extraída dela tem prioridade. A fonte é o recurso oficial **Bandeira Tarifária - Acionamento** da ANEEL, que informa mensalmente a cor acionada e seu adicional em R$/MWh. O usuário pode selecionar outra bandeira ou informar um adicional manualmente para fins de cenário e auditoria.

`Custo de bandeira ACR = adicional da bandeira (R$/MWh) × consumo total de energia (MWh)`.

O custo é acrescentado exclusivamente ao cenário ACR. O campo de TE ACL continua livre e representa somente a TE negociada; não há adição automática de bandeira ao ACL.

## Simulação MMGD SCEE — Grupo B (inclui B3)

O aplicativo separa três enquadramentos operacionais para a usina-fonte: **GD I**, **GD II** e **GD III**. Esses rótulos não substituem o enquadramento formal da unidade: representam as hipóteses de transição dos arts. 26 e 27 da Lei nº 14.300/2022. A energia compensada é limitada ao percentual de alocação informado. A fatura Light simulada considera a energia não compensada, a parcela residual incidente sobre o crédito e o maior valor entre esse resultado e o custo de disponibilidade. A bandeira incide apenas sobre a energia não compensada, conforme art. 19 da Lei nº 14.300/2022.

- **GD I:** não há parcela residual sobre a energia compensada; aplica-se a proteção transitória do art. 26 da Lei nº 14.300/2022.
- **GD II:** a parcela residual é aplicada ao Fio B informado pelo usuário, em 15% (2023), 30% (2024), 45% (2025), 60% (2026), 75% (2027) ou 90% (2028), conforme art. 27, caput.
- **GD III:** a parcela residual inclui 100% do Fio B, 40% da base de Fio A/conexão/demais sistemas e 100% da base de P&D, eficiência energética e TFSEE, conforme art. 27, § 1º.

O pagamento à fornecedora é calculado sobre a energia compensada por `(TE + TUSD Energia) × (1 − desconto comercial)`. A simulação permite os anos de 2023 a 2028 — o art. 27 remete à regra do art. 17 a partir de 2029, cuja apuração demanda componentes não abertos pela API tarifária usada pelo aplicativo. A abertura de Fio B e das demais incidências também deve ser obtida pelo usuário na REH/memória tarifária aplicável. Tributos, CIP, serviços diversos e particularidades da UC permanecem fora do escopo.

## Vigência

A consulta mensal inclui toda composição cuja vigência alcance pelo menos um dia do mês. Quando houver mais de uma REH no período, ambas permanecem disponíveis e devem ser desambiguadas na simulação. A data exata elimina essa ambiguidade quando aplicável.

## Limitações

- Não contempla tributos, reativos, ultrapassagem, encargos ou regras particulares da unidade consumidora. A bandeira e o desconto SCEE/GD, quando usados, seguem exclusivamente as premissas descritas acima.
- O resultado é uma estimativa técnica e não substitui o faturamento da distribuidora.
- Séries históricas preservam cada observação publicada, com REH e período de vigência; não há média ou consolidação entre versões tarifárias.

## Importação de fatura Light

PDFs com camada textual são lidos diretamente; PDFs escaneados e imagens usam OCR local. O arquivo não é transmitido a serviços externos. Para cada item de energia ou demanda, o aplicativo lê quantidade, valor com tributos, PIS/COFINS, ICMS e tarifa unitária líquida. Quando necessário, reconstrói:

`Tarifa líquida = (Valor com tributos − PIS/COFINS − ICMS) ÷ Quantidade`.

Energia em kWh é convertida para MWh. A fatura normalmente apresenta uma tarifa líquida agregada; a separação entre TE e TUSD vem da composição ANEEL selecionada no aplicativo. Por isso, o app exibe a diferença entre a tarifa líquida da conta e `TE + TUSD` da base e exige conferência do usuário antes de aplicar os dados à simulação.
