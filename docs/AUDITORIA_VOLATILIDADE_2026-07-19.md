# Auditoria de referências voláteis — 19/07/2026

## Escopo

Varredura de `AGENTS.md`, `CLAUDE.md`, `skills/**/*.md`, respostas de avaliação e catálogo,
procurando datas, percentuais, valores, expressões de vigência, consultas públicas e atos
de 2025-2026. A varredura identifica risco; a confirmação depende de fonte primária.

## Achados materiais

| Severidade | Local | Achado | Tratamento |
|---|---|---|---|
| Crítica | baseline 001 | Datas de 01/08/2026 e 01/12/2027 atribuídas à lei convertida, embora o art. 15, § 17, I, preveja prazos de 24 e 36 meses | Preservado como regressão; caso marcado com falha crítica |
| Alta | referência institucional SUI | Parâmetros de 110%, 180 dias e designação automática da distribuidora | Removidos; consulta pública classificada como proposta |
| Alta | modelo de parecer | Decreto nº 5.163/2004 qualificado integralmente como vigente | Substituído por verificação obrigatória do dispositivo compilado |
| Alta | referência TE/TUSD Light | Dados futuros de novembro/2026 e REH não confirmada | Mantida em quarentena explícita; proibido uso em cálculo/parecer |
| Média | armazenamento | Números de REN 1.161/2026 e 1.162/2026 não confirmados | Mantidos apenas como alerta negativo; proibida citação |
| Média | PLD e descontos | Valores e versões CCEE 2026 mudam por ciclo | Exigida data-base e confirmação da versão oficial |
| Média | órgãos/agentes | Eventos, composição e percentuais do SIN sensíveis ao tempo | Referência em quarentena parcial; uso apenas para descoberta |

## Conclusão

A auditoria detectou uma regressão real no primeiro benchmark, demonstrando que o controle
positivo dos gabaritos não substitui execução cega. As referências mais perigosas estão
agora removidas ou explicitamente quarantinadas. Permanecem como dívida verificável:
confirmar a regulamentação operacional do armazenamento e promover apenas versões CCEE
cuja aprovação, vigência e hash tenham sido conferidos.
