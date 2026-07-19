# Consulta Tarifas ANEEL

Ferramentas para consultar a API pública de Dados Abertos da ANEEL — dataset
[Tarifas de aplicação das distribuidoras de
energia elétrica](https://dadosabertos.aneel.gov.br/dataset/tarifas-distribuidoras-energia-eletrica).
Duas interfaces sobre a mesma lógica de consulta (`aneel_api.py`):

- **`app.py`** — interface web (Streamlit): filtros de tarifa + cálculo de
  energia (TE+TUSD) e demanda (TUSD) estimadas a partir de consumo/demanda
  informados
- **`consulta_tarifas_aneel.py`** — script de linha de comando, com mais filtros (subgrupo, modalidade, classe, datas, CNPJ)

Não requer autenticação. Consulta diretamente o endpoint CKAN `datastore_search`
sobre o recurso `tarifas-homologadas-distribuidoras-energia-eletrica.csv`
(~320 mil registros, atualizado semanalmente pela ANEEL).

**Controle de revisão**: `app.py` está na **Revisão 2**. O histórico de
mudanças e a versão anterior (`revisions/app_v1.py`) estão documentados em
[REVISIONS.md](REVISIONS.md).

## Instalação

```bash
pip install -r requirements.txt
```

## Interface web

```bash
streamlit run app.py
```

Abre em `http://localhost:8501`. Layout em dois cartões — **Inputs** e
**Outputs** — com tema claro/escuro selecionável no topo da página.

### Inputs

Filtros em cascata (cada um já vem restrito às opções que existem dado o que
foi selecionado antes):

1. **Distribuidora** — dropdown com busca por digitação (obrigatório; carrega
   todos os registros dessa distribuidora, o que habilita os demais filtros)
2. **Ano/Mês** — Ano de início de vigência e, opcionalmente, o Mês. Com os
   dois preenchidos, o filtro de REH passa a considerar a **vigência no mês
   de referência** (não só o ano de início) — mais preciso em transições de
   REH dentro do mesmo ano
3. **REH (Resolução Homologatória)** — busca por digitação
4. **Base tarifária** — Tarifa de Aplicação e Base Econômica são ambas
   elegíveis para o cálculo (ver "versão" da tarifa abaixo)
5. **Subgrupo → Modalidade → Detalhe → Posto** — cascata completa, sem
   expander de "filtros avançados" (tudo na grade principal)
6. **Classe** e **Acessante** — filtros adicionais
7. **Demanda HPT/HFP (kW)** e **Consumo HPT/HFP (MWh)** — campos livres,
   usados para calcular os totais em R$ no Outputs. Ficam **travados
   automaticamente** conforme Subgrupo/Modalidade: Grupo B (baixa tensão) usa
   só Consumo HFP (sem demanda contratada); tarifas sem posto Ponta (ex.:
   Convencional) usam só os campos HFP
8. Botão **Consultar**

### Outputs

- Tabela de resultados com a coluna calculada **"Energia Composta TUSD+TE
  (R$/MWh)"** (soma `VlrTUSD + VlrTE` da própria linha, só para linhas de
  energia — `DscUnidadeTerciaria = "MWh"`; linhas de demanda `kW` ficam em
  branco nessa coluna) e botão **Baixar CSV**.
- **Popup de desambiguação**: se os filtros ainda deixarem mais de uma
  "versão" de tarifa elegível simultaneamente (REH/base tarifária/subgrupo/
  modalidade/classe/subclasse/detalhe/vigência), abre uma janela pedindo para
  escolher qual delas usar nos totais calculados. As demais linhas continuam
  visíveis na tabela — só não entram nos totais.
- **Energia (TE + TUSD)**: TE ponderada e TUSD ponderada (R$/MWh) — média
  ponderada por posto tarifário usando pesos fixos de horas/mês (Ponta =
  66h, Intermediário = 44h só na modalidade Branca, Fora Ponta = resto até
  720h) — e **Total energia (R$)** = (TE ponderada + TUSD ponderada) ×
  (Consumo HPT + Consumo HFP).
