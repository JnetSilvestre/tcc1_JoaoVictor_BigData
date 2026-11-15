# TCC2 — Etapa 10 / C4 — checkpoint de agendamento multinó virtual

**Data:** 15/11/2026. **Branch:** `tcc2/desenvolvimento`. **Estado:** diagnóstico E10-D01 aprovado com saída textual Windows; arquivos C4 preparados no GitHub, ainda **não executados no Windows nem aplicados ao cluster**.

## 1. Diagnóstico E10-D01: evidência real recebida

- Cluster `kind-tcc2-pon` com `tcc2-pon-control-plane` e `tcc2-pon-worker`; ambos `UNSCHEDULABLE: False`.
- `control-plane`: rótulo `kubernetes.io/hostname=tcc2-pon-control-plane`; taint `node-role.kubernetes.io/control-plane:NoSchedule`. Não remover o taint: utilizar toleration específica, apenas em um novo Deployment do C4.
- `worker`: rótulo `kubernetes.io/hostname=tcc2-pon-worker`; nenhum taint efetivo identificado na saída textual (`TAINT:` sem chave/efeito).
- Ambos reportaram `allocatable cpu=8` e `memory=8052380Ki`; são nós **virtuais compartilhando os recursos de um único host físico** e não representam duas máquinas de 8 CPUs cada.
- C3 preservado: três Pods `Running` `1/1`, `RESTARTS=0`, no `tcc2-pon-worker`; namespace `tcc2-pon-c4` ainda ausente.
- Diagnóstico somente leitura; não há implantação C4 demonstrada neste momento.

## 2. Decisão de arquitetura e isolamento

**Cenário C4** usa **novo namespace** `tcc2-pon-c4`, três Deployments/Services ClusterIP e ConfigMap independentes, uma réplica por papel, a **mesma imagem C2 aprovada**, escuta `0.0.0.0:8080`, sem alterações no núcleo `pon/` ou `c1/`. Configuração replicada de C3 em `infraestrutura/kubernetes/c4/manifests.yaml`.

| Papel | Nó pretendido | Justificativa |
|---|---|---|
| attribute-source | `tcc2-pon-worker` | Origem dos eventos no worker |
| logic-engine | `tcc2-pon-control-plane` | Avaliação no outro nó; toleration restrita ao taint NoSchedule |
| rule-executor | `tcc2-pon-worker` | Executor no worker: ambas as interfaces entre serviços cruzam nós virtuais |

`nodeSelector` por `kubernetes.io/hostname` garante a intenção de agendamento, sujeita à capacidade e condições reais. Apenas `logic-engine` recebe a toleration `operator: Exists`, `effect: NoSchedule`, chave `node-role.kubernetes.io/control-plane`; **não remover o taint global** nem desproteger todo o control-plane. Se o posicionamento falhar, interromper a rodada e investigar. Não migrar Pods com estado.

Resources por Pod: requests CPU=100m, memoria=128Mi; limits CPU=500m e memoria=256Mi; valores de configuração, não medidos, e não estabelecidos como parâmetros finais de benchmarking. `imagePullPolicy: Never`: imagem já carregada nos dois nós por E09-I02. Probes Kubernetes /health/live para readiness de rede/liveness; prontidão funcional /health/ready apenas após snapshot.

**Não apagar, reiniciar, escalar, editar nem enviar eventos aos Pods C3** no namespace `tcc2-pon`.

## 3. Procedimento de validação C4 previsto

1. Sincronizar branch limpa `tcc2/desenvolvimento`; validar sintaxe Python sem executar (`ast.parse`) e manifests via `kubectl apply --dry-run=client`. Não repetir a suíte C2 de 93 testes, porque o runtime não foi modificado.
2. Aplicar **somente** o manifesto C4, aguardar rollouts de três Deployments e registrar `kubectl get deploy,pods,svc -n tcc2-pon-c4 -o wide`. Verificar nó real de cada Pod e ausencia de restarts. Não assumir cross-node apenas pelo `nodeSelector`.
3. Executar **uma única vez** `python -m c4.runner --output resultados-locais/c4-e10-i02-v1` a partir de `prova-conceito`. Antes de qualquer POST, o script verifica Git, imagem, Pods/Services, UIDs/containers distintos, dois nós realmente usados, estados frios e ausência de mutações prévias.
4. Se preflight aprovado, enviar **um único snapshot C4 novo** com `run_id=c4-e10-i02-v1` e confirmar estados prontos, sem efeitos.
5. Em seguida reutilizar o **mesmo validador de sete passos** C3 (agora parametrizado com `SCENARIO=C4` e `RUN_ID` C4) sem alterar o código de execução; preservar fixture original, oráculo independente, logs/causalidade, topologia, estados, hashes. Esperados: cinco AttributeChanged, três ConditionChanged e dois efeitos passos 3/7.
6. O pacote C4 `c4-e10-i02-v1.zip` inclui evidências pré-snapshot, logs, resposta do snapshot e **ZIP da fixture** aninhado, além de `validation-c4.json` e `checksums.sha256`. Guardar SHA-256 e original fora do GitHub para auditoria independente.

