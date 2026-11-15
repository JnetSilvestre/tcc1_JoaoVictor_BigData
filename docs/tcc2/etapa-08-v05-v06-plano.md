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
