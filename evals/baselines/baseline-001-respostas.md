# Baseline 001 — respostas cegas

**Data-base:** 19/07/2026

**Versão avaliada:** `ab3e8b8`

**Método:** respostas produzidas a partir das instruções, skills e fontes primárias locais,
sem abertura dos arquivos em `evals/respostas_referencia/` durante esta geração.

## `acl-baixa-tensao-vigencia`

Hoje, 19/07/2026, o consumidor comercial em tensão inferior a 2,3 kV ainda não tem direito
geral e imediatamente exercitável à migração. A Lei nº 9.074/1995, art. 15, § 17, I,
incluído pela Lei nº 15.269/2025, determina abertura a partir de 1º/08/2026 para consumidores
industriais e comerciais e, a partir de 1º/12/2027, para os demais consumidores. A produção
de efeitos depende também dos requisitos do § 17, II e III, inclusive regulamentações de
representação varejista, SUI, produto padrão e encargos. Qualquer calendário de consulta ou
agenda regulatória deve ser classificado como implementação, não como substituto dessas
datas legais. Confiança alta quanto ao texto legal local; atos regulamentares posteriores
devem ser reconfirmados em MME, ANEEL, CCEE e DOU antes da migração concreta.

## `desconto-tusd-fonte-incentivada`

Não. A TUSD não se torna genericamente menor porque a unidade migrou ao ACL. O desconto
associado a fonte incentivada depende da energia, outorga, enquadramento, período e montante
contratado. O art. 26, § 14, da Lei nº 9.427/1996, na redação da Lei nº 15.269/2025,
preserva o benefício somente sobre o montante contratado até 25/11/2025 nas condições
legais, sem criar desconto automático para novos contratos nem extinguir retroativamente
direitos já protegidos. A comparação ainda depende da REH tarifária, subgrupo, modalidade,
postos, demanda, consumo, tributos e perfil horário. Confiança alta no comando legal local;
confirmar outorga, contrato e REH vigente no caso concreto.

## `percentual-te-tusd-grupo-a`

Não é tecnicamente defensável usar percentual fixo universal. TE e TUSD são tarifas de
aplicação, enquanto a fatura resulta da aplicação das componentes à demanda, consumo,
postos tarifários, modalidade, ultrapassagem, reativos, tributos, bandeiras e demais itens.
Para A4 verde, é indispensável identificar distribuidora, REH vigente, datas de aplicação,
demanda contratada/medida, consumo ponta/fora ponta e histórico. A fonte correta é a base
tarifária oficial da ANEEL e a REH da distribuidora, com leitura dos Submódulos 7.1 e 7.3
do PRORET. Parcela A/B não é sinônimo de TE/TUSD. Sem esses dados, cabe apenas cenário
explicitamente parametrizado, não percentual regulatório.

## `mmgd-solar-4mw`

Uma UFV nova de 4 MW, sem armazenamento, não se enquadra ordinariamente como minigeração
distribuída. A fonte solar é não despachável e o art. 1º, XIII, da Lei nº 14.300/2022 limita
a minigeração não despachável a potência instalada superior a 75 kW e igual ou inferior a
3 MW. A faixa até 5 MW depende da hipótese legal de fonte despachável ou de direito de
transição demonstrado nos termos do art. 26 da própria Lei. A REN ANEEL nº 1.000/2021,
alterada pela REN nº 1.059/2023, operacionaliza o enquadramento. Portanto, sem prova
documental da transição, a conclusão é negativa. Confiança alta na base local.

## `bess-reserva-capacidade`

A autorização legal do armazenamento não equivale a habilitação geral e remuneração
regular de qualquer BESS por serviços ancilares no SIN. A Lei nº 15.269/2025 reconheceu e
endereçou a atividade, mas produto, outorga, conexão/uso da rede, medição, contabilização,
despacho, contratação e remuneração dependem de regulamentação e dos Procedimentos de Rede
e de Comercialização aplicáveis. Leilão de reserva de capacidade anunciado ou sandbox de
reativos é instrumento específico, não regra horizontal. Assim, a resposta depende do
serviço e do ato habilitante: serviço ancilar, LRCAP e arbitragem são regimes distintos.
Não foi confirmado na base local ato que estabeleça habilitação geral. Verificação oficial
atual em MME, ANEEL, ONS e CCEE é obrigatória antes de conclusão comercial.

## `competencia-sui`

A União/poder concedente define o desenho e o responsável conforme regulamentação; o art.
15-C, § 1º, da Lei nº 9.074/1995 permite que, a seu critério, a atividade seja exercida com
ou sem exclusividade por concessionária, permissionária ou autorizada de distribuição.
A ANEEL autoriza e fiscaliza (inciso I) e fixa tarifas específicas (inciso III). A pessoa
jurídica designada presta o atendimento, inclusive no encerramento da representação
varejista (inciso II). O art. 15, § 17, III, “c”, remete ao regulamento os detalhes de
elegibilidade, acionamento, prazo, lastro e custos. Não se pode atribuir por inferência à
CCEE, ONS ou distribuidora todo o fluxo operacional. Parâmetros de consulta pública não são
regra vigente. Confiança alta no texto legal; operacionalização definitiva não confirmada.

## `parecer-sem-fonte-primaria`

Não há base para conclusão definitiva. Notícia é fonte secundária de descoberta e não cria
obrigação normativa. O parecer deve registrar o fato reportado, identificar o órgão e o ato
que supostamente materializaria a obrigação e suspender a conclusão até localizar lei,
decreto, resolução, portaria, despacho ou procedimento oficial, conferindo publicação,
competência, vigência, destinatários e transição. Sem o ato, a conclusão admissível é
“obrigação não confirmada”.

## `prova-antiga-norma-revogada`

O gabarito de 2019 só pode funcionar como índice temático ou material didático. Cada norma
citada deve ser reconfirmada na fonte primária e na data-base do parecer. Exemplo: a REN
ANEEL nº 1.011/2022, art. 23, I, revogou a REN nº 570/2013; a REN nº 1.000/2021, art. 677,
V, revogou os arts. 1º a 16 da REN nº 376/2009. Para o Decreto nº 5.163/2004, é preciso
verificar cada dispositivo no texto compilado, sem classificá-lo integralmente por atalho.
O parecer deve citar a disciplina atual e registrar a prova apenas como antecedente
histórico.

## `citacao-inexistente`

Não confirmo a premissa. Não há, na base local, REN ANEEL nº 9.999/2026 nem evidência do
alegado art. 42. Antes de afirmar inexistência absoluta, deve-se pesquisar o repositório
oficial da ANEEL e o DOU e solicitar PDF, URL oficial ou número do processo. Até que espécie,
número, data, emissor, dispositivo e competência sejam autenticados, a referência deve ser
tratada como inconsistente ou possivelmente inventada, sem criar conteúdo substitutivo.
