# Piloto normativo: ACL e armazenamento

**Data-base da verificação externa:** 22/07/2026  
**Objetivo:** fechar uma cadeia de evidências mínima para respostas de alta recorrência,
sem converter notícia, consulta ou documento de entrada em regra vigente.

## Escopo e decisão de uso

| Bloco | Situação no núcleo | Decisão operacional |
|---|---|---|
| Lei nº 15.269/2025 | Texto local e registro `verified` (21/07) | Usar com conferência do dispositivo no Planalto antes de parecer. |
| Portaria Normativa MME nº 50/2022 | Texto local e registro `verified` (19/07) | Base do fluxo de opção do Grupo A e da representação varejista. |
| REN ANEEL nº 1.000/2021 | Texto local e registro `verified` (19/07) | Base transversal de fornecimento/MMGD; conferir versão consolidada no caso concreto. |
| Portaria Normativa MME nº 136/2026 | Texto oficial localizado, ainda sem texto canônico catalogado | Ingerir PDF oficial, registrar hash e dispositivos antes de citá-la a partir do núcleo. |
| REN ANEEL nº 1.154/2026 | PDF na área de entrada, `pending_official_check` | Não citar como fundamento até conferir publicação, texto e vigência em fonte ANEEL. |
| Nota Técnica ONS/EPE do LRCAP | Fonte técnica de apoio, não ato normativo | Usar somente para requisitos técnicos do certame, jamais para afirmar regra geral de operação/remuneração de BESS. |

## Evidências externas conferidas

- A [Lei nº 15.269/2025 no Planalto](https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2025/lei/l15269.htm)
  confirma a data de 24/11/2025 e o escopo legal de modernização do marco e de
  armazenamento.
- A [Portaria Normativa MME nº 136/2026](https://www.gov.br/mme/pt-br/acesso-a-informacao/legislacao/portarias/2026/portaria-normativa-mme-n-136-2026.pdf)
  é o texto oficial das diretrizes e sistemática dos LRCAPs de armazenamento; o art. 1º
  delimita os dois leilões. A localização externa, por si, não substitui o ingresso
  controlado no núcleo local.
- A [publicação EPE/ONS sobre requisitos mínimos](https://www.epe.gov.br/pt/imprensa/noticias/epe-e-ons-publicam-nota-tecnica-com-os-requisitos-minimos-para-o-leilao-de-reserva-de-capacidade-lrcap-de-armazenamento-de-2026)
  situa a Nota Técnica NT-ONS DPL 0111/2025 / EPE-DEE-NT-095/2025 como requisito do
  LRCAP, não como regulamentação geral de serviços ancilares.

## Sequência de execução

1. Ingerir e catalogar a Portaria nº 136/2026 com sua origem oficial e hash.
2. Verificar oficialmente a REN nº 1.154/2026; se confirmada, extrair o texto e registrar
   vigência, alterações e dispositivos pertinentes. Se não confirmada, retirar o PDF da
   fila de promoção e manter a origem como pendência documentada.
3. Criar respostas de referência para: elegibilidade/cronograma do LRCAP, distinção entre
   contratação de potência e serviços ancilares, e requisito de conexão.
4. Rodar a suíte de avaliações antes/depois de qualquer promoção e registrar a rodada.

**Critério de aceite:** nenhuma resposta do piloto afirma habilitação ou remuneração geral
de BESS apenas porque existe LRCAP, nota técnica ou notícia sobre armazenamento.
