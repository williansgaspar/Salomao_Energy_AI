# Consulta BBCE Curva Forward

Ferramentas para consultar a API do **BBCE Connect** (Portal do Desenvolvedor
BBCE) e obter dados da **BBCE Curva Forward** -- a referência de cotações de
preços futuros de energia elétrica do país com base em negócios reais,
calculada diariamente pela BBCE a partir do pregão da plataforma [EHUB
BBCE](https://www.bbce.com.br/ehub/). Duas interfaces sobre a mesma lógica de
consulta (`bbce_api.py`):

- **`app.py`** -- interface web (Streamlit), com abas para curva geral e
  curva por produto, gráfico e tabela
- **`consulta_curva_forward.py`** -- script de linha de comando

## Credenciais (obrigatório)

Ao contrário da ferramenta de tarifas ANEEL (`tools/consulta_tarifas_aneel`),
esta API **requer autenticação** e uma assinatura do BBCE Connect no **plano
Essentials**. Você precisa ter, junto à BBCE:

- `apiKey` -- chave de API da sua empresa
- e-mail e senha de um usuário da plataforma
- `companyExternalCode` -- código externo numérico da sua empresa na BBCE

Copie `.env.example` para `.env` (nesta pasta) e preencha os quatro valores.
**Nunca compartilhe ou faça commit do `.env` preenchido** -- ele contém
segredos de acesso à sua conta na BBCE.

### Como obter as credenciais (fonte: FAQ/"Primeiros Passos" do Portal do
Desenvolvedor BBCE, confirmado em 15/07/2026)

O login da API **é diferente do login do site EHUB** (que exige código por
e-mail/2FA) -- são dois sistemas de autenticação separados:

- `BBCE_EMAIL` / `BBCE_PASSWORD` -- são as **mesmas credenciais que você já
  usa para logar no EHUB** (`ehub.bbce.com.br`). O endpoint de login da API
  (`POST /v2/login`) não pede código de 2FA -- esse OTP por e-mail é uma
  camada de segurança só da sessão de navegador do EHUB, não do canal de
  API.
- `BBCE_API_KEY` -- **não é autogerada nem enviada por e-mail de login**. É
  fornecida uma única vez pelo time de suporte da BBCE. Para obtê-la:
  1. Confirme que sua empresa tem o **BBCE Connect contratado** (e,
     especificamente, o plano que dá acesso à Curva Forward -- a
     documentação indica "Plano Requerido: Essentials"). Se ainda não,
     contato comercial: `comercial@bbce.com.br`.
  2. Peça a `apiKey` ao suporte técnico: `suporte@bbce.com.br` ou telefone/
     WhatsApp `(11) 3077-0900`.
- `BBCE_COMPANY_EXTERNAL_CODE` -- código externo numérico da empresa no
  EHUB (o mesmo usado no login do site).

O login é feito uma vez (`POST /v2/login`) e o token (`idToken`, válido por
4h) fica em cache local (`cache/session.json`, criado automaticamente); as
consultas seguintes reusam o token ou o renovam via `POST /v1/refresh-token`
sem exigir novo login. Se você trocar de usuário/empresa no `.env`, apague
`cache/session.json` para forçar um novo login.

## Instalação

```bash
pip install -r requirements.txt
```

## Interface web

```bash
streamlit run app.py
```

Abre em `http://localhost:8501`. Duas abas:

1. **Curva Forward (geral)** -- `GET /v1/curve/bbce-fwd`: a curva de preço
   projetado por vértice de data (ex.: PLD futuro), com filtros opcionais de
   fonte de energia e submercado.
2. **Curva por Produto** -- `GET /v1/curve-product/bbce-fwd`: a curva
   detalhada por ticker/produto negociável (mensal, trimestral etc.), com
   filtro opcional de tipo de preço (Preço Fixo ou SWAP).

Cada aba mostra um gráfico de linha, a tabela completa e um botão para baixar
CSV.

## Uso do CLI

```bash
# Curva geral na data de hoje
python consulta_curva_forward.py

# Curva geral em uma data específica, filtrada por fonte e submercado
python consulta_curva_forward.py -d 2026-07-10 --fonte CON --regiao SE

# Curva por produto (ticker), filtrada por tipo de preço
python consulta_curva_forward.py -d 2026-07-10 --por-produto --tipo-curva PrecoFixo

# Salvar em um caminho específico
python consulta_curva_forward.py -d 2026-07-10 -o saida/curva.csv
```

Filtros disponíveis: `--data/-d` (obrigatório conceitualmente -- padrão é
hoje), `--fonte` (`CON | I0 | I5 | I1 | CQ5`), `--regiao` (`SE | SU | NE |
NO`, só se aplica à curva geral), `--tipo-curva` (`PrecoFixo | SWAP`, só se
aplica à curva por produto), `--por-produto`, `-o/--output`, `--sem-amostra`.

## Saída

Por padrão, salva um CSV (separador `;`, `utf-8-sig` -- abre direto no Excel
BR) em `output/curva_forward_<data>.csv`, e imprime uma amostra de 10
registros no terminal.

## Notas técnicas

- Endpoint base usado nos exemplos do Portal do Desenvolvedor:
  `https://api-beta.qa.bbce.tech/bus`. **Não confirmado independentemente se
  esta é também a URL de produção** ou se há uma URL distinta para uso em
  produção -- os exemplos de resposta da própria documentação trazem dados
  que parecem reais (tickers, datas e preços de negócios de 2025), então é o
  endpoint usado por padrão aqui. Se a BBCE informar uma URL diferente,
  defina `BBCE_BASE_URL` no `.env` para sobrescrever.
- Endpoints cobertos (todos de leitura): `POST /v2/login`, `POST
  /v1/refresh-token`, `GET /v1/curve/bbce-fwd`, `GET
  /v1/curve-product/bbce-fwd`. Os endpoints de escrita da mesma seção da API
  (`GET/POST /v1/curve/call` -- consulta e inserção de "calls"/contribuições
  de preço) **não foram implementados** aqui, por serem operações de escrita
  na plataforma de negociação, fora do escopo de uma ferramenta de consulta.
  Se precisar deles no futuro, o padrão de `bbce_api.py` (função `_get`,
  headers de autenticação) é diretamente reutilizável para um `_post`
  equivalente.
- `bbce_api.py` concentra toda a lógica de autenticação e chamada à API
  (login, cache/renovação de token, retentativa) e é importado tanto por
  `app.py` quanto por `consulta_curva_forward.py`.
- Fonte da documentação da API: [Portal do Desenvolvedor
  BBCE](https://portaldodesenvolvedor.bbce.com.br/), coleção "BBCE Curva
  Forward" (requer plano Essentials).
