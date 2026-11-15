# TCC2 — Etapa 08: auditoria independente de ConditionChanged inicial (E08-D17L-R2)

**Data:** 15/11/2026 · **Cenário:** C2 (três contêineres Docker no mesmo host Windows) · **Critério:** V05 · **Origem:** E08-D17K · **Auditoria:** E08-D17L-R2.

## 1. Evidência e identificação

| Item | Valor |
|---|---|
| ZIP recebido e inspecionado diretamente | `c2-v05-condition-first-20261115-160357.zip` |
| Tamanho do ZIP | **8840 bytes** |
| SHA-256 do ZIP recalculado | `46787fb0ac9d7ae068aa9e13ef3cf3977bfdf84017acd1f61e8868709a52b587` |
| Captura PowerShell recebida | `image(20261115-191445).png` |
| Tamanho da captura | **86408 bytes** |
| SHA-256 da captura recalculado | `e4c148bfe59c029e23e780151069469b3a1180ed2ba3c4f6b4b3f68340b567c8` |
| SHA-256 do evento `condition-event-original.json` | `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54` |
| Diretório local de origem | `prova-conceito/resultados-locais/c2-v05-condition-first-20261115-160357` |
| Commit da execução (declarado no manifesto, confirmado no print) | `ba200b85bfe24f81b15a3f1ec838480a6cc10e49` |
| Imagem Docker (declarada no manifesto) | `tcc2-pon:c2-e08-dbefcd2cf3d2` |
| Rede Docker (declarada no manifesto) | `tcc2-pon-c2-v05`, `internal=true` |

O ZIP e o PNG originais permanecem anexados à conversa/host Windows; **não foram adicionados ao GitHub**. Identificadores de rede, contêineres e imagem foram fornecidos pelo manifesto capturado pelo executor, não reconsultados em tempo real pelo auditor.

## 2. Integridade verificável

- ZIP aberto diretamente com `zipfile.ZipFile`; **15 entradas não duplicadas**, com prefixo de pasta `c2-v05-condition-first-20261115-160357`, nenhuma falha de CRC (`testzip()=None`).
- `checksums.sha256` contém **14 linhas válidas e distintas**. Todos os nomes correspondem aos 14 arquivos de dados no ZIP, sem entradas extras/ausentes; os 14 SHA-256 foram recalculados a partir dos **bytes descompactados**: **14/14 coincidentes**.
- Os arquivos `.json` e os registros `.jsonl` foram analisados com parse JSON válido; estados e logs comparados independentemente, sem depender somente de `validation.status=PASS`.
- SHA-256 independente de `condition-event-original.json`: `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`. Coincide com o arquivo e `checksums.sha256` e com o diagnóstico E08-D17L-R1/R2.
- **Falha E08-D17L inicial:** o hash digitado manualmente diferia no oitavo caractere (usou `04687836...` em vez do real `04687b36...`). O E08-D17L-R1 confirmou `Real=Manifesto: True` e `Real=Anterior: False`; nenhum arquivo foi modificado. E08-D17L-R2 removeu essa comparação manual e concluiu o empacotamento.

## 3. Resposta e causalidade auditadas

- `request-intent.json`: `target=tcc2-v05-attribute-source`, `path=/attributes/change`, payload `{"run_id":"v05-dedup-v1","request_id":"v05-req-atB-1","entity_id":"atB","value":1,"step":2}`, `attempt_count=1`, `automatic_retry=false`.
- `attribute-response.json`: **HTTP 200**, `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atB:1`, `sequence=1`.
- `attribute-event-original.json`: `AttributeChanged`, `event_id=v05-dedup-v1:atB:1`, `entity_id=atB`, `value=1`, `sequence=1`, `emitted_at=2026-11-15T19:03:59.105657+00:00`.
- `condition-event-original.json`: `ConditionChanged`, `event_id=v05-dedup-v1:cn1:1`, `entity_id=cn1`, `approved=true`, `sequence=1`, `caused_by=v05-dedup-v1:atB:1`, `emitted_at=2026-11-15T19:03:59.142115+00:00`, `step=2`. Objeto exatamente igual ao único item de `logic-engine.condition_events` em `states-after.json`.
- `states-before.json`: ambos os serviços de atributos em `atA=5, atB=0`, sequências `1/0`; avaliador com condição falsa e contador 0; executor `approved=false`, `effects=[]`. `states-after.json`: atributos `atA=5,atB=1`, sequências `1/1`; avaliador com `condition=true`, `condition_sequence=1`; executor `approved=true`, `received_ids=["v05-dedup-v1:cn1:1"]`, `effects` de comprimento **1**, identificado por `v05-dedup-v1:rl1:1`, `caused_by=v05-dedup-v1:cn1:1`, `attribute_event_id=v05-dedup-v1:atB:1`, `effect="executed"`, `step=2`. Ambos permanecem sem falha.
- `validation.json`: `scenario=C2`, `criterion=V05`, `increment=E08-D17K`, `status=PASS`, `attempted=true`, `condition_sequence=1`, `effects_count=1`, IDs consistentes.

## 4. Logs por serviço: comparação independente

| Serviço | Antes | Depois | Novos registros |
|---|---:|---:|---|
| `attribute-source` | 7 | 10 | +3: `send /notifications/attribute` com payload original, `ack` `duplicate=false`, `mutation /attributes/change` HTTP 200 |
| `logic-engine` | 7 | 10 | +3: `send /notifications/condition` com payload original, `ack` `duplicate=false`, `mutation /notifications/attribute` HTTP 200 |
| `rule-executor` | 2 | 4 | +2: um `effect` `rl1:1` e `mutation /notifications/condition` HTTP 200 `duplicate=false` |

A sequência anterior de cada log é prefixo idêntico do respectivo log posterior. Os payloads de `attribute-source.send`, `logic-engine.mutation` e `attribute-event-original.json` são iguais. Os payloads de `logic-engine.send`, `rule-executor.mutation`, `condition-event-original.json` e `logic-engine.condition_events[0]` são iguais. O `rule-executor.effect` corresponde ao efeito final.

## 5. Conclusão e limites

**E08-D17L-R2 APROVADO por auditoria independente dos bytes enviados.** Os dados verificam a transição funcional `atB=1 → ConditionChanged approved=true → 1 efeito` em C2 para a rodada documentada, preservando os eventos originais com timestamps e SHA-256. O E08-D17L-R1 foi um erro de referência digitada, **não corrupção de evidência**.

Este resultado **não testa a deduplicação de ConditionChanged**, nem desempenho, disponibilidade, falhas de rede, persistência, Kubernetes ou distribuição entre máquinas. A contagem de uma tentativa depende do executor e dos logs disponíveis, não de captura externa do tráfego de rede.

**Próximo E08-D17M:** reenvio idêntico de `condition-event-original.json` ao `rule-executor` após preflight de estado e logs, exigindo HTTP 200 `duplicate=true`, estados inalterados e nenhum novo efeito. Não repetir `atB=1`, não reiniciar contêineres V05, não modificar `master`, referência `codigoPon`, imagem Docker ou cluster kind.
