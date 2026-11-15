# TCC2 — Etapa 08: auditoria independente E08-D17G (V05 replay atributo)

**Data:** 15/11/2026 · **Cenário:** C2 (três contêineres Docker no mesmo host) · **Critério:** V05 · **Incremento de execução:** E08-D17F · **Incremento de auditoria:** E08-D17G.

## 1. Identificação e proveniência

| Evidência | Resultado |
|---|---|
| ZIP original recebido e aberto | `c2-v05-duplicate-20261115-151112.zip` |
| Tamanho do ZIP | 7163 bytes |
| SHA-256 do ZIP, calculado diretamente do upload | `532281718862cc28bd17654721b6d01d0a78d8d9cc9c7283730e8c943b9ca3cb` |
| Captura Windows da criação do ZIP | `image(20261115-182817).png`, 98401 bytes |
| SHA-256 da captura recalculado diretamente | `fca5defd9745c52a91604034e8938be44401a645dbf0b190c0eac5c604d5fdcc` |
| Imagem Docker declarada no manifesto | `tcc2-pon:c2-e08-dbefcd2cf3d2` |
| ID da imagem declarado | `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a` |
| Revisão OCI declarada | `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` |
| Código do executor no manifesto | `cb212667616b5e94128b1337f7a12b6d499891e8` |
| Rede declarada | `tcc2-pon-c2-v05`, interna |
| Diretório local no Windows | `prova-conceito/resultados-locais/c2-v05-duplicate-20261115-151112` |

O ZIP e a captura foram fornecidos neste diálogo. Os arquivos binários originais não foram incorporados ao GitHub, mas os respectivos hashes permitem rastreá-los. A identidade da imagem/rede é uma propriedade reportada pelo manifesto do executor e foi verificada no preflight do Windows; **a auditoria deste ZIP não inspeciona o daemon Docker em tempo real**.

## 2. Integridade dos arquivos

- ZIP contém **14 entradas distintas**, todas sob `c2-v05-duplicate-20261115-151112\\`.
- `zipfile.testzip()` não encontrou falhas de CRC.
- O `checksums.sha256` contém **13 linhas válidas**, cada uma referenciando uma entrada única; SHA-256 foi recalculado diretamente dos bytes extraídos do ZIP: **13/13 coincidiram**.
- Itens incluídos: `attribute-source-before.jsonl`, `attribute-source-after.jsonl`, `logic-engine-before.jsonl`, `logic-engine-after.jsonl`, `rule-executor-before.jsonl`, `rule-executor-after.jsonl`, `states-before.json`, `states-after.json`, `event-original.json`, `request-intent.json`, `replay-response.json`, `manifest.json`, `validation.json` e `checksums.sha256`.
- SHA-256 do evento original dentro do pacote: `b325a023eac26d9601307a84aab0d1d8d30ecd21b8211a5f4b0ab4ea5c7c2e25`, igual ao hash que apareceu no PowerShell E08-D17F.
- Estados `states-before.json` e `states-after.json` são **idênticos em bytes**, ambos com SHA-256 `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`.

## 3. Consistência funcional auditada

- `request-intent.json`: `target=tcc2-v05-logic-engine`, `path=/notifications/attribute`, `event_id=v05-dedup-v1:atA:1`, `attempt_count=1`, `automatic_retry=false`.
- `event-original.json`: evento `AttributeChanged` originalmente emitido, `schema_version=1`, `run_id=v05-dedup-v1`, `entity_id=atA`, `sequence=1`, `value=5`, `step=1`, `request_id=v05-req-atA-1`, `emitted_at=2026-11-15T17:57:08.636308+00:00`.
- `replay-response.json`: **HTTP 200**, corpo `{"accepted":true,"duplicate":true}`.
- `validation.json`: `status=PASS`, `replay_attempted=true`, `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`.
- Estado dos três serviços foi comparado antes/depois por igualdade estrutural e byte a byte. `logic-engine.received_ids` permaneceu `["v05-dedup-v1:atA:1"]`, `sequences.atA=1`, `condition=false`, `condition_sequence=0`; `rule-executor.effects=[]` antes e depois.
- Logs `attribute-source`: **7 antes/7 depois**, bytes idênticos; `rule-executor`: **2 antes/2 depois**, bytes idênticos; `logic-engine`: **5 antes/6 depois**, todos os cinco eventos originais preservados na ordem, acrescido de uma única linha `mutation /notifications/attribute`, HTTP 200, payload igual ao evento original, ACK `{"accepted":true,"duplicate":true}`.
- O envio original da fonte, o primeiro recebimento do avaliador e o replay registrado no log do avaliador compartilham **payload idêntico**. O primeiro recebimento tem `duplicate=false`; o segundo, `duplicate=true`.

## 4. Conclusão e delimitação de escopo

**E08-D17G APROVADO:** os artefatos são íntegros e coerentes com a deduplicação de **um replay idêntico** de `AttributeChanged` em C2. A auditoria confirma um novo registro HTTP sem alteração funcional nos estados e sem efeitos adicionais. O resultado é independente dos checks reportados pelo executor para os estados globalmente antes/depois e para o conteúdo dos logs, pois seus bytes foram examinados diretamente.

**Limitações:** os bytes são evidência da rodada reportada, não observação direta da rede por auditor externo; a afirmação `attempt_count=1` se baseia no registro do próprio executor, embora o acréscimo de um único log HTTP seja compatível. Não há prova de tolerância a falhas, concorrência arbitrária, persistência, distribuição entre hosts, Kubernetes ou desempenho.

**Próximos incrementos:** E08-D17H — ensaio controlado de conflito de `event_id` com payload divergente esperando HTTP 409 e estados inalterados; depois deduplicação de `ConditionChanged` no executor, V06 em rede isolada, revisão de V07 e encerramento. **Não repetir o replay E08-D17F nem reiniciar os contêineres V05**.
