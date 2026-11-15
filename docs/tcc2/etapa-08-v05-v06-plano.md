# TCC2 — Etapa 08: planejamento de V05/V06 em Docker (E08-D17)

**Data:** 15/11/2026. **Estado:** especificação e preparação; testes adversariais V05/V06 **ainda não executados no Windows**.  
**Branch:** `tcc2/desenvolvimento` (referência antes do planejamento: `36b51625655304e3cf3f0bd58f03f4d817826aeb`).  
**Referência:** `docs/tcc2/etapa-05-protocolo-experimental.md`, critérios V05/V06; contratos `prova-conceito/c1/protocol.py`; estado `prova-conceito/c1/state.py`; HTTP `prova-conceito/c1/service.py`.

## 1. Evidências já preservadas

- E08-D11/D12: C2 demonstrou equivalência funcional C2 ↔ C0/oráculo para a fixture de 7 passos, dois efeitos nos passos 3 e 7; ZIP já auditado.
- E08-D14–D16: V03 em estado frio, 10/10 HTTP 4xx, invariância dos estados, ZIP auditado.
- A imagem de runtime `tcc2-pon:c2-e08-dbefcd2cf3d2` (revisão `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`) não deverá ser modificada; tampouco o código `JnetSilvestre/codigoPon`, a `master` ou o cluster kind.

## 2. Decisão de isolamento

Criar bancada própria **V05**:

- Rede `tcc2-pon-c2-v05`: driver `bridge`, `internal=true`, nenhuma porta publicada.
- Três contêineres independentes, todos da mesma imagem aprovada, com rótulo `tcc2.test=V05`: `tcc2-v05-attribute-source`, `tcc2-v05-logic-engine`, `tcc2-v05-rule-executor`.
- Usar aliases DNS privados `attribute-source`, `logic-engine`, `rule-executor`, escuta `0.0.0.0:8080` e downstream HTTP entre serviços.
- **Não reutilizar V03 ou C2** para este ensaio; não remover nem reiniciar contêineres de rodadas auditadas.
- A bancada V06 será criada **depois**, em rede e contêineres separados (`tcc2-pon-c2-v06`, `tcc2-v06-*`). Isso previne contaminação do ledger entre cenários.

## 3. Etapas planejadas e critérios

### E08-D17A — preparar bancada V05 (próximo comando)

Preflight Git/branch limpa, imagem OCI Linux/amd64 com SHA de revisão fixado, inexistência dos nomes e da rede V05; só então criar rede e três contêineres. Validar Running, IDs distintos, associação à mesma rede, absence de ports host, logs iniciais `listening`. **Aceite de D17A é apenas infraestrutura**, sem status funcional V05.

### E08-D17B — preparar executor de ensaios adversariais (após aceite de D17A)

Script Python no host Windows, invocando `docker exec` por lista de argumentos, e não `python -c` longo no PowerShell; guardar transcrições, três estados antes/depois de cada caso, logs, identificadores Docker, imagem, revisão OCI e SHA-256. Repetir preflight antes de qualquer POST. Não enviar mensagens se o estado já foi consumido.

### V05 — deduplicação em Docker

1. Inicialização do snapshot com `run_id` distinto da fixture principal; verificar `ready=true` nos três.
2. Requisição válida `/attributes/change` para `atA=5` (evento de atributo sequência 1, nenhuma ativação de condição). Capturar o **payload real do evento** nos logs `send` do produtor (incluindo `emitted_at`).
3. Reenviar `POST /notifications/attribute` ao avaliador com exatamente o mesmo payload: esperar HTTP 200 com `duplicate=true`, sem nova mudança/condição.
4. Requisição válida para `atB=1` ativa condição; registrar `ConditionChanged` e um efeito no executor. Capturar payload exato do log `send` do avaliador.
5. Reenviar `POST /notifications/condition` ao executor com mesmo evento: esperar HTTP 200 `duplicate=true`, sem novo efeito.
6. Reutilizar cada `event_id` com payload diferente mas estruturalmente válido: HTTP **409**, sem mutação. Conferir ledger, estados e contagem de efeitos em cada ponto.

