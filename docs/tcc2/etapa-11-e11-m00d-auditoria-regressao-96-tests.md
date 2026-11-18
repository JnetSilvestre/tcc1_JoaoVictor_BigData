# TCC2 — E11-M00D — Auditoria da regressão de 96 testes (ownership e backup)

**Data:** 17/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fonte primária:** saída textual PowerShell enviada pelo acadêmico na conversa, como `Texto colado(3).txt` (anexo do diálogo). Esta auditoria não representa execução independente pelo assistente.

## 1. Evidências efetivamente observadas

- `git pull --ff-only origin tcc2/desenvolvimento`: atualização fast-forward reportada de `e6e83ff` para `e86d2e8`.
- `git rev-parse HEAD`: **`e86d2e884f0bb70a22de4ba6409e8fe98713b40c`**.
- Compilação de `benchmark` e `tests`: **`COMPILACAO: PASS`** com guarda do exit code.
- `python -m unittest discover -s tests -p "test_benchmark*.py" -v`: todos os testes apresentados retornaram `ok`; resumo final: **`Ran 96 tests in 0.352s`**, `OK`, **`TESTES: PASS`**.
- Verificação final do working tree: **`GIT: LIMPO`**. O script tinha condição de interrupção se `git status --porcelain` retornasse modificações, portanto a evidência relatada confirma ausência de alterações locais observadas no final.
- A duração **0,352 s** refere-se à suíte `unittest`, **não** à duração de lote HTTP, custo de contêineres, Kubernetes nem benchmark.
- Foram efetivamente encontrados e aprovados os oito casos `OwnershipTests`, cinco `BackupIntegrityTests` e dois casos novos de `LifecycleAuditTests`, além da suíte antiga (81). Os testes novos simulam os recursos e arquivos, **não verificam recursos reais de uma bancada M01**.

**Decisão:** `E11_M00D_SYNTHETIC_REGRESSION_PASS` para o SHA preciso indicado.

## 2. O que essa evidência comprova

O código testado exige labels positivas da rodada `m01`, `run_id` correspondente, quatro IDs/UIDs para papéis de cenário, comparação de ZIP primário/cópia por checksum e CRC, exclusão de nomes históricos, e mantém a política `commands=[]` e `delete_authorized=false` no retorno documental. Os testes sintéticos validaram também que o manifesto C3/C4 gerado recebe o label somente no namespace novo M01, sem aplicar manifestos.

**Limites:** mocks não comprovam que os objetos reais carregarão labels/UIDs exatamente como o código espera, que os contêineres possam ser criados sob a RAM atual, que o arquivo ZIP de uma rodada real tenha backup em volume distinto, ou que seja seguro desativar/remover recursos. **Não foi desenvolvida nem executada rotina de limpeza**.

## 3. Bloqueios operacionais preservados

1. Margem de segurança pré-registrada: **RAM física Windows livre >= 3 GiB** e **disco no local do projeto >= 15 GiB**. Última evidência de RAM livre foi ~**2,01 GiB**, inferior ao piso, e permanece **não reavaliada nesta transcrição**. Não extrapolar situação do host atual a partir de leitura anterior sem nova medição.
2. Quotas cgroup V2 reais `cpu.max`, `memory.max` e `memory.swap.max` ainda exigem auditoria em uma bancada **nova e autorizada**, sem POST nem snapshot antes do resultado do gate.
3. Fluxo completo de backup externo e decisão de retirada de recursos apenas NOVOS `m...` não foi observado em ambiente real/sacrificial; esse passo exige pré-registro, teste e aprovação separada.
4. Continua proibida qualquer operação em históricos, `docker prune`, `docker rm`/stop genérico, `kubectl delete`, restart, aplicação de manifesto histórico ou reuso de IDs.
5. CPU/RAM comparativas permanecem `NOT_APPROVED`, e os 30 lotes principais **não começaram**.

**Próxima atividade recomendada:** fase E11-M00E apenas de **planejamento de validação operacional sacrificial**, com checklist fechado de inexistência de recursos, propriedade/UID, memória, armazenamento, cgroups, controle de falha e backup, a ser aprovada **antes** de qualquer criação de recurso. Não repetir os 96 testes se código permanecer idêntico.

**Status:** `DESIGN_FROZEN / M00D_SYNTHETIC_REGRESSION_PASS / E11_M01_BLOCKED`. Nenhuma execução Docker/Kubernetes, POST, snapshot, benchmark, stop, delete, limpeza ou mutação de históricos é alegada neste documento.
