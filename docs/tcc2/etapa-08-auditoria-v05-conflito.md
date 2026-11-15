# TCC2 — Etapa 08: auditoria independente do conflito V05 (E08-D17I)

**Data da auditoria:** 15/11/2026.  
**Cenário:** C2 (três contêineres Docker isolados no mesmo host Windows).  
**Critério:** V05 (reutilização de `event_id` com payload conflitante).  
**Resultado:** **APROVADO no caso ensaiado e nos arquivos efetivamente auditados**.

## 1. Evidências e proveniência

| Artefato | Identificador |
|---|---|
| ZIP recebido nesta conversa | `c2-v05-conflict-20261115-154229.zip` |
| Tamanho recalculado | **7.683 bytes** |
| SHA-256 do ZIP recalculado | `4aef50d86c83feceb8c007dfa959e82a5e57a9ced23df2ef827a7d39839f327b` |
| Captura PowerShell recebida | `image(20261115-184927).png` |
| Tamanho da captura | **92.871 bytes** |
| SHA-256 da captura recalculado | `379d4257acef5be2875696e1ce6512085bba5017c5d7e379fc73765db33c91de` |
| Diretório original declarado no Windows | `prova-conceito/resultados-locais/c2-v05-conflict-20261115-154229` |
| Código usado no ensaio (manifesto) | `5787a095045d37d24b2b141070823676277d90f0` |
| Imagem Docker (manifesto) | `tcc2-pon:c2-e08-dbefcd2cf3d2` |
| Revisão OCI (manifesto) | `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` |
| Rede Docker (manifesto) | `tcc2-pon-c2-v05`, `internal=true` |

ZIP e captura foram inspecionados **diretamente a partir dos arquivos enviados**; o ZIP binário **não foi versionado no GitHub**. Os identificadores do Docker são valores registrados no manifesto pelo executor da rodada; não representam uma inspeção independente do daemon Docker em tempo real.

## 2. Integridade do ZIP

- ZIP aberto com a biblioteca Python `zipfile`. `testzip()` retornou `None`: sem falhas de CRC.
- **15 entradas únicas**, todas sob um único diretório; nenhum caminho absoluto ou contendo `..`.
- `checksums.sha256` contém **14 entradas únicas**, sem caminho inesperado e com SHA-256 válido. Recomputados sobre **os bytes extraídos de cada entrada**, 14/14 coincidem. Inventário de dados é completo.
- Arquivos presentes: `attribute-source-before.jsonl`, `attribute-source-after.jsonl`, `logic-engine-before.jsonl`, `logic-engine-after.jsonl`, `rule-executor-before.jsonl`, `rule-executor-after.jsonl`, `states-before.json`, `states-after.json`, `event-original.json`, `event-conflict.json`, `conflict-response.json`, `request-intent.json`, `manifest.json`, `validation.json` e `checksums.sha256`.
- `states-before.json` e `states-after.json` são **idênticos em bytes**, ambos SHA-256 `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`. Os JSON/JSONL foram analisados sem erros de sintaxe.

## 3. Verificação independente de contrato e causalidade

1. `event-original.json` possui `event_id=v05-dedup-v1:atA:1`, `run_id=v05-dedup-v1`, `entity_id=atA`, `sequence=1`, `value=5`, `request_id=v05-req-atA-1`, `step=1`, `emitted_at=2026-11-15T17:57:08.636308+00:00`.
2. `event-conflict.json` preserva todos esses campos, inclusive ID e timestamp, **alterando exclusivamente `value` de 5 para 6**.
3. `request-intent.json` declara `attempt_count=1`, `automatic_retry=false`, `target=tcc2-v05-logic-engine` e `path=/notifications/attribute`.
4. `conflict-response.json` contém **HTTP 409** e `body.error="event_id reutilizado com payload diferente"`.
5. `validation.json` contém `scenario=C2`, `criterion=V05`, `increment=E08-D17H`, `status=PASS`, `expected_http=409`, `observed_http=409`, `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`.
6. Os estados antes/depois preservam `atA=5`, `atB=0`, sequências `atA=1`, `atB=0`, ledger do avaliador com um ID, `condition=false`, `condition_sequence=0`, `rule-executor.approved=false` e `effects=[]` — sem alteração funcional.
7. Logs do `attribute-source`: **7→7**, idênticos em bytes. Logs do `rule-executor`: **2→2**, idênticos em bytes. Logs do `logic-engine`: **6→7**, seis registros prévios preservados e **exatamente um** novo `mutation` HTTP 409 para o payload conflitante, com corpo de erro correspondente.
8. Os dois registros anteriores `mutation /notifications/attribute` contidos no log inicial do avaliador são coerentes com as etapas anteriores: evento original `value=5` aceito com HTTP 200, `duplicate=false`; reenvio idêntico aceito com HTTP 200, `duplicate=true`. O novo evento `value=6` foi rejeitado com HTTP 409.

**Interpretação:** `new_logic_mutations=1` descreve um registro adicional do logger HTTP, **não** alteração do estado PON. O número de tentativas é informado pelo executor, mas o acréscimo de uma única entrada HTTP no log do avaliador é compatível com uma tentativa no escopo do registro.

## 4. Aceite e limitações

**E08-D17I APROVADO:** integridade do ZIP e dos hashes, resposta 409 esperada, estados binariamente iguais e logs coerentes com a rejeição do conflito de ID no C2. A integridade e as comparações de estado/log não dependem apenas do campo `PASS` emitido pelo executor.

Este laudo não comprova concorrência arbitrária, recuperação após falhas, execução multinó físico, escalabilidade, desempenho ou implantação Kubernetes. V05 ainda requer deduplicação de `ConditionChanged` no `rule-executor`, além da revisão da cobertura final; V06/V07 permanecem pendentes.

## 5. Continuidade

**Próximo E08-D17J:** preflight de estado antes da primeira transição de condição na bancada V05. Conferir `atA=5,atB=0`, `condition=false`, executor sem efeitos, versão de snapshot e IDs. Depois, em incremento próprio, enviar uma mudança nova `atB=1` via `/attributes/change`, que conforme `c1/state.py` deverá produzir a transição de condição aprovada, uma notificação `ConditionChanged` e um efeito. Capturar o payload original da condição antes de qualquer duplicação. **Não repetir o HTTP 409 de E08-D17H**, nem reiniciar contêineres ou alterar o cluster kind.
