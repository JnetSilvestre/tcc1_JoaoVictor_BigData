# TCC2 — E11-M00B — Auditoria da transcrição de regressão executada em HEAD anterior

**Data do registro documental:** 16/11/2026 (America/Sao_Paulo).  
**Fonte primária:** transcrição PowerShell fornecida pelo acadêmico nesta conversa. **Não** é um ZIP/TXT original com SHA recalculado; não há evidência de coleta instrumental, benchmark ou snapshot neste registro.  
**Escopo:** classificar somente o que a transcrição demonstra e comparar o SHA com o GitHub.

## 1. Evidência efetivamente recebida

- Branch reportada: `tcc2/desenvolvimento`.
- HEAD de execução reportado: `5ae84606dde4262a0025ed8f8719a3a8d88b9d2f`.
- Suíte: `Ran 38 tests in 0.096s`, `OK`. Os 38 testes listados referem-se às classes antigas de `test_benchmark.py`, `test_benchmark_docker_c2.py`, `test_benchmark_docker_engine_api.py`, `test_benchmark_docker_engine_window.py`, `test_benchmark_kube_c4_recovery.py` e `test_benchmark_kube_preflight.py`. Trata-se do **tempo da suíte Python**, NÃO duração de lote experimental.
- Nenhuma linha de falha ou erro de compilação foi exibida; entretanto, a transcrição não apresenta marcadores independentes de exit code para `compileall`, nem comprovante auditável de arquivo de log/hash.
- Não constam na lista de 38 casos os novos arquivos `test_benchmark_measurement_profile.py` e `test_benchmark_resource_contract.py`. Sua execução **NÃO está comprovada**.

## 2. Confronto de commits no GitHub

Comparação GitHub `5ae84606dde4262a0025ed8f8719a3a8d88b9d2f...tcc2/desenvolvimento` mostrou `ahead_by=17` (ramo remoto 17 commits à frente do SHA relatado) e incluiu, entre outros, os arquivos de M00A/M00B: `benchmark/measurement_profile.py`, `benchmark/resource_contract.py`, alterações em `benchmark/docker_c2.py`/`benchmark/runner.py` e os dois módulos de testes sintéticos novos.

**Decisão:** `LEGACY_REGRESSION_PASS` para a revisão testada; `M00B_NEW_CODE_NOT_TESTED` para a instrumentação atual. **Não** declarar regressão M00B PASS, nem iniciar E11-M01, nem considerar `timing_only` validado no Windows.

## 3. Próxima verificação segura — nenhum experimento

No clone correto, verificar primeiro branch/working tree. Com tree limpa, `git pull --ff-only origin tcc2/desenvolvimento`; em caso de erro ou mudanças locais, parar e investigar, **sem `git reset --hard`, `git clean` ou exclusões**. Confirmar que o HEAD local coincide com o HEAD remoto. Dentro de `prova-conceito`, executar `python -m compileall -q benchmark tests` e `python -m unittest discover -s tests -p 'test_benchmark*.py' -v`, verificando `$LASTEXITCODE` após ambos.

Os dois novos módulos contêm **5 testes sintéticos cada** no código versionado; espera-se uma contagem de **48** se não houver outras alterações e se a descoberta carregar todos os módulos. Isso é expectativa do código, **não resultado obtido**. Conferir nominalmente os testes `MeasurementProfileTests` e `ResourceContractTests`; a contagem isolada não basta.

Opcionalmente, após regressão comprovada, executar apenas `PLAN_ONLY` do perfil `timing_only` em caminhos de fixture canônica válidos e identificadores inéditos, sempre **sem `--execute`**. O `PLAN_ONLY` não valida quotas reais nem desempenho sob carga.

## 4. Proteção experimental

Este registro apenas lê dados documentais e versiona a classificação. **Nenhum snapshot, POST, benchmark, `kubectl apply`, modificação de Pods/contêineres/redes históricas, reinício, remoção ou teste no Windows foi realizado por esta auditoria.** E11-M00C permanece pendente; E11-M01/A01/V12 não autorizados.
