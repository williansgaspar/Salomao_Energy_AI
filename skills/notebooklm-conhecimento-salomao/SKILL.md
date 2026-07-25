---
name: notebooklm-conhecimento-salomao
description: Consulta automaticamente o acervo externo do SalomãoAI no Gemini Notebook (NotebookLM) por meio do wrapper do projeto. Use quando a pergunta depender de material, precedente, arquivo, análise ou dado que esteja no "Salomão AI - Repositório do Conhecimento", quando o usuário mencionar NotebookLM, Gemini Notebook ou base de conhecimento, ou quando a base local não contiver o conteúdo solicitado. Não use como substituto de fontes primárias locais ou oficiais para afirmar regra vigente do SEB.
---

# Acervo Gemini Notebook do SalomãoAI

## Fluxo obrigatório

1. Consulte `references/notebooks.md` para selecionar o notebook e usar o UUID completo.
2. Execute `./tools/notebooklm/Salomao-NotebookLM.ps1 check` antes de consultar o acervo. Exija `status: "ok"` e `token_fetch: true`.
3. Se a credencial estiver inválida, execute `./tools/notebooklm/Salomao-NotebookLM.ps1 login`, deixe o usuário concluir o login na janela aberta e repita `check`.
4. Consulte o conteúdo com:

   ```powershell
   .\tools\notebooklm\Salomao-NotebookLM.ps1 run ask "<pergunta objetiva>" -n <UUID> --json
   ```

5. Sintetize a resposta e identifique o notebook e as fontes internas citadas pelo retorno JSON.

## Regras de uso

- Use sempre o wrapper do projeto; ele seleciona o executável `uv`, aplica a compatibilidade para `notebook.google.com` e limita a configuração ao processo atual.
- Passe o UUID do notebook explicitamente. Não use `notebooklm use` nem contexto implícito.
- Não use `--save-as-note`, não crie nem altere notebooks, fontes ou artefatos sem solicitação específica do usuário.
- Não exponha `storage_state.json`, cookies, tokens ou qualquer valor de credencial.
- Trate o notebook como fonte de descoberta, contexto e recuperação documental. Para conclusão técnico-regulatória, cumpra também o protocolo do `AGENTS.md`: texto primário local, boletim e fonte oficial quando exigido.
- Se a consulta não recuperar evidência suficiente, declare a lacuna; não preencha com inferência.
