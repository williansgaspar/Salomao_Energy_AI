---
name: seb-arcabouco-legal
description: Identifica, verifica e encadeia o fundamento jurídico-regulatório do Setor Elétrico Brasileiro, incluindo leis, decretos, atos do MME e da ANEEL, Regras e Procedimentos da CCEE e Procedimentos de Rede do ONS. Use para pesquisar fundamento legal, conferir vigência ou revogação, revisar citações, distinguir regra vigente de proposta regulatória e construir a cadeia normativa de pareceres sobre ACL, ACR, MMGD, tarifas, armazenamento, operação e comercialização.
---

# Arcabouço legal-regulatório do SEB

## Princípio

Tratar toda afirmação normativa como uma alegação que precisa de evidência. Não presumir que um documento é vigente apenas porque está na base local, em um índice ou em uma skill.

## Fluxo obrigatório

1. Delimitar a questão jurídica, a data de referência e o fato regulado.
2. Consultar `knowledge_base/catalogo_normativo/catalogo.json` para localizar instrumentos e verificar o estado da conferência.
3. Pesquisar o texto local em `Legislacao/` e `knowledge_base/normas/`.
4. Consultar `Atualizacoes_Mercado/Boletim_Atualizacoes_SEB.html` para identificar atos ou processos recentes que possam afetar a resposta.
5. Confirmar em fonte oficial quando o registro não estiver verificado, a resposta depender de vigência ou transição, o tema for temporalmente sensível ou não houver texto primário local.
6. Montar a cadeia aplicável, sem forçar níveis inexistentes: Constituição ou lei → decreto → ato ANEEL/MME → Regra/Procedimento CCEE ou Procedimento de Rede ONS.
7. Separar texto normativo, interpretação, processo regulatório em curso e inferência técnica.
8. Informar a data, o método e o nível de confiança da verificação.

## Hierarquia e competência

- Constituição e leis estabelecem competência, direitos e obrigações estruturantes.
- Decretos regulamentam a lei dentro da competência do Poder Executivo.
- RENs estabelecem regras gerais da ANEEL; REHs homologam valores, tarifas ou resultados específicos.
- Portarias e outros atos do MME veiculam diretrizes e decisões dentro de sua competência legal.
- Regras e Procedimentos da CCEE e Procedimentos de Rede do ONS disciplinam a execução técnica e comercial depois da aprovação regulatória aplicável.

Não tratar essa lista como hierarquia linear absoluta entre todos os atos infralegais. Verificar competência, fundamento legal e ato de aprovação em cada caso.

## Política de fontes

Usar como evidência final, por ordem de preferência:

1. texto oficial compilado ou publicação oficial do ato;
2. Diário Oficial e bases oficiais do Planalto, ANEEL, MME, CCEE ou ONS;
3. texto primário local cuja origem e integridade estejam registradas;
4. nota técnica ou documento institucional oficial;
5. fonte secundária, somente para contexto e descoberta.

Índices, boletins, glossários, provas e pareceres anteriores não substituem o texto primário. Nunca converter notícia, consulta pública, agenda regulatória ou minuta em obrigação vigente.

## Vigência e relações

Verificar separadamente existência e autenticidade; data do instrumento, publicação, entrada em vigor e produção de efeitos; alterações, revogações, decisões judiciais e transições; versão aplicável à data do fato; e dispositivo exato que sustenta a afirmação.

Se a cadeia de vigência não puder ser fechada, declarar a limitação e evitar conclusão definitiva.

## Citação e parecer

Usar `references/modelo-citacao-parecer.md` para o formato de citação e a estrutura formal. Consultar `references/hierarquia-normativa.md` apenas como mapa de descoberta; reconfirmar fatos voláteis no catálogo e na fonte oficial.

## Incorporação de novo ato

1. Salvar o texto primário na pasta temática existente.
2. Registrar o instrumento no catálogo com `status: pending`.
3. Conferir fonte oficial, integridade, datas e relações.
4. Promover para `verified` somente com `official_url`, `checked_at` e `method`.
5. Atualizar índices derivados quando necessário.
6. Executar `scripts/validate_project.py`.

Não embutir fatos voláteis no corpo desta skill. Mantê-los no catálogo ou em referência datada.
