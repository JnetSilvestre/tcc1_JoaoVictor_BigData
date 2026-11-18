# E11-M00J — Revisão pré-GO B01/C2 do controlador generalizado

**Data:** 18/11/2026 (America/Sao_Paulo). **Escopo:** controlador `benchmark/m01_lifecycle.py`, matriz imutável de 30 slots e futura primeira rodada `e11-c2-m01-b01`. **Sem autorização de executar B01 nesta revisão.**

## 1. Resultado real recebido

A saída PowerShell apresentada pelo acadêmico para o commit **`e2da6a36fde5d7a924e3f730730b5cfd91ca6b38`** informa:
- `Ran 173 tests in 0.379s`, `OK`, `REGRESSAO: 173/173 PASS`, compilação sem erro;
- `python -m benchmark.m01_lifecycle --position 1 --stage plan` retornou **`M01_SLOT_PLAN_ONLY`**;
- `slot.block=B01`, `position=1`, `scenario=C2`, `label=m01-b01`, `run_id=e11-c2-m01-b01`, `resource_base=tcc2-pon-e11-c2-m01-b01`, 1000 requisições, seed 20260502, `measurement_mode=timing_only`;
- `capacity=CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL`, `start_authorized=false`, `commands=[]`.
- Não foi criado recurso, não ocorreu snapshot, POST, benchmark ou retirada de M01.

**Conclusão delimitada:** `E11_M00J_PLAN_B01_C2_READONLY_173_PASS`, **não** `E11_M01_EXECUTION_APPROVED`.

## 2. Revisão de código e endurecimentos posteriores

Foram inspecionadas as rotinas de `benchmark.m01_lifecycle`, `benchmark.docker_c2`, `benchmark.runner`, `benchmark.prepare`, `benchmark.ownership`, `benchmark.lifecycle_audit`, `benchmark.backup_integrity`, `benchmark.environment_snapshot` e `benchmark.runtime_gate` no repositório `JnetSilvestre/tcc1_JoaoVictor_BigData`, branch `tcc2/desenvolvimento`.

**Ajustes preventivos novos (não estavam no commit de 173 PASS):**
1. O journal `COMPLETE/M01_RUN_PASS_BACKED_UP` da rodada atual deve registrar **o mesmo SHA-256** do ZIP auditado e do backup antes de `review` ou qualquer `retire`; não basta que o journal informe apenas PASS.
2. Um arquivo de precondição Kubernetes de uma **rodada futura** (`-delete-options.json`) é tratado como artefato residual e bloqueia iniciar uma rodada anterior — evita mascarar tentativa incerta.
3. Antes de qualquer `run` mutante, o diretório de backup da M01 deve existir e estar em **volume filesystem distinto** do diretório do projeto/evidência original; é necessário ter **pelo menos 15 GiB livres nesse volume D**. Assim, um backup sem espaço ou num mesmo volume provoca STOP **antes** de criação e dos 1.000 POSTs. Volumes lógicos distintos **não comprovam discos físicos independentes**.
4. Foram acrescentados **5 testes sintéticos**: três bloqueios (`same-filesystem`, `SHA journal diverge`, `delete-options` futuro inesperado), mais a simulação do `RUN` C4 com dois comandos `kubectl apply` para namespace **novo** e nenhuma remoção automática, e a simulação de `RETIRE` C2 com 4 `stop`, 4 `rm` e 1 `network rm` **apenas pelos IDs congelados**.

**Regressão esperada agora: 178 testes** (173 observados na revisão anterior + 5 novos). **Não foram executados no Windows nesta nova revisão**. Os testes sintéticos não substituem a comprovação de que um lote real funcionou.

## 3. Regras ainda aplicadas e limites

- `MAIN_CAMPAIGN_ENABLED = False` permanece no código. As fases mutantes `run`/`retire` estão **indisponíveis até aprovação operacional específica**.
- Não iniciar `B01/C2` nem as próximas 29 rodadas sem revisar e aprovar a versão exata testada, procedimento de aceitação e tratamento de falhas.
- As entradas `m01-s01` foram qualificações sacrificiais e **não integram** a matriz de 30 rodadas.
- Cada execução M01 terá um único snapshot/1000 POSTs sequenciais `timing_only`; CPU/memória durante a janela continuam **NOT_COLLECTED**, e nenhum ganho comparativo foi constatado.
- Falha parcial em qualquer fase preserva contêineres/namespace e o journal `INTERRUPTED_DO_NOT_RETRY`, impedindo retry automático. Antes de liberar B01, deve existir um caminho de análise/recuperação manual documentado para journals incertos, sem `docker prune`, `kubectl delete --all`, `--force` ou qualquer histórico.
- As autorizações futuras para `RUN` e `RETIRE` são distintas e próprias de cada `run_id`. Para B01/C2 seriam, respectivamente, `AUTORIZO_RUN_E11_C2_M01_B01` e `AUTORIZO_RETIRE_E11_C2_M01_B01`, mas **não são solicitadas nem permitidas nesta revisão**.

## 4. Procedimento imediato permitido

Atualizar checkout para o SHA completo do código da revisão, verificar Git limpo, rodar `python -m compileall -q benchmark tests`, a suíte `python -m unittest discover -s tests -p "test_benchmark*.py"` esperando **178/178 PASS**, e reexecutar **`--position 1 --stage plan`** verificando `M01_SLOT_PLAN_ONLY`, `start_authorized=false`, `commands=[]`. **Não usar `--stage run`**.

Após resultado PASS, poderá ser preparada uma liberação restrita somente à primeira execução `B01/C2`, com comando explícito e SHA exato do código testado; a permissão de desmobilização continuará independente e somente depois do ZIP+backup PASS. Não extrapolar automaticamente essa aprovação para os 29 slots restantes.

**Decisão:** `E11_M00J_CONTROLADOR_GENERALIZADO_REVISADO_TESTE_WINDOWS_PENDENTE / MAIN_CAMPAIGN_DISABLED / E11_M01_MAIN_SERIES_BLOCKED`.
