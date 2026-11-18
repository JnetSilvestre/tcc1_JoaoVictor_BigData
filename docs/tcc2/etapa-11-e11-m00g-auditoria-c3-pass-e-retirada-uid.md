# E11-M00G — C3-S01 qualificada (PASS) e retirada protegida por UID preparada

**Data:** 18/11/2026 (America/Sao_Paulo). **Cenário:** C3 em Kubernetes kind, Pod cliente e serviços no worker virtual. **Tipo de execução:** qualificação sacrificial **fora da matriz de 30 rodadas**.

## 1. Evidência real fornecida pelo acadêmico

A execução no SHA **`f797ea94673429ead627e939ddfce38ef0191c45`** reportou:
- `python -m compileall` sem erro; **`Ran 118 tests in 0.218s`, `OK`**.
- Capacidade Windows pré-qualificação: **RAM livre 6,08 GiB**, C **64,90 GiB** e D **69,53 GiB**.
- Aceite explícito **`AUTORIZO_EXECUTAR_QUALIFICACAO_C3_S01`**; manifesto gerado e validado em dry-run.
- **`kubectl apply` real somente do namespace novo `tcc2-pon-e11-c3-m01-s01`**: Namespace, ConfigMap, três Deployments, três Services e Pod cliente. Os Deployments terminaram rollout; cliente `Ready`.
- Executor `benchmark.runner`: **`STATUS: PASS`, `ETAPA: complete`**, com `run_id=e11-c3-m01-s01`, `timing_only` e fixture canônica de **1000 requisições** previamente validada.
- `audit_archive`: **`ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION`**, `scenario=C3`, `run_id=e11-c3-m01-s01`, **27 membros**, `functional_pass_verified=true`, `delete_authorized=false`.
- ZIP original **`C:\Users\João Victor\TCC2-Evidencias\E11-M00G\C3-m01-s01\resultado.zip`**; backup verificado em **`D:\TCC2-Backup\E11-M00G\C3-m01-s01.zip`**; ambos reportados com SHA-256 **`463f56042536c95874a4f36dadfd5fd211fec18325132704c9f585d2ec6e80c8`**. A cópia passou em `backup_integrity` (reportado pelo script, não é conferência independente da cópia no volume D pelo assistente).
- Journal de qualificação **`D:\TCC2-Backup\E11-M00G\C3-m01-s01-journal.jsonl`**; Namespace UID **`41fa5e1b-1de5-40da-b72a-e051742788c1`**.
- Identidades de namespaces históricos e contêineres históricos foram comparadas na execução sem diferenças reportadas.

**Veredito:** `E11_M00G_C3_S01_SACRIFICIAL_QUALIFICATION_PASS_BACKED_UP`. O namespace **permanece existente**, e nenhum `kubectl delete` ocorreu na qualificação. **C4 e a série B01–B10 NÃO começaram**. A saída do acadêmico é a fonte documental desta etapa; o ZIP C3 não foi enviado ao ambiente do assistente para conferência binária independente.

## 2. Estratégia de retirada exclusivamente de C3-S01

Kubernetes define `DeleteOptions.preconditions.uid` como condição obrigatória de exclusão; quando o UID do objeto mudou, a API pode responder `409 Conflict`. O módulo `benchmark/retirement_execute_c3_s01.py` usa **`kubectl delete --raw /api/v1/namespaces/tcc2-pon-e11-c3-m01-s01 -f <DeleteOptions JSON>`**, com JSON:
```json
{"apiVersion":"meta.k8s.io/v1","kind":"DeleteOptions","preconditions":{"uid":"41fa5e1b-1de5-40da-b72a-e051742788c1"},"propagationPolicy":"Foreground"}
```

**Antes de permitir o DELETE**, o programa:
1. Audita o ZIP e a cópia em D por CRC/SHA com o SHA original C3-S01 fixado; a cópia deve estar em volume distinto.
2. Confere a identidade do Namespace `m01-s01`, UID fixado, labels `campaign=m01` e `run-id=e11-c3-m01-s01`, e compara UID/nome/containerID dos quatro Pods atuais com `ownership-start.json` armazenado no ZIP.
3. Exige Pods sem restart e `Running` pelo capturador de ownership; uma mudança decorrente de reboot bloqueará a retirada até nova apreciação.
4. Inspeciona objetos comuns do namespace, rejeitando Pods estranhos, Deployments/Services/ConfigMaps fora do esperado, ReplicaSets extras e outros recursos explícitos (Secrets, Jobs, PVC etc.).
5. Rejeita quaisquer outros novos contêineres/redes Docker `m...` ou namespaces Kubernetes `m...` concorrentes, incluindo contêineres parados.
6. Exige branch Git limpa e o SHA de código testado, além do **aceite interativo** `AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C3_M01_S01`, que é diferente do aceite anterior para criar e executar a qualificação.
7. Cria registro JSONL exclusivo e o corpo `DeleteOptions` em D antes do ato mutante. Imediatamente antes de remover, revalida a identidade/inventário. Efetua **um DELETE protegido por UID**, espera a remoção até 180s, verifica IDs de todos os namespaces históricos e SHA das evidências.
8. Falha parcial: registra `INTERRUPTED_DO_NOT_RETRY`, **não faz force, não remove finalizers, não recria nem repete automaticamente**; journal existente impede nova tentativa sem auditoria.

**Nenhum código altera ou remove namespace histórico:** `tcc2-pon`, `tcc2-pon-c4` e os namespaces de piloto `p...` são intocáveis. Nenhum `kubectl delete namespace` genérico, `kubectl delete --all`, `--force`, `docker prune` ou mudança de dados/ZIP está autorizado. Namespace novo C3-S01 será **desmobilizado somente após aprovação operacional específica**.

## 3. Suíte nova e bloqueio

Adicionados **10 testes sintéticos** em `tests/test_benchmark_retirement_execute_c3_s01.py`, incluindo ACEITE/HEAD recusado, objeto estranho, ReplicaSet sem dono, namespace alterado antes do DELETE, journal anterior, simulação de DELETE com UID correto e falha parcial sem retry. A regressão prevista agora contém **128 casos (118 já PASS + 10 novos)**, **ainda não executados no Windows na revisão nova**.

**Próximo procedimento:** `git pull --ff-only`; validar `compileall` + **128 testes**; executar prévia real `python -m benchmark.retirement_execute_c3_s01 --primary ... --backup ...` (somente leitura). Se PASS, solicitar novo aceite de remoção exclusivamente de C3-S01. Após `C3_S01_RETIREMENT_COMPLETE`, verificar journal e inventários e iniciar a qualificação sacrificial C4-S01 em namespace inédito.

**Estado oficial:** `E11_M00G_C3_QUALIFIED / C3_S01_RETIREMENT_NOT_EXECUTED / C4_NOT_EXECUTED / E11_M01_MAIN_SERIES_BLOCKED`.

**Referência normativa externa:** [Kubernetes API, DeleteOptions](https://kubernetes.io/docs/reference/kubernetes-api/definitions/delete-options-v1-meta/); [Namespace endpoint REST](https://kubernetes.io/docs/reference/kubernetes-api/core/namespace-v1/). O código foi preparado, mas ainda não testado no Windows e **nenhuma remoção real é alegada**.