### V06 — ordenação / lacunas em bancada separada

1. Snapshot novo, com watermarks iniciais 0 e `run_id` exclusivo; validar estado frio → pronto.
2. Enviar diretamente ao avaliador um `AttributeChanged` válido com sequência **2** antes da 1: esperar HTTP **409** e watermark/atributos/efeitos inalterados.
3. Enviar evento com `run_id` divergente: HTTP **409**, sem alteração.
4. Enviar `ConditionChanged` válido ao executor com sequência **2** sem ter recebido sequência 1: HTTP **409** e nenhuma execução.
5. Após a verificação desses bloqueios, se necessário, enviar um evento válido sequência 1 e testar comportamento de evento antigo/conflictante, sem misturá-lo com a fixture principal. Registrar decisão e rastreabilidade.

## 4. Riscos e limitações

- No código, `LogicEngine.receive` e `RuleExecutor.receive` aceitam idempotência de payload igual **antes** da validação de sequência, e rejeitam divergência de corpo/reordenação com `ContractError(status=409)`. Duplicata não deve mutar o estado.
- `emitted_at` faz parte do payload comparado pelo ledger: não gerar novo timestamp ao reenviar um mesmo `event_id`; usar o evento original.
- O HTTP atual é serial por serviço (`HTTPServer`), não houve demonstração de tolerância a falhas, replicação ou ordenação sob concorrência arbitrária.
- Após qualquer erro ou interrupção de script, **preservar os contêineres e logs**, sem reexecutar as alterações automaticamente. Sem afirmar V05/V06 antes da saída real e da auditoria de ZIP.
- Não inferir distribuição física ou uso da aplicação no Kubernetes a partir de vários contêineres no host.

## 5. Critério de encerramento E08

Provar funcionalidade C2 da fixture e auditar evidências (concluído); complementar V03/V05/V06 com delimitação de escopo; revisar V07 quanto à cobertura real; consolidar topologia, comandos, logs, imagens/digests, hashes, limitações e checkpoint, preservando insumos para a monografia. Kubernetes seguirá somente na Etapa 09.

## 6. Continuidade real E08-D17A e E08-D17B (15/11/2026)

- **E08-D17A aprovado:** rede V05 bridge interna, 3 contêineres em execução, IDs distintos, sem portas publicadas, logs `listening`.
- **E08-D17B aprovado:** preflight de saúde e estado frio via HTTP real nos três contêineres. Print `image(20261115-174707).png` (93.598 bytes), SHA-256 `514ec8a34b30ec28d4afb95c65908b548ac559e124144c0e6a7b2fbfac9b3582`. Original na conversa e não versionado no GitHub. Estado de cada papel como esperado e Git limpo.
- A subseção anterior descrevia o desenvolvimento do executor como D17B; o diagnóstico de saúde recebeu o identificador **D17B** na execução real. Para evitar colisões, o próximo incremento é **E08-D17C (snapshot funcional)**; a automação posterior da deduplicação será numerada após esse aceite.
- **Não realizado:** qualquer snapshot ou notificação V05 e a verificação dos ACKs de deduplicação; só a infraestrutura e o estado frio foram aprovados. Não reiniciar contêineres.

## 7. E08-D17C — primeiro snapshot V05 aprovado (15/11/2026)

- Execução Windows recebida: `image(20261115-175306).png` (142.516 bytes), SHA-256 `3b03035b4e1fa64c24750f9de658aa06ef67b76693a5430d58d1dce91fa92e0c`, original somente na conversa.
- 3/3 preflights frios OK; HTTP POST do snapshot no atributo fonte com resultado 200, `duplicate=false`, `run_id=v05-dedup-v1`, `snapshot_version=v05-dedup-v1:snapshot:0`. Três serviços `ready=true`, condição `false`, regra `false`, 0 efeitos, sem notificações de mudança; logs demonstram ACKs da cadeia.
- **E08-D17C APROVADO**, mas V05 deduplicação ainda **não** ensaiada. **E08-D17D** deve testar apenas primeira mudança `atA=5` (sem ativação da condição) e guardar evento de atributo ORIGINAL para reenvio. Para verificação de payload duplicado, `emitted_at`, `request_id` e demais campos precisam permanecer idênticos; não gerar um segundo evento manual novo.

