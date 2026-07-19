---
name: estrutura-institucional-seb
description: Identifica natureza jurídica, competência, responsabilidade e fluxo decisório entre CNPE, MME, CMSE, ANEEL, EPE, ONS, CCEE, agentes e consumidores do Setor Elétrico Brasileiro. Use para responder quem formula política, planeja, concede, regula, fiscaliza, opera, contabiliza ou executa determinada atividade, inclusive em questões sobre SUI, governança, abertura do ACL e novas tecnologias.
---

# Estrutura institucional do SEB

## Princípio

Responder competência por função e fundamento legal, não por associação temática. Um mesmo tema pode envolver política, planejamento, regulação, fiscalização, operação física e operação comercial em instituições diferentes.

## Fluxo obrigatório

1. Delimitar a decisão ou atividade concreta e sua data de referência.
2. Classificar a função: política; planejamento; poder concedente; regulação; fiscalização; operação física; comercialização/contabilização; execução pelo agente.
3. Identificar a instituição e o dispositivo que atribui a competência.
4. Aplicar `seb-arcabouco-legal` para verificar lei, decreto, regimento ou ato delegatório vigente.
5. Separar competência própria, delegada, compartilhada, consultiva e operacional.
6. Descrever o fluxo entre instituições quando houver mais de uma etapa.
7. Informar limites da competência e pontos ainda pendentes de regulamentação.

## Mapa funcional de descoberta

- CNPE: diretrizes de política energética, conforme competência legal.
- MME: formulação e implementação de política e exercício das competências do poder concedente.
- CMSE: monitoramento de segurança de suprimento e coordenação dentro de sua competência.
- ANEEL: regulação e fiscalização das atividades que a lei lhe atribui.
- EPE: estudos e planejamento energético.
- ONS: coordenação e controle da operação do SIN conforme autorização legal e Procedimentos de Rede.
- CCEE: viabilização comercial, registro, contabilização e liquidação conforme lei, convenção, regras e procedimentos.
- Agentes: execução das atividades autorizadas, concedidas, permitidas ou contratadas.

Usar esse mapa apenas para roteamento. Confirmar o fundamento específico antes de responder formalmente.

## Regras de análise

- Não confundir órgão público, autarquia, empresa pública, associação civil e sistema físico.
- Não atribuir ao ONS competência comercial nem à CCEE operação física do SIN.
- Não atribuir automaticamente à ANEEL toda decisão setorial; verificar se a matéria é de lei, CNPE, MME ou poder concedente.
- Não tratar estudo da EPE como decisão normativa.
- Não confundir aprovação regulatória de procedimento com sua execução operacional.

## SUI e reformas recentes

Para SUI, separar criação legal, designação do prestador, autorização/fiscalização, hipóteses de acionamento, duração, preço, custeio e procedimentos CCEE. Cada elemento pode ter fonte e estágio regulatório distintos.

Não usar parâmetros de consulta pública como regra vigente. Conferir o texto atualizado da Lei nº 9.074/1995, atos do MME/ANEEL e procedimentos publicados na data da análise.

## Referência datada

`references/orgaos-e-agentes-seb.md` é material de trabalho consolidado em 13/07/2026. Usar para formular buscas, não como fonte final para composição atual, prazos, parâmetros de SUI ou eventos institucionais recentes.

## Condições de parada

Se a competência depender de regimento, delegação ou ato recente não localizado, declarar a limitação. Não resolver conflito institucional por inferência.

## Atualização

Registrar instrumentos estruturantes no catálogo e manter fatos voláteis fora do corpo da skill. Executar `scripts/validate_project.py` após alterações.
