---
name: mmgd-novas-tecnologias
description: Analisa o enquadramento técnico-regulatório de MMGD, SCEE, armazenamento de energia, BESS/SAE, usinas reversíveis, microrredes, VPP, Recursos Energéticos Distribuídos e volantes de inércia. Use para verificar limites, conexão, compensação, outorga, uso da rede, leilões, serviços ancilares, sandboxes e lacunas regulatórias, distinguindo norma vigente, decisão ainda não publicada, piloto, estudo e inferência tecnológica.
---

# MMGD e novas tecnologias

## Princípio

Classificar o estágio regulatório antes de analisar a tecnologia. Não transformar viabilidade técnica, anúncio, roadmap, consulta pública, decisão colegiada ou sandbox em direito ou obrigação geral.

## Fluxo obrigatório

1. Definir tecnologia, configuração, potência, ponto de conexão, função pretendida, agente responsável e data de referência.
2. Identificar o regime jurídico relevante: MMGD/SCEE, geração, transmissão, distribuição, comercialização, consumidor, reserva de capacidade ou serviço ancilar.
3. Consultar `references/status-regulatorio-tecnologias.md` apenas como mapa datado.
4. Aplicar `seb-arcabouco-legal`: catálogo → base local → boletim → fonte oficial.
5. Classificar cada afirmação como:
   - **norma vigente:** ato publicado e dispositivo aplicável;
   - **transição:** regra vigente condicionada por data, protocolo ou direito adquirido;
   - **decisão sem ato identificado:** deliberação confirmada, mas publicação normativa ainda não localizada;
   - **sandbox/piloto:** autorização específica, temporária e não generalizável;
   - **estudo/planejamento:** roadmap, inventário, PDE/PNE ou pesquisa;
   - **lacuna:** ausência de disciplina específica confirmada;
   - **inferência técnica:** conclusão de engenharia, não regra jurídica.
6. Responder separando enquadramento, obrigações, oportunidades, limitações e pontos pendentes.
7. Informar fonte oficial, dispositivo, data da verificação e confiança.

## Roteamento por tema

### MMGD e SCEE

Conferir Lei nº 14.300/2022, texto compilado da REN ANEEL nº 1.000/2021 e atos que a alteram. Para limites de potência, despachabilidade e transição, citar o dispositivo legal exato e verificar a data do pedido de conexão. Não decidir enquadramento apenas pela potência nominal.

### BESS e SAE

Separar ao menos: SAE colocalizado, autônomo, componente de MMGD, ativo associado a outorga, participante de leilão e prestador de serviço ancilar. Cada configuração pode envolver competência, contratação e cobrança de rede distintas.

Uma decisão da ANEEL ou notícia institucional não substitui o ato publicado. Não citar os números 1.161/2026 ou 1.162/2026 como REN de armazenamento sem localizar os atos oficiais correspondentes.

### UHR e armazenamento hidráulico

Separar diretriz de política energética, estudo/inventário, contratação competitiva, outorga, acesso à rede e operação. Diretriz do CNPE não equivale a regulamentação operacional completa.

### Microrredes, VPP e RED

Identificar se o caso é isolado, conectado, sandbox, projeto de PDI ou operação comercial. Não generalizar autorização concedida a distribuidora ou projeto específico.

### Volantes e serviços ancilares

Analisar o serviço prestado — frequência, inércia, reativos, reserva ou qualidade — antes da tecnologia. Confirmar se há produto, procedimento, remuneração e agente habilitado; analogia técnica não cria enquadramento regulatório.

## Condições de parada

Não emitir conclusão definitiva quando faltar configuração técnica essencial, ato publicado, regra de transição aplicável ou versão vigente do procedimento operacional. Declarar exatamente o documento ou dado necessário.

## Atualização da referência

Ao confirmar mudança:

1. registrar o ato no catálogo;
2. atualizar a linha correspondente em `references/status-regulatorio-tecnologias.md` com fonte e data;
3. manter o corpo desta skill livre de cronogramas e números voláteis;
4. executar `scripts/validate_project.py`.
