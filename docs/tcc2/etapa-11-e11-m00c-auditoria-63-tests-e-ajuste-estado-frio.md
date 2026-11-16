# TCC2 — E11-M00C — Auditoria 63/63 e correção prospectiva do estado frio

**Data:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fontes de evidência:** transcrição PowerShell fornecida pelo acadêmico no chat e arquivos efetivamente examinados `prova-conceito/c1/state.py`, `c1/service.py`, `benchmark/campaign_controls.py`, `benchmark/docker_c2.py`, `benchmark/runner.py` e respectivos testes.  
**Status:** `E11_M00C_STATIC_REGRESSION_PASS_FOR_4ba69a3`; `CORRECTION_UNTESTED_ON_WINDOWS`; `E11_M01_BLOCKED`.

## 1. Resultado comprovado

No commit **`4ba69a3464cb6c2e0d225875ea753a6133da1a18`**, a transcrição mostrou fast-forward, **`COMPILACAO: PASS`**, `Ran 63 tests in 0.284s`, **`OK`** e **`TESTES: PASS`**. Os 15 casos novos dos três módulos `test_benchmark_campaign_controls.py`, `test_benchmark_environment_snapshot.py` e `test_benchmark_lifecycle_audit.py` foram descobertos e listados com `ok`. Trata-se de testes sintéticos e compilação local, NÃO de lotes experimentais; `0.284s` refere-se apenas à suíte. O comando `git status --porcelain` não foi mostrado explicitamente no trecho final recebido.

## 2. Discrepância descoberta na revisão posterior

Os fixtures sintéticos do teste de preflight reproduziam um estado frio INCORRETO para os serviços que ainda não receberam snapshot:

- `c1/state.py: AttributeSource.state()` tem `attributes={atA:0,atB:0}`, `sequences={atA:0,atB:0}`, `pending_request_id=null` e `ready=false`;
- `LogicEngine.state()` **antes de initialize** retorna `attributes=null`, `condition=null`, `sequences={atA:0,atB:0}`, `condition_sequence=0`, `received_ids=[]`, `condition_events=[]`, `faulted=false`;
- `RuleExecutor.state()` **antes de initialize** retorna `approved=null`, `condition_sequence=0`, `received_ids=[]`, `effects=[]`, `faulted=false`.

A implementação original de `benchmark/campaign_controls.py` exigia erroneamente que `logic.attributes` fossem zeros e que `logic.condition` e `executor.approved` fossem `false`. Se uma bancada inédita executasse o novo preflight, essa divergência impediria o snapshot, ainda que o estado real estivesse corretamente frio. **Nenhuma bancada nova foi executada neste diagnóstico.**

A inspeção demonstrou também que a versão inicialmente integrada lia todos os logs antes dos GETs, embora o teste mock verificasse a ordem intercalada (GET live, GET state, logs) por papel. É um descompasso de ordem não mutante; foi corrigido no harness.

## 3. Correção versionada sem alterar o código funcional

- `benchmark/campaign_controls.py` passou a exigir **`logic.attributes=null`, `logic.condition=null`, `executor.approved=null`** antes do snapshot; os atributos da fonte e os contadores fonte/lógica continuam obrigatoriamente zerados; os ledgers continuam vazios.
- `tests/test_benchmark_campaign_controls.py` ajustou os fixtures de estado frio; adicionou caso explícito de nulos e um **teste baseado diretamente em `c1.state.AttributeSource`, `LogicEngine` e `RuleExecutor`**, sem HTTP ou infraestrutura.
- `benchmark/docker_c2.py` e `benchmark/runner.py` passaram a fornecer o leitor de logs à função de preflight em vez de capturar logs de todos os papéis antes, preservando a ordem final idêntica de 3 GET live, 3 GET state e 3 leituras de logs por papel.

As mudanças foram restritas ao harness e aos testes. `c1/state.py` e os serviços HTTP aprovados **NÃO foram modificados**, assim como as imagens, os dados de pilotos e os Pods/contêineres históricos.

## 4. Gate operacional, sem inferências indevidas

- **PASS confirmado:** 63/63 testes no SHA anterior `4ba69a3...`, por transcrição.
- **NÃO confirmado:** sintaxe, 65 casos (previsão: 63+2 testes novos) e execução de `environment_snapshot.py` no Windows da **revisão corrigida**. A nova suíte ainda não foi executada pelo acadêmico.
- **Próximos passos seguros:** atualizar Git após confirmar tree limpa, `python -m compileall -q benchmark tests`; `python -m unittest discover -s tests -p "test_benchmark*.py" -v`; assegurar resultado 65/65 e `git status --porcelain` limpo.
- Após regressão, testar `capture_environment("C2", "e11-c2-m01-b01")` e `capture_environment("C3", "e11-c3-m01-b01")` / C4 exclusivamente read-only, gravando JSON em arquivo temporário **fora do clone**; nunca usar `--execute` neste checkpoint. Isso é teste de inventário, não snapshot de aplicação nem benchmark.
- CPU/RAM de carga continuam `NOT_APPROVED`; política de ciclo de vida `REVIEW_ONLY` permanece sem comandos destrutivos. E11-M00-v1 não congelado, E11-M01 bloqueado até gates finais e deliberação formal.

**Integridade:** nenhum benchmark, POST, snapshot, `kubectl apply`, `docker run`, stop/delete/rm/prune ou mutação de histórico foi realizado nesta atividade.
