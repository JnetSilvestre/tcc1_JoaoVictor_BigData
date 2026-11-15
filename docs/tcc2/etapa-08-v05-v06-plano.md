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
