# Órgãos e Agentes do SEB — Fundamentos Legais e Competências

> **QUARENTENA PARCIAL — NÃO CITAR COMO FONTE FINAL.** Fundamentos estruturais podem orientar a pesquisa, mas composição, governança, eventos de 2025-2026 e parâmetros do SUI precisam de reconfirmação em lei, decreto, regimento ou ato oficial vigente.

> Conteúdo consolidado em 13/07/2026, combinando conhecimento de treinamento (até maio/2025) com busca web para eventos de 2025-2026. Confirme composição/governança atual (ex: diretoria da ANEEL, regimento interno do ONS/CCEE) na fonte oficial antes de usar em um parecer.

## Sumário

1. [CNPE](#cnpe)
2. [MME](#mme)
3. [CMSE](#cmse)
4. [ANEEL](#aneel)
5. [EPE](#epe)
6. [ONS](#ons)
7. [CCEE](#ccee)
8. [SIN](#sin)
9. [Categorias de agentes](#categorias-de-agentes)
10. [SUI — Supridor de Última Instância](#sui)

## CNPE

- **Base legal:** Lei nº 9.478, de 6 de agosto de 1997 (mesma lei que criou a ANP).
- **Natureza:** órgão colegiado de assessoramento ao Presidente da República.
- **Composição:** ministros de Estado de áreas afins (Minas e Energia, Fazenda, Meio Ambiente, Agricultura etc.) e representantes de outros setores (não é um colegiado fechado só de ministros), presidido pelo Ministro de Minas e Energia — os Ministros podem ser representados por seus Secretários-Executivos nas reuniões. As atividades dos integrantes são consideradas de relevante interesse público e **não remuneradas**. Reúne-se ordinariamente uma vez por ano e extraordinariamente quando convocado pelo presidente; pode constituir Grupos de Trabalho e Comitês Técnicos.
- **Competência:** formular a política nacional de energia (petróleo, gás, energia elétrica, biocombustíveis), assegurando o suprimento em todo o território e a proteção do consumidor; edita Resoluções CNPE (ex: Resolução CNPE nº 01/2024, sobre governança de modelos computacionais, mencionada nas atribuições do CMSE).

## MME

- **Natureza:** Ministério do Poder Executivo federal.
- **Competência:** formula e implementa a política energética nacional; é o poder concedente de concessões e autorizações do setor elétrico; edita portarias (ex: Portaria Normativa MME nº 97/2024, sobre LRCAP); preside CNPE e CMSE; conduz consultas públicas sobre regulamentação de política (ex: CP MME nº 196/2025, sobre abertura do ACL de baixa tensão e regras do SUI).

## CMSE

- **Base legal:** vinculado ao MME; atribuições detalhadas por decreto e por resoluções do CNPE.
- **Competência:** monitorar as condições de atendimento eletroenergético e avaliar riscos de descontinuidade/desabastecimento; coordenar ações preventivas entre ANEEL, ONS, EPE e CCEE; define parâmetros de governança de risco dos modelos computacionais do setor (ex: CVaR — Conditional Value at Risk — usado para calibrar a aversão a risco dos modelos de otimização do despacho/preço).
- **Marco recente:** 307ª Reunião (jul/2025) — regras de governança do CVaR; reunião de jun/2026 — manutenção dos parâmetros de CVaR para 2027 e cobrança de cronograma para novos modelos do SIN.

## ANEEL

- **Base legal:** Lei nº 9.427, de 26 de dezembro de 1996.
- **Natureza:** autarquia em regime especial, vinculada ao MME.
- **Competência:** regular e fiscalizar a produção, transmissão, distribuição e comercialização de energia elétrica; outorgar (por delegação do poder concedente) e fiscalizar concessões/permissões/autorizações; definir e homologar tarifas (REH); editar Resoluções Normativas (REN); aprovar os Procedimentos de Rede do ONS e as Regras/Procedimentos de Comercialização da CCEE antes de entrarem em vigor; julgar recursos administrativos e aplicar penalidades.
- **Ponto de atenção:** a ANEEL não opera o sistema nem comercializa energia — ela regula e fiscaliza quem faz isso (ONS e CCEE).

## EPE

- **Base legal:** Lei nº 10.847, de 15 de março de 2004.
- **Natureza:** empresa pública federal vinculada ao MME.
- **Competência:** planejamento de longo e médio prazo do setor energético — Plano Nacional de Energia (PNE, horizonte ~30 anos), Plano Decenal de Expansão de Energia (PDE, horizonte 10 anos); estudos de viabilidade socioambiental de empreendimentos de geração/transmissão; suporte técnico aos leilões de energia (cálculo de garantia física, por exemplo).
- **Ponto de atenção:** a EPE não decide política (isso é CNPE/MME) nem regula (isso é ANEEL) — ela produz os estudos técnicos que fundamentam as decisões de expansão.

## ONS

- **Base legal:** Lei nº 9.648, de 27 de maio de 1998 (mesma lei que criou o MAE, predecessor da CCEE).
- **Natureza:** associação civil de direito privado, sem fins lucrativos, sob fiscalização e regulação da ANEEL.
- **Competência:** coordenar e controlar a operação das instalações de geração e transmissão do SIN, buscando menor custo para o sistema, garantindo confiabilidade e qualidade do suprimento; elaborar os Procedimentos de Rede (submódulos técnico-operacionais), submetidos à aprovação da ANEEL; realizar o Programa Mensal de Operação (PMO) em conjunto com a CCEE para cálculo de PLD.
- **Marco recente:** reestruturação, junto com a CCEE, do comitê PMO/PLD em jun/2026 para calibrar preços e modelos.

## CCEE

- **Base legal:** Lei nº 10.848, de 15 de março de 2004 (sucede o MAE, criado pela Lei nº 9.648/1998).
- **Natureza:** associação civil de direito privado, sem fins lucrativos, sob fiscalização e regulação da ANEEL.
- **Competência:** viabilizar a comercialização de energia elétrica no ACR e no ACL; contabilizar e liquidar financeiramente as diferenças entre energia contratada e energia gerada/consumida (Mercado de Curto Prazo); calcular o Preço de Liquidação das Diferenças (PLD); gerir cadastro de agentes, garantias financeiras e penalidades; elaborar as Regras e os Procedimentos de Comercialização (submetidos à aprovação da ANEEL — ver skill `seb-arcabouco-legal` para o índice detalhado desses instrumentos).
- **Associados:** geradores, distribuidores, comercializadores e consumidores (livres/especiais) que atuem nos ambientes de contratação — a adesão à CCEE é obrigatória para quem comercializa nesses ambientes.

## SIN

- **Natureza:** não é uma pessoa jurídica — é o sistema elétrico físico interligado (geração + transmissão) que atende a grande maioria do território nacional (mais de 98% da carga). Sistemas isolados (parte da região Norte) não fazem parte do SIN e têm regras específicas.

## Categorias de agentes

| Categoria | Descrição |
|---|---|
| Gerador (concessão/permissão/autorização) | Produz energia para venda no ACR/ACL. |
| Autoprodutor | Produz energia prioritariamente para consumo próprio; pode comercializar excedentes. |
| Transmissor | Concessionário da Rede Básica e demais instalações de transmissão. |
| Distribuidor | Concessionário/permissionário que atende consumidores cativos e dá acesso à rede a consumidores livres na sua área de concessão. |
| Comercializador | Agente CCEE que compra/vende energia por conta própria no ACL/ACR. |
| Varejista | Representa consumidores (especialmente de menor porte) no ACL, inclusive no modelo simplificado (submódulo CCEE 1.8). |
| Consumidor cativo | Só pode comprar energia da distribuidora local, sob tarifa regulada. |
| Consumidor livre | Escolhe livremente seu fornecedor no ACL; requisitos de carga/tensão mínimos em redução acelerada desde a Lei 15.269/2025. |
| Consumidor especial | Variante de consumidor livre com requisitos menores, tipicamente para contratar fontes incentivadas (PCH, eólica, solar, biomassa). |
| MMGD (micro/minigerador distribuído) | Gerador conectado à rede de distribuição sob o SCEE (Lei 14.300/2022), classificado em GD I/II/III. |

## SUI

- **Base legal vigente:** art. 15-C da Lei nº 9.074, de 7 de julho de 1995, incluído pela Lei nº 15.269, de 24 de novembro de 2025.
- **Instituição e desenho de política pública:** cabem ao poder concedente. O § 1º do art. 15-C não designa automaticamente um prestador: permite que, a critério do poder concedente e conforme regulamento, a atividade seja exercida, com ou sem exclusividade, por concessionária, permissionária ou autorizada de distribuição.
- **Regulação econômica e fiscalização:** o serviço deve ser autorizado e fiscalizado pela ANEEL (art. 15-C, I); as tarifas específicas são fixadas pela Agência, sob modicidade tarifária e cobertura dos custos incorridos (art. 15-C, III).
- **Prestação:** será realizada por pessoa jurídica responsável, entre outros, pelo atendimento quando se encerrar a representação por agente varejista, na hipótese do art. 4º-A, § 1º, da Lei nº 10.848/2004 (art. 15-C, II).
- **Custeio de déficit involuntário:** rateio entre todos os consumidores do ACL, por encargo tarifário específico e conforme regulamentação (art. 15-C, § 2º).
- **Limite da conclusão:** a lei não atribui, por si só, à CCEE, ao ONS ou à distribuidora local todo o fluxo operacional. Responsável, elegibilidade, hipóteses obrigatórias, prazo máximo, eventual uso de energia de reserva, dispensa de lastro e forma de cálculo/alocação de custos dependem dos atos regulamentares previstos no art. 15, § 17, III, “c”, da Lei nº 9.074/1995.
- **Consultas públicas:** parâmetros de minutas ou notas técnicas — inclusive percentuais tarifários, duração do atendimento ou escolha transitória do prestador — são propostas até que incorporados a ato vigente. Não os apresentar como obrigação atual.
- **Status verificado em 19/07/2026:** a base local e a pesquisa oficial consultada confirmam o comando legal acima, mas não permitiram localizar ato definitivo que feche todo o arranjo institucional e operacional. Reconfirmar MME, ANEEL, CCEE e DOU antes de parecer conclusivo sobre esses elementos.
