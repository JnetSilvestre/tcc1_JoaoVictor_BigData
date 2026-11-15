# TCC2 — Etapa 08: auditoria independente de conflito de condição (E08-D17Q)

**Data:** 15/11/2026  
**Cenário:** C2, três processos Python em contêineres Docker separados, mesmo host Windows, rede Docker `bridge` interna `tcc2-pon-c2-v05`  
**Critério:** V05 — rejeitar `ConditionChanged` com mesmo `event_id` e payload divergente, sem efeito adicional  
**Decisão:** **E08-D17P aprovado experimentalmente no Windows e E08-D17Q aprovado por auditoria independente das evidências. V05 concluído nos casos planejados e executados.**

## 1. Origem das evidências

- Arquivo ZIP disponibilizado na conversa: `c2-v05-condition-conflict-20261115-171101.zip`, **9.296 bytes**.
- SHA-256 calculado diretamente sobre os bytes recebidos: `2c9b1dc47cb59a8d403dc8ad8c3cd9c12a967f6ac6dfe10f0f753ad0662d3640`. Igual ao valor mostrado no print do PowerShell.
- Captura PowerShell recebida: `image(20261115-202708).png`, **93.002 bytes**, SHA-256 `00462f5ea25bf6025f0c1cf0ed6e124b58c12488ee21fdd270758ecf759bc323` (calculado sobre a imagem).
- Pasta original no Windows: `prova-conceito/resultados-locais/c2-v05-condition-conflict-20261115-171101`.
- HEAD do código executado no Windows e registrado em `manifest.json`: `0b647d64b1f8a66d6b5f1cb01f3692ebfc2f7286`, branch `tcc2/desenvolvimento`.
- Imagem declarada em `manifest.json`: `tcc2-pon:c2-e08-dbefcd2cf3d2`, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, revisão `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Os ZIPs e PNGs originais estão na conversa/host, **não** versionados como arquivos binários no GitHub. Os comandos Docker e a regressão foram realizados pelo acadêmico no Windows; a auditoria binária a seguir foi executada independentemente sobre os ZIPs recebidos, não no daemon Docker do acadêmico.

## 2. Inventário, CRC e hashes

- ZIP: **15 arquivos distintos**, nenhum extra, com prefixo de diretório esperado; `zipfile.testzip() == None` (CRC válido).
- `checksums.sha256`: **14 entradas únicas**, correspondentes aos 14 arquivos de dados; **14/14** SHA-256 recalculados sobre os bytes descompactados e conferidos.
- `validation.json`: `scenario=C2`, `criterion=V05`, `increment=E08-D17P`, `status=PASS`, `attempted=true`, `expected_http=409`, `observed_http=409`, `state_unchanged=true`, `new_effects=0`, `new_executor_mutations=1`.
- `conflict-response.json`: `{"status":409,"body":{"error":"event_id reutilizado com payload diferente"}}`.
- Print: `compileall` código 0, **88/88 testes OK** em 11,246 s (duração da suíte, **não** benchmark), E08-D17P código 0, Git limpo. Print E08-D17Q exibiu **15/15**, **14/14**, ZIP/CRC OK, sem erros.

## 3. Cadeia de evidências entre rodadas

Auditoria cruzada dos três ZIPs anexados à conversa: primeira `ConditionChanged` (`c2-v05-condition-first-20261115-160357.zip`), replay idêntico (`c2-v05-condition-replay-20261115-162246.zip`) e conflito (`c2-v05-condition-conflict-20261115-171101.zip`).

1. `event-original.json` do conflito é **idêntico byte a byte** ao `condition-event-original.json` dos ZIPs da primeira condição e do replay; SHA-256 `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`.
2. `event-conflict.json` conserva `event_id=v05-dedup-v1:cn1:1`, `run_id`, `emitted_at=2026-11-15T19:03:59.142115+00:00`, `sequence=1`, `caused_by` e demais campos; **única alteração**: `approved=true` → `false`.
3. `manifest.previous_validation_sha256=1622d82df4302b27b06c53312e3e3d3965ea559b9804ac23c873abb0dc89c4ee` confere com o SHA-256 recalculado de `validation.json` do replay. `original_condition_sha256` confere com os bytes reais do evento original.
4. `states-before.json` do conflito é **idêntico byte a byte** a `states-after.json` e `states-before.json` da rodada de replay. Os três logs pré-conflito são **idênticos byte a byte** aos logs finais da rodada de replay.
5. Entre os manifestos de replay e conflito coincidem rede, `internal=true`, nome/tag/ID/revisão da imagem, os três IDs completos e horários de início dos contêineres. Assim, os arquivos indicam continuidade da mesma bancada V05.

## 4. Comportamento funcional verificado nos bytes

- Estados `states-before.json` e `states-after.json` do conflito: **idênticos byte a byte**; SHA-256 `2a53df80250bc2b72fd614c20b586108550d84a71f6347baaa3ca0dfb805ae0f`.
- `attribute-source`: 10 → 10 registros nos logs, sem alterações de bytes.
- `logic-engine`: 10 → 10 registros nos logs, sem alterações de bytes.
- `rule-executor`: 5 → 6 registros; os cinco registros anteriores são prefixo exato dos posteriores, e o registro adicional é `mutation`, `/notifications/condition`, payload exatamente igual ao `event-conflict.json`, HTTP **409**, resposta de erro esperada.
- Estado final mantido: `atA=5,atB=1`, condição verdadeira, sequência de condição 1; `rule-executor.approved=true`, `received_ids=["v05-dedup-v1:cn1:1"]`, **exatamente um efeito antigo**, `v05-dedup-v1:rl1:1`, e **nenhum novo efeito**.
- `request-intent.json` declara um único POST ao executor, `attempt_count=1`, `automatic_retry=false`. O registro único de HTTP conflitante é consistente com esse protocolo; não prova ausência de tentativas fora dos logs coletados.

## 5. Encerramento limitado e continuidade

**V05 aprovado nos casos previstos na matriz de ensaio:** duplicação exata de atributo (HTTP 200 sem novo efeito), conflito de atributo (HTTP 409), transição inicial para condição verdadeira com um efeito, duplicação exata de condição (HTTP 200 sem novo efeito), conflito de condição (HTTP 409 sem novo efeito); os ZIPs correspondentes foram auditados anteriormente e/ou nesta rodada. A aprovação se limita ao cenário determinístico, serial, na rede Docker interna de **um único host físico**; não demonstra exatamente-uma-vez em falhas de rede, concorrência arbitrária, tolerância a falhas, distribuição física ou Kubernetes.

**E08-D17Q aprovado**. **Próximo incremento: E08-D18A (V06)**: diagnóstico somente leitura de conflitos com contêineres/redes V05/V03/C2 e do digest da imagem; confirmar critérios V06 na Etapa 05; planejar rede interna **separada** `tcc2-pon-c2-v06`, e, após aceite do diagnóstico, criar 3 contêineres frescos `tcc2-v06-*` para testes de lacunas/ordenação. Não reutilizar a bancada V05 já consumida; não executar Kubernetes antes das Etapas 09/10. Revisão V07 e encerramento documental da Etapa 08 permanecem pendentes.
