# TCC2 — E11-D12: falha de quoting PowerShell e recuperação E11-R01

## Evidência recebida

- Transcrição local 16/11/2026 ~00:13:28 BRT, Git `dd47bb62e6ff1d4d61667e260d4f015be374f998`, 33/33 testes PASS.
- `kubectl apply` de `tcc2-pon-e11-c4-p20261116-001328` executado uma vez, criação de Namespace/ConfigMap/3 Deployments/3 Services/Pod cliente. Todos os rollouts concluídos, quatro Pods Ready, node C4 conforme planejamento, quatro UIDs reportados no terminal. **Não há evidência de snapshot ou requisições de carga.**
- `NameError: name 'status' is not defined` quando o PowerShell passou via `python -c $checkCold` um bloco multiline que continha strings com aspas. A interpretação do código foi danificada antes da execução da checagem Python; o erro não demonstra falha do estado interno nem prova que ele está frio.
- ZIP real `/mnt/data/preflight.zip` auditado diretamente: 15.635 bytes SHA-256 `a48ef81ad9cd11db456387990b01e53579f2a5076e785b29f49315854568d02d`, **6/6 CRCs e 5/5 hashes internos** OK. Status `PASS_READ_ONLY`, HEAD/fixture corretos, dois nós Ready, imagem aprovada, namespaces candidatos ausentes ANTES do apply. Contém apenas preflight de leitura, **não contém** snapshot de Pods da bancada pós-apply nem `/state`. O ZIP final do E11-D12 **não foi criado** após a falha.

## Decisão segura

Não repetir `kubectl apply`, não excluir ou reiniciar Pods, não emitir `/init/snapshot`, não executar carga. Usar a bancada **já criada** e a evidência local da execução interrompida: `resultados-locais/e11-d12-20261116-001328/pods-c4.json`, `historical-before.json`, `preflight/e11-d09-report.json`.

## Recuperação E11-R01

`python -m benchmark.kube_c4_recovery --namespace tcc2-pon-e11-c4-p20261116-001328 --run-id e11-c4-p20261116-001328 --evidence <pasta-e11-d12> --output <nova-pasta>`.

O novo módulo faz APENAS `kubectl get`, `kubectl logs` e `kubectl exec` para GET `/state` na aplicação (sem POST), mais verificações locais Git/imagem. Impede erro de quoting `python -c`; exige mesmo namespace/run e mesma configuração de 4 Pods (UID, imagem, containerID, no, Ready, restartCount=0), comparando `pods-c4.json` original com snapshot atual, UIDs históricos antes/depois, e todos os estados frios: `ready=false`, `run_id=null`, `snapshot_version=null`, atributos/sequências zero, condição false, sem ledger/effects/fault. `benchmark.runner.preflight` também lê logs e bloqueia qualquer evento `mutation` anterior. Salva ZIP SHA-256 e relatório.

**O código E11-R01 foi preparado no GitHub; ainda não foi executado no Windows.** PASS_COLD_READ_ONLY confirma apenas pré-voo e não é autorização automática para executar E11-P06. Verificar real estado da bancada, auditar o ZIP, então decidir piloto C4/1000. Preservar C2/P04 e C3/P05, não repetir experimentos históricos.
