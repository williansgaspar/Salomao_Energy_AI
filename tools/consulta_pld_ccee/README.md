# Consulta PLD CCEE

Ferramentas para consultar a API pública de Dados Abertos da CCEE — família de
datasets do **PLD (Preço de Liquidação das Diferenças)**, organização
[Preço de Liquidação das Diferenças](https://dadosabertos.ccee.org.br/organization/preco_liquidacao_diferenca):

| Dataset | Conteúdo |
|---|---|
| `pld_horario` | PLD horário corrente (modelo DESSEM) — o dado de referência hoje |
| `pld_media_diaria` | PLD médio diário |
| `pld_media_mensal` | PLD médio mensal |
| `pld_final_historico` | PLD Final histórico — **semanal, só abr–set/2013**, mecanismo ΔPLD da Res. CNPE nº 3/2013 (legado; **não é o PLD corrente**) |

Duas interfaces sobre a mesma lógica de consulta (`ccee_api.py`):

- **`app.py`** — interface web (Streamlit), com filtro de Dataset, Submercado e período
- **`consulta_pld_ccee.py`** — script de linha de comando

Não requer autenticação. Consulta diretamente os endpoints CKAN `package_show` e
`datastore_search` do portal `dadosabertos.ccee.org.br`.

## ⚠️ Sobre o acesso bloqueado da CCEE (leia antes de usar)

Este código foi escrito em 15/07/2026 num sandbox que **não conseguiu acessar
`dadosabertos.ccee.org.br` de jeito nenhum** — todas as tentativas (WebFetch direto,
`curl` direto, proxy do Google Translate) voltaram `403 Forbidden` com a mensagem
"acesso bloqueado por políticas de segurança da CCEE" (um WAF, provavelmente
bloqueando por reputação de IP de datacenter/cloud). Isso significa que:

1. **Não foi possível confirmar ao vivo** os `resource_id` (UUID) de cada dataset,
   nem os nomes exatos das colunas (submercado, data, valor). Por isso o cliente
   (`ccee_api.py`) **não hardcoda nenhum dos dois**:
   - resolve os `resource_id` em tempo de execução via `package_show` (cacheado 1 dia
     em `cache/`);
   - detecta submercado/data/valor/patamar heuristicamente a partir do `fields`
     devolvido por `datastore_search` (substring case-insensitive: "submerc" para
     submercado, "dat_"/"din_"/"data" para data, "val_"/"vlr_"/"preco" para valor).
2. **Rode a primeira consulta a partir da sua rede** (não deste sandbox — o bloqueio
   parece ser específico daqui). Antes de montar filtros finos ou usar os dados em
   parecer, rode `--listar-campos` (CLI) ou abra o expander "Detecção de campos"
   (app web) para conferir se a heurística bateu com o schema real. Se não bater,
   ajuste manualmente o nome do campo no filtro (`--submercado` assume o nome
   detectado; para filtro por outro campo, edite `montar_filtros`/`filtros` no script).
3. Se voltar a dar 403 mesmo da sua rede, é o WAF mesmo — não é bug deste código.
   Veja a mensagem de erro (CLI já trata isso com uma dica) e considere abrir chamado
   com a CCEE informando o Error Code/IP mostrados na página de bloqueio.

## Escopo do dataset citado (`pld_final_historico`)

O dataset [pld_final_historico](https://dadosabertos.ccee.org.br/dataset/pld_final_historico),
que motivou este desenvolvimento, cobre **só o período abr–set/2013** (PLD Final =
PLD1 + ΔPLD, mecanismo de transição da Res. CNPE nº 3/2013) — não é o PLD atual. Por
isso a ferramenta foi construída para cobrir **toda a família PLD** (`pld_horario`,
`pld_media_diaria`, `pld_media_mensal` além do próprio `pld_final_historico`), com o
usuário escolhendo o dataset relevante para cada consulta.

## Instalação

```bash
pip install -r requirements.txt
```

## Interface web

```bash
streamlit run app.py
```

Abre em `http://localhost:8501`. Fluxo:

1. **Dataset** — dropdown com os 4 datasets da família PLD
2. Expander **"Detecção de campos"** mostra as colunas reais do dataset e qual foi
   mapeada para submercado/data/valor/patamar/ano — confira antes de confiar no filtro
3. **Submercado** — dropdown (se a coluna foi detectada), populado com os valores
   distintos reais do dataset (cache de 24h)
4. **Filtrar por período** (opcional) — filtro local de data, aplicado depois da busca
5. Se nenhum submercado for selecionado, a ferramenta oferece limitar o número de
   registros (recomendado para `pld_horario`/`pld_media_diaria`, que sem filtro podem
   ser bem grandes)
6. Botão **Consultar** exibe a tabela de resultados, métricas de média/mín/máx da
   coluna de valor (se detectada) e um botão **Baixar CSV**

## Uso do CLI

Descobrir schema e valores válidos (com cache local de 1 dia em `cache/`):

```bash
python consulta_pld_ccee.py --listar-datasets
python consulta_pld_ccee.py --dataset pld_horario --listar-recursos
python consulta_pld_ccee.py --dataset pld_horario --listar-campos
python consulta_pld_ccee.py --dataset pld_horario --listar-submercados
```

Consultar PLD:

```bash
python consulta_pld_ccee.py --dataset pld_horario --submercado SE --data-inicio 2026-01-01 --data-fim 2026-01-31

python consulta_pld_ccee.py --dataset pld_media_mensal --submercado NE -o pld_mensal_ne.csv

python consulta_pld_ccee.py --dataset pld_final_historico
```

Filtros disponíveis: `--dataset`, `--submercado` (nome exato do campo detectado
heuristicamente), `--data-inicio`/`--data-fim` (filtro local, formato AAAA-MM-DD),
`--limit`.

## Saída

Por padrão, salva um CSV (separador `;`, `utf-8-sig` — abre direto no Excel BR) em
`output/pld_<dataset>_<timestamp>.csv`, com todas as colunas do dataset (não só as
detectadas), e imprime uma amostra de 10 linhas no terminal. Use `--sem-amostra` para
suprimir a amostra e `-o` para escolher o caminho/nome do arquivo.

## Notas técnicas

- Endpoints: `https://dadosabertos.ccee.org.br/api/3/action/package_show` (lista de
  recursos de um dataset) e `.../datastore_search` (dados paginados de um recurso).
- Datasets com mais de um recurso (padrão observado em outros datasets da CCEE, ex.:
  um resource por ano) são percorridos **integralmente** — todos os recursos do
  dataset são concatenados. Use `--limit`/filtros para conter o volume se necessário.
- `cache/` guarda a lista de recursos por dataset (`recursos_<dataset>.json`, 1 dia) e
  valores distintos de campos (`distintos_<dataset>_<campo>.json`, 1 dia); use
  `--atualizar-cache` para forçar atualização. Cache mais curto que o do
  `consulta_tarifas_aneel` (7 dias) porque o PLD é publicado semanalmente.
- `ccee_api.py` concentra toda a lógica de chamada à API (resolução dinâmica de
  `resource_id`, detecção heurística de campos, paginação, cache, conversão de
  valores BRL) e é importado tanto por `app.py` quanto por `consulta_pld_ccee.py`.
