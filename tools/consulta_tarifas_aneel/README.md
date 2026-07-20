# Consulta de Tarifas ANEEL

Aplicativo para consulta, simulação, comparação e análise histórica das tarifas de aplicação das distribuidoras publicadas na API de Dados Abertos da ANEEL.

Versão atual: **Revisão 10 (19/07/2026)**. O histórico está em [REVISIONS.md](REVISIONS.md) e a metodologia em [docs/metodologia.md](docs/metodologia.md).

## Funcionalidades

- Consulta por distribuidora, data/mês, subgrupo e modalidade.
- Filtros avançados de REH, base tarifária, classe, detalhe, acessante e posto.
- Vigência por data exata ou por qualquer sobreposição com o mês selecionado.
- Simulação por consumo em cada posto ou por consumo total estimado.
- Cálculo separado de TE, TUSD Energia e TUSD Demanda.
- Comparação de duas composições tarifárias com o mesmo perfil.
- Importação de perfil CSV/XLSX com colunas `posto` e `consumo_mwh`.
- Memória auditável por componente, posto, tarifa, quantidade e subtotal.
- Resumo separado de TE, TUSD Energia e TUSD Demanda, protegido contra resultados obsoletos após mudança de parâmetros.
- Tema institucional claro/escuro com marcas oficiais da Prefeitura do Rio e do Projeto Rio de Energia Verde.
- Indicadores de TE, TUSD Energia e TUSD Demanda ponderadas por mês típico de 720 horas para comparação preliminar ACL × ACR, sem efeito sobre a simulação.
- Leitura local de fatura Light Grupo A em PDF ou imagem, com OCR, conversão kWh→MWh, retirada de PIS/COFINS e ICMS, conferência manual e reconciliação TE/TUSD com a composição ANEEL.
- Histórico visual de TE/TUSD.
- Exportações CSV, XLSX e PDF com metadados da fonte.

## Instalação e execução

```powershell
cd "tools\consulta_tarifas_aneel"
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Abra `http://localhost:8501`.

## Testes

Na raiz do projeto Salomão AI:

```powershell
python -m pytest -q
```

## Estrutura

```text
consulta_tarifas_aneel/
├── app.py                       # interface Streamlit
├── consulta_tarifas_aneel.py   # CLI
├── aneel_api.py                # cliente CKAN legado compatível com o CLI
├── src/
│   ├── aneel/                  # repositório/fachada da fonte
│   ├── domain/                 # vigência, composição e cálculos
│   ├── exports/                # XLSX e PDF
│   └── ui/                     # tema e componentes comuns
├── tests/                      # testes unitários
├── docs/metodologia.md
├── revisions/                  # versões históricas da interface
├── assets/
└── .streamlit/config.toml
```

## API

- Endpoint: `https://dadosabertos.aneel.gov.br/api/3/action/datastore_search`
- Resource ID: `fcf2906c-7c32-4b9b-a637-054e7a5234f4`
- Acesso público, sem autenticação.
- Consultas paginadas, com cache local das listas de valores distintos.

## Limitações

O resultado é uma estimativa técnica. Não contempla tributos, bandeiras, reativos, ultrapassagem, descontos, encargos ou condições particulares da unidade consumidora, e não substitui a fatura da distribuidora.

## CLI

```powershell
python consulta_tarifas_aneel.py --listar-distribuidoras
python consulta_tarifas_aneel.py -d "LIGHT" --subgrupo A4 --data-vigencia 2026-07-01
```

Use `python consulta_tarifas_aneel.py --help` para a relação completa de filtros.
