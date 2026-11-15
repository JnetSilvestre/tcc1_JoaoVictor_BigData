# Etapa 08 — auditoria direta do ZIP V05: replay de condição (E08-D17N)

**Data da auditoria:** 15/11/2026. **Cenário:** C2 Docker, três contêineres no mesmo host Windows. **Critério:** V05, deduplicação idempotente de `ConditionChanged` em `rule-executor`. **Resultado:** **APROVADO no caso experimental auditado**.

## 1. Proveniência dos arquivos e hashes

| Evidência | Identificação verificável |
|---|---|
| ZIP enviado na conversa | `c2-v05-condition-replay-20261115-162246.zip` |
| Tamanho real | **8.703 bytes** |
| SHA-256 do ZIP (recalculado diretamente) | `0378c162b45bd44b316754023577daec5b41a19583dbef68c0f0d8b6340bfb42` |
| Captura PowerShell principal | `image(20261115-192914).png`, 91.684 bytes, SHA-256 `be019d1eda8515f840822f28d95106ad0207ae8ec09ce2ad9ca02b66ab730e1d` |
| Captura PowerShell final | `image(20261115-192920).png`, 29.822 bytes, SHA-256 `322b901d40a75320b2ec9a2d1d3047e00a3f382412081ce655107b0d313131fa` |
| Diretório original no Windows | `prova-conceito/resultados-locais/c2-v05-condition-replay-20261115-162246` |
| ZIP anterior comparado independentemente | `c2-v05-condition-first-20261115-160357.zip`, SHA-256 `46787fb0ac9d7ae068aa9e13ef3cf3977bfdf84017acd1f61e8868709a52b587` |
| Commit efetivamente executado (print e manifesto) | `a654453c284563ec3324a1c1b3462f759e9d10ec` |
| Imagem declarada no manifesto | `tcc2-pon:c2-e08-dbefcd2cf3d2`, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a` |
| Rede declarada | `tcc2-pon-c2-v05`, `internal=true` |

A auditoria acessou diretamente os **bytes do ZIP e das capturas enviadas**; não inferiu o conteúdo a partir de fotos. Os ZIPs/prints originais permanecem no host do acadêmico e anexados à conversa, **não versionados no GitHub**. IDs de contêineres e horários Docker foram comparados entre manifestos, mas não houve consulta direta ao daemon em tempo real na máquina do acadêmico.

## 2. Integridade do arquivo compactado

1. ZIP aberto com `zipfile.ZipFile`: `testzip() == None` (CRC sem erros).
2. Inventário completo: **14 entradas únicas** sob `c2-v05-condition-replay-20261115-162246`, sem entradas extras. A convenção de caminhos ZIP criada pelo Windows usa separador `\` no nome de cada entrada; extraído o nome-base, não há colisões.
3. `checksums.sha256` contém **13 entradas únicas** válidas, correspondentes exatamente aos 13 arquivos de dados; todos os SHA-256 recalculados sobre os bytes descompactados coincidem (**13/13**).
4. Os arquivos JSON e JSONL foram analisados com parse válido. Condição original SHA-256 `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`; os estados anterior/posterior têm SHA-256 idêntico `2a53df80250bc2b72fd614c20b586108550d84a71f6347baaa3ca0dfb805ae0f`.

## 3. Rastreabilidade exata entre a rodada original e o replay

- `condition-event-original.json` é **idêntico byte a byte** ao registrado em `c2-v05-condition-first-20261115-160357.zip`; contém `event_id=v05-dedup-v1:cn1:1`, `approved=true`, `sequence=1`, `caused_by=v05-dedup-v1:atB:1`, `emitted_at=2026-11-15T19:03:59.142115+00:00`.
- `manifest.json` do replay contém `previous_validation_sha256=8113d4e0f7967697839fbd2ca324c4c48aabb323c26a011db320721b2cc8b577`, **recalculado e confirmado** como SHA-256 de `validation.json` do ZIP original.
- Os IDs completos, horários de inicialização dos três contêineres, ID de imagem e nome da rede nos manifestos **são iguais** entre as duas rodadas.
- `states-before.json` do replay é **idêntico byte a byte** a `states-after.json` da rodada original E08-D17K. `states-after.json` do replay é **idêntico byte a byte** a `states-before.json` do replay.
- Os logs `*-before.jsonl` do replay são **idênticos byte a byte** aos `*-after.jsonl` da rodada original, para cada um dos três serviços.

## 4. Resposta HTTP, estado e logs

- `request-intent.json`: alvo `tcc2-v05-rule-executor`, rota `/notifications/condition`, `event_id=v05-dedup-v1:cn1:1`, `attempt_count=1`, `automatic_retry=false` (declaração do executor).
- `replay-response.json` contém exatamente `{"status":200,"body":{"accepted":true,"duplicate":true}}`.
- `validation.json` contém `scenario=C2`, `criterion=V05`, `increment=E08-D17M`, `status=PASS`, `replay_attempted=true`, `expected_http=200`, `observed_http=200`, `duplicate=true`, `state_unchanged=true`, `new_effects=0`, `new_executor_mutations=1`.
- Estado final: `attribute-source` e `logic-engine` com `atA=5,atB=1`; avaliador com `condition=true`, `condition_sequence=1`, exatamente um evento de condição; executor `approved=true`, `condition_sequence=1`, `received_ids=["v05-dedup-v1:cn1:1"]`, **um único efeito** `v05-dedup-v1:rl1:1`. Antes/depois **inalterados em bytes**.
- Logs: `attribute-source` **10→10** (bytes iguais), `logic-engine` **10→10** (bytes iguais), `rule-executor` **4→5** (quatro registros anteriores como prefixo exato, e um novo `mutation` `/notifications/condition` com payload **igual ao original**, HTTP 200, `accepted=true`, `duplicate=true`). **Nenhum novo registro `effect`**.
- Prints do Windows: `python -m compileall` retornou 0, suíte completa **80/80 OK em 11,065 s**, comando E08-D17M com código de saída 0, contêineres V05 em `Up`; E08-D17N registrou `Relatorio: PASS`, `HASHES INTERNOS: 13/13 OK`, `ZIP OK` para 14 arquivos e `CRC: OK`. Duração de testes **não** constitui benchmark do PON.

## 5. Decisão e pendências científicas

**E08-D17N APROVADO — auditoria independente de integridade e comportamento V05/ConditionChanged.** Com a evidência de E08-D17G (replay de atributo), E08-D17I (conflito de atributo), E08-D17L-R2 (primeira condição) e E08-D17N (replay de condição), os casos V05 efetivamente executados possuem dados verificáveis. A matriz planejada de V05 ainda prevê testar **reutilização de `ConditionChanged.event_id` com payload divergente**, exigindo HTTP 409 sem mudança de estado ou efeito; não marcar essa parte como concluída sem execução.

**Próximo E08-D17O:** preflight somente leitura do estado e dos logs finais da bancada V05 antes de qualquer conflito de `ConditionChanged`. Após aceite, preparar envio único do payload conflitante, conservando `event_id` e `emitted_at` do original e alterando somente um campo válido (por exemplo, `approved=true→false`); exigir HTTP 409 e invariância. **Não repetir o replay E08-D17M ou alterar `atB` outra vez.**

V06 (ordenação/lacunas em bancada separada), revisão de V07, consolidação de evidências e encerramento da Etapa 08 permanecem pendentes. Não se realizou implantação da aplicação em Kubernetes, benchmark ou distribuição entre hosts físicos.
