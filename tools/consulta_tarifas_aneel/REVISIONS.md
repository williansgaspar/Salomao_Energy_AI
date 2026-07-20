# Controle de revisão — Consulta Tarifas ANEEL (app.py)

Este projeto não é um repositório git; o controle de revisão da interface web
é feito por cópia de arquivo (`revisions/app_vN.py`) + este changelog. `app.py`
na raiz da pasta é sempre a versão em uso.

## Revisão 13 (19/07/2026) — atual

- Regra de detalhe diferenciada pela origem dos dados.
- Com documento válido, `Detalhe documental` permanece fixado em `Não se aplica`.
- Sem documento, `Detalhe tarifário (obrigatório)` permite seleção explícita entre as opções disponíveis, incluindo `APE` e `SCEE`.
- Consulta manual permanece bloqueada até a escolha do detalhe.
- Revisão 12 preservada no commit `77b9547`.

## Revisão 12 (19/07/2026)

- Campo `DscDetalhe` fixado obrigatoriamente em `Não se aplica` nos fluxos documental e manual.
- Opções `APE`, `SCEE` e `Todas` deixam de participar da composição consultada.
- Consulta é bloqueada quando a combinação tarifária não contém registro com detalhe `Não se aplica`.
- Detalhe aplicado passa a integrar o contexto auditável da consulta e das exportações.
- Revisão 11 preservada nos commits `82c8325` e `337de5b`.

## Revisão 11 (19/07/2026)

- Upload de PDF, imagem, CSV ou XLSX transferido para o início da Aba 1, antes dos parâmetros tarifários.
- Documento válido passa a constituir o perfil documental único usado pelas três abas.
- Campos disponíveis no documento prevalecem; parâmetros ausentes ficam obrigatoriamente disponíveis para preenchimento manual.
- Consulta manual exige distribuidora, ano, mês, subgrupo, modalidade e base tarifária.
- CSV/XLSX aceita `posto` e uma ou ambas as colunas `consumo_mwh` e `demanda_kw`, além de metadados tarifários opcionais.
- Aba 2 deixa de processar uploads e apenas recebe consumo/demanda já consolidados na Aba 1.
- Incluída opção explícita para descartar o documento e reiniciar o fluxo manual.
- Validação pós-implementação corrigiu CSV brasileiro com delimitador `;` e vírgula decimal.
- Parâmetros da Aba 1 também recebem identidade por documento/modo manual, impedindo restauração de filtros antigos pelo frontend.
- Descarte passa a limpar o `file_uploader` antes da renderização, evitando reprocessamento automático do arquivo removido.
- Revisão 10 preservada no histórico Git pelo commit `f5ccb40`.

## Revisão 10 (19/07/2026)

- Os quatro campos de consumo e demanda recebem uma identidade de widget vinculada ao hash da fatura.
- O estado manual anterior não pode mais restaurar zeros sobre as grandezas extraídas durante o rerun do Streamlit.
- Grandezas passam entre as abas em estrutura semântica por posto, sendo convertidas em chaves de widget somente antes da renderização.
- Incluída confirmação visível de consumo HFP/HPT e demanda HFP/HPT efetivamente aplicados aos campos.
- Faturas abertas na revisão anterior são reaplicadas automaticamente uma vez pelo protocolo de estado `v10`.
- Revisão 9 preservada no histórico Git pelo commit `d04e7af`.

## Revisão 9 (19/07/2026)

- PDF e imagem passam pelo mesmo pipeline visual de OCR, eliminando diferenças de coordenadas da camada textual do PDF.
- Adicionadas guardas semânticas para rejeitar alíquotas fora de 0%–100% e tributos monetários superiores ao valor bruto do item.
- Preenchimento automático das quatro grandezas deixa de depender da geometria interna da camada textual do PDF.
- REH é selecionada automaticamente quando a competência e o enquadramento resultam em uma única resolução aplicável.
- Cartões tributários reorganizados em duas linhas para exibir valores completos, sem truncamento, e percentual em padrão brasileiro.
- Revisão 8 preservada no histórico Git pelo commit `adaef90`.

## Revisão 8 (19/07/2026)

- Fatura carregada passa a ser a fonte autoritativa para competência, distribuidora, subgrupo, modalidade, classe e subclasse.
- Aba 1 é sincronizada e a consulta ANEEL é refeita automaticamente quando houver divergência com o documento.
- Consumos HPT/HFP e demandas HPT/HFP reconhecidos passam a preencher a simulação sem depender de botão manual.
- PIS/COFINS e ICMS retirados são consolidados e exibidos em R$, mantendo as alíquotas identificadas separadamente em %.
- Incluído filtro de subclasse na consulta avançada para maior precisão da composição tarifária.
- Mantido botão de reaplicação apenas para eventuais correções manuais feitas na tabela de conferência.
- Revisão 7 preservada no histórico Git pelo commit `95f7922`.

