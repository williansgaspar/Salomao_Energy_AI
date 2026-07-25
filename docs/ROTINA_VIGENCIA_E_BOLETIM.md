# Rotina de vigência e boletim

**Status:** operacional a partir de 22/07/2026  
**Princípio:** o boletim é descoberta; a promoção ao catálogo exige fonte primária,
conferência de vigência e decisão humana registrada.

## Fluxo diário (dias úteis)

1. A rotina de monitoramento atualiza o boletim em `Atualizacoes_Mercado/`.
2. Executar `python scripts/triage_bulletin.py` para preservar os julgamentos já feitos
   e atualizar a fila com data, origem e contagem de links oficiais pendentes.
3. Executar `python scripts/monitor_verification.py --strict`. Um resultado não nulo
   bloqueia a promoção automática; não bloqueia a leitura do acervo, desde que a resposta
   declare a limitação de atualização.
4. Revisar primeiro os links oficiais pendentes que afetem ACL, armazenamento, MMGD,
   tarifas/REH, PLD ou regras e procedimentos CCEE.
5. Para um ato a promover: baixar/preservar a origem, comparar texto e versão, registrar
   URI oficial, hash, dispositivo relevante, `checked_at`, método e relações no catálogo.
   Só então atualizar skill, referência ou resposta-padrão afetada.

## Prazos e responsabilidades

| Controle | Limite | Responsável pela decisão |
|---|---:|---|
| Fila e conteúdo-fonte do boletim | 1 dia útil | curadoria regulatória |
| ACL, armazenamento, MMGD, tarifas, PLD e CCEE | 30 dias desde a verificação | curadoria regulatória |
| Demais instrumentos verificados | 90 dias desde a verificação | curadoria regulatória |
| Ato usado em parecer concreto | conferência na abertura do trabalho | responsável técnico do parecer |

O limite do catálogo é uma regra de manutenção, não uma presunção de vigência. Para
parecer, precificação ou orientação comercial concreta, continua obrigatória a conferência
do ato e do dispositivo aplicável na data da análise.

## Estados de triagem

- `pending`: link ainda não analisado; não pode sustentar resposta normativa.
- `reviewed_no_promotion`: analisado, mas sem ato primário ou sem pertinência ao catálogo.
- `promoted`: documento conferido e registrado no catálogo; incluir o `id` do instrumento
  e a justificativa nas notas.
- `superseded`: descoberta superada; conservar histórico e apontar o instrumento sucessor.

## Comandos de controle

```powershell
python scripts/triage_bulletin.py
python scripts/monitor_verification.py
python scripts/monitor_verification.py --strict
python scripts/run_quality_gate.py
```

O relatório de monitoramento é deliberadamente somente leitura: ele identifica atraso e
expiração, mas não altera fontes, status de vigência nem o catálogo.
