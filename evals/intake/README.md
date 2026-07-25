# Entrada de casos reais anonimizados

O conjunto dourado somente deve receber casos reais após anonimização concluída e revisão
do responsável técnico. Não inserir dados de cliente, CNPJ, unidade consumidora, preço,
contrato, pessoa ou processo identificável.

Para cada caso, copie `caso_real_anonimizado.template.json`, preencha os campos e mantenha
o arquivo nesta pasta até a aprovação. Após aprovação, crie a resposta de referência,
adicione o item ao manifesto dourado com `provenance: real_anonymized` e
`anonymization: completed`, e registre a decisão de revisão no campo `review_status`.

O caso deve testar um risco efetivo de prática: vigência, citação, transição, cálculo ou
limite de conclusão. Não deve reproduzir texto confidencial desnecessário.
