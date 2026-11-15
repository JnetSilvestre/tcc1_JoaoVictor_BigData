# TCC2 — Etapa 09 — Auditoria direta do ZIP C3 E09-I04

**Data:** 15/11/2026. **Cenário:** C3, Kubernetes `kind-tcc2-pon`, namespace `tcc2-pon`.  
**Natureza:** auditoria documental e estrutural dos bytes do ZIP bruto recebido do acadêmico. Não é nova execução no computador acadêmico nem benchmark.  
**ZIP original:** `c3-e09-i04-v1.zip`, anexado à conversa e preservado no Windows do acadêmico; **não versionado no GitHub**.

## 1. Integridade do artefato

- **Tamanho efetivamente inspecionado:** 27.165 bytes.
- **SHA-256 recalculado:** `aad71cea5e90b9c6a334f66180f54dc5609a024b907b7c7f121f6ed4d5855b83`.
- O hash recalculado coincide com `ZIP_SHA256` da execução e com `Get-FileHash` independente mostrado na saída textual do PowerShell.
- **28/28 entradas ZIP** únicas e legíveis; `ZipFile.testzip()` não reportou falhas CRC.
- **27/27 entradas listadas em `checksums.sha256`** foram recalculadas e corresponderam aos hashes declarados; a lista cobre integralmente as 27 entradas restantes do ZIP, sem entradas duplicadas ou ausentes.
- `manifest.json` confirma correspondência entre os SHA-256 dos arquivos originais `fixture-original.jsonl` e `expected-original.jsonl` e os valores registrados.
- `manifest.json`: `git_sha=8669e8364118e30333c90fd798763c18a23fb1ea`, host `Windows-10-10.0.19045-SP0`, Python host `3.13.9`, `seed=20260501`, `run_id=c3-e09-i03-v1`. São metadados documentados pela execução, não rechecados remotamente após o ZIP.
- A imagem registrada é a tag `tcc2-pon:c2-e08-dbefcd2cf3d2`, Docker image ID aprovado `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a` e revisão OCI `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`. O `imageID` do runtime kind usa representação `import-2026-11-15@sha256:c05bd0d...` (registro diferente da identidade local); **não equiparar esses hashes nem afirmar digest de registro remoto**.

## 2. Estado inicial, execução e resultado

- `states-initial.json`: três serviços com `ready=true`, `run_id=c3-e09-i03-v1`, `snapshot_version=c3-e09-i03-v1:snapshot:0`; produtor e avaliador com `atA=0`, `atB=0`, sequências zero; avaliador com `condition=false`, executor `approved=false`, efeitos e ledgers vazios, sem `pending_request_id`.
- `fixture-c3.jsonl`: sete entradas em ordem, seed 20260501, valores iguais aos da fixture C0 aprovada; foi trocado somente o `run_id` para o identificador do snapshot C3.
- `attempts.jsonl`: sete intenções de envio `BEFORE_POST`. `http.jsonl`: sete respostas HTTP 200, `duplicate_request=false`, e campos `changed` / `sequence` / `event_id` coerentes com cada entrada.
- Mudanças reais nos passos **2, 3, 5, 6 e 7**; valores repetidos nos passos **1 e 4** sem `AttributeChanged`.
- Logs estruturados de `attribute-source`, `logic-engine`, `rule-executor` confirmam, na ordem e com payload idêntico de ponta a ponta:
  - cinco eventos de atributo enviados e cinco recebidos pelo avaliador;
  - três eventos de condição enviados e três recebidos pelo executor;
  - dois registros `effect`, idênticos aos eventos em `effects.jsonl`.
- Todos os registros `mutation` nos logs finais analisados tiveram HTTP 200; não se observaram IDs duplicados entre notificações ou efeitos na rodada.
- `effects.jsonl` contém exatamente dois objetos, nos passos **3 e 7**, com preservação da ordem, multiplicidade e IDs de correlação:
  - passo 3: causa `c3-e09-i03-v1:cn1:1` originada em `c3-e09-i03-v1:atB:1`;
  - passo 7: causa `c3-e09-i03-v1:cn1:3` originada em `c3-e09-i03-v1:atB:3`.