## 8. E08-D17D — primeiro AttributeChanged validado (15/11/2026)
- Captura PowerShell `image(20261115-175816).png`, 166635 bytes, SHA-256 recalculado `a22f086a610d52e024a97fce1c8ec107036f882a403db7072b5037bf269f71c1`. O arquivo original está na conversa, não no repositório.
- HEAD Windows `7f6294431a97a49388518e817cf153b9edfee73f`, branch `tcc2/desenvolvimento`, Git limpo. Estados antes 3/3 aprovados.
- POST único `/attributes/change` em `tcc2-v05-attribute-source` com `run_id=v05-dedup-v1`, `request_id=v05-req-atA-1`, `entity_id=atA`, `value=5`, `step=1`: HTTP 200, `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atA:1`, `sequence=1`.
- GET `/state` depois: fonte/avaliador atributos `atA=5,atB=0`, sequências `atA=1,atB=0`; avaliador `received_ids=["v05-dedup-v1:atA:1"]`, `condition=false`, `condition_sequence=0`, `condition_events=[]`; executor `approved=false`, `received_ids=[]`, `effects=[]`. Sem falhas.
- Logs reais: produtor `send /notifications/attribute` e `ack` com resposta `{accepted:true,duplicate:false}`, avaliador `mutation /notifications/attribute` status 200 com payload original e ACK correspondente. Nenhum evento de condição ou efeito esperado.
- **E08-D17D aprovado**, mas **não houve replay** e V05 deduplicação permanece pendente.
- **Próximo E08-D17E:** capturar os logs originais e validar por leitura o evento `send` único, sem gerar novo timestamp. Guardar arquivo de payload original e seu SHA-256 para futuro replay único E08-D17F. Não reiniciar os contêineres e não alterar a imagem.

## 9. E08-D17E — evento original capturado no Windows (15/11/2026)

- Print real `image(20261115-180441).png` enviado: 94724 bytes, SHA-256 recalculado `88eceb148d582b57a27f37a72113a4c2c0d1dde76ce95a7c4fa64d6d7d2e1141`. Original permanece na conversa, não no repositório.
- Git Windows em `600fa9e636611d7e5c52c0a9a7a18590388ec5cf`, limpo ao final. O script somente leu logs `docker logs`, sem enviar qualquer POST.
- Saída real: `EVENTO ORIGINAL: OK`, `ENVIO: 1`, `ACK: 1`, `RECEBIMENTO: 1`, `PAYLOADS IDENTICOS: True`, `EFEITOS: 0`, `HASHES: 5` e `E08-D17E: CAPTURA CONCLUIDA`.
- Evento: `event_id=v05-dedup-v1:atA:1`, `request_id=v05-req-atA-1`, `run_id=v05-dedup-v1`, `source=attribute-source`, `entity_id=atA`, `value=5`, `sequence=1`, `step=1`, `schema_version=1`, `emitted_at=2026-11-15T17:57:08.636308+00:00` (UTC original capturado, não reproduzir com novo timestamp).
- Evidências locais: `prova-conceito/resultados-locais/c2-v05-original-20261115-150412`: três logs, `attribute-event-original.json`, `capture-summary.json`, `checksums.sha256` (5 hashes referenciados no manifesto).
- **E08-D17E aprovado como captura/consistência de payload**; replay idempotente ainda NÃO executado, não há resultado V05 de deduplicação.
- **E08-D17F preparado, não executado:** `prova-conceito/c2/v05_duplicate.py`, replay único com pré-condições de estado, imagem e logs, verificação de SHA-256 do payload original, um único `POST /notifications/attribute` ao avaliador, comparação de estados e logs antes/depois, registro SHA-256 e teste local. `tests/test_c2_v05_duplicate.py` contém 7 testes unitários, ainda pendentes de validação no Windows.
- Não reconstruir imagem, não reinicializar V05, não repetir `/attributes/change`, não tocar em V03, C2 principal nem cluster kind.

