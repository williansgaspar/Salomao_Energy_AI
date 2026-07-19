# Estratégia de testes do Salomão

## Objetivo

Detectar regressões de fundamentação, vigência, classificação epistemológica e calibração da conclusão. A avaliação mede comportamento; não tenta substituir revisão técnico-regulatória por contagem de palavras.

## Pirâmide

1. **Validação estrutural:** `scripts/validate_project.py` verifica catálogo, skills, casos e higiene do Git.
2. **Casos regulatórios:** `scripts/evaluate_responses.py` registra notas reproduzíveis para os casos de `casos_regulatorios.yaml`.
3. **Revisão especializada:** respostas com impacto externo, conclusão condicionada ou controvérsia passam por revisão humana e conferência das fontes primárias.

## Dimensões

Cada resposta recebe nota de 0 a 2:

- `fundamentacao`: 0 sem fonte; 1 fonte incompleta/secundária; 2 instrumento, dispositivo e fonte primária adequados.
- `vigencia`: 0 presume; 1 ressalva sem fechar cadeia; 2 verifica datas, alterações e transições aplicáveis.
- `classificacao`: 0 mistura categorias; 1 separação parcial; 2 distingue norma, fato, processo, interpretação e inferência.
- `conclusao`: 0 certeza indevida/não responde; 1 resposta condicionada incompleta; 2 responde no grau de certeza suportado.
- `rastreabilidade`: 0 não reproduzível; 1 fontes genéricas; 2 links/caminhos, data e método verificáveis.

Qualquer `critical_failure: true` reprova a rodada independentemente da média.

## Portões de qualidade

- Nenhuma falha crítica.
- Média geral mínima de 1,60/2,00.
- Nenhuma dimensão com média inferior a 1,40.
- Casos `citacao-inexistente` e `parecer-sem-fonte-primaria` devem obter nota 2 em `conclusao`.

## Execução

```powershell
python scripts/evaluate_responses.py init --output evals/resultados/rodada.json
# Preencher as notas após produzir/revisar as respostas
python scripts/evaluate_responses.py report evals/resultados/rodada.json
python scripts/evaluate_responses.py self-test
python scripts/evaluate_responses.py reference-round --output evals/resultados/calibracao-referencias.json
```

Guardar cada rodada com identificação da versão do modelo, data, commit e observações. Não substituir resultados anteriores.

`reference-round` é um controle positivo da suíte: confirma que os nove gabaritos e a
rubrica atravessam o executor, mas não mede desempenho de um modelo. Uma rodada de modelo
deve ser inicializada com `init`, receber respostas produzidas sem acesso aos gabaritos e
ser pontuada com evidências por avaliador.
