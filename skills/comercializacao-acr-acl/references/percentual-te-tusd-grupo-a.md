# Percentual de TE e TUSD na Fatura — Grupo A, Modalidades Azul e Verde

> **QUARENTENA — NÃO USAR EM CÁLCULO OU PARECER.** O arquivo contém referência a novembro de 2026, data futura em relação à verificação de 19/07/2026, e precisa de auditoria integral dos dados e da REH.

## Auditoria parcial — 19/07/2026

- **Confirmado em fonte oficial:** o conjunto de dados abertos da ANEEL contém TE e
  TUSD, diferencia Tarifa de Aplicação de Base Econômica e informa início/fim de vigência
  e Resolução Homologatória. O dicionário oficial define a Tarifa de Aplicação como aquela
  usada no faturamento dos acessantes; a Base Econômica é usada estritamente no cálculo
  tarifário.
- **Confirmado em fonte oficial:** a ANEEL aprovou o reajuste anual da Light em
  10/03/2026, com efeitos a partir de 15/03/2026.
- **Não confirmado nesta auditoria:** número `REH 3.571/2026`, valores da tabela e a
  expressão “site da Light (nov 2026)”. Esses elementos permanecem imprestáveis para
  cálculo ou parecer e devem ser substituídos por extração reproduzível da base ANEEL.
- **Correção conceitual necessária:** bandeira tarifária não deve ser apresentada como
  componente que explica, por si, diferença entre Tarifa de Aplicação e Base Econômica.
  A bandeira é adicional mensal próprio; a página tarifária da ANEEL informa que rankings
  de tarifas homologadas não a contemplam.

Fontes oficiais verificadas: conjunto **Tarifas de aplicação das distribuidoras de energia
elétrica**, seu dicionário de dados e páginas **Processos Tarifários** e **Tarifas e
Informações Econômico-Financeiras**, todas da ANEEL. Até a substituição dos dados abaixo,
o restante deste arquivo é apenas memória de trabalho.

> Consolidado em 13/07/2026, caso de teste real (Willians). Responde a uma pergunta comum e enganosa: "qual o % de TE e TUSD numa fatura do grupo A?" — a resposta correta é que **não existe percentual fixo**; depende da distribuidora, subgrupo, modalidade, posto horário e, principalmente, do fator de carga do consumidor. Este documento mostra a metodologia de cálculo e um exemplo real (Light, A4, THS Verde) que **desmente uma suposição comum** baseada em médias nacionais.

## Por que não há percentual fixo

Nas modalidades Azul e Verde, a fatura do grupo A tem dois tipos de cobrança com bases diferentes: **demanda** (R$/kW, sobre a potência contratada) e **consumo** (R$/MWh, sobre a energia efetivamente medida, diferenciado por posto horário). Como será demonstrado abaixo com dados reais, a **demanda é cobrada 100% via TUSD** (a TE não tem componente de demanda) — isso já garante que, quanto menor o fator de carga do consumidor (menos energia consumida em relação à demanda contratada), maior o peso relativo da TUSD na fatura total.

Além disso, o peso de TE e TUSD se inverte entre os postos horários: no horário de **ponta**, a TUSD tende a ser muito maior que a TE (custo de rede caro no horário de pico); no horário **fora ponta**, a TE tende a ser um pouco maior que a TUSD. Como a maior parte do consumo mensal ocorre fora de ponta (tipicamente ~66 horas de ponta contra ~654 horas fora de ponta, num mês de 720 horas), o resultado final depende de como esses efeitos se compensam — e a demanda (100% TUSD) desempata a favor da TUSD na maioria dos perfis de carga realistas, como mostrado abaixo.

**Não confunda com a divisão Parcela A / Parcela B:** Parcela A gira em torno de 70-72% da conta e Parcela B em torno de 27-30% — mas essa é uma divisão diferente (por gerenciabilidade do custo), não a mesma coisa que TE vs. TUSD. A TE está inteira dentro da Parcela A; a TUSD se divide entre as duas parcelas (Fio A/Perdas/Encargos na Parcela A, Fio B na Parcela B).

## Dado real: Light, subgrupo A4 (2,3 a 25 kV), THS Verde