## 10. E08-D17F — replay idempotente do atributo aprovado no Windows (15/11/2026)

- Prints originais recebidos na conversa: `image(20261115-181207).png` **85.792 bytes**, SHA-256 **`076be5e983dd8327a73b0afea7eba77725a602bc824e0a39e589d87d6c254938`**, e `image(20261115-181217).png` **58.509 bytes**, SHA-256 **`d318ab4b2ccde10908c44327ca4d7d12ec390ba9e8d526493e82f929e8cb898e`**. Hashes calculados dos PNGs enviados; originais permanecem anexados à conversa, não ao Git.
- Windows: fast-forward para HEAD `cb212667616b5e94128b1337f7a12b6d499891e8`, `Compilacao: 0`, **57/57 testes OK em 11.260 s**, `Testes: 0`, branch e Git final limpos. Tempo é da regressão, não benchmark.
- Arquivo original em `resultados-locais/c2-v05-original-20261115-150412/attribute-event-original.json`; SHA-256 **`b325a023eac2609601307a84aab0d1d8d30ecd21b8211a5f4b0ab4ea5c7c2e25`** exibido pelo PowerShell; não reconstituído de memória.
- Execução única `python -m c2.v05_duplicate`: `scenario=C2`, `criterion=V05`, `increment=E08-D17F`, **`status=PASS`**, `replay_attempted=true`, `event_id=v05-dedup-v1:atA:1`, `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`, `V05: 0`.
- Resposta HTTP efetivamente exibida: **200**, `body={"accepted":true,"duplicate":true}`. `new_logic_mutations=1` significa **um evento adicional do logger HTTP do avaliador**, não alteração do estado PON, conforme `states-before.json` e `states-after.json` comparados pelo executor. Os logs da fonte e do executor permaneceram sem acréscimos segundo o executor.
- Evidências locais da rodada: `prova-conceito/resultados-locais/c2-v05-duplicate-20261115-151112` com `manifest.json`, `event-original.json`, `request-intent.json`, `replay-response.json`, `states-before.json`, `states-after.json`, `validation.json`, três pares de logs antes/depois e `checksums.sha256` (**13 arquivos listados no manifesto + manifesto = 14 arquivos esperados**).
- **Conclusão:** E08-D17F **aprovado operacionalmente na única duplicação de atributo ensaiada**. Os bytes da pasta, incluindo hashes internos, **não foram ainda auditados independentemente**; só se verificaram os hashes exibidos na captura. A pasta de evidências deve ser empacotada e enviada em ZIP antes de declarar integridade independente.
- **Próximo E08-D17G:** realizar apenas verificações de hashes e arquivamento ZIP; não repetir `/notifications/attribute`, `/attributes/change` ou reiniciar contêineres. Após auditoria, abordar event_id conflitante (HTTP 409), duplicação de ConditionChanged e V06 em rodada separada. Sem Kubernetes/benchmark nesta etapa.

## 11. E08-D17G — integridade V05 deduplicação de atributo aprovada (15/11/2026)
- ZIP original recebido e auditado: 7163 bytes, SHA-256 `532281718862cc28bd17654721b6d01d0a78d8d9cc9c7283730e8c943b9ca3cb`, 14/14 entradas e CRC corretos, 13/13 SHA-256 internos; estados idênticos; logs source 7→7, logic 5→6, executor 2→2, único ACK duplicado 200 sem novo efeito.
- Laudo `docs/tcc2/etapa-08-auditoria-v05-atributo.md`. V05 deduplicação de atributo **aprovada no caso ensaiado**; conflitos de corpo (HTTP 409) e deduplicação de condição **pendentes**.
- Próximo E08-D17H: validar reuso do mesmo `event_id` com corpo divergente, sem reinicializar V05 e sem repetir o replay, esperando 409 e invariância; depois avançar para ConditionChanged e V06.

## E08-D17H — executor de conflito preparado (ainda NÃO executado)