**Restrições:** qualquer falha no preflight deve impedir POST; qualquer falha após tentativa de POST **não autoriza repetição, reset, novo snapshot ou reexecução**, até auditar logs/estados. C4 precisa de execução isolada em estado frio, pois componentes são stateful sem replay persistente. A possibilidade de disponibilidade/recuperação após restart não é requisito demonstrado.

## 4. Critérios e pendências

**E10-D01:** aprovado somente como diagnóstico de taint e preservação do C3. **C4/V09:** pendente de evidência real de Pods em nós virtuais distintos E **eventos recebidos de ponta a ponta**. A mera criação dos Pods não aprova V09. **C4 funcional:** exige V02 e V08 equivalentes no escopo C4, sem falhas ou perdas. **V10 e V12:** fora do incremento; não gerar benchmark a partir dos logs/timestamps. **V11:** documentação/código fornecidos, mas reprodução por terceiro não realizada.

**Próximo:** executar no Windows um único bloco que faça Git sync, validação read-only, implantação C4, conferência dos nós e disparo de runner único. Enviar a saída textual e ZIP C4 para auditoria; se ocorrer erro, não repetir.


## 5. Encerramento funcional E10-C4 — EXECUÇÃO REAL E AUDITORIA APROVADAS (15/11/2026)

**Esta seção substitui as pendências anteriores sobre execução C4.** O acadêmico sincronizou Git até f84c8384f33168219213757f9b2027216a2511e4, validou AST de c3/runner.py e c4/runner.py, verificou isolamento do namespace, obteve dry-run de 8 recursos e implantou C4 no Kubernetes. Três rollouts concluídos, 3 Pods Running/Ready 1/1, sem reinícios, em dois nós virtuais.

**Distribuição comprovada:** attribute-source (10.244.1.6) e rule-executor (10.244.1.5) no tcc2-pon-worker; logic-engine (10.244.0.5) no tcc2-pon-control-plane. Toleration específica permitiu agendamento sem remover o taint do nó. Dois nós kind são containers virtuais no MESMO host físico.

**Snapshot C4:** cold preflight dos 3 serviços (live=200, ready=503), nenhum estado anterior, envio único de run_id c4-e10-i02-v1, HTTP 200, três estados prontos, nenhum efeito inicial, comprovado pelo ZIP. Fixture com sete POSTs HTTP 200, 14/14 checks true, dois efeitos passos 3 e 7, cinco eventos de atributo e três de condição, correlação integral; E10_C4_EXIT=0. C3 permaneceu com 3 Pods Running/Ready, 0 restarts.

**ZIP ORIGINAL auditado diretamente:** c4-e10-i02-v1.zip, 36.370 bytes, SHA-256 8f77d981abb6977890f948168924b594398828ef3d843d7f38baf66d09acca7c; 16/16 entradas externas, CRC OK, 15/15 hashes externos. ZIP interno fixture.zip com 27.505 bytes, SHA-256 21dcdc0239bb51d41e4148b8834e626c32dd5ac355f7fe4ba78a245dc3dfe2be, 28/28 entradas, CRC OK e 27/27 hashes internos. **48/48 verificações independentes documentais** aprovadas. Não são novas rodadas experimentais. Laudo: docs/tcc2/etapa-10-auditoria-c4-zip.md. Original bruto NÃO versionado no GitHub.

**Critério V09:** APROVADO apenas para comunicação e notificações entre dois nós Kubernetes virtuais em um único host físico (posicionamento dos Pods + identidades e igualdade send/receive). Não é teste de dois hosts físicos e não foi feita captura de pacotes. V02/V04/V08 também aprovados para fixture mínima C4. V07 global parcial; V10/V12 não executados; V11 global parcial. Não se deve inferir performance, escalabilidade ou tolerância a falhas.

**Decisão:** Etapa 10 concluída funcionalmente no escopo C4 mínimo; snapshots e fixture de C3 e C4 já executados e não devem ser repetidos sobre esses Pods. Próximo passo: Etapa 11, desenho/verificação da instrumentação quantitativa e novas rodadas independentes. Preservar todos os ZIPs e metadados SHA-256.
