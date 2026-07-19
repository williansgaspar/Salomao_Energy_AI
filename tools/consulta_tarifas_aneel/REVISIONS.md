# Controle de revisão — Consulta Tarifas ANEEL (app.py)

Este projeto não é um repositório git; o controle de revisão da interface web
é feito por cópia de arquivo (`revisions/app_vN.py`) + este changelog. `app.py`
na raiz da pasta é sempre a versão em uso.

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
