# Salomão Core

Camada local de recuperação de evidências normativas. Ela não substitui a análise
jurídico-regulatória nem gera parecer por conta própria: impede que qualquer camada
gerativa responda sem fontes canônicas rastreáveis.

## Uso rápido

```powershell
python tools/salomao_core/consulta.py query "consumidores Grupo A carga individual inferior a 500 kW"
python tools/salomao_core/consulta.py query "consumidores Grupo A carga individual inferior a 500 kW" --minuta
python tools/salomao_core/consulta.py self-test
python -m streamlit run tools/salomao_core/app.py
```

## Bancada regulatória

A interface Streamlit é a camada de trabalho local do núcleo auditável. Ela conduz um
fluxo operacional completo:

1. **Rotina de hoje** — ordena as fontes oficiais pendentes do boletim por tema de trabalho,
   abre a fonte e exporta um caderno diário de triagem.
2. **Abrir caso** — registra questão, fatos e produto esperado; recupera somente evidências
   primárias verificadas e aciona alerta adicional para assuntos sensíveis ao tempo.
3. **Análise e minuta** — monta a minuta local rastreável e, opcionalmente, pede uma análise
   à API a partir do pacote de evidências já recuperado.
4. **Monitoramento** — apresenta a situação do boletim, catálogo e fila de curadoria.

O copiloto por API é opcional. A chave é informada na barra lateral, permanece apenas na
sessão do navegador e a chamada só ocorre após o clique em **Gerar análise controlada**. A
pergunta, os fatos informados e os trechos das fontes recuperadas são enviados à API nessa
etapa; não use o recurso com dados que não possam sair do ambiente local.

Ela não promove fontes, não altera o catálogo e não produz conclusão normativa sem
evidência primária `verified`.

## Contrato operacional

1. Recuperar apenas registros `verified`, `primary_text` e existentes localmente.
2. Aplicar a matriz de compatibilização para priorizar cópias canônicas.
3. Entregar trecho, caminho local, status e data de verificação.
4. Só então permitir uma resposta que cite instrumento, data e dispositivo.
5. Sem evidência, a saída é `insufficient_evidence`; não há conclusão normativa.

## Minuta auditável

`--minuta` e a interface local estruturam a redação a partir do pacote recuperado.
Cada fundamento recebe instrumento, data, dispositivo identificado, trecho, arquivo,
status de verificação e nível de confiança. A minuta não infere a regra aplicável nem
dispensa a verificação de vigência e do caso concreto.

O SharePoint e o Copilot Notebook permanecem como canais complementares de publicação
e consulta, nunca como a fonte decisória do núcleo.