- **Demanda (TUSD)** — só Grupo A: TUSD Demanda Ponta e Fora Ponta (R$/kW),
  lidas direto das linhas de demanda (`kW`) da versão escolhida, e **Total
  demanda (R$)** = TUSD Demanda Ponta × Demanda HPT + TUSD Demanda Fora Ponta
  × Demanda HFP.
- **Total geral estimado (R$/mês)** = Total energia + Total demanda.
- Expander **"Memória de cálculo"** com as fórmulas e horas consideradas.

**Isso é uma aproximação**, não o custo real de uma unidade consumidora
específica: a parcela de energia pondera por horas-relógio fixas (pesos
padrão, não editáveis), assumindo estrutura constante ao longo do mês —
detalhes e limitações em [REVISIONS.md](REVISIONS.md#revisão-2-16072026--atual).
Estruturas sazonais antigas (postos "seca"/"úmida") não são calculadas
automaticamente.

## Uso do CLI

Descobrir valores válidos para os filtros (com cache local de 7 dias em `cache/`):

```bash
python consulta_tarifas_aneel.py --listar-distribuidoras
python consulta_tarifas_aneel.py --listar-subgrupos
python consulta_tarifas_aneel.py --listar-modalidades
python consulta_tarifas_aneel.py --listar-classes
```

Consultar tarifas (aceita nome parcial da distribuidora — o script resolve para o
`SigAgente` exato e avisa se houver ambiguidade):

```bash
python consulta_tarifas_aneel.py -d "LIGHT" --subgrupo B1 --modalidade Convencional

python consulta_tarifas_aneel.py -d "CPFL JAGUARI" --subgrupo A4 --data-vigencia 2026-01-15

python consulta_tarifas_aneel.py -d "ENEL RJ" -o enel_rj_tarifas.csv
```

Filtros disponíveis: `--distribuidora/-d`, `--cnpj`, `--reh`, `--subgrupo`, `--modalidade`,
`--classe`, `--subclasse`, `--base-tarifaria`, `--ano`, `--data-vigencia`,
`--data-inicio`/`--data-fim` (sobreposição de intervalo), `--limit`.

Os filtros de igualdade (distribuidora, subgrupo, modalidade, classe, subclasse,
base tarifária, CNPJ) são aplicados no servidor da ANEEL via parâmetro `filters`
do CKAN. Os filtros de data são aplicados localmente após a busca, pois a API não
suporta filtro de intervalo de datas nativamente.

## Saída

Por padrão, salva um CSV (separador `;`, decimal com ponto, `utf-8-sig` — abre
direto no Excel BR) em `output/tarifas_<timestamp>.csv`, e imprime uma amostra de
10 linhas no terminal. Use `--sem-amostra` para suprimir a amostra e `-o` para
escolher o caminho/nome do arquivo.

## Notas técnicas

- Endpoint: `https://dadosabertos.aneel.gov.br/api/3/action/datastore_search`
- `resource_id` fixo: `fcf2906c-7c32-4b9b-a637-054e7a5234f4`
- `datastore_search_sql` **não** está habilitado nesta instância CKAN — por isso
  o script usa `datastore_search` com paginação (limite de 32.000 registros por
  requisição) em vez de SQL bruto.
- `cache/` guarda listas de valores distintos (distribuidoras, subgrupos etc.)
  por até 7 dias; use `--atualizar-cache` para forçar atualização.
- Não existe campo "Ano" nativo no dataset — é derivado do ano de
  `DatInicioVigencia`.
- `aneel_api.py` concentra toda a lógica de chamada à API (paginação, cache,
  resolução de distribuidora, conversão de valores BRL) e é importado tanto por
  `app.py` quanto por `consulta_tarifas_aneel.py`.
