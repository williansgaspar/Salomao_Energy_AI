# Status operacional — Salomão AI

**Posição de reconciliação:** 21/07/2026  
**Escopo:** repositório local, biblioteca SharePoint SalomaoAI e notebook operacional.

## Estado confirmado

- A biblioteca SharePoint contém as cinco coleções canônicas: Leis Federais, Decretos Federais, Portarias MME, Resoluções ANEEL e Regras/Procedimentos CCEE.
- A Lei nº 15.269/2025 está publicada em texto integral e em recorte canônico do art. 2º e do art. 15, § 17, da Lei nº 9.074/1995.
- A Portaria Normativa MME nº 50/GM/MME, de 27/09/2022, está publicada em texto integral canônico. O teste no notebook identificou corretamente o art. 1º, § 2º.
- A REN ANEEL nº 1.110/2024 possui versão integral canônica. O arquivo-resumo legado deve permanecer fora das referências permanentes do notebook.
- Os 30 submódulos ordinários de Procedimentos de Comercialização estão catalogados como
  `verified`, a partir dos PDFs baixados diretamente da CCEE em 17/07/2026 e da
  conferência da página de vigentes em 21 e 22/07/2026.

## Regra operacional para o notebook

1. Referenciar preferencialmente o TXT integral canônico.
2. Não manter como referência permanente HTML ou resumo quando houver TXT canônico equivalente.
3. Tratar recortes como complemento de recuperação, nunca como substitutos do texto integral.
4. Exigir instrumento, data e dispositivo na resposta técnico-regulatória.

## Pendências controladas

- Auditar e registrar a lista completa de referências permanentes do notebook.
- Monitorar alterações de versão/data dos PdCs e a substituição dos procedimentos provisórios.
- Manter os arquivos HTML legados no SharePoint até auditoria de dependências; não excluí-los automaticamente.

## Atualização operacional — 22/07/2026

- A fila de triagem passou a registrar data de geração, data do conteúdo-fonte e contagem
  de links oficiais pendentes; a rotina `monitor_verification.py` diferencia fila recente
  de boletim-fonte efetivamente atualizado.
- Na primeira execução, o catálogo não apresentou verificações vencidas, mas o boletim
  canônico indicou última modificação em 06/07/2026: estado `source_stale`, com 26 links
  oficiais pendentes de revisão. A atualização diária do boletim deve ser retomada antes
  de qualquer promoção proveniente dessa fila.
- O piloto ACL/armazenamento foi delimitado. A Portaria Normativa MME nº 136/2026 foi
  localizada na fonte oficial, mas permanece fora do núcleo até ingresso controlado com
  arquivo, hash e metadados. A REN ANEEL nº 1.154/2026 permanece pendente de verificação
  oficial; não deve ser citada pelo núcleo.
- Foi criada a entrada controlada para casos reais anonimizados de avaliação. Nenhum caso
  real foi incorporado sem fornecimento e revisão do responsável técnico.

## Atualização operacional — 03/09/2026

- Reconciliação de defasagem: este documento e `ARQUITETURA_E_ROADMAP_SALOMAO.md` estavam
  parados desde 21-22/07/2026 enquanto `tools/consulta_tarifas_aneel/` evoluiu até a
  Revisão 18 (commit de 30/08/2026) — módulos de bandeiras tarifárias, componentes
  homologadas, enquadramento SCEE/MMGD e publicação privada via Microsoft Entra ID
  (Azure Container Apps). `README.md` do app e a estrutura de pastas foram atualizados
  para refletir essa revisão. `python -m pytest -q` (73/73) e
  `python scripts/run_quality_gate.py` seguem OK.
- **Boletim diário parado.** `Atualizacoes_Mercado/Boletim_Atualizacoes_SEB.html` não é
  modificado desde 22/07/2026 (43 dias corridos até 03/09/2026), apesar de `AGENTS.md`
  descrever a tarefa agendada `briefing-seb-diario` (dias úteis, 07h10). `CronList` nesta
  sessão — rodando na máquina `XPS_Willians`, não no mini PC "salomão" que hospeda a
  operação de produção deste projeto (ver nota de infraestrutura) — não retornou nenhuma
  tarefa agendada, o que é compatível tanto com a tarefa ter sido perdida na migração de
  máquina quanto com ela simplesmente não ser visível a partir desta sessão. **Pendência:
  confirmar em sessão aberta no mini PC "salomão" se `briefing-seb-diario` ainda existe
  (`list_scheduled_tasks`) e, se não existir, recriá-la; enquanto isso, o protocolo de
  vigência do `AGENTS.md` não pode se apoiar no boletim como atualizado.**
- A fila de triagem (`knowledge_base/triagem/fila_boletim.json`) não avançou desde 22/07
  pelo mesmo motivo — segue com os 26 links oficiais pendentes já registrados, sem
  contagem nova.
- As RENs ANEEL nº 1.012/2022, nº 1.110/2024, nº 1.154/2026 e nº 1.000/2021 continuam
  como `pending_official_check` em `knowledge_base/catalogo_normativo/inventario_entrada.json`,
  sem promoção ao catálogo canônico.