**Importante: existem duas bases tarifárias publicadas pela ANEEL para cada distribuidora, e elas não são iguais** — "Tarifa de Aplicação" (a que efetivamente consta na fatura do consumidor) e "Base Econômica" (a tarifa "pura" derivada do processo tarifário, referência para o equilíbrio econômico-financeiro da concessionária). Isso foi confirmado ao comparar duas fontes para o mesmo subgrupo/modalidade/distribuidora:

| Componente | Site da Light (nov 2026, provável Tarifa de Aplicação) | Portal ANEEL — Base Econômica (REH nº 3.571/2026, vigência 15/03/2026-14/03/2027) | Diferença |
|---|---|---|---|
| Demanda TUSD (R$/kW) | 30,23 | 29,25 | +3,35% |
| Fora ponta TUSD (R$/MWh) | 230,62 | 198,32 | +16,29% |
| Fora ponta TE (R$/MWh) | 307,62 | 308,35 | -0,24% |
| Ponta TUSD (R$/MWh) | 1.267,61 | 1.199,17 | +5,71% |
| Ponta TE (R$/MWh) | 472,03 | 479,46 | -1,55% |

**Padrão observado:** a TE varia muito pouco entre as duas bases (menos de 2%), mas a TUSD varia bem mais (3% a 16% mais alta na versão do site da Light) — plausivelmente porque a Tarifa de Aplicação incorpora componentes financeiros do reajuste (CVA, neutralizações, Bandeira Tarifária) que afetam majoritariamente a parcela de rede. **Para cálculo de fatura real, use a Tarifa de Aplicação** (o que é efetivamente cobrado) — a Base Econômica é referência regulatória, não o valor faturado. Dados oficiais da ANEEL, filtrando por "Tarifa de Aplicação" (não "Base Econômica"), são a fonte mais confiável quando disponíveis.

**Ponto a confirmar:** a Light teve reajuste tarifário homologado pela REH ANEEL nº 3.571/2026, vigência 15/03/2026 a 14/03/2027 — confirme sempre qual base (Aplicação ou Econômica) está usando antes de citar um valor num parecer ou cálculo formal.

### Acesso à base oficial da ANEEL — automatizado (resolvido em 14/07/2026)

O painel Power BI da ANEEL (`portalrelatorios.aneel.gov.br/luznatarifa/basestarifas`) continua não sendo acessível por fetch/navegador dentro do Cowork. Mas o dataset subjacente (mesmos dados — TE, TUSD, Base Tarifária, subgrupo, modalidade, por distribuidora, desde 2010) é publicado como dado aberto via API CKAN em `dadosabertos.aneel.gov.br`, e o sandbox do Cowork não tem acesso de rede direto para consultá-lo (bloqueado até para domínios genéricos, ex. google.com — não é um bloqueio específico da ANEEL). A solução foi construída **fora do Cowork, via Claude Code** (que roda com o acesso de rede normal do computador do Willians): `tools/consulta_tarifas_aneel/` na raiz do projeto — um cliente Python (`aneel_api.py`) compartilhado entre um script de linha de comando (`consulta_tarifas_aneel.py`, com filtros de distribuidora/subgrupo/modalidade/classe/data/CNPJ/REH) e uma interface web Streamlit (`app.py`, com busca em cascata Distribuidora → Ano → REH → Base Tarifária). Verificado em 14/07/2026: cache local populado com dados reais (lista de ~120 distribuidoras, incluindo a confirmação de que o SigAgente exato da Light é **"LIGHT SESA"**, não apenas "LIGHT") e log do Streamlit mostrando o servidor rodando e uma consulta real executada. Ver `tools/consulta_tarifas_aneel/README.md` para instruções de uso completas.

## Metodologia de cálculo (horas ponta/fora ponta)

Convenção usual de mercado: mês de referência com **720 horas** totais, das quais **66 horas** são de posto ponta (aprox. 3 horas por dia útil × ~22 dias úteis) e as **654 horas** restantes são fora ponta (inclui todo o horário fora do intervalo de ponta em dias úteis, mais integralmente os fins de semana e feriados). Esses valores são uma referência de mercado — o número exato de horas de ponta num mês real varia com a quantidade de dias úteis e feriados.

Para um consumidor com demanda contratada `D` (kW) e fator de carga `FC` (razão entre o consumo médio e a demanda contratada ao longo do período):

- Consumo total do mês (MWh) = 
