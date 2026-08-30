# Publicação privada — Azure Container Apps + Microsoft Entra ID

## Escopo

O app permanece aberto no desenvolvimento local. No ambiente publicado, `SALOMAO_REQUIRE_LOGIN=true` torna o login Microsoft obrigatório e libera a aplicação apenas aos endereços em `SALOMAO_ALLOWED_EMAILS`.

Os PDFs enviados são tratados pelo processo da aplicação. Não configure volume persistente para `tmp/`, `cache/` ou `output/` na publicação.

## 1. Registro no Microsoft Entra

No tenant `d9d56945-4ae7-4ab2-9905-2020f57a3fde`:

1. Acesse **App registrations** e crie `Salomão AI — Tarifas ANEEL`.
2. Selecione **Accounts in this organizational directory only**.
3. Em **Authentication**, adicione a plataforma **Web** e a URI de redirecionamento final: `https://<dominio-do-app>/oauth2callback`.
4. Em **Certificates & secrets**, crie um segredo de cliente com prazo reduzido e guarde o valor uma única vez no cofre de segredos do Azure.
5. Copie o **Application (client) ID**. O Tenant ID já é `d9d56945-4ae7-4ab2-9905-2020f57a3fde`.

## 2. Segredos e variáveis do Container App

Cadastre `SALOMAO_AUTH_COOKIE_SECRET` e `SALOMAO_AUTH_CLIENT_SECRET` como *secrets* no Azure Container Apps. Crie um valor aleatório longo para o primeiro; ele não é a senha de nenhum usuário.

Defina as variáveis de ambiente abaixo no Container App:

| Variável | Valor |
| --- | --- |
| `SALOMAO_REQUIRE_LOGIN` | `true` |
| `SALOMAO_AUTH_TENANT_ID` | `d9d56945-4ae7-4ab2-9905-2020f57a3fde` |
| `SALOMAO_AUTH_CLIENT_ID` | Application (client) ID do registro |
| `SALOMAO_AUTH_REDIRECT_URI` | `https://<dominio-do-app>/oauth2callback` |
| `SALOMAO_AUTH_COOKIE_SECRET` | Referência ao secret correspondente |
| `SALOMAO_AUTH_CLIENT_SECRET` | Referência ao secret correspondente |
| `SALOMAO_ALLOWED_EMAILS` | E-mails permitidos, separados por vírgula |

Não inclua segredos em Git, Dockerfile, variáveis de build ou arquivos `.toml` versionados.

## 3. Publicação

Construa a imagem a partir desta pasta e publique-a em um Azure Container Registry. Depois, crie um Azure Container App com ingresso externo e porta de destino `8501`.

Antes de abrir o acesso aos usuários, informe o domínio HTTPS definitivo no registro Entra e confirme que a URI de redirecionamento termina exatamente em `/oauth2callback`.

## 4. Validação de aceite

1. Abrir a URL anônima: deve mostrar somente a tela de acesso.
2. Entrar com e-mail listado: deve abrir o simulador e permitir sair.
3. Entrar com e-mail do tenant que não conste na lista: deve receber bloqueio de autorização.
4. Acessar `/oauth2callback` fora do fluxo: não deve revelar conteúdo do simulador.
5. Enviar uma fatura de teste e confirmar que não há arquivo persistido após a reinicialização da revisão do Container App.