- O contrato em `c1/state.py` rejeita o mesmo `event_id` com payload diferente (`ContractError(status=409)`, `error="event_id reutilizado com payload diferente"`). `c1/protocol.py` permite `value=6` para `atA`.
- Preparado `prova-conceito/c2/v05_conflict.py`: valida SHA-256 E17E/E17F, topologia, estado atual, logs anteriores (original e único replay), registra intenção antes do POST; altera apenas `value=5 → 6` em cópia do payload original, preservando ID e timestamp; exige HTTP 409, estado global imutável, um registro 409 novo no avaliador, nenhuma mudança nos logs de fonte/executor; salva evidências e checksums SHA-256. **Sem retry.**
- Adicionados 7 testes locais (sem Docker): `prova-conceito/tests/test_c2_v05_conflict.py`. Pendentes compilação/regressão no Windows. A nova suíte esperada é de **64 testes** (57 prévios + 7), não resultado medido.
- Próximo: sincronizar branch, compilar, executar regressão, executar uma vez `python -m c2.v05_conflict --capture ... --previous ... --output ...`, preservar qualquer `FAIL` sem reenvio, auditar novo ZIP antes de novos ensaios.

## 12. E08-D17H — conflito de event_id aprovado operacionalmente (15/11/2026)

- Capturas originais enviadas nesta conversa: `image(20261115-184410).png` (94.191 bytes, SHA-256 `2b1a2ada040bede5e617cd081fe1e98bfff72be05cc2848f190df1b863066c5b`), `image(20261115-184423).png` (76.959 bytes, SHA-256 `b558ed6efcfc82dc685a7417634cdc0825701330816ab2f9071d32bb7bd7e727`). Hashes calculados diretamente sobre os PNGs montados, que não foram versionados no Git.
- HEAD executado no Windows: `5787a095045d37d24b2b141070823676277d90f0`; compilação `0`; suíte de **64 testes aprovada em 11,012 s** (tempo da suíte, não benchmark); Git final limpo.
- Rodada `E08-D17H`, cenário `C2`, critério `V05`, relatório `status=PASS`, `attempted=true`; `event_id=v05-dedup-v1:atA:1`; `expected_http=409`, `observed_http=409`; `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`; código de saída `V05 conflito: 0`.
- Resposta HTTP observada: status 409, `body.error="event_id reutilizado com payload diferente"`. O teste alterou `value` de 5 para 6 preservando `event_id` segundo o executor; verificar evento original e conflito diretamente após receber o ZIP.
- Pasta de evidências no host: `prova-conceito/resultados-locais/c2-v05-conflict-20261115-154229`, incluindo `event-original.json`, `event-conflict.json`, `conflict-response.json`, estados/logs antes/depois, `request-intent.json`, `validation.json`, `manifest.json`, `checksums.sha256`.
- **Aceite operacional E08-D17H** baseado em saída real. O relatório de estado inalterado foi emitido pelo executor, ainda sem comparação binária externa; auditoria independente de integridade **pendente**.
- **E08-D17I próximo:** somente empacotar arquivos e verificar hashes SHA-256; arquivo esperado 15 entradas = 14 arquivos de dados listados no manifesto + `checksums.sha256`. Não repetir o POST 409. Após upload, auditar ZIP e então prosseguir V05 condição.

## 13. E08-D17I — auditoria de conflito V05 aprovada (15/11/2026)
- ZIP de conflito validado diretamente: 7.683 bytes, SHA-256 `4aef50d86c83feceb8c007dfa959e82a5e57a9ced23df2ef827a7d39839f327b`; 15 entradas, CRC OK, 14/14 hashes internos corretos. Estado idêntico antes/depois com SHA `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`. Logs 7→7 (fonte), 6→7 (avaliador, um 409), 2→2 (executor). Evento conflitante difere somente em `value=6` vs original 5; resposta HTTP 409 coerente.
- Relatório técnico: `docs/tcc2/etapa-08-auditoria-v05-conflito.md`.
- A cobertura principal de deduplicação e rejeição de conflito **de AttributeChanged** está registrada e auditada; resta `ConditionChanged` no executor, V06, revisão V07 e documentação final. Próximo E08-D17J: preflight de estado V05 após conflito, sem qualquer POST.

