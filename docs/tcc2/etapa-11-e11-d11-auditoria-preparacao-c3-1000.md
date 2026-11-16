# TCC2 — Etapa 11 / E11-D11: auditoria do preparo C3/1000

**Data da execução Windows:** 15/11/2026 às 23:57, aproximadamente (America/Sao_Paulo). **Objeto:** preparação isolada do Kubernetes C3; não constitui piloto/benchmark. Fonte primária: ZIP real `e11-d11-20261115-235728.zip` recebido do acadêmico, lido diretamente, mais saída PowerShell. Nenhuma nova consulta a Kubernetes ou mutação ocorreu nesta auditoria.

## 1. Integridade e proveniência

- Arquivo ZIP bruto **31.500 bytes**; SHA-256 independente `651c0c447e8ab5aea16fd2554436d1cf939108f09f52d49c06472673043f44db`, idêntico ao apresentado no PowerShell. **8 entradas distintas e 8/8 CRCs válidos**.
- ZIP interno `preflight.zip`: 15.658 bytes, SHA-256 independente `bfb4551661eb8eb640863d9aecf7453716dafa93139d6ff5d5198501398c20a4`; todas as seis entradas com CRC válido e **5/5 SHA-256 internos** do `checksums.sha256` válidos. Os cinco arquivos repetidos em diretório `preflight\` no ZIP externo são consistentes com o ZIP interno.
- SHA-256 de `preflight\c3-manifest-NOT-APPLIED.yaml`: `c1960450e1a9744dd983471aeee779f19a908b90fa6a10ae8c9ca094701aa09a`, concorda com PowerShell. Fixture canônica 1000: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; oráculo `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`.
- Git local reportado no E11-D11 `2d5b789ead6d73a2545c3453e31e7c654fdee9e9`, 33/33 testes unittest aprovados, contexto `kind-tcc2-pon`. A suíte em 0,116 s NÃO é medição de desempenho.

## 2. Estado C3 na fotografia de Pods

- Namespace recém-criado **`tcc2-pon-e11-c3-p20261115-235728`**, run ID reservado **`e11-c3-p20261115-235728`**, confirmado no PowerShell. O preflight imediatamente anterior confirmou o namespace ausente; a saída do apply informa a criação de namespace/ConfigMap/Deployments/Services/cliente. O ZIP externo contém `pods-c3.json` da bancada preparada.
- `pods-c3.json`: **4/4 Pods** com namespace correto, `status.phase=Running`, `Ready=True`, `ContainersReady=True`, todos no nó virtual `tcc2-pon-worker`; **0 reinícios**, 4 UIDs distintos, mesma imagem tag `tcc2-pon:c2-e08-dbefcd2cf3d2` e runtime imageID igual para os quatro containers. A confirmação de runtime via tag + imageID comum aos Pods não é recálculo independente do SHA-256 das camadas.
- CPU limite de **500m** para cada Pod; memória limite de **256 MiB** para os três serviços e **128 MiB** para cliente. Requests de 100m/128Mi nos serviços e 100m/64Mi no cliente.

| Papel | Pod | UID |
|---|---|---|
| attribute-source | attribute-source-64fb7d77c-wgtsd | `3740a675-1d96-46c0-a4ad-6715b69d6246` |
| logic-engine | logic-engine-684ff7d87b-rjr57 | `0582b752-ad56-41fb-b8ae-a308d25d0a17` |
| rule-executor | rule-executor-d9c67b7bd-zln56 | `87d99d0d-504f-41ce-8f09-631dc2e04b79` |
| e11-benchmark-client | e11-benchmark-client | `a3e0d0a5-b78d-4f5b-bbd1-b077f2fbda5a` |

- O PowerShell reporta que UIDs dos Pods nos namespaces históricos `tcc2-pon` e `tcc2-pon-c4` foram preservados, mas **as listagens históricas antes/depois não estão incluídas no ZIP**. Trata-se de evidência por transcrição, sem revalidação independente no arquivo.

## 3. Ressalvas e bloqueios

- **NÃO há no ZIP uma captura de `states-cold.json`, estados `/state` dos serviços nem logs de aplicação após apply.** Estar Ready equivale a prontidão de transporte, não prova `ready=false`, `run_id=null`, atributos iniciais nem ausência de POST prévio. O controlador `benchmark.runner` possui preflight de estado frio e logs antes de executar snapshot; esse gate deverá ser verificado **na execução real**, e bloquear a carga se não passar.
- Preflight Kubelet de C3/C4 retornou `PASS_READ_ONLY_WITH_TIMESTAMP_WARNING`: no worker, 1/5 timestamps CPU avançaram entre duas leituras ociosas; no control-plane, 0/1. Ele avalia namespaces **históricos**, não os Pods novos C3. `sampling_approved=false`, sem implicar falha de aplicativo e sem aprovar CPU/memória sob carga.
- `RUN_ID` não foi ainda aplicado na aplicação pelo snapshot, conforme transcrição. Contudo, só um GET `/state`/logs real antes do primeiro POST pode comprovar isso.
- **Nenhuma requisição de benchmark foi executada em E11-D11**. C3/1000 pode ser autorizado condicionalmente para uma **ÚNICA** rodada piloto E11-P05 na mesma bancada reservada, com validação de UIDs e estado frio antes de qualquer mutação. Falha/timeout depois do primeiro snapshot pode deixar estado incerto: não repetir.

## 4. Decisão

**E11-D11 APROVADO para criação/isolamento/prontidão de quatro Pods** na fotografia recebida; **preflight frio obrigatório pendente** até execução do E11-P05. Liberar E11-P05 apenas com commit Git esperado, fixture SHA correta, Kubelet e Pod UID conferidos, `PLAN_ONLY`, pré-verificação fria pelo runner e um snapshot/uma carga de 1.000. Preservar namespaces históricos C3/C4 e não criar C4 novo antes da auditoria da rodada.

**Próximo:** piloto C3/1000 único, auditoria de ZIP e correção de 250 efeitos. CPU/memória são exploratórias e serão rejeitadas para comparação se clocks/gaps/duplicações impedirem cobertura. O E11-M01/A01 da Etapa 11 ainda não começou.
