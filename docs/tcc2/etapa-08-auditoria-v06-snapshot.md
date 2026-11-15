# TCC2 — Etapa 08: Auditoria do snapshot inicial da bancada V06 (E08-D18B–E)

**Data:** 15/11/2026. **Branch de referência:** `tcc2/desenvolvimento`. **Commit do código executado no Windows:** `6c850128efb5226ac31575206f6b23fc69171fc4`.

## 1. Evidências originais

- Captura Windows `image(20261115-210656).png` confirma o E08-D18D: 88 testes `unittest` aprovados em 10,734 s (tempo de regressão, não benchmark), preflight frio e da topologia OK, **um** POST `/init/snapshot` no produtor HTTP 200, três estados validados, logs fonte 4 / avaliador 4 / executor 2, relatório `PASS` e saída 0.
- Captura Windows `image(20261115-211110).png` (92.761 bytes, SHA-256 `90acb6e9f7a54e42a034bf42e674aa329883c6bd5bc720e248378f285922ca95`) confirma E08-D18E: 13/13 arquivos, 12/12 hashes, ZIP/CRC OK, tamanho 5.896 bytes e Git sem alterações exibidas.
- ZIP original recebido na conversa `c2-v06-snapshot-20261115-180612.zip`: **5.896 bytes**, SHA-256 calculado diretamente sobre bytes recebidos `544e9fe8eb12878268393db5eeddaa698a9c02cee5c19080f56cb490a2c21987`, idêntico ao impresso no Windows. Contém 13 entradas únicas com caminho-base esperado, sem erros de CRC; `checksums.sha256` possui **12/12** SHA-256 válidos dos arquivos integrantes. O ZIP fica no computador do acadêmico e na conversa, **não foi adicionado em binário ao GitHub**.

## 2. Topologia e continuidade da bancada

- Cenário **C2 em um host**, rede Docker `tcc2-pon-c2-v06`, imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, revisão `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Os IDs e datas de `StartedAt` dos três contêineres `tcc2-v06-*` em `manifest.json` correspondem aos apresentados na captura E08-D18B. `restart_count=0` nos três. O manifesto também registra três contêineres `tcc2-v05-*` preservados. O ZIP não demonstra por si só o estado **atual** do Docker fora do instante da coleta.
- E08-D18B (prints do acadêmico): rede `bridge/internal=true`, três membros, três contêineres `Running=true`, IDs distintos, sem portas publicadas, três logs `listening` na porta 8080, V05 preservado. E08-D18C (prints): `GET /health/live` HTTP 200, `GET /health/ready` HTTP 503 no estado frio, `GET /state` sem `run_id`, HTTP 200 fonte→avaliador e avaliador→executor via DNS interno. Nenhum POST até esse ponto.

## 3. Auditoria funcional do snapshot E08-D18D

- `request-intent.json`: `method=POST`, alvo `tcc2-v06-attribute-source`, rota `/init/snapshot`, corpo `{"run_id":"v06-order-v1"}`, `max_attempts=1`, `automatic_retry=false`. Este registro estabelece intenção; a execução do POST é sustentada por resposta e logs.
- `snapshot-response.json`: HTTP **200**, `ready=true`, `duplicate=false`, `snapshot_version=v06-order-v1:snapshot:0`.
- `states-before.json`: três serviços `ready=false`, `run_id=null`, `snapshot_version=null`, água-marca de atributos e condição 0, nenhum efeito/ID recebido. `states-after.json`: três serviços `ready=true`, mesmo `run_id=v06-order-v1`, mesma versão; atributos fonte e avaliador `atA=0,atB=0`, sequências 0, condição `false`, executor `approved=false`, sequência de condição 0, **0 efeitos** e **0 received_ids**.
- Logs `attribute-source`: **1→4** `listening,send,ack,mutation`; `logic-engine`: **1→4** com mesmo encadeamento; `rule-executor`: **1→2** `listening,mutation`. Os registros anteriores são prefixos exatos dos posteriores, com reconhecimento e respostas de inicialização coerentes. Nenhum `AttributeChanged`, `ConditionChanged` ou `effect` aparece nos logs do ZIP.
- `validation.json`: `scenario=C2`, `criterion=V06`, `increment=E08-D18D`, `status=PASS`, `attempted=true`, `http_status=200`, `ready_services=3`, `initial_effects=0`.
- Validação feita **independentemente sobre os bytes recebidos**; não constitui nova execução Docker no Windows nem teste de latência ou desempenho.

## 4. Decisão e próximo incremento

**E08-D18B/C/D/E aprovados no escopo declarado.** Snapshot V06 inicializado e arquivado. **V06 ainda não concluído**, pois faltam os ensaios de sequência 2 antes de 1 (`AttributeChanged` no avaliador), `run_id` divergente e lacuna de `ConditionChanged` no executor; a matriz está em `docs/tcc2/etapa-08-v05-v06-plano.md` e o protocolo da Etapa 05.

**Próximo E08-D18F:** ensaio isolado de `AttributeChanged` válido em sintaxe com `sequence=2` antes de 1, usando `run_id=v06-order-v1`, endereço interno do `logic-engine` e POST único. Critério de aceite: HTTP **409** com `error="evento atrasado ou lacuna de sequence"`, três estados iguais antes/depois, ausência de novos efeitos, fonte/executor sem novos logs, **um** registro HTTP de rejeição no avaliador. Registrar todos os bytes, hashes e POST sem retry; arquivar ZIP depois. **Não reinicializar V06 ou repetir snapshot; não tocar V05 nem Kubernetes.**