## 14. E08-D17J — preflight V05 para condição aprovado no Windows (15/11/2026)

- Captura real `image(20261115-185446).png` recebida: **102.442 bytes**, SHA-256 recalculado `198375f957fb03bbcae26e36ae32310e91abba0d8e18dc67eed1f215599c7c96`, resolução 1920×1080; original permanece na conversa.
- HEAD Windows `7e4069c0df5f93ab4313d4968e65375c72ef40b6` após fast-forward, branch `tcc2/desenvolvimento` e Git final limpo. Rede `tcc2-pon-c2-v05` driver=bridge `Internal=true`.
- `/health/live`: 3/3 `LIVE: OK`. `/state`: 3/3 `STATE: OK`, `ready=true`, `run_id=v05-dedup-v1`, `snapshot_version=v05-dedup-v1:snapshot:0`. Fonte e avaliador `atA=5,atB=0` com sequências `1,0`; avaliador `condition=false`, `condition_sequence=0`, `received_ids=["v05-dedup-v1:atA:1"]`; executor `approved=false`, `condition_sequence=0`, `received_ids=[]`, `effects=[]`. Três contêineres V05 UP. Nenhum POST nesta etapa.
- **E08-D17J APROVADO como preflight, não como transição ou deduplicação de condição**.
- **E08-D17K preparado no repositório, ainda NÃO executado no Windows:** `prova-conceito/c2/v05_condition_first.py` para um único `POST /attributes/change` com `atB=1`, `request_id=v05-req-atB-1`, `step=2`, após verificar hashes/estado/topologia/logs, com evidências pré/pós e captura do `ConditionChanged` original. `tests/test_c2_v05_condition_first.py` adiciona 8 testes locais, que ainda não foram executados no Windows.
- Esperado, não medido: condição `true`, sequência 1, aprovação da regra `true` e 1 efeito, `event_id=v05-dedup-v1:cn1:1` causado por `v05-dedup-v1:atB:1`; capturar a mensagem com timestamp original para ensaio de replay posterior. Não repetir POST em caso de falha.

## 15. E08-D17K — transição de condição e primeiro efeito V05 aprovados operacionalmente (15/11/2026)