- **Equivalência exata:** `effects.jsonl == expected-c3.jsonl == oracle-independente.jsonl == c0-effects.jsonl` em objetos JSON ordenados (ignorando apenas formatação de arquivo). Uma checagem independente adicional por máquina de estados reproduziu os dois efeitos a partir das sete entradas, sem reutilizar a saída C3 como oráculo.
- `states-final.json`: atributos `atA=6`, `atB=1`; sequências `atA=2`, `atB=3`; `condition=true`, `approved=true`; sequência de condição 3, 5 `received_ids` no avaliador, 3 no executor, 2 efeitos; três `ready=true`, nenhum `faulted`, sem requisição pendente.
- `validation.json`: `status=PASS`, `started_changes=true`, **14/14** verificações internas verdadeiras.
- **Auditoria adicional independente do ZIP:** **25/25** checagens de conteúdo, identificadores, logs, snapshots, respostas, oráculo, estabilidade e causalidade passaram. Estas são checagens documentais sobre o material recebido, não 25 novos ensaios Kubernetes.

## 3. Topologia auditada

`topology-initial.json` e `topology-final.json` possuem os mesmos dados de identidade essenciais dos três Pods. A captura do Kubernetes registra:

| Papel | Pod | Pod IP | Nó Kubernetes virtual | Restarts |
|---|---|---|---|---:|
| attribute-source | `attribute-source-84ff976f49-z6v7b` | `10.244.1.2` | `tcc2-pon-worker` | 0 |
| logic-engine | `logic-engine-fcc5cc476-hr2ww` | `10.244.1.4` | `tcc2-pon-worker` | 0 |
| rule-executor | `rule-executor-fdd69799c-kz2k2` | `10.244.1.3` | `tcc2-pon-worker` | 0 |

- Três **Pod UIDs distintos** e três **container IDs distintos**; estabilidade das identidades e das contagens de reinício durante a rodada.
- `tcc2-pon-control-plane` e `tcc2-pon-worker` informados `Ready`. Apesar disso, todos os Pods da aplicação foram alocados ao **mesmo worker virtual**, sobre **um único host físico**.
- Serviços `ClusterIP` por papel, comunicação HTTP/JSON demonstrada pelos logs e pela execução. O êxito não prova comunicação **entre nós**, escalabilidade horizontal, tolerância a falhas ou persistência de estado.

## 4. Classificação científica e limites

| Critério | Estado após E09-I04 | Fundamentação |
|---|---|---|
| V01 | Aprovado para fixture C3 mínima | Valores repetidos não geram notificações, efeitos apenas nas transições falso→verdadeiro |
| V02 | Aprovado para fixture C3 mínima | Equivalência exata C0/manual/oráculo/C3, com ordem e multiplicidade |
| V04 | Aprovado no escopo C3 ensaiado | Eventos e causas correlacionados em logs de Pods/contêineres distintos |
| V07 | Parcial globalmente | Snapshot único e watermarks coerentes; não foi feita corrida de alteração durante inicialização C3 |
| V08 | **Aprovado para C3 funcional mínimo** | Deployments/Services/probes operacionais, DNS HTTP, fixture e oráculo corretos |
| V09 | **Não demonstrado** | Todos os Pods da aplicação no mesmo nó virtual; C4 ainda pendente |
| V10 | Não executado em C3 | Não houve restart controlado nem replay |
| V11 | Parcial globalmente | Artefatos reproduzíveis e íntegros para esta rodada; validação por terceiros em ambiente novo não realizada |
| V12 | Não executado | Não há medições de desempenho, CPU, RAM, vazão ou latência de carga |

V03, V05, V06 e outras verificações de erro/idempotência prévias não devem ser promovidas para o escopo C3 por mera analogia ao C2. A duração entre timestamps de mensagens/logs não constitui benchmark. Um host com dois nós `kind` não equivale a duas máquinas físicas.

## 5. Decisão, entregáveis, pendências

**Decisão:** considerar **Etapa 09 concluída funcionalmente no escopo C3 mínimo**, apoiada em saídas Windows e auditoria direta do ZIP, sem declarar C4, V09 ou métricas aprovados. Preservar C2 e C3, especialmente snapshot já processado e sete POSTs enviados; **não repetir a fixture sobre os mesmos Pods**.

**Entregáveis:** manifestos versionados `infraestrutura/kubernetes/c3/manifests.yaml`; `prova-conceito/c3/runner.py`; checkpoint `docs/tcc2/etapa-09-checkpoint.md`; este relatório; ZIP original externo com SHA-256 verificável.

**Próximo passo sugerido:** Etapa 10/C4 — diagnosticar taints/tolerations e agendamento no cluster; preparar namespace/bancada isolada para colocar ao menos dois papéis em **nós virtuais diferentes**, sem reiniciar ou migrar estados dos Pods C3. Para validação C4 será necessária nova rodada identificada, com snapshot e fixture próprios. Registrar que tudo continua no mesmo host físico. Sem avançar a estimativas de desempenho sem um protocolo de métricas adequado.