## Revisão 7 (19/07/2026)

- Upload ampliado para PDF, PNG, JPG e WEBP de faturas Light Grupo A, além de CSV/XLSX.
- Extração textual de PDF com PyMuPDF e fallback de OCR local com RapidOCR.
- Extração de Energia Ativa HPT/HFP em kWh, convertida automaticamente para MWh, e Demanda HPT/HFP em kW.
- Retirada auditável de PIS/COFINS e ICMS por item, usando a tarifa líquida da fatura ou reconstrução algébrica.
- Separação TE/TUSD reconciliada com a composição ANEEL selecionada, com alerta para divergência de competência/enquadramento/tarifa.
- Tela de conferência editável antes de preencher os inputs; nenhum dado da fatura é enviado a serviço externo.
- Revisão 6 preservada em `revisions/app_v6.py`.

## Revisão 6 (19/07/2026)

- Reintroduzidos indicadores de TE ponderada, TUSD Energia ponderada e TUSD Demanda ponderada.
- Ponderação de referência: 720 h/mês típico, 66 h de Ponta, 44 h de Intermediário quando aplicável e saldo em Fora Ponta.
- Indicadores posicionados antes dos inputs de simulação para apoiar comparação preliminar TE(ACL) × TE ponderada(ACR).
- Os indicadores são independentes de consumo/demanda e não influenciam os totais calculados.
- Incluída observação dimensional específica para TUSD Demanda ponderada em R$/kW.
- Revisão 5 preservada em `revisions/app_v5.py`.

## Revisão 5 (19/07/2026)

- Corrigida a associação entre parâmetros e resultados: cada simulação recebe uma assinatura SHA-256 do contexto; ao alterar composição, modo, consumo ou demanda, o resultado anterior é ocultado.
- Resultado passou a decompor explicitamente TE, TUSD Energia, TUSD Demanda, Energia total e Total geral.
- Tabela das tarifas utilizadas passou a ser exibida antes dos inputs da simulação.
- Nova identidade visual institucional com marca oficial `RIO PREFEITURA`, logo do Projeto Rio de Energia Verde e hierarquia visual mais sóbria.
- Adicionado interruptor de tema claro/escuro, com paletas completas para superfícies, campos, tabelas, métricas e navegação.
- Marca oficial obtida do portal `prefeitura.rio` e armazenada localmente em `assets/logo_prefeitura_rio_oficial.png`.
- Revisão 4 preservada em `revisions/app_v4.py`.

## Revisão 4 (19/07/2026)

- Interface reorganizada em três áreas: Consulta, Simulação e comparação, e Histórico.
- Filtros principais reduzidos; REH, base, classe, detalhe, acessante e posto movidos para Consulta avançada.
- Seleção automática de Tarifa de Aplicação quando disponível.
- Comparação de até duas composições com o mesmo perfil de consumo/demanda.
- Importação de perfil em CSV/XLSX (`posto`, `consumo_mwh`).
- Exportações CSV, XLSX auditável e PDF executivo com fonte, resource ID, versão e data/hora.
- Série histórica visual de TE ou TUSD por posto.
- Código separado em `src/aneel`, `src/domain`, `src/exports` e `src/ui`.
- Tema Streamlit institucional, responsividade básica e ocultação de controles de desenvolvimento.
- Artefatos de execução excluídos via `.gitignore`; metodologia documentada em `docs/metodologia.md`.
- Revisão 3 preservada em `revisions/app_v3.py`.

## Revisão 3 (19/07/2026)

- Corrigido o cálculo de energia para aplicar TE e TUSD Energia diretamente ao consumo de cada posto tarifário.
- Criado modo alternativo de consumo total estimado, com distribuição explícita por pesos horários.
- Incluído consumo intermediário para a modalidade Branca, inclusive Grupo B.
- Vigência mensal passou a considerar qualquer sobreposição com o mês, incluindo REH iniciada no decorrer do período.
- Valores tarifários ausentes agora interrompem o cálculo com diagnóstico, em vez de serem tratados como zero.
- Memória de cálculo estruturada por componente, posto, tarifa, quantidade e subtotal.
- Núcleo de domínio isolado em `src/domain/`, acompanhado de testes automatizados.
- Revisão 2 preservada em `revisions/app_v2.py`.

## Revisão 2 (16/07/2026)

Redesign do layout e novos cálculos de energia/demanda, a partir de mockup
fornecido por Willians Gaspar (ver anotações da imagem em 16/07/2026).