- Evidência primária: três capturas PowerShell recebidas na conversa (binários não versionados em Git): `image(20261115-190447).png`, 87305 bytes, SHA-256 `f82580a41fd28ed2b23cecf411d6438a7f682941d599bf3fef4c7b4d1364f3e5`; `image(20261115-190457).png`, 70254 bytes, SHA-256 `d61c84381b94ee931bc04f907eb0047f4d785f19a32e45950815d8bf3f656e80`; `image(20261115-190509).png`, 65438 bytes, SHA-256 `73c096f0d318483945f579c93a2727b99c1818102639d8049eb7a2becab27ea4`.
- Branch `tcc2/desenvolvimento`, HEAD Windows `ba200b85bfe24f81b15a3f1ec838480a6cc10e49` após fast-forward, Git final limpo. Compilação `0`; **72/72 testes automatizados aprovados em 10,837 s** (tempo da regressão, **não** benchmark).
- Executor `c2.v05_condition_first`: `scenario=C2`, `criterion=V05`, `increment=E08-D17K`, `status=PASS`, `attempted=true`, `condition_sequence=1`, `effects_count=1`, retorno `V05 condicao: 0`.
- Envio único planejado e registrado pelo executor: `POST /attributes/change`, `{"run_id":"v05-dedup-v1","request_id":"v05-req-atB-1","entity_id":"atB","value":1,"step":2}`. Resposta HTTP observada **200**, corpo `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atB:1`, `sequence=1`.
- No `/state` exibido dos três serviços: `atA=5,atB=1`, sequências `1/1`, avaliador `condition=true`, `condition_sequence=1`, `condition_events` contém **um** evento `ConditionChanged` `v05-dedup-v1:cn1:1`, `approved=true`, `caused_by=v05-dedup-v1:atB:1`; executor `approved=true`, sequência 1, `received_ids=["v05-dedup-v1:cn1:1"]`, **um efeito** `event_id=v05-dedup-v1:rl1:1`, `caused_by=v05-dedup-v1:cn1:1`, `attribute_event_id=v05-dedup-v1:atB:1`, `step=2`.
- Evento de condição original exibido: `emitted_at=2026-11-15T19:03:59.142115+00:00`. SHA-256 de `condition-event-original.json` mostrado pelo PowerShell: `04687836e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`. **Ainda não foi recalculado independentemente**, pois a pasta binária não foi enviada.
- Pasta local da rodada: `prova-conceito/resultados-locais/c2-v05-condition-first-20261115-160357`. O código do executor prevê 14 arquivos de dados mais `checksums.sha256` (total **15**), desde que não tenha ocorrido erro; verificar inventário real.
- Os três contêineres `tcc2-v05-*` constam `Up` na saída. Não ocorreu modificação do código PON, da imagem Docker ou do cluster kind.
- **Classificação:** E08-D17K **aprovado operacionalmente** com base nos prints e no relatório do executor; integridade do ZIP e validação independente dos bytes dos estados/logs **pendentes**. A transição `atB:1 → cn1:1 → rl1:1` fornece material de rastreabilidade para diagrama de sequência futuro, **sem mensuração de latência/desempenho**.
- **Próximo E08-D17L:** apenas conferir SHA-256, conteúdo funcional, empacotar pasta em ZIP e verificar 15 entradas antes de enviar para auditoria independente. **Não repetir o POST `atB=1` nem reiniciar os serviços.** Após auditoria, preparar replay idempotente exato de `ConditionChanged` no `rule-executor`.

## 16. E08-D17L-R2 — auditoria da primeira transição ConditionChanged aprovada (15/11/2026)

- O ZIP `c2-v05-condition-first-20261115-160357.zip` foi recebido e auditado diretamente: **8.840 bytes**, SHA-256 recalculado `46787fb0ac9d7ae068aa9e13ef3cf3977bfdf84017acd1f61e8868709a52b587`; captura `image(20261115-191445).png` **86.408 bytes**, SHA-256 `e4c148bfe59c029e23e780151069469b3a1180ed2ba3c4f6b4b3f68340b567c8`. O print confirmou Git limpo no HEAD `f6293046a405aa76de672a7807b5e6ac80a422a5`, `Real=Manifesto: True` no diagnóstico anterior e `E08-D17L-R2: ARQUIVAMENTO CONCLUIDO`.
- Integridade: **15/15 entradas**, CRC OK, **14/14 SHA-256** coincidentes com bytes extraídos. Condição original SHA-256 `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`; o valor manual do primeiro comando estava errado (`04687836` vs `04687b36` no início), sem alteração do dado original.
- Dados auditados: HTTP 200 `changed=true`, `duplicate_request=false`; atributos `atA=5,atB=0` → `atA=5,atB=1`; condição `false→true`, sequência 0→1, payload `v05-dedup-v1:cn1:1` `approved=true`; executor `approved=false→true`, produz **um** efeito `v05-dedup-v1:rl1:1`. Logs: fonte **7→10**, avaliador **7→10**, executor **2→4**, todos os prefixos anteriores preservados; novos payloads e confirmações coerentes com cadeia causal.
- **E08-D17L-R2 aprovado independentemente.** Relatório `docs/tcc2/etapa-08-auditoria-v05-condicao-inicial.md`. As notas anteriores de auditoria pendente de E08-D17K estão superadas.
- **Próximo E08-D17M:** reenvio idêntico de `condition-event-original.json` ao executor, apenas uma tentativa HTTP, após verificações preventivas de estado/topologia/logs e evidências; exigir ACK `duplicate=true`, nenhum efeito adicional e estados idênticos. Não repetir alteração `atB=1`.

