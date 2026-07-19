---
name: geracao-pareceres-seb
description: Planeja, pesquisa, redige e revisa pareceres e notas técnico-regulatórias sobre o Setor Elétrico Brasileiro com matriz de alegações e evidências, cadeia normativa, competência institucional, análise do caso e conclusão calibrada. Use quando o usuário pedir parecer formal, nota técnica, posicionamento regulatório, análise para cliente ou recomendação para gestão pública municipal envolvendo ACL, ACR, MMGD, tarifas, operação, armazenamento ou comercialização.
---

# Pareceres técnico-regulatórios do SEB

## Regra de saída

Não iniciar pela redação. Fechar primeiro a questão, os fatos relevantes e a matriz de alegações e evidências. Fluência não compensa lacuna normativa.

## Fluxo obrigatório

### 1. Delimitar

Registrar:

- consulta objetiva e data de referência;
- destinatário e finalidade;
- fatos fornecidos, fatos assumidos e fatos faltantes;
- recortes fora do escopo;
- urgência e nível de formalidade.

Só pedir esclarecimento quando uma premissa faltante alterar materialmente a conclusão. Nos demais casos, declarar a premissa adotada.

### 2. Montar a matriz de alegações

Antes de redigir, listar internamente cada proposição material com:

| Alegação | Tipo | Fonte primária | Dispositivo | Data verificada | Estado | Confiança |
|---|---|---|---|---|---|---|

Usar como `Tipo`: norma, fato, interpretação, processo regulatório ou inferência. Usar como `Estado`: vigente, transição, proposta, revogado, controvertido ou não confirmado.

Uma alegação sem fonte suficiente não pode aparecer como conclusão definitiva.

### 3. Fechar a fundamentação

Aplicar `seb-arcabouco-legal` para:

- consultar catálogo, base local e boletim;
- confirmar fonte oficial e vigência;
- identificar cadeia normativa e dispositivo aplicável;
- distinguir data do ato, publicação, vigência e produção de efeitos.

Não citar índice, notícia, glossário, prova ou parecer anterior como substituto do texto primário.

### 4. Mapear competência e conteúdo

Usar `estrutura-institucional-seb` para competência. Consultar `comercializacao-acr-acl` ou `mmgd-novas-tecnologias` quando o mérito exigir, tratando seus fatos voláteis como pistas a reconfirmar, não como prova final.

### 5. Verificar precedentes

Pesquisar `knowledge_base/pareceres_anteriores/`. Tratar parecer anterior como precedente argumentativo, não como fonte normativa. Explicitar divergência relevante.

### 6. Analisar

Separar:

1. regra aplicável;
2. subsunção aos fatos;
3. interpretações alternativas e riscos;
4. lacunas ou regulamentação pendente;
5. consequência prática.

Não esconder controvérsia na fundamentação e apresentar certeza na conclusão.

### 7. Redigir e revisar

Escolher o modelo em `references/templates-por-audiencia.md`, usar o padrão de citação de `../seb-arcabouco-legal/references/modelo-citacao-parecer.md` e executar `references/checklist-qualidade.md`.

## Níveis de conclusão

- **Conclusiva:** texto primário, vigência, dispositivo e fatos estão confirmados.
- **Condicionada:** depende de premissa factual ou regra de transição explicitada.
- **Preliminar:** falta documento, ato oficial ou dado material.
- **Não conclusiva:** há controvérsia ou lacuna que impede posição responsável.

Informar o nível adotado e a data da verificação.

## Entregáveis

Por padrão, entregar o conteúdo na conversa. Se houver pedido de DOCX ou PDF, fechar primeiro o conteúdo e depois usar a skill específica de documentos ou PDF para produzir e verificar o arquivo.

Não duplicar nesta skill instruções de formatação de DOCX/PDF nem fatos regulatórios voláteis.