**Layout**
- Sidebar removida; layout em dois cartões na área principal — **Inputs**
  (filtros + campos livres de demanda/consumo) e **Outputs** (tabela +
  métricas calculadas), com bordas arredondadas e sombra sutil.
- Tema claro/escuro selecionável no topo da página (alternância via CSS
  injetado).
- **Identidade visual institucional** (16/07/2026, mesmo dia): paleta e
  cabeçalho inspirados em fazenda.prefeitura.rio (tema padrão das
  secretarias da Prefeitura do Rio, WordPress "secretarias-prefeitura-rio"),
  pensando numa futura hospedagem na intranet da Prefeitura:
  - Barra utilitária cinza-escura (`#363636` claro / `#1B1B1B` escuro) com o
    wordmark "PREFEITURA.RIO" (azure `#12BBEF` + branco, como no site
    oficial) e o nome do órgão/núcleo.
  - Faixa de título azul institucional (`#004A80` claro / `#0B2E4D` escuro),
    espelhando a barra de navegação azul das secretarias.
  - Azul `#1863DC` (claro) / `#4C9CFF` (escuro) como cor de destaque de
    botões, links e métricas — é a cor mais usada no site de referência.
  - Verde `#0BB975` (claro) / `#2FE39A` (escuro) reservado como destaque do
    "Total geral estimado" (cartão com borda esquerda verde) — cor que
    coincidentemente também aparece no site institucional, e que aqui reforça
    a identidade do Rio de Energia Verde.
  - Cantos menos arredondados (8-10px, antes 16px) e sombra mais sutil,
    aproximando do visual "oficial" mais reto do padrão de secretarias.
  - Fonte institucional (Cera Pro/Museo Sans) é proprietária da Prefeitura e
    não está disponível fora da rede interna — usa-se `Inter` (Google Fonts)
    como substituta de geometria parecida, com fallback para fontes do
    sistema (`Segoe UI` etc.) caso a intranet não tenha saída à internet.
- **Logo do Projeto Rio de Energia Verde** (16/07/2026, mesmo dia): arquivo
  original (`assets/Logo - Projeto Rio de Energia Verde.jpg`, fundo branco)
  processado localmente com Pillow (`scripts` ad-hoc, não versionados) —
  remoção do fundo por flood-fill a partir das bordas (preserva os "buracos"
  internos das letras O/D/G e o brilho decorativo, que não ficam conectados
  ao fundo externo) e recorte pela bounding box do conteúdo. Resultado salvo
  em `assets/logo_rio_energia_verde.png` (RGBA, fundo transparente),
  embutido no cabeçalho como data URI base64 (`logo_data_uri()`, cacheado)
  — não depende de servir arquivo estático à parte, o que facilita a futura
  hospedagem na intranet. Exibida dentro de uma "plaquinha" branca
  (`.pref-logo-badge`) na faixa azul do cabeçalho: colada direto sobre o
  azul/verde da faixa, a franja de anti-aliasing clara do recorte ficava
  visível e o texto "PROJETO" (azul-marinho) ficava ilegível sobre o
  `band_bg` — a plaquinha branca resolve as duas coisas em qualquer tema.
  Decisão de usar Python local em vez do Canva (conector já autorizado no
  Claude): o conector só aceita ativos que já estejam numa URL pública, e
  publicar a logo num host externo só para essa edição não fazia sentido
  para um arquivo privado do usuário.
- **Correções de CSS para o tema escuro** (mesmo dia, achadas via screenshot
  com Playwright): em Streamlit 1.59, `st.container(border=True)` não expõe
  mais um `data-testid="stVerticalBlockBorderWrapper"` (versões antigas
  tinham) — o border/radius é aplicado direto no `stVerticalBlock`, sem
  testid distinto, então o seletor original nunca casava e o "card" ficava
  sempre transparente (mostrando o fundo da página por trás). Corrigido
  usando `st.container(..., key="card_inputs"/"card_outputs")`, que o
  Streamlit expõe como classe estável `.st-key-<key>` — abordagem oficial
  recomendada para estilizar containers específicos, em vez de depender de
  classes `st-emotion-cache-*` (hash instável entre versões). Título dos
  blocos "Energia (TE+TUSD)"/"Demanda (TUSD)" (`h5`, via `#####`) também
  precisou de `!important` na regra de cor — a regra própria do Streamlit
  para headings (`.st-emotion-cache-xxx h5 {...}`) tem especificidade CSS
  maior que um seletor de elemento puro (`h5`), então vencia mesmo aparecendo
  depois no documento.
