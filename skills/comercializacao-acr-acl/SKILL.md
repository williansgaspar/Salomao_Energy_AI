---
name: comercializacao-acr-acl
description: Analisa contratação, contabilização, liquidação e custos nos ambientes ACR e ACL, incluindo CCEAR, CCEAL, migração, representação varejista, PLD, MCP, garantias, penalidades, MRE/GSF, TE, TUSD, TUST e encargos. Use para responder questões comerciais ou tarifárias do SEB, comparar alternativas contratuais, verificar requisitos e prazos ou fundamentar pareceres, sempre reconfirmando parâmetros, versões CCEE, tarifas e regras de transição.
---

# Comercialização — ACR e ACL

## Princípio

Separar contrato, lastro, contabilização, liquidação, uso da rede e tarifa. Não inferir uma regra de uma camada a partir de outra e não usar parâmetro de mercado sem data-base.

## Fluxo obrigatório

1. Identificar agente, ambiente, submercado, período, ponto de conexão, tensão, distribuidora e finalidade da análise.
2. Classificar a questão: elegibilidade/migração; contrato e risco; registro/representação; contabilização/liquidação; PLD/MCP; garantia/penalidade; tarifa/rede; ou encargo/transição.
3. Aplicar `seb-arcabouco-legal` e localizar a cadeia normativa.
4. Consultar as versões vigentes das Regras e Procedimentos CCEE em `knowledge_base/normas/regras_procedimentos_ccee/`, confirmando-as no portal oficial quando a versão afetar a resposta.
5. Usar `tools/consulta_tarifas_aneel/` para TE/TUSD, `tools/consulta_pld_ccee/` para PLD e `tools/bbce_curva_forward/` para curva forward quando aplicável.
6. Registrar data-base, filtros, unidade, base tarifária e origem do dado.
7. Separar resultado normativo, cálculo, premissa comercial e sensibilidade.

## Roteamento

### Migração e representação varejista

Verificar tensão, carga, classe, data pretendida, denúncia do contrato regulado, medição, representação e transições. Distinguir prazo legal máximo, cronograma regulatório vigente e proposta em consulta.

### ACR e leilões

Identificar produto, modalidade contratual, diretriz do certame, risco, início de suprimento e homologação. Não transformar nomenclatura histórica A-n em obrigação permanente sem conferir a norma vigente.

### ACL e contratos

Separar liberdade negocial do CCEAL das obrigações de registro, lastro, medição, garantias, contabilização e representação. Tratar preço, flexibilidade, sazonalização, modulação, garantias, rescisão, tributos e MCP como dimensões distintas.

### PLD, MCP, MRE e GSF

Não tratar PLD como preço universal dos contratos. Para valores, consultar dado oficial e registrar submercado e período. Para metodologia, citar Regra CCEE e ato aprovador aplicáveis à competência analisada.

### TE, TUSD e TUST

Não usar percentual médio como substituto de cálculo. Conferir distribuidora, subgrupo, modalidade, posto, classe, demanda, consumo, base tarifária, REH e período. Distinguir tarifa de aplicação, base econômica, tributos, bandeiras, demanda e energia.

### Descontos e encargos

Verificar beneficiário, fonte, outorga, data, expansão, transição e versão da Regra CCEE. Não generalizar desconto por fonte incentivada para todo consumidor livre.

## Referências em quarentena

Os arquivos em `references/` são estudos de trabalho produzidos em 13/07/2026 e podem conter dados incompletos, futuros ou não reconfirmados. Usá-los apenas para formular buscas e hipóteses. Nunca citar valores ou conclusões em parecer sem fonte primária atual.

## Condições de parada

Não concluir quando faltar versão CCEE, REH, período tarifário, configuração contratual, regra de transição ou dado oficial necessário. Informar exatamente o insumo faltante.

## Atualização

Promover informação recorrente somente depois de registrar a fonte no catálogo ou em índice operacional versionado. Manter parâmetros anuais e valores fora do corpo desta skill. Executar `scripts/validate_project.py` após alterações.
