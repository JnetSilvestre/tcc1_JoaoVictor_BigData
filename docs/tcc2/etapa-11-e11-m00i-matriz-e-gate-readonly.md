# E11-M00I — Preparação de abertura da campanha E11-M01: matriz imutável e gate read-only

**Data:** 18/11/2026, America/Sao_Paulo. **Relação com o planejamento:** transição das qualificações E11-M00E/G/H, finalizadas e retiradas com evidência, para a campanha pré-registrada **E11-M01 (30 lotes)**. Este documento **NÃO** substitui o pré-registro original `docs/tcc2/etapa-11-e11-m00-v1-pre-registro-e-gates-m01.md`.

## 1. Evidência anterior homologada

O acadêmico forneceu saída PowerShell em HEAD `b1735eb11abce6775c1755a3e780b36d60772bb5`:

- `Ran 140 tests in 0.329s`, `OK`, `REGRESSAO: 140/140 PASS`;
- prévia **`C4_S01_RETIREMENT_READONLY_PASS_NOT_AUTHORIZED`**, 4 Pods com UIDs/containerIDs esperados, 16 objetos do namespace, 3 ReplicaSets e nenhum outro recurso M01, ZIP e cópia em volumes distintos, SHA `8e2f5a0918bcfe398e3d76b737973a08f35c59d62bfc9c03eea1939b29883f27`;
- consentimento explícito `AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C4_M01_S01`;
- executor `C4_S01_RETIREMENT_COMPLETE` para **somente** `tcc2-pon-e11-c4-m01-s01`, UID `08c6e166-4fc3-4aaf-b1d4-67ac5f628a30`, `historic_resources_targeted=0` e `original_and_backup_preserved=true`;
- journal de retirada em `D:\TCC2-Backup\E11-M00H\C4-m01-s01-retirement.jsonl`, último registro `COMPLETE/C4_S01_RETIREMENT_COMPLETE`, conferido pelo script do acadêmico; hashes dos ZIPs original e backup revalidados;
- C2-S01 e C3-S01 já tinham qualificações e retiradas protegidas, com seus ZIPs/journals preservados.

**Estado factual:** C2/C3/C4 sacrificiais qualificados e desmobilizados, **nenhuma rodada principal realizada**. Não extrapolar aprovação funcional nem números de testes unitários para uma afirmação de desempenho comparativo.

## 2. Código novo — plano e gate não mutantes

`prova-conceito/benchmark/m01_readiness.py` materializa exatamente a matriz B01–B10 (C2,C3,C4 / C3,C4,C2 / C4,C2,C3 / C4,C3,C2 / C3,C2,C4 / C2,C4,C3 / C2,C3,C4 / C3,C4,C2 / C4,C2,C3 / C4,C3,C2), gerando 30 `run_id` únicos `e11-cX-m01-bNN` com seed 20260502 e modo `timing_only`. Não implementa aleatorização, reordenação adaptativa, rejeição de tempos altos ou reposições automáticas. O primeiro slot continua **B01/C2**.

O gate **somente leitura**:
1. Confere branch `tcc2/desenvolvimento`, working tree limpa e SHA Git.
2. Confere fixture de 1000 requisições, SHA **`26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`**; conserva oráculo SHA **`430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`**.
3. Executa `audit_archive` nos três ZIPs sacrificiais, confirma hash conhecido de cada um e `compare_backup_pair` com as cópias D, CRC e SHA internos, `different_filesystem_volume=true`. Inspeciona **o último evento de cada journal de retirada** `COMPLETE` com status e run_id esperados.
4. Confere que não existem novos contêineres M01 **inclusive parados** via `docker ps -a`, redes Docker M01 nem namespaces M01 C3/C4. Compara a presença de namespaces históricos `default`, `tcc2-pon`, `tcc2-pon-c4`, sem tocá-los.
5. Reusa `capture_environment` para confirmar Docker context, cgroup v2, SHA da imagem aprovada, **apenas dois nós kind Ready** com UIDs e os limiares conservadores via `assess_capacity`: RAM física Windows >=3 GiB e disco do projeto >=15 GiB.
6. Retorna status **`M01_READONLY_BASELINE_PASS_NOT_EXECUTION_AUTHORIZATION`**, `main_b01_started=false`, `generalized_retirement_lifecycle_approved=false`, `start_authorized=false`, `mutation_commands=[]`. O PASS deste gate não cria Pods/contêineres, não faz snapshot/POST e **NÃO autoriza B01**.

**Código e suíte:** `tests/test_benchmark_m01_readiness.py` acrescenta **11 testes sintéticos** para ordem congelada de 30 slots, 10 por cenário, bloqueio de novos recursos M01 ainda presentes, integridade da fixture/journals, Git modificado e ausência de autorização. O último PASS comprovado no Windows permanece **140/140** na versão anterior; a nova revisão **prevê 151 testes, ainda NÃO executados**.

## 3. Execução exclusivamente para verificar o gate

Partindo de `prova-conceito` com Git limpo, após `git pull --ff-only` para o SHA deste registro e `compileall`/regressão esperada:

```powershell
$fixture = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl"
python -m benchmark.m01_readiness --fixture $fixture --backup-root "D:\TCC2-Backup"
```

A saída é um relatório JSON **read-only**, com matriz e entradas do primeiro slot; nenhum comando operacional de criação, POST ou exclusão é emitido.

## 4. Critérios finais de liberação da série definitiva

Mesmo com esse gate PASS, exige-se homologar **o controlador geral do ciclo de vida** para cada rodada `m01-bNN` inédita: (a) checar inventário e capacidade imediatamente antes de criar, (b) criar uma única bancada nova sem reutilizar recursos, (c) estado frio/quotas pré-snapshot, (d) um snapshot e 1000 POSTs `timing_only` sem retry, (e) ZIP completo com integridade, (f) cópia verificada em D, (g) retirada **somente após aceitar IDs/UID da rodada arquivada e consentimento explícito**, com journal e interrupção definitiva diante de falha incerta. Não permitir que um `FAIL` apague bancadas ou seja descartado da contagem documental; substituições B11/B12 exigem aditamento específico conforme pré-registro.

O código deste estágio **não implementa o controlador mutante geral** e nenhum consentimento para iniciar B01 foi solicitado. **`E11_M01_MAIN_SERIES_BLOCKED`** permanece até esse programa estar implementado, testado e aprovado de modo verificável. Nenhum CPU/RAM de lote foi aprovado para comparação; apenas `T_batch`/throughput/RTTs estão previstos.
