# TCC2 — Etapa 08: auditoria independente V06 E08-D18G/H

**Data:** 15/11/2026. **Cenário:** C2, Docker, três serviços em contêineres separados de um mesmo host. **Resultado:** APROVADO nos dois casos específicos; não representa teste Kubernetes, multinó, benchmark ou recuperação após falhas.

## Evidências recebidas

- Print original PowerShell: `image(20261115-215030).png` (104.310 bytes), SHA-256 dos bytes recebidos `ae4245ae058afee042619de42f042024fe0aa5bceb21b47f6e6ced53b2364da4`; mostra `Ran 93 tests in 10.966s; OK`, compilação sem erro exibido, dois casos `PASS`, Git final limpo e `E08-D18G/H: EXECUCAO CONCLUIDA`. **10,966 s é duração da regressão, não benchmark do PON**.
- Arquivo bruto: `c2-v06-batch-20261115-184915.zip`, 13.566 bytes; SHA-256 calculado independentemente sobre os bytes recebidos: `24ff2fbc4aa28acfec0bad90c3677301cfadbce7efea51c9368b6e50953c1be1`, idêntico ao print. `zipfile.testzip()` sem erro; 27/27 entradas distintas; `checksums.sha256` contempla todos os outros 26 arquivos, com 26/26 SHA-256 recalculados idênticos.
- `manifest.json`: branch usada `tcc2/desenvolvimento`, commit executado `2ea999a712032b2bf295362264e6a5a204b9986f`, imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`, image ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, revisão OCI `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`, rede `tcc2-pon-c2-v06` interna (`bridge` registrada previamente) e os mesmos três container IDs reportados nos aceites anteriores, todos com `restart_count=0` no momento da coleta.
- O código do executor faz o preflight contra a evidência auditada de E08-D18F, verifica estados/logs, cria intent antes de cada POST, sem retry, e interrompe ao primeiro erro. O ZIP comprova registro `attempt_count=1` e `automatic_retry=false` para cada novo caso; não prova ausência universal de retransmissão externa fora do escopo da rodada.

## Auditoria semântica dos casos

| Caso | Payload e receptor | Resposta observada | Invariância |
|---|---|---|---|
| **E08-D18G** | `AttributeChanged` `run_id=v06-other-run`, `sequence=1`, `event_id=v06-other-run:atA:1` ao `logic-engine` | HTTP **409**, `{"error":"run_id divergente"}` | `states-before.json` = `states-after.json` byte a byte; somente 1 log HTTP `mutation` novo no avaliador |
| **E08-D18H** | `ConditionChanged` `run_id=v06-order-v1`, `sequence=2`, `event_id=v06-order-v1:cn1:2` ao `rule-executor` | HTTP **409**, `{"error":"evento atrasado ou lacuna de sequence"}` | `states-before.json` = `states-after.json` byte a byte; somente 1 log HTTP `mutation` novo no executor |

Logs globais entre preflight e término: `attribute-source` **4→4**, `logic-engine` **5→6**, `rule-executor` **2→3**, preservando rigorosamente os prefixos anteriores. Ambos os novos registros exibem rota, payload e resposta coincidentes com o caso. A transição entre G e H não acrescentou estado funcional. Estados globais antes/depois byte-idênticos: os três serviços continuam `ready=true`, `run_id=v06-order-v1`, `snapshot_version=v06-order-v1:snapshot:0`; atributos `atA=atB=0`, sequências de atributo/condição 0, `condition=false`, `approved=false`, `effects=[]` e ausência de fault.

`validation.json`: `status=PASS`, `cases_planned=2`, `cases_completed=2`, `automatic_retry=false`. O arquivo comprova o resultado gerado pelo executor; a auditoria acima cruzou independentemente a resposta, o estado e os logs originais do ZIP.

## Decisão acadêmica

**E08-D18G/H aprovados. V06 concluído no conjunto de casos serializados previsto (snapshot, lacuna de atributo, `run_id` divergente, lacuna de condição).** Não executar novamente os POSTs nem reinicializar V06. E08-D18F-R1 já fora auditado em separado (6.807 bytes, SHA-256 `4a92b7e6307e46161c6a5cf818a7ffdf7a241ba69be24fe0ef126a82655e77da`). Não confundir as respostas 409 deliberadamente esperadas com falha de execução.

**Limites:** V07 no C2 comprova apenas o snapshot inicial/coerência, não uma corrida HTTP de alterações durante a inicialização da mesma bancada; o ensaio C1 cobriu caso limitado com ACK retido. O plano científico original exige também C3, portanto V07 global permanece **parcial** e requer avaliação no Kubernetes. V08/V09/V10/V12 não foram aprovados aqui. Nenhuma distribuição física em múltiplos nós, persistência, recuperação nem desempenho experimental é inferível.

Arquivos brutos originais anexados à conversa do acadêmico, não commitados em binário no repositório.