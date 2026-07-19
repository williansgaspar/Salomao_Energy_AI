# TE e TUSD — roteiro regulatório de análise

> **REFERÊNCIA OPERACIONAL — SEM VALORES.** Verificada em 19/07/2026. Este arquivo
> orienta a classificação e a busca das fontes; não substitui o PRORET vigente, a
> Resolução Homologatória da distribuidora nem a base oficial de tarifas.

## Fontes controladoras

Na data-base desta revisão:

- PRORET Submódulo 7.1, **versão 2.9**, aprovado pela REN ANEEL nº 1.147/2025:
  procedimentos gerais da estrutura tarifária;
- PRORET Submódulo 7.3, **versão 2.7**, aprovado pela REN ANEEL nº 1.098/2024:
  construção das tarifas de aplicação;
- REN ANEEL nº 1.000/2021, art. 1º, § 2º: a disciplina da prestação do serviço de
  distribuição é complementada pelo PRORET e pelo PRODIST;
- Resolução Homologatória e memória de cálculo do processo tarifário da distribuidora:
  instrumentos necessários para valores e vigência;
- conjuntos de dados abertos **Tarifas de aplicação das distribuidoras de energia
  elétrica** e **Componentes Tarifárias**, da ANEEL.

Antes de utilizar esta referência, conferir na página oficial do PRORET se as versões
acima continuam vigentes.

## Distinções obrigatórias

Não tratar como equivalentes:

- TE e TUSD;
- Tarifa de Aplicação e Base Econômica;
- tarifa homologada e fatura final;
- Parcela A e Parcela B;
- cobrança por energia, em R$/MWh, e por demanda, em R$/kW;
- consumidor cativo e usuário livre da rede;
- componentes econômicos, componentes financeiros, tributos, CIP e bandeira tarifária.

A Tarifa de Aplicação é a tarifa utilizada pela distribuidora no faturamento dos
acessantes. A Base Econômica é utilizada no cálculo tarifário. A base aberta da ANEEL
identifica ambas, bem como REH, vigência, distribuidora, subgrupo, modalidade, classe,
posto, unidade, TE e TUSD.

## Estrutura de trabalho

Para fins de investigação, classificar os custos da tarifa de distribuição nas árvores
de TE e TUSD apresentadas no PRORET 7.1. Em termos gerais:

- a TE concentra custos associados à energia adquirida e componentes a ela alocados;
- a TUSD remunera o uso do sistema de distribuição e contém componentes de transporte,
  perdas, encargos e outros itens alocados à rede;
- a TUSD compreende componentes associados ao Fio A e ao Fio B;
- a alocação de um encargo entre TE e TUSD deve ser obtida no PRORET aplicável, não
  inferida pela natureza econômica aparente do encargo.

Não manter neste arquivo uma árvore nominal detalhada de componentes. Essa árvore muda
com revisões do PRORET e deve ser lida diretamente na versão vigente ou extraída do
conjunto oficial **Componentes Tarifárias** com data-base.

## Procedimento para cálculo ou parecer

1. Fixar distribuidora, data de referência, subgrupo, modalidade, classe, detalhe, posto
   tarifário e unidade.
2. Identificar a REH vigente e sua memória de cálculo.
3. Selecionar **Tarifa de Aplicação** quando a pergunta for faturamento; usar Base
   Econômica somente quando a finalidade regulatória exigir essa base.
4. Extrair TE e TUSD da base ANEEL usando `tools/consulta_tarifas_aneel/` e registrar os
   filtros e a data de geração do conjunto.
5. Para composição interna, consultar o PRORET 7.1/7.3 e o conjunto **Componentes
   Tarifárias**, mantendo a nomenclatura oficial da competência analisada.
6. Acrescentar separadamente demanda, consumo, ultrapassagem, reativos, bandeira,
   tributos, CIP, benefícios e demais itens aplicáveis à fatura.
7. Não apresentar “percentual de TE/TUSD” sem explicitar perfil de carga, demanda,
   consumo por posto e todos os itens incluídos ou excluídos.

## Alegações proibidas sem verificação específica

- percentual médio nacional como proxy da fatura de uma unidade consumidora;
- lista fixa e atemporal de componentes da TE ou da TUSD;
- valor ou percentual de CFURH, CDE, P&D/EE, ESS/EER ou outro encargo sem norma,
  competência e memória de cálculo;
- afirmação de que bandeira tarifária integra a tarifa homologada de aplicação;
- afirmação de que TE + TUSD, isoladamente, reproduz o valor final da conta;
- equivalência automática entre tarifa de consumidor cativo e livre apenas porque ambos
  pertencem ao mesmo subgrupo.

## Fontes oficiais

- ANEEL, página do PRORET:
  <https://www.gov.br/aneel/pt-br/centrais-de-conteudos/procedimentos-regulatorios/proret>
- PRORET 7.1, versão vigente na data-base:
  <https://git.aneel.gov.br/publico/centralconteudo/-/raw/main/procreg/proret/modulo07/subm7.1/Proret_Submod_7.1_V_2.9_aren20251147.pdf>
- REN ANEEL nº 1.098/2024, que aprovou o PRORET 7.3 versão 2.7, vigente desde
  31/07/2024:
  <https://www2.aneel.gov.br/cedoc/ren20241098.pdf>
- ANEEL, tarifas e informações econômico-financeiras:
  <https://www.gov.br/aneel/pt-br/centrais-de-conteudos/relatorios-e-indicadores/tarifas-e-informacoes-economico-financeiras>
- ANEEL, conjunto **Componentes Tarifárias**:
  <https://dadosabertos.aneel.gov.br/dataset/componentes-tarifarias>

### Alerta sobre o portal

Em 19/07/2026, o hiperlink rotulado como “versão vigente” do Submódulo 7.3 na página
do PRORET direcionava para a versão 2.6. Esse destino conflita com a REN nº 1.098/2024 e
com o quadro compilado da REN nº 1.003/2022, que registram a versão 2.7 desde
31/07/2024. Até correção do portal, prevalece o ato normativo oficial.
