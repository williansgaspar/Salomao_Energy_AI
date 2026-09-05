# Consulta de Tarifas ANEEL

Aplicativo para consulta, simulação, comparação e análise histórica das tarifas de aplicação das distribuidoras publicadas na API de Dados Abertos da ANEEL.

Versão atual: **Revisão 18 (29/07/2026)**. O histórico está em [REVISIONS.md](REVISIONS.md), a metodologia em [docs/metodologia.md](docs/metodologia.md) e o roteiro de publicação privada em [docs/publicacao_azure_entra.md](docs/publicacao_azure_entra.md).

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
- Bandeira tarifária mensal: sugestão automática pelo histórico oficial de acionamento da ANEEL (por competência), seleção manual entre bandeiras já apuradas ou informação de um adicional avulso; o valor integra a conta ACR de referência.
- Cenário SCEE/MMGD para Grupo B: parâmetros legais de transição do Fio B (arts. 26 e 27 da Lei nº 14.300/2022, GD I/II/III) aplicados sobre a tarifa B3 vigente, com desconto e ajustes financeiros informáveis; a classificação do subgrupo só seleciona o simulador — não atesta adesão ao SCEE.
- Leitura das componentes tarifárias homologadas publicadas pela ANEEL (datasets 2023-2026), complementar à consulta de tarifas de aplicação.
- Publicação privada opcional: autenticação Microsoft Entra ID (OIDC) com lista de e-mails autorizados, para o ambiente hospedado — o uso local segue aberto por padrão. Ver [docs/publicacao_azure_entra.md](docs/publicacao_azure_entra.md).

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
│   ├── aneel/                  # repositório/fachada da fonte (tarifas, bandeiras, componentes)
│   ├── domain/                 # vigência, composição, cálculos, enquadramento A/B, preenchimento e SCEE
│   ├── exports/                # XLSX e PDF
│   └── ui/                     # tema e componentes comuns
├── tests/                      # testes unitários
├── docs/metodologia.md
├── docs/publicacao_azure_entra.md  # roteiro de publicação privada (Azure Container Apps + Entra ID)
├── revisions/                  # versões históricas da interface
├── assets/
├── Dockerfile                  # imagem para publicação
├── docker-entrypoint.sh        # entrada segura em container
├── .streamlit/config.toml
└── .streamlit/secrets.example.toml  # modelo de segredos; não versionar o secrets.toml real
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