## 17. E08-D17M — replay de ConditionChanged preparado, ainda não executado
- Código `prova-conceito/c2/v05_condition_replay.py` preparado com preflight completo: SHA-256 do evento de condição aprovado em E08-D17L-R2; integridade de 14 arquivos anteriores; estado e logs atuais **iguais aos arquivos auditados**; os três IDs e horários de inicialização dos contêineres e a topologia Docker coerentes. Exige o `run_id=v05-dedup-v1`.
- Após esse preflight, faz **um único** `POST /notifications/condition` ao `rule-executor` com o payload original íntegro, incluindo `emitted_at`. Exige HTTP 200 `accepted=true,duplicate=true`, todos os estados idênticos, **zero efeito adicional** e um único novo registro HTTP no executor; logs source/logic invariáveis.
- Evidências: manifesto de imagem, IDs e hashes anteriores, intenção de envio escrita antes do POST, respostas, estados/logs pré/pós, `validation.json` e `checksums.sha256`. Em caso de falha após envio, preservar os arquivos, **NÃO repetir**.
- Adicionados **8 testes unitários preparados** em `tests/test_c2_v05_condition_replay.py` (ainda não executados no Windows). Total esperado na próxima suíte: **80** (72 anteriormente aprovados + 8 novos), não uma medição atual.
- Não houve reconstrução de imagem nem reimplantação de serviços, alteração de núcleo PON, de `master` ou do cluster kind.

## 18. E08-D17M — replay exato de ConditionChanged V05 aprovado operacionalmente (15/11/2026)

- Capturas PowerShell fornecidas pelo acadêmico: `image(20261115-192312).png` (87.353 bytes; SHA-256 recalculado `ac0515c61ea42ca9d590e86d97f0f59281bb9467b93c631bcdef5219f892e6fa`) e `image(20261115-192356).png` (71.569 bytes; SHA-256 `405c09d2d24927fc287345355b2cef2bdd3b7d5d5ae9cc50f945ce40c5c9dfb6`). Arquivos de imagem anexados à conversa, não versionados no GitHub.
- Branch `tcc2/desenvolvimento`, HEAD Windows `a654453c284563ec3324a1c1b3462f759e9d10ec` após `git pull --ff-only`; compilação código 0; **80 testes automatizados OK em 11,065 s** (duração da regressão, **não** métrica de desempenho experimental); Git final sem alterações exibidas.
- Executor `c2.v05_condition_replay` reportou `scenario=C2`, `criterion=V05`, `increment=E08-D17M`, `status=PASS`, `replay_attempted=true`, `event_id=v05-dedup-v1:cn1:1`, `expected_http=200`, `observed_http=200`, `duplicate=true`, `state_unchanged=true`, `new_effects=0`, `new_executor_mutations=1`, retorno `V05 replay: 0`.
- Resposta HTTP exibida: `{"status":200,"body":{"accepted":true,"duplicate":true}}`. Três serviços `tcc2-v05-attribute-source`, `tcc2-v05-logic-engine`, `tcc2-v05-rule-executor` exibidos em estado `Up`. Sem novo evento `atB=1`, sem reinicialização ou alteração de imagem demonstrada.
- Pasta de evidências no Windows: `prova-conceito/resultados-locais/c2-v05-condition-replay-20261115-162246`; o print apresenta `checksums.sha256` com **13 arquivos listados**, mais o próprio manifesto (inventário total esperado: **14**). **Ainda não recebemos ZIP; CRC, 13 SHA-256 internos e consistência independente dos bytes de logs/estados permanecem pendentes**.
- Classificação: **E08-D17M aprovado operacionalmente pelos prints e relatório**, não auditado independentemente até receber ZIP.
- Próximo **E08-D17N**: somente leitura e empacotamento da pasta de evidências V05: validar `validation.json`, `replay-response.json`, igualdade exata `states-before.json`/`states-after.json`, logs fonte/avaliador invariáveis e um novo log de `mutation` no executor com `duplicate=true` (nenhum novo `effect`), checar 13 SHA-256 locais, empacotar 14 entradas e conferir conteúdo ZIP/CRC. **Não repetir POST** ou reiniciar contêineres.