- Filtros reorganizados em grade: Distribuidora, Ano/Mês, REH, Base Tarifária
  na primeira linha; Subgrupo, Modalidade, Detalhe, Posto na segunda; Classe e
  Acessante (`SigAgenteAcessante`) numa terceira linha. O filtro **Posto**
  (`NomPostoTarifario`) e o filtro **Acessante** são novos — não existiam na
  Revisão 1. Filtro **Classe** deixou de ficar num expander "Filtros
  avançados" (removido) e passou para a grade principal.
- **Campo "Tipo de Outorga" do mockup foi descartado**: o dataset de tarifas
  da ANEEL (`fcf2906c-7c32-4b9b-a637-054e7a5234f4`) não tem esse campo — só
  existiria cruzando com outro dataset da ANEEL (agentes/concessionárias) por
  CNPJ, fora do escopo desta revisão. Decisão tomada com o Willians em
  16/07/2026.

**Novo filtro Ano/Mês (mês de referência)**
- Além do filtro por ano de início de vigência (como na Revisão 1), agora é
  possível escolher também o mês. Quando Ano e Mês estão preenchidos, o
  filtro de REH passa a considerar a **vigência no mês de referência**
  (`DatInicioVigencia <= data_ref <= DatFimVigencia`, usando o novo helper
  `vigente_em()` em `aneel_api.py`) em vez de só o ano de início — mais
  preciso em transições de REH dentro do mesmo ano.

**Novos campos de input: Demanda e Consumo por posto**
- 4 campos numéricos livres: Demanda HPT (kW), Demanda HFP (kW), Consumo HPT
  (MWh), Consumo HFP (MWh).
- **Congelamento automático** (`calcular_congelamento()`): os campos ficam
  desabilitados (visíveis, mas travados em zero) conforme Subgrupo/Modalidade
  selecionados — Grupo B (baixa tensão) usa só Consumo HFP (sem demanda
  contratada); tarifas sem posto Ponta (ex.: Convencional) usam só os campos
  HFP. Critério: prefixo do Subgrupo (`A*`/`B*`) e prefixo/valor da
  Modalidade (`Azul*`, `Verde*`, `Branca` têm Ponta).

**Novos cálculos de output**
- Removido o antigo expander "Tarifa média ponderada por horas do mês" com
  horas editáveis pelo usuário (66h Ponta / 22h Intermediário eram
  `number_input`). Substituído por pesos **fixos**: Ponta = 66h/mês,
  Intermediário = 44h/mês (só modalidade Branca — derivado de "1h antes + 1h
  depois da Ponta", em vez das 22h da Revisão 1), Fora Ponta = resto até
  720h/mês.
- **TE ponderada / TUSD ponderada (R$/MWh)**: média ponderada pelos pesos
  fixos acima, sobre as linhas de energia (`DscUnidadeTerciaria = "MWh"`).
- **Total energia (R$)** = (TE ponderada + TUSD ponderada) × (Consumo HPT +
  Consumo HFP).
- **TUSD Demanda Ponta / Fora Ponta (R$/kW)** — novo: lido direto das linhas
  de demanda (`DscUnidadeTerciaria = "kW"`), só para Grupo A.
- **Total demanda (R$)** = TUSD Demanda Ponta × Demanda HPT + TUSD Demanda
  Fora Ponta × Demanda HFP.
- **Total geral estimado (R$/mês)** = Total energia + Total demanda.
- Expander "Memória de cálculo" com as fórmulas e horas consideradas.

**Nota de interpretação (transparência sobre o mockup):** a anotação original
dizia "(TUSD) ponderada ... R$/MWh → calcular idem ao TE, entretanto
considerando os inputs de Demanda", o que seria dimensionalmente inconsistente
(R$/MWh × kW). Resolvido pela estrutura tarifária real do setor: TUSD-energia
(R$/MWh) compõe com TE sobre o Consumo, e TUSD-demanda (R$/kW) é tratada à
parte, direto pelas linhas `kW` do dataset, sobre os campos Demanda HPT/HFP.
Se essa não for a leitura pretendida, sinalizar para ajuste.

**Outros**
- `aneel_api.py`: novo helper `vigente_em(registro, data_referencia)`.
- `montar_dataframe`/`COLUNAS_EXIBICAO`: coluna `SigAgenteAcessante` →
  "Acessante" passou a ser exibida na tabela (já vinha na resposta da API,
  só não estava mapeada para exibição).

## Revisão 1 (até 16/07/2026)

Versão original, preservada em `revisions/app_v1.py`. Sidebar com filtros em
cascata (Distribuidora → Ano → REH → Base tarifária → Detalhe → [expander:
Subgrupo → Modalidade → Classe]); coluna calculada "Energia Composta
TUSD+TE"; painel de tarifa média ponderada por horas do mês com horas
editáveis pelo usuário (total, Ponta, Intermediário). Sem campos de
Demanda/Consumo, sem cálculo de totais em R$, sem tema claro/escuro.
