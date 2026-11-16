# TCC2 — E11-M00B — Auditoria da regressão atualizada (48 testes)

**Data do registro:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fonte primária:** transcrição textual de PowerShell fornecida pelo acadêmico nesta conversa (não arquivo de log original assinado ou ZIP). **Classificação:** `STATIC_REGRESSION_PASS` para o SHA testado; `ENVIRONMENT_AND_EXPERIMENT_NOT_VALIDATED`.

## 1. Identidade e resultados observados

- `git pull --ff-only origin tcc2/desenvolvimento`: **fast-forward reportado** de `b20919f` para `2d237ba`; apenas `STATUS_ATUAL_TCC2.md` e `prova-conceito/benchmark/docker_c2.py` alterados nessa atualização.
- `git rev-parse HEAD`: **`2d237ba8f91cd5ba7d7f6c65a451d45bb7c1d21c`**.
- `python -m compileall -q benchmark tests`: saída **`COMPILACAO: PASS`**, emitida pelo script PowerShell somente após verificar `$LASTEXITCODE -eq 0`; nenhum erro de compilação apresentado na transcrição.
- `python -m unittest discover -s tests -p "test_benchmark*.py" -v`: todos os testes listados retornaram `ok`; resultado final **`Ran 48 tests in 0.121s`**, **`OK`**, **`TESTES: PASS`** com `$LASTEXITCODE -eq 0`.
- Dos 48 casos, **cinco** são `MeasurementProfileTests` e **cinco** são `ResourceContractTests`; ambos os arquivos adicionados na fase E11-M00B foram efetivamente descobertos. Os demais 38 testes são a suíte pré-existente.
- A transcrição textual termina após `TESTES: PASS` e não contém a saída final de `git status --porcelain`. Portanto, **não é possível afirmar a partir deste trecho isolado** que o último `git status` foi executado ou estava vazio; o HEAD/branch reportados e o fast-forward foram comprovados.
- `0.121s` é duração da suíte `unittest`, **NÃO** duração da aplicação distribuída, experimento nem benchmark.

## 2. Escopo do PASS e limites da evidência

O erro `IndentationError` relatado anteriormente em `benchmark/docker_c2.py`, linha 21, deixou de ocorrer na nova compilação após correção documentada no commit `b74b66a2204a20e13b806f77ae022024c4d75ebf`.

Os testes sintéticos aprovados verificam, por exemplo, ausência de construção de sampler em `timing_only`, tratamento `NOT_COLLECTED`, IDs `m...`, rejeição de modos inválidos e contrato de requests/limits declarado em dicionários simulados. **Não verificam**: chamada integrada do runner em ambiente real, recursos físicos/cgroups, quota e swap efetivos, condições de rede/WSL2/Docker/kind, proteção de namespaces reais por consulta de existência, equivalência de overhead, calibração do monitor, qualidade de dados de CPU/RAM ou segurança de nova operação mutante.

**Decisão:** `E11-M00B_STATIC_REGRESSION_PASS`; iniciar redação E11-M00C, **não liberar E11-M01** nem alterar a classificação instrumental CPU/RAM (continua `BLOCKED`).

## 3. Gate operacional seguinte — sem POST e sem experimento

Antes de declarar `READY_FOR_M01`, requer-se:
1. Conferência do HEAD/working tree e `PLAN_ONLY` para C2/C3/C4 com a fixture canônica de 1.000 e `--measurement-mode timing_only`, usando labels `m...`, sem `--execute`.
2. Inventário real **somente leitura** de host/WSL2/Docker/kind e verificação dos requests/limits, disponibilidade de recursos, imagem/digest, topologia e identidades/namespaces históricos **sem modificá-los**.
3. Congelamento do protocolo E11-M00-v1 com controles/critério de falha, aquecimento não mutante, teto de reposições, documentação e status explícito. Nunca prometer independência física ou comparação CPU/RAM por causa de testes mock.
4. Sem upload de arquivo de log original, a evidência deste laudo permanece a transcrição textual e deve ser citada na metodologia como inspeção do procedimento, não como experimento.

**Integridade:** laudo documental; nenhuma ação Docker/Kubernetes ou execução Python foi realizada pelo assistente para criar este registro. Todas as bancadas históricas C2/C3/C4 seguem preservadas.
