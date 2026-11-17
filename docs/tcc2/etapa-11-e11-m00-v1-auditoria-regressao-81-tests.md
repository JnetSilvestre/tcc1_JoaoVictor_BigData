# TCC2 — E11-M00-v1 — Auditoria de regressão do pacote de gates (81 testes)

**Data documental:** 17/11/2026, America/Sao_Paulo. **Branch:** `tcc2/desenvolvimento`.  
**Origem da evidência:** transcrição PowerShell enviada pelo acadêmico como `Texto colado(2).txt`. Não se trata de log assinado nem resultado reproduzido pelo assistente.

## 1. Identidade e resultados observados

- `git pull --ff-only origin tcc2/desenvolvimento`: fast-forward `f8b1260...` -> **`e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`**.
- `git rev-parse HEAD`: **`e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`**.
- `Test-Path .\benchmark\runtime_gate.py` passou, evidência `ARQUIVOS: PASS`.
- `python -m compileall -q benchmark tests` com teste de `$LASTEXITCODE`: **`COMPILACAO: PASS`**.
- `python -m unittest discover -s tests -p "test_benchmark*.py" -v` com teste de `$LASTEXITCODE`: **`Ran 81 tests in 0.314s`**, `OK`, **`TESTES: PASS`**; os 81 casos listados retornaram `ok`.
- Novos controles explicitamente descobertos: cinco casos em `test_benchmark_campaign_exclusivity.py`, dez em `test_benchmark_runtime_gate.py` (incluindo o leitor cgroup embutido e rejeição de swap), e o sexto caso em `test_benchmark_lifecycle_audit.py` de ZIP sem gates. Todos `ok`.
- A duração `0.314s` pertence à **suíte unitária**, NÃO à prova de conceito, a um benchmark nem à campanha de 30 lotes.
- O comando `git status --porcelain` estava no script, mas a transcrição recebida termina em `TESTES: PASS`, sem mostrar eventual saída de status; a condição final da árvore de trabalho **não está documentada explicitamente nesse trecho**. O `git status` inicial passou por um guard sem mudanças relatadas.

**Classificação:** `E11_M00_V1_SYNTHETIC_REGRESSION_PASS` **para o SHA exato acima**. Não atribuir esse PASS a alterações futuras sem nova regressão.

## 2. O que os testes realmente comprovam

- Funções sintéticas de política de capacidade para RAM/disco e interpretação cgroup v2; rejeição de CPU ilimitada, memória divergente, OOM prévio, swap ausente/ilimitado, IDs históricos e ausência de nova bancada exclusiva.
- Verificação do script de leitura de cgroup por compilação em memória, **não execução desse script em cgroup real de um contêiner novo**.
- Validação do ZIP sintético com entradas obrigatórias `capacity-gate.json`, `effective-quotas.json` e `campaign-exclusivity.json`.
- Persistência da suíte anterior que testava fixture canônica, oráculo, coleta instrumental, estado frio C1, IDs e segurança dos pilotos.

**Não demonstra:** existência real de quotas 500m/256Mi/128Mi/swap=0 para C3/C4; disponibilidade de RAM do Windows acima de 3 GiB; isolamento físico entre nós kind; ausência de interferência, CPU/RAM comparativas, efetiva robustez sob carga, criação ou descarte seguro de recursos novos, capacidade de 30 lotes nem autorização do orientador.

## 3. Riscos operacionais ainda abertos

1. Última RAM livre reportada do Windows = **2.159.898.624 bytes (~2,01 GiB)**, **abaixo do piso operacional de 3 GiB**, previamente fixado por precaução. Se repetida imediatamente antes de uma bancada, o gate deve falhar fechado; isso não é erro no teste unitário.
2. Nenhum mecanismo de encerramento/remoção de bancadas novas M01 está aprovado nem implementado. Como há exigência de **uma bancada nova por vez**, iniciar sem o procedimento de identidade, backup e ciclo de vida aprovado criaria um bloqueio após a primeira tentativa. Preservar históricos mesmo que o host fique pressionado.
3. Controles de `cpu.max`, `memory.max`, `memory.swap.max` apenas podem ser provados para quatro contêineres/Pods **novos e autorizados**, depois da criação e **antes de snapshot/POST**. Não consultar/modificar históricos como substituto.
4. Qualquer erro de preflight após criar uma nova bancada deve preservar IDs/artefatos e interromper. Não executar limpeza genérica ou retry de snapshot.
5. `DESIGN_FROZEN` significa desenho pré-registrado; NÃO significa `READY_FOR_M01`, implementação observada real, capacidade validada ou coleta iniciada.

## 4. Decisão e encaminhamento

- **Fechar** pendência de compileall e 81 casos sintéticos para o SHA `e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`.
- **Manter** E11-M01 `BLOCKED` até política segura de ciclo de vida exclusiva de recursos novos, autorização operacional, margem RAM/disco e quotas reais por papel. Não repetir suíte sem alterar código.
- **Próxima entrega documental/operacional:** especificar e verificar o fluxo de inventário com Docker container IDs/network IDs ou Kubernetes namespace UIDs para uma bancada **nova e sacrificial**, backup externo íntegro e allowlist, revisão separada da autorização para eventual desativação da bancada nova. Procedimento não deve alcançar nenhuma bancada histórica.
- **Manter** CPU/RAM como `NOT_COLLECTED/NOT_APPROVED` na série temporal v1.

**Integridade:** o assistente somente analisou a transcrição e registrou o laudo. Nenhum Docker/kubectl mutante, benchmark, snapshot, POST, restart, stop, rm/prune ou delete foi realizado nesta atividade.
