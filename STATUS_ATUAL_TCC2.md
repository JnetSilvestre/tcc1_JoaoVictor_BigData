# STATUS ATUAL — TCC2

Atualizado em: 2026-11-15

## Leitura rápida — última situação verificada

- **E08-D18B/C/D/E APROVADOS (15/11/2026):** prints reais Windows confirmaram criação da bancada V06 (`bridge/internal=true`, 3 contêineres, mesma imagem, V05 preservado), estado frio + DNS/GET internos 200, e snapshot único `v06-order-v1` HTTP 200, 3/3 `ready=true`, 0 efeitos e 88/88 testes automatizados. Auditoria independente do ZIP `c2-v06-snapshot-20261115-180612.zip`: **5.896 bytes**, SHA-256 `544e9fe8eb12878268393db5eeddaa698a9c02cee5c19080f56cb490a2c21987`, 13/13 arquivos íntegros, 12/12 SHA-256 internos, CRC OK; estados frios→prontos e logs fonte/avaliador 1→4, executor 1→2. Laudo: `docs/tcc2/etapa-08-auditoria-v06-snapshot.md`. **Próximo E08-D18F: teste único de lacuna `AttributeChanged` seq=2 antes de 1, HTTP 409 esperado, sem retry nem modificação funcional. V06 e V07 ainda pendentes.**

- **E08-D18A APROVADO (15/11/2026):** print PowerShell `image(20261115-203614).png` confirma `tcc2/desenvolvimento` limpa em `1364bda7623467934dd897f016fe038dc0b75956`, Docker `desktop-linux` Linux/x86-64, imagem OCI/ID/revisão C2 corretas, rede e 3 nomes V06 disponíveis, três contêineres V05 Running=true. Nenhuma criação nem evento HTTP. **Próximo E08-D18B: criar rede bridge interna V06 e 3 contêineres novos (apenas infraestrutura); V06 funcional e V07 pendentes.**

- **E08-D17P e E08-D17Q aprovados em 15/11/2026 (V05 encerrado nos casos previstos):** execução Windows do conflito de `ConditionChanged` no HEAD `0b647d64b1f8a66d6b5f1cb01f3692ebfc2f7286` com compilação 0, 88/88 testes OK (11,246 s), HTTP 409, estado inalterado, zero efeitos novos, executor 5→6 registros e Git limpo. Auditoria direta do ZIP `c2-v05-condition-conflict-20261115-171101.zip`: **9.296 bytes**, SHA-256 `2c9b1dc47cb59a8d403dc8ad8c3cd9c12a967f6ac6dfe10f0f753ad0662d3640`, CRC OK, **15/15 arquivos, 14/14 hashes internos**, evento original idêntico às duas rodadas anteriores, somente `approved:true→false`, estados byte a byte iguais, logs fonte/avaliador 10→10 e executor 5→6, continuidade de IDs dos 3 contêineres, imagem e rede. Laudo `docs/tcc2/etapa-08-auditoria-v05-conflito-condicao.md`. Próximo **E08-D18A: diagnóstico V06 somente leitura**, em bancada separada. V07 e encerramento Etapa 08 ainda pendentes; sem Kubernetes, benchmark ou distribuição física.

- **Etapa 07 concluída funcionalmente em C0/C1:** 39 testes reais aprovados no Windows, V01–V07 nos casos ensaiados; código testado em `be6b850d599504e9ea8166f02fd87b35313e5445`. O ZIP V07 foi auditado diretamente (12/12 hashes internos, 20/20 checagens).
- **Etapa 08 aberta em 13/11/2026:** E08-D01/D02 comprovam branch limpa e Docker/WSL2 operacionais; E08-D03 comprova atualização fast-forward ao HEAD `3dadef829846fdf5f0bcf0c47c956b44eb89d821`, compilação 0 e 39/39 testes OK em 10,813 s na máquina do acadêmico. Capturas e SHA-256 em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I01 e E08-I02 aprovados no Windows (E08-D04):** commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, `compileall=0`, 42/42 testes OK em 11,564 s (duração da suíte, não benchmark), `Testes: 0` e Git limpo. Capturas/hashes em `docs/tcc2/etapa-08-diagnostico-rede.md`; os testes de DNS usam mocks, não rede Docker.
- **E08-D05 aprovado no Windows:** `python:3.13-slim` Linux/amd64, Python 3.13.18 executado com `--network none`; digest exato `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`, Git limpo e kind preservado. Print e SHA-256 registrados em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I03 concluído no Windows (E08-D08, 13/11/2026):** no commit `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`, resolução do manifesto `linux/amd64` corrigido (`Registro: 0`), build (`Build: 0`), imports (`Imports: 0`) e CLI (`CLI: 0`) aprovados; imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`, Python 3.13.18, UID 10001, Git limpo. Dois PNGs originais e hashes SHA-256 registrados em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I04 e E08-D10 aprovados no Windows:** três contêineres independentes em rede interna `tcc2-pon-c2`, HTTP e snapshot inicial propagados corretamente; evidências em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-D11 aprovado na execução Windows (13/11/2026):** HEAD do código de ensaio `5eee8e7a7c931491d3668cc9472a46191de6180c`; compilação 0; 45/45 testes aprovados em 11,028 s (duração da suíte); `python -m c2.runner` retornou 0 com `validation.json` exibindo `PASS` e 11 verificações `true`. Dois efeitos nos passos 3 e 7, comparações exibidas `matches_manual`, `matches_oracle`, `matches_c0` = true. Pasta local de evidência `prova-conceito/resultados-locais/c2-20261113-182248`. Três capturas/hashes no diagnóstico. **Não verificado ainda de forma independente:** os bytes dos 13 artefatos cobertos por `checksums.sha256`.
- **E08-D12 APROVADO por auditoria independente do ZIP (15/11/2026):** `c2-20261113-182248.zip` (7.417 bytes, SHA-256 `e90a3b1741b6b68d89ca0ea3fecb1583ab869e8cdfca0938db8bceeb8567de6e`), 14/14 arquivos válidos, 13/13 SHA-256 internos conferidos, 11/11 checks do relatório verdadeiros; análise independente de 7 chamadas, 5 notificações de atributo, 3 de condição, 2 efeitos nos passos 3/7, mesmos efeitos de C0/fixture/oráculo e estados finais coerentes. Os originais foram recebidos na conversa, **ZIP não versionado** no GitHub. Detalhes em `docs/tcc2/etapa-08-auditoria-zip.md`.
- **E08-D13 aprovado como diagnóstico no Windows (15/11/2026):** HEAD `f6e087f974d1359b63606077ce538c4542d5dcc4`, bridge interna `tcc2-pon-c2`, mesmos três IDs de contêiner, `Running=true`, `StartedAt` em 15/11/2026 14:16 UTC, `RestartCount=0`; `GET /state` exibiu `ready=false`, `run_id=null` e estados em memória zerados. Causa da nova inicialização **não determinada**; **não é ensaio formal F1/V10**. Captura/hash em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-D14A aprovado no Windows:** bancada V03 separada e fria em `tcc2-pon-c2-v03`. **E08-D14B-R1 bloqueado no preflight (15/11/2026):** compilação 0, 45/45 testes OK em 11,039 s; runner retornou `V03: 1`, `FAIL`, `cases_completed=0`, `error=atributos alterados: logic-engine`. A causa foi uma expectativa errada do runner (LogicEngine frio tem `attributes=null`, `condition=null`), não uma falha HTTP comprovada. Correção somente no executor `c2/v03_cold.py` e cinco testes unitários novos em `tests/test_c2_v03_cold.py` publicados e **validados na rodada R2**. Capturas/hash no diagnóstico. V05/V06/V07, Kubernetes e desempenho pendentes.
- **E08-D14B-R2 aprovado pela saída real do Windows (15/11/2026):** HEAD `66dfef80d7c9bf17e4343d6087c8d51e397ae523`, compilação 0, **50/50 testes OK**, runner V03 frio `PASS`, `cases_completed=10/10`, `V03: 0`; evidências em `prova-conceito/resultados-locais/c2-v03-r2-20261115-140543`. Print dos casos mostrou apenas cabeçalho da tabela; relatório do runner comprova execução/checagens, mas **os bytes de `http-cases.json` e seus hashes não foram auditados independentemente**. Próximo E08-D15: exibir dez linhas por leitura direta do JSON, verificar integridade e enviar ZIP. Nenhuma alteração no runtime; sem V03 inicializado, V05/V06/V07, Kubernetes ou benchmark.
- **E08-D15 aprovado por leitura direta no Windows (15/11/2026):** `http-cases.json` exibiu `TOTAL: 10`, S01–S10 com HTTP observado=esperado (422/400/415/404) e `state_unchanged=True` em todos; leitura finalizada sem erro. SHA-256 do arquivo **exibido no PowerShell** `95cd9cc95a4dd03bd83113cd6380f4897bb64fd989bc2850791190389a050113`; PNG da captura com SHA-256 `d098d72e6da1d1a99c490d41dd25c14f2fe016403fe98475a99af5ad1db1a62e`. **Pendente auditoria dos bytes dos nove artefatos V03:** próximo E08-D16, conferir 8 hashes internos, empacotar ZIP e enviar para auditoria. Os 10 POSTs não devem ser reenviados.

- **E08-D16 concluído e auditado diretamente (15/11/2026):** após R1 (erro PowerShell ao ler array JSON) e R2 (erro de aspas em `python -c`), R3 criou ZIP V03 com 9 arquivos e 9 hashes dos conteúdos do arquivo compactado conferidos contra origem. Original enviado: `c2-v03-r2-20261115-140543.zip`, **4.489 bytes**, SHA-256 `718213c176dbb7dbf7982f9615d5f31b5955739b992edb8e1326cdac4749ab9c`; **CRC OK, 9/9 arquivos e 8/8 hashes internos válidos**, `http-cases.json` 10/10 status esperados, estados inicial/final idênticos, 9 requisições rejeitadas reproduzidas em logs e 404 final no transcript. Laudo independente em `docs/tcc2/etapa-08-auditoria-v03.md`; ZIP original permanece na conversa e no host, não foi versionado como binário. **Aprovado V03 frio nos dez casos; ainda não V03 com snapshot, V05/V06/V07 completos, benchmarks ou Kubernetes.**

- **E08-D17 (15/11/2026):** planejamento V05/V06 conferido com o protocolo Etapa 05 e contratos do código em `docs/tcc2/etapa-08-v05-v06-plano.md`. **E08-D17A e D17B aprovados na saída real do Windows (15/11/2026):** rede isolada `tcc2-pon-c2-v05` com 3 contêineres de IDs distintos, bridge `Internal=true`, mesma imagem aprovada e logs `listening`; `/health/live` retornou `live=true` nos três; `/state` apresentou estado frio em todos (`ready=false`, `run_id=null`, atributos iniciais coerentes, nenhuma notificação nem efeito). Captura E08-D17B `image(20261115-174707).png`, SHA-256 `514ec8a34b30ec28d4afb95c65908b548ac559e124144c0e6a7b2fbfac9b3582` (93.598 bytes); captura original apenas na conversa. **E08-D17C aprovado pela execução Windows (15/11/2026):** HEAD `5800839e1ff7589b188d925541824fb53a558e2a`, três preflights OK, `POST /init/snapshot` HTTP 200 (`duplicate=false`), versão `v05-dedup-v1:snapshot:0`, três estados `ready=true`, `run_id=v05-dedup-v1`, atributos/sequências zerados, condição e aprovação `false`, efeitos vazios; logs comprovam envio/ACK do snapshot source→logic→executor. Captura `image(20261115-175306).png` (142.516 bytes), SHA-256 `3b03035b4e1fa64c24750f9de658aa06ef67b76693a5430d58d1dce91fa92e0c`. **Próximo E08-D17D:** enviar uma única alteração válida `atA=5` e preservar evento original para posterior reenvio idempotente. Deduplicação V05 ainda não testada. V06 terá bancada própria. **Nenhuma execução V05/V06 realizada ainda, sem Kubernetes ou benchmark.**

- **E08-D17D aprovado com evidência real Windows (15/11/2026):** HEAD `7f6294431a97a49388518e817cf153b9edfee73f`, 3 preflights antes OK, único `POST /attributes/change` para `atA=5` retornou HTTP 200, `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atA:1`, `sequence=1`; estados depois OK: fonte e avaliador `atA=5,atB=0`, sequências `atA=1,atB=0`, ledger do avaliador contém um ID, `condition=false`, executor sem efeitos. Logs mostram envio, ACK `accepted=true,duplicate=false` e recebimento HTTP 200. Git final limpo. Screenshot `image(20261115-175816).png`, 166635 bytes, SHA-256 `a22f086a610d52e024a97fce1c8ec107036f882a403db7072b5037bf269f71c1`, arquivo original somente na conversa. **Próximo E08-D17E:** capturar, por somente leitura, o payload original completo `send /notifications/attribute` (sem recriar `emitted_at`), para reenvio idempotente no passo seguinte. **V05 deduplicação ainda não demonstrada**.
- **E08-D17E aprovado pela saída real do Windows (15/11/2026):** evento original `v05-dedup-v1:atA:1` capturado dos logs; envio/ACK/recebimento únicos e payloads idênticos, sem efeitos; arquivos em `resultados-locais/c2-v05-original-20261115-150412` com 5 SHA-256 internos. Print `image(20261115-180441).png`, SHA-256 `88eceb148d582b57a27f37a72113a4c2c0d1dde76ce95a7c4fa64d6d7d2e1141`. **E08-D17F apenas preparado:** script de replay único e 7 testes unitários publicados, ainda não executados no Windows. V05 duplicação ainda não comprovada.

- **E08-D17F aprovado pela saída real Windows (15/11/2026):** Git `cb212667616b5e94128b1337f7a12b6d499891e8`, compilação 0, **57 testes OK**, reenvio único HTTP 200 `accepted=true,duplicate=true`, V05 PASS e código 0, estados idênticos, 0 efeitos; pasta local `resultados-locais/c2-v05-duplicate-20261115-151112` com 13 arquivos de dados mais checksum. Capturas `image(20261115-181207).png` SHA `076be5e983dd8327a73b0afea7eba77725a602bc824e0a39e589d87d6c254938` e `image(20261115-181217).png` SHA `d318ab4b2ccde10908c44327ca4d7d12ec390ba9e8d526493e82f929e8cb898e`. **Próximo E08-D17G:** arquivar e auditar ZIP por bytes, sem repetir POST. V05 completo (conflito e duplicata de condição) e V06 ainda pendentes.

- **E08-D17G auditado independentemente (15/11/2026):** ZIP `c2-v05-duplicate-20261115-151112.zip`, 7163 bytes, SHA-256 `532281718862cc28bd17654721b6d01d0a78d8d9cc9c7283730e8c943b9ca3cb` recalculado; 14/14 arquivos ZIP/CRC, 13/13 SHA-256 internos corretos; resposta HTTP 200 `accepted=true,duplicate=true`; estados antes/depois idênticos; logs fonte 7→7, avaliador 5→6 (um registro HTTP duplicado), executor 2→2, sem efeito novo. Captura Windows SHA-256 `fca5defd9745c52a91604034e8938be44401a645dbf0b190c0eac5c604d5fdcc`. Relatório `docs/tcc2/etapa-08-auditoria-v05-atributo.md`. **Aceite restrito a um replay idêntico de AttributeChanged; V05 completo, V06 e V07 ainda pendentes.** Próximo E08-D17H: conflito `event_id` com payload divergente (esperado HTTP 409).

- **E08-D17H preparado, não executado:** script `prova-conceito/c2/v05_conflict.py` implementa preflight dos hashes da captura E17E e rodada D17F, estados/logs e rede, altera unicamente `value` de 5 para 6 no mesmo `event_id` e envia **uma tentativa** esperando HTTP 409 sem mutação. Testes de preparação em `tests/test_c2_v05_conflict.py` (7 testes novos) **ainda não executados no Windows**. Não reconstruir imagem, não repetir replay antigo e interromper após eventual erro para preservar logs.

- **E08-D17H aprovado operacionalmente no Windows (15/11/2026):** Git HEAD `5787a095045d37d24b2b141070823676277d90f0`, compilação 0, 64/64 testes aprovados (11,012 s), ensaio V05 de `event_id` conflitante status `PASS`, tentativa única, HTTP esperado/observado 409, mensagem `event_id reutilizado com payload diferente`, `state_unchanged=true`, `new_effects=0`, `new_logic_mutations=1` (registro HTTP, sem mutação funcional), código de saída 0; Git final limpo. Evidências locais `resultados-locais/c2-v05-conflict-20261115-154229`. Screenshots: `image(20261115-184410).png` 94191 bytes SHA-256 `2b1a2ada040bede5e617cd081fe1e98bfff72be05cc2848f190df1b863066c5b`, e `image(20261115-184423).png` 76959 bytes SHA-256 `b558ed6efcfc82dc685a7417634cdc0825701330816ab2f9071d32bb7bd7e727` (hash dos originais recebidos). **Ainda não há auditoria independente dos bytes da pasta/ZIP.** Próximo E08-D17I: validar 14 SHA-256 internos e arquivar em ZIP 15 arquivos, sem reenviar requisição, aguardando upload para auditoria.

- **E08-D17I auditado independentemente (15/11/2026):** ZIP `c2-v05-conflict-20261115-154229.zip` de **7.683 bytes**, SHA-256 `4aef50d86c83feceb8c007dfa959e82a5e57a9ced23df2ef827a7d39839f327b`, CRC sem erros, **15/15 arquivos íntegros e 14/14 hashes internos corretos**. JSON de conflito alterou exclusivamente `value:5→6` com mesmo `event_id`; resposta HTTP 409 conforme contrato; `states-before.json` e `states-after.json` iguais em bytes (SHA-256 `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`); logs fonte 7→7, avaliador 6→7 (um 409), executor 2→2; 0 efeitos novos. Captura `image(20261115-184927).png`, SHA-256 `379d4257acef5be2875696e1ce6512085bba5017c5d7e379fc73765db33c91de`. Laudo `docs/tcc2/etapa-08-auditoria-v05-conflito.md`. **V05 ainda parcial**: falta duplicação de ConditionChanged; próximo E08-D17J é preflight somente leitura para primeira transição. V06/V07 e Kubernetes pendentes.

- **E08-D17J preflight aprovado pela saída Windows (15/11/2026):** três serviços V05 LIVE e STATE OK, atributo `atA=5,atB=0`, condição falsa, executor sem efeitos, rede bridge interna, Git limpo no HEAD `7e4069c0df5f93ab4313d4968e65375c72ef40b6`. Captura `image(20261115-185446).png` SHA-256 `198375f957fb03bbcae26e36ae32310e91abba0d8e18dc67eed1f215599c7c96`. **E08-D17K preparado** com executor de emissão única `atB=1` e 8 testes novos; execução real pendente.

- **E08-D17K aprovado operacionalmente (15/11/2026):** no HEAD `ba200b85bfe24f81b15a3f1ec838480a6cc10e49`, compilação 0, **72 testes OK em 10,837 s**, HTTP 200 `atB=1`, `ConditionChanged` `v05-dedup-v1:cn1:1` aprovado, `condition_sequence=1`, um efeito `v05-dedup-v1:rl1:1`, V05 código 0 e Git limpo. Evidências locais `resultados-locais/c2-v05-condition-first-20261115-160357` e três prints SHA-256 no checkpoint. Integridade binária **ainda pendente** de ZIP/auditoria E08-D17L. Não repetir POST. Próximo: arquivamento somente leitura e posterior replay exato de ConditionChanged.

- **E08-D17L-R2 auditado independentemente (15/11/2026):** ZIP `c2-v05-condition-first-20261115-160357.zip` 8840 bytes SHA-256 `46787fb0ac9d7ae068aa9e13ef3cf3977bfdf84017acd1f61e8868709a52b587` e captura SHA `e4c148bfe59c029e23e780151069469b3a1180ed2ba3c4f6b4b3f68340b567c8`; 15/15 entradas CRC OK, 14/14 SHA-256 internos corretos. Hash verdadeiro da condição original `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54` (primeira tentativa E08-D17L falhou devido a 1 caractere transcrito errado; R1 verificou `Real=Manifesto: True` e R2 arquivou sem modificar dados). Logs fonte 7→10, avaliador 7→10, executor 2→4; cadeia `atB:1→cn1:1→rl1:1` auditada com 1 efeito. Laudo `docs/tcc2/etapa-08-auditoria-v05-condicao-inicial.md`. Próximo E08-D17M: reenvio idêntico de ConditionChanged, não repetir atB=1.

- **E08-D17M preparado (ainda não executado):** `c2/v05_condition_replay.py` e 8 testes unitários novos para reenvio de `v05-dedup-v1:cn1:1` ao executor. Preflight exige hashes, topologia, estado/logs exatamente como fim de E08-D17K; único POST sem retry, estado imutável e nenhum efeito adicional. Esperados **80 testes** após executar regressão no Windows. Referência do evento `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`. Não executar uma segunda vez em caso de erro.

- **E08-D17M aprovado operacionalmente (15/11/2026):** no HEAD `a654453c284563ec3324a1c1b3462f759e9d10ec`, compilação 0, **80/80 testes OK em 11,065 s**, replay da `ConditionChanged v05-dedup-v1:cn1:1`: HTTP 200, `accepted=true`, `duplicate=true`, `state_unchanged=true`, `new_effects=0`, `new_executor_mutations=1`, código V05=0, três contêineres V05 Up e Git limpo. Evidências locais `resultados-locais/c2-v05-condition-replay-20261115-162246`; integridade binária pendente E08-D17N (ZIP/13 hashes/CRC). Não repetir POST. Checkpoint atualizado.

- **E08-D17N auditado diretamente (15/11/2026):** ZIP `c2-v05-condition-replay-20261115-162246.zip`, 8703 bytes, SHA-256 `0378c162b45bd44b316754023577daec5b41a19583dbef68c0f0d8b6340bfb42`, 14/14 arquivos, CRC OK, 13/13 hashes internos corretos. Payload `ConditionChanged v05-dedup-v1:cn1:1` idêntico ao original; estado antes/depois igual em bytes (SHA `2a53df80250bc2b72fd614c20b586108550d84a71f6347baaa3ca0dfb805ae0f`), logs source/logic 10→10, executor 4→5 com HTTP 200 `accepted=true,duplicate=true`, zero efeitos novos, 1 efeito total. **V05/ConditionChanged replay aprovado por auditoria independente**. Laudo `docs/tcc2/etapa-08-auditoria-v05-condicao-replay.md`. V05 ainda requer conflito de `ConditionChanged`; V06/V07 e encerramento pendentes. Próximo E08-D17O: preflight somente leitura, sem POST.

- **E08-D17O-R1 aprovado (15/11/2026):** corrigido erro do inventário anterior (D17K 14 arquivos de dados versus D17M 13); print confirma 13/13 hashes, topologia 3/3, estados 3/3, logs 10/10/5, 1 efeito, sem POST, Git limpo. **E08-D17P preparado, ainda não executado:** conflito do mesmo ConditionChanged com \`approved=false\` e \`event_id\` original; esperar HTTP 409, estado invariável e zero novos efeitos. 8 testes adicionados; esperado 88 testes no Windows, sem execução confirmada nesta revisão. Não repetir POST automaticamente.

- Branch permanente: `tcc2/desenvolvimento`; preservar `master` e a referência original `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.

## Etapas
- Etapa 02: concluída, conforme informação do acadêmico.
- Etapa 03: concluída; referência `2eb080b93a38db47ea1149bb660a5379c6478bd4`.
- Etapa 04: concluída como **especificação arquitetural**; nenhuma implementação distribuída comprovada.
- Etapa 05: **protocolo experimental e esqueleto LaTeX documentados**; sem execução de testes.
- Etapa 06: **infraestrutura básica concluída e validada em ambiente local**; limitações e dependências restantes documentadas.
- Etapa 07: **concluída funcionalmente em C0/C1** em 12/11/2026; evidências e limitações documentadas no encerramento e na auditoria do ZIP.

## Repositórios e branches
- Monografia: `JnetSilvestre/tcc1_JoaoVictor_BigData`.
- Branch permanente de trabalho: `tcc2/desenvolvimento`; **não modificar master**.
- Marco histórico: `tcc2/etapa-03-fundamentacao`.
- Código-base experimental: `JnetSilvestre/codigoPon`, `main`, commit de referência `c2d525b5c675820806af34348e259bff32a6bc5f` (não modificado nesta etapa).

## Entregáveis concluídos
- `docs/tcc2/etapa-04-arquitetura-distribuida.md`: três serviços propostos, contratos HTTP/JSON, estado, riscos e V01–V12.
- `capitulos/cap-proposta.tex`: texto e figura conceitual do TCC1 preservados; proposta Python acrescentada na Etapa 04.
- `docs/tcc2/etapa-05-protocolo-experimental.md`: cenários C0–C5 e F1, entradas/saídas, oráculo, matriz V01–V12, métricas, coleta, aceitação, evidências, procedimento reprodutível e rastreabilidade.
- `capitulos/cap-metodologia-tcc2.tex`: esqueleto não incluído em `main.tex`, a consolidar na Etapa 13.

## Decisões metodológicas
- Objetivos aprovados do TCC1 inalterados; prioridade à viabilidade técnica e correção funcional, sem exigir ganho de desempenho.
- C0 (processo único), C1 (três processos), C2 (Docker), C3 (Kubernetes) compõem validação nuclear; C4 (multinó), C5 (carga) e F1 (reinício) condicionais.
- Arquitetura proposta: `attribute-source`, `logic-engine`, `rule-executor`; 1 réplica por serviço, HTTP/JSON.
- Entrada determinística e oráculo local; comparar ordem, multiplicidade e causalidade dos efeitos. Separar resultado esperado de medição real.
- Modelo arquitetural 1: figura preliminar do TCC1, preservada e identificada como hipótese; modelo 2: diagrama de três serviços especificado na Etapa 04. **Figura definitiva somente depois da implementação e validação, com inserção LaTeX na Etapa 13**.
- Nenhum dado quantitativo criado como resultado experimental; carga, repetição e instrumentos ainda serão ajustados à infraestrutura real.

## Arquivos e commits da Etapa 05
- `docs/tcc2/etapa-05-protocolo-experimental.md`: `ceabba2496cfb5f2460459f6d8676385842f114f`.
- `capitulos/cap-metodologia-tcc2.tex`: `898ca18d31161a6016c3fb92cc260cb8712c1915`.
- Este arquivo atualizado no commit de encerramento da Etapa 05.

## Evidências e validações
- Consulta por conector GitHub à branch `tcc2/desenvolvimento` e leitura do status, da arquitetura da Etapa 04 e de `capitulos/cap-proposta.tex`.
- Commits documentais na branch de desenvolvimento, sem alterar o código experimental.
- **Não executados:** testes Python, Docker, Kubernetes, medições, compilação LaTeX/Overleaf ou validação real dos componentes.

## Pendências
- Orientador: confirmar aderência da prova Python e da divisão em três serviços ao escopo.
- Corrigir e testar `Condition`, `Rule`, IDs, ordenação, deduplicação e inicialização de snapshots na Etapa 07.
- Implementar comunicação e os serviços, criar fixtures e oráculo automatizado; validar C0/C1 antes de conteinerizar.
- Inventariar recursos do hardware e selecionar ferramentas, topologia e instrumentos na Etapa 06.
- Confirmar recursos suficientes para C4/C5, definição da latência e validade das medições.
- Revisar e integrar capítulo LaTeX e duas representações arquiteturais no momento apropriado, com compilação real.

## Planejamento histórico da Etapa 06 — concluída (preservado para rastreabilidade)
1. Identificar SO, CPU, RAM, disco, virtualização e permissões da máquina real.
2. Verificar Python, Git, Docker, Kubernetes/kubectl, versões e dependências por comandos completos e evidências de saída.
3. Escolher uma opção realista de cluster (inclusive restrições de um só nó), sem confundir múltiplos Pods com multinó.
4. Definir requests/limits e possibilidade de coleta de CPU, RAM, rede e latência compatíveis com o ambiente.
5. Registrar inventário, scripts de diagnóstico e verificações reais; avançar para a Etapa 07 apenas com ambiente validado.


## Encerramento da Etapa 06 — 11/11/2026 (horário local, logs UTC em 12/11)

**Situação:** infraestrutura de desenvolvimento preparada e operacional, com limitações explícitas. Registro integral: `docs/tcc2/etapa-06-preparacao-ambiente.md`.

**Ambiente confirmado por prints de comandos executados na máquina do acadêmico:**
- Windows 10 Home 64 bits, Intel i5-9300H (4 núcleos/8 threads), 15,84 GB RAM utilizável, C: 69,44 GB livres na coleta inicial, WSL2 e virtualização disponíveis.
- Python 3.13.9, pip 25.2, venv criado e validado; Git 2.45.0.windows.1; acesso remoto às branches dos dois repositórios confirmado.
- Docker Desktop 4.99.0 / Engine 29.9.3; hello-world com Exited (0); build próprio Python Linux/amd64 e execução com Exited (0), Python na imagem 3.13.18.
- kind v0.33.0; cluster `tcc2-pon` Kubernetes v1.37.0 (um control-plane + um worker), ambos Ready; DNS e Service validados com Nginx/curl e HTTP 200 em dois percursos entre Pods posicionados em nós virtuais diferentes.
- `kubectl top` indisponível por ausência da Metrics API; `docker stats --no-stream` funcional, mas somente amostra pontual de nós virtuais, não medições do PON.
- Namespace `tcc2-infra-test` removido, dois nós permaneceram Ready e cluster preservado. Contêiner local `tcc2-python-validacao` ainda sem prova de remoção; não executar limpeza genérica.

**Arquivos reprodutíveis adicionados na branch permanente:**
- `infraestrutura/kind/kind-config.yaml`
- `infraestrutura/kind/testes/pod-servidor-teste.yaml`
- `infraestrutura/kind/testes/service-servidor-teste.yaml`
- `infraestrutura/kind/testes/pod-cliente-teste.yaml`
- `infraestrutura/docker/teste-python/Dockerfile`
- `infraestrutura/docker/teste-python/teste.py`

**Commits relevantes:** documentação de base `93cdba227074dca8e23831653ed4294caf107bcf`; imagem de teste `7af27c944e18e14dccae90dccdef87edf77cb929` e `88144ce30ffe1e349de62334c11972ae2e31d082`; consolidação técnica `20943378fd85f8f6b01027e0227d4701ba12c621`. O SHA deste status é o commit de encerramento a registrar pela própria publicação.

**Limitações e ressalvas científicas:**
- Dois nós kind virtuais no mesmo computador não demonstram máquinas físicas distintas nem escalabilidade física.
- Leituras de RAM com outros programas abertos não são condições controladas; medição adicional com aplicativos fechados não foi realizada.
- A imagem `python:3.13-slim` foi usada por tag, não congelada por digest na prova preliminar.
- Não houve testes do núcleo PON nem implantação de `attribute-source`, `logic-engine` e `rule-executor`; C0–C5/F1 e V01–V12 da aplicação continuam pendentes.
- Não há `requirements.txt` no commit inspecionado do `codigoPon`; imports Python verificados na árvore principal referenciam módulos locais e bibliotecas padrão `json`/`asyncio`. A compatibilidade funcional permanece por provar.
- Windows 10 Home / Docker Desktop e memória compartilhada são limitações de suporte e reprodutibilidade; monitoramento por serviço e séries históricas não instrumentados.
- Capturas originais enviadas em conversa não foram incorporadas ao repositório; preservar arquivos e hashes quando arquivar evidências.
- As duas representações arquiteturais permanecem preservadas; nenhuma figura definitiva da implementação foi inserida na monografia.

**Encaminhamento à Etapa 07:** congelar referência `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`, criar testes e oráculo determinístico C0, revisar `Condition`/`Rule`/IDs, implementar e validar os contratos HTTP/JSON em três processos C1 antes da conteinerização definitiva nas etapas subsequentes. Confirmar com orientador aderência da prova Python.


## Abertura da Etapa 07 — 12/11/2026

- Consultados nesta ordem: `STATUS_ATUAL_TCC2.md` e `docs/tcc2/etapa-06-preparacao-ambiente.md`; depois preservadas as decisões em `docs/tcc2/etapa-04-arquitetura-distribuida.md` e `docs/tcc2/etapa-05-protocolo-experimental.md`.
- Inspecionados `main.py`, `pon/__init__.py`, `Notifiable`, `Notifier`, `Attribute`, `Premise`, `Condition`, `Rule`, `Action`, `Instigation` e `NOPManager` no commit fixado `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.
- Sem dependências de terceiros explicitamente importadas no núcleo examinado (apenas `json` e `asyncio` da biblioteca padrão); não foi localizado `requirements.txt` na revisão.
- Defeitos estáticos prováveis: referência a `self.__id` em `Condition.update`; notificação aos elementos de entrada em lugar dos observadores; `asyncio.create_task` sem loop garantido em `Rule.update`; registro de IDs com risco de colisão.
- Documento novo: `docs/tcc2/etapa-07-implementacao-validacao-local.md`, commit `c4da4d2ad7f8d23329919c9ece006039275aafb7`.
- **Executados no Windows e comprovados por prints em 12/11/2026:** checkout no SHA fixado e `git status --short` limpo; Python 3.13.9 e pip 25.2; `compileall` com código 0; `main.py` com código 0; reprodução do erro `AttributeError: 'Condition' object has no attribute '_Condition__id'` na transição da condição, com código 1. Referências e checksums dos prints em `docs/tcc2/etapa-07-implementacao-validacao-local.md` (seção 8).
- **Ainda não executados/aprovados:** testes V01–V07 da aplicação adaptada, C0/C1 completos, prints de correção, medições ou implantação PON. A reprodução de defeito não equivale a aprovação de V01.
- Próxima atividade: executar comandos de diagnóstico e caso mínimo da `Condition` no PowerShell da máquina de desenvolvimento; arquivar stdout/stderr e prints originais; depois implementar testes de regressão, correções, oráculo C0 e C1 com três processos.
- **Fora do escopo atual:** Docker e Kubernetes da aplicação (Etapas 08–10); atualização dos diagramas/figuras na monografia (Etapa 13).

## Atualização de evidências — 12/11/2026

- Registro de E07-D01, E07-D02 e E07-D03 feito na Etapa 07, com outputs confirmados visualmente, hashes SHA-256 das duas capturas fornecidas, indicação de que os PNGs ainda não estão no repositório e classificação de teste funcional como **não aprovado**.
- Commit de documentação das evidências: `d7d2cc0214128c807c546f832a084caac0d9b2cc` (somente `tcc2/desenvolvimento`).
- Correção inicial de `Condition` e três testes de regressão adicionados em `prova-conceito/`, **ainda sem execução comprovada no Windows**. Próximo passo: atualizar o clone local com `git pull --ff-only` e executar o `unittest` da prova adaptada antes de avançar com Rule/IDs e C0/C1.

## Incremento da Etapa 07 — regressão isolada de Condition (12/11/2026)

- **E07-D04:** imagem do terminal prova clone de `tcc2/desenvolvimento`, branch ativa e `git status --short` limpo. PNG original somente nesta conversa: `image(20261112-195720).png`; SHA-256 `2f9494d6524e10821f665e1dd530b7e9feb1f80dcb7c4ab57be932da73ff224b`.
- **Código incluído:** cópia rastreável de `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` em `prova-conceito/`. Commit `41792b5a459b348c39eacb4ad63e63b7f61cb15f` somente na branch `tcc2/desenvolvimento`.
- **Correção restrita:** `Condition.update` usa notificação aos observadores e `getId()`; criados três testes `unittest` para transição, repetição e composição aninhada. `Rule`, `NOPManager` e demais módulos mantidos da fonte nesta primeira alteração.
- **Documentação do pacote:** `prova-conceito/README.md`, com formatação corrigida no commit `c2d253a91bbc13675a19e76fbb961ea2b45fc7ac`; atualização de evidências na Etapa 07 no commit `c4625cc46ea99122f0fef84d5aa0a3dcdf49831c`.
- **Situação dos testes:** a referência defeituosa falhou conforme print anterior; a correção e os três novos testes **não foram executados no Windows**. Não aprovar V01 ainda. Próximo comando: `python -m unittest discover -s tests -p "test_*.py" -v` a partir de `prova-conceito`, após sincronizar a branch local.
- **Docker e Kubernetes da aplicação:** não iniciados. As duas representações arquiteturais e o capítulo LaTeX continuam preservados.

## Atualização da Etapa 07 — 12/11/2026: validação de Condition e segundo incremento

- **E07-D05/E07-D06 confirmados por prints enviados pelo acadêmico:** `git pull --ff-only` completado, HEAD local `4dcaf328ef31893246260623e741eb65aa71773f`, Python 3.13.9, `compileall` retorno 0, **3/3 regressões de Condition OK em 0,003 s**, `main.py` retorno 0.
- Arquivos PNG originais na conversa (ainda não publicados no GitHub): `image(20261112-200509).png`, SHA-256 `60391e4f7a6ca6889f413e0635e32ffe4d9cc6e2e1bc54e790c65da9841495ea`; `image(20261112-200539).png`, SHA-256 `393f224361e1aa9a25f05d81cd7691951a6b29e0903a300fc03c46d00b5f837e`.
- **Situação de V01:** aprovação **parcial documentada apenas para Condition**; V01 completo e demais critérios V02–V07 pendentes.
- **Segundo incremento de código publicado:** `6165bfdbcfa152218452cf91776fc0be6b345ede`, corrigindo disparo síncrono determinístico de `Rule` e consistência/colisão de IDs em `Notifier`/`NOPManager`. Adicionados `test_rule.py` (4 testes) e `test_ids.py` (4 testes); suíte prevista de 11 testes incluindo os três anteriores.
- **Ainda não executados no Windows:** novos testes da suíte de 11; a execução real é a próxima ação. Não considerar o incremento aprovado antes de receber saída e evidência.
- Continuam fora do escopo atual: Docker/Kubernetes da aplicação e figura definitiva na monografia. C0 completo e C1 aguardam validação do núcleo.


## Checkpoint Etapa 07 — 12/11/2026, 11 testes reais aprovados

- **E07-D07/D08**: prints originais `image(20261112-201405).png` e `image(20261112-201417).png`; hashes SHA-256, dimensões, saídas e limites de validade constam na seção 12 de `docs/tcc2/etapa-07-implementacao-validacao-local.md`. PNGs ainda somente na conversa.
- **Ambiente:** Python 3.13.9 em Windows; HEAD `eb9d21780b4074a03accc9711d586f70ba38505b`, branch `tcc2/desenvolvimento`. `compileall` retorno 0, **11/11 testes `unittest` OK em 0.011 s**, `main.py` retorno 0. A duração da suíte é apenas tempo de teste, não benchmark PON.
- **Aprovado parcialmente:** V01 no alcance dos testes unitários da cadeia local, incluindo dois disparos nos passos 3/7; **ainda pendentes** oráculo independente/fixture JSONL e execução documentada do cenário C0 completo; C1/V02–V07, Docker/Kubernetes da aplicação não executados.
- **Continuidade:** preparar C0 com rastreamento determinístico de `AttributeChanged`, `ConditionChanged` e efeitos; comparação contra oráculo manual e independente. Registrar execução na máquina antes de avançar a C1. 
- **Preservado:** referência `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`, decisões Etapas 04/05, objetivos TCC1, figuras e capítulos LaTeX.


## Checkpoint mais recente — Etapa 07, C0 estruturado (12/11/2026)

- **Última validação real do usuário:** 11 regressões Python aprovadas, execução `main.py` retorno 0, HEAD da execução `eb9d21780b4074a03accc9711d586f70ba38505b`, evidências E07-D07/E07-D08 e SHA-256 na seção 12 do documento da Etapa 07.
- **Novo código publicado, não validado ainda no Windows:** `f75b9c8be0d7d6eb54eb091d49dc3d3c1df1bf0a` — fixture JSONL fixa, expected JSONL manual, oráculo independente, cadeia PON com trace, comparador e sete novos testes. Instruções em `docs/tcc2/etapa-07-c0-oraculo-local.md`.
- **Próxima ação comprovável:** `git pull --ff-only`, suíte `unittest` (18 casos previstos), `python -m c0.runner` e exame de `validation.json`, `effects.jsonl`, `trace.jsonl`, `manifest.json`, `checksums.sha256`, com prints reais e exit codes. Registrar falhas sem mascarar.
- **Não executados/comprovados:** o novo C0 completo e os serviços HTTP C1; V02–V07 permanecem pendentes. Sem Docker/Kubernetes da aplicação, sem métricas experimentais nem figuras finais.
- **Rastreabilidade da continuidade:** decisões Etapas 04/05, status Etapa 06 e referência original `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` permanecem inalterados. Usar este checkpoint e a seção 13 da Etapa 07 como contexto mínimo em vez de carregar toda a conversa.


## Checkpoint Etapa 07 — 12/11/2026: C0 comprovado

- **Execução real no Windows:** branch `tcc2/desenvolvimento`, HEAD `51b3539f8735eb56da754a6239886a3a725860ad`, Python 3.13.9; `compileall` retorno 0; **18/18 testes `unittest` OK em 0.478s**; execução `python -m c0.runner` retornou `C0: 0`, relatório `status: PASS`.
- **Saídas C0 observadas:** 2 efeitos nos passos 3 e 7, 7 requisições, 5 mudanças de atributos, 3 transições de condição, final `atA=6`/`atB=1`, sequências `atA=2`, `atB=3`. Igualdade observada entre fixture manual, oráculo independente e execução PON.
- **Evidências:** E07-D09 a E07-D11 com nomes/dimensões/SHA-256 das 3 capturas na seção 14 de `docs/tcc2/etapa-07-implementacao-validacao-local.md`; PNGs e arquivos brutos da rodada não estão versionados no GitHub.
- **Classificação:** C0 mínimo **aprovado funcionalmente**; V01 e parte do controle de regressão V11 sustentados pelas evidências. **C1, V02–V07 interprocessos e etapas Docker/Kubernetes da aplicação seguem não executados**. Duração de `unittest` não é benchmark.
- **Próxima etapa técnica dentro da Etapa 07:** implementar `attribute-source`, `logic-engine`, `rule-executor` em três processos HTTP/JSON com snapshot antes das alterações, `event_id` estável, sequência por origem, deduplicação e saída comparável ao oráculo C0; executar testes reais antes de considerar V02–V07 aprovados.


## Checkpoint de continuidade — C1, incremento 01 (12/11/2026)

- **Base real aprovada:** C0 no Windows (18/18 testes, `status: PASS`, 2 efeitos nos passos 3/7) conforme E07-D09–D11; nenhuma medição de desempenho da aplicação.
- **Incremento C1 publicado, ainda NÃO executado no Windows:** pacote `prova-conceito/c1/protocol.py` e `__init__.py`, sete regressões em `tests/test_c1_contracts.py`, documentação `docs/tcc2/etapa-07-c1-contratos.md`. Commits de implementação `cb56eabbb003c1b146c12b6311c0326c258ccb2b`, `e90a3ae942072b4c7cb3b2222a371639fc6f634b` e `eaa03334a256c5ab97ae8e841476ab61980f8ac6`, documentação `d9a12f10e67ed8fb21c0b9d23239b4f6d69dac88`.
- **Próxima execução solicitada:** sincronizar branch `tcc2/desenvolvimento`, compilar, executar `unittest` (25 casos previstos), enviar prints para validação. Não confundir contratos validáveis com três serviços rodando.
- **Depois:** implementar máquinas de estado, snapshot, ordenação/deduplicação, transporte HTTP/JSON em três processos e validar V02–V07 contra C0. Nenhum Docker/Kubernetes da aplicação, sem modificar capítulos LaTeX/figuras ou a referência original.


## Checkpoint — contratos C1 validados em 12/11/2026

- **E07-D12:** screenshot `image(20261112-203727).png`, 1920 × 1080, 135.992 bytes, SHA-256 `a20f0d787f2ceeb7c53dbfe7c362ca14bee695a6214d2ddd1c81b2ad09680d0c`. Origem: PowerShell do acadêmico, ainda não arquivado no GitHub.
- **Validação real:** HEAD `fe7e4d9b066d3c3f69b3d781ed9184c9ee2d8943`, Python 3.13.9, compilação 0, **25/25 unittest OK em 0.542 s**, `Testes: 0`.
- **Comprova:** C0 mínimo aprovado anteriormente e sete testes de contratos C1 aprovados; **não comprova** os serviços C1, snapshots instalados, deduplicação real no transporte, PIDs separados nem V02–V07 completos.
- **Próximo incremento:** máquinas de estado `attribute-source`, `logic-engine`, `rule-executor`; testes de snapshot, ordenação, duplicatas e efeitos. Depois HTTP/JSON em processos diferentes, ainda sem Docker/Kubernetes da aplicação.


## Checkpoint de continuidade — C1, máquinas de estado publicadas (12/11/2026)

- **Última execução real comprovada no Windows:** 25/25 testes, `Compilacao: 0`, `Testes: 0`, Python 3.13.9, HEAD `fe7e4d9b066d3c3f69b3d781ed9184c9ee2d8943`, evidência E07-D12 (print e SHA-256 na seção 16 do documento da Etapa 07).
- **Novo incremento ainda não executado no Windows:** `prova-conceito/c1/state.py` (commit `efbc597fc733b14fb31bbb07bcca3232f30a2f5a`) e `prova-conceito/tests/test_c1_state.py` (commit `21c1de121fbe862bceed8883b64674096212a576`). São 11 novos testes de estado (suíte prevista de 36 testes).
- **Arquitetura em código:** `AttributeSource`, `LogicEngine`, `RuleExecutor`, snapshots antes das notificações, sequências/IDs, deduplicação, erro explícito para lacunas e estados em memória. `RuleExecutor` utiliza de fato `Attribute → Premise → Condition → Rule → Action → Instigation`. Transporte ainda por callbacks locais, **sem HTTP ou PIDs distintos**.
- **Limitações:** snapshot inicial apenas com watermarks zero; sem ressincronização/replay automático, sem persistência, sem concorrência thread-safe; se houver falha parcial no avaliador, sinaliza `faulted`. Falha de ACK simulada é teste unitário, não experimento de rede.
- **Documento para retomar a conversa:** `docs/tcc2/etapa-07-c1-estados.md`. **Próxima execução do acadêmico:** `git pull --ff-only`, `compileall`, `unittest` de 36 casos, capturas e códigos de saída; depois implementar HTTP/JSON entre três processos e validar V02–V07.
- **Preservados:** decisões Etapas 04/05, código original `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`, monografia LaTeX, figuras conceituais; nenhuma implantação da aplicação em Docker/Kubernetes.

## E07-D13 — validação das máquinas de estado (12/11/2026)

Captura original do PowerShell do acadêmico: `image(20261112-204915).png`.
SHA-256: `c1a9fdb5fedd4a144a01d4b392b271bfba4dd5f37c8bc240e5534780726a7f69`.
Branch `tcc2/desenvolvimento`, HEAD `52dd849727f179ec938172def7c37daeecec302b`,
Python 3.13.9, `compileall` retorno 0, 36/36 `unittest` OK em 0.471 s, retorno 0.
O tempo é da suíte. A evidência cobre as máquinas de estado em memória.

## C1 HTTP/JSON — rodada automatizada

Três processos em localhost, snapshot inicial e fixture C0 executados com
`PASS`, 12 verificações verdadeiras e efeitos nos passos 3 e 7. A suíte
integrada passou com 37 testes nesta sessão. A reprodução do C1 pelo acadêmico
aguarda nova saída. Evidência anterior E07-D13 registra 36/36 testes das
máquinas de estado no PowerShell do acadêmico. Procedimento, alcance de V02–V07
e hashes em [C1 HTTP](docs/tcc2/etapa-07-c1-http.md).


## Atualização mais recente — 12/11/2026, evidências C1 e ZIP local

- **C1 validado no Windows pelo acadêmico:** revisão testada `f37dbc998eb5114a60335f5275c86b6e8bedee61`, Python 3.13.9, compilação 0, **37/37** testes `unittest` OK em 7,388 s, `C1: 0`, `PASS`, 12/12 verificações verdadeiras; efeitos nos passos 3 e 7; três PIDs distintos `20472`, `19548`, `22276`.
- **ZIP das evidências:** criado pelo acadêmico no Windows; hash SHA-256 mostrado `D7A62AC62AFA23302F272D303E00DB6B622B92FA04E5B3B7F1DE7367BF735D17`; bytes do ZIP não acessados pela IA. Prints E07-D14–E07-D17 na conversa, hashes verificados e inventário em `docs/tcc2/etapa-07-aceite-tecnico.md`.
- **Aceite científico:** V01–V06 aprovados somente para fixture e transporte localhost serial testados. **V07 parcial**: snapshot inicial e barreira pré-inicialização verificados, mas não a chegada concorrente de alterações durante a instalação via HTTP.
- **Incremento novo pendente de validação Windows:** um teste local determinístico de snapshot foi acrescentado em `tests/test_c1_state.py`, commit `e77b166f78cafd13369e1a1664b340cfb4718133`. Suíte prevista: **38 testes**; não atribuir sucesso antes da execução.
- **Próximas ações:** executar 38 testes, arquivar evidência, concluir V07 de acordo com o critério original e finalizar relatório técnico da Etapa 07. **Ainda sem Docker/Kubernetes da aplicação, medições científicas ou desenhos finais da monografia.**


## Checkpoint recente — 12/11/2026, regressão de 38 casos e V07 HTTP

**E07-D18 — captura original do PowerShell:** `image(20261112-215913).png`, dimensões 1920 × 1080, tamanho 150.253 bytes, SHA-256 **calculado sobre os bytes da imagem recebida**: `538070b0635b8a078750f745071a2b459fd3d9aae7610ff44b49b879d51808b9`.

Resultados observados no Windows: branch `tcc2/desenvolvimento`, HEAD `3742a852a7b448f15a998b18207a02765954019c`, Python 3.13.9, `Compilacao: 0`, `Ran 38 tests in 7.354s`, `OK`, `Testes: 0`. O teste `test_change_during_snapshot_handshake_is_rejected_before_ack` aparece com `ok`. **Esse teste é local em memória e não prova concorrência HTTP**. A duração é da suíte `unittest`, não benchmark do PON. A imagem foi enviada nesta conversa e ainda não é um arquivo bruto do repositório.

- **Novo incremento C1 publicado, ainda não executado no Windows:** `c1/snapshot_race.py` (ensaio de HTTP com ACK de snapshot controlado), `tests/test_c1_snapshot_http_race.py` (mais um teste de integração), documentação `docs/tcc2/etapa-07-c1-snapshot-http.md`. A suíte agora tem **39 testes previstos**, não validados ainda nesta revisão.
- Objetivo: observar requisição recebida por socket HTTP enquanto o produtor aguarda o ACK do snapshot, depois confirmar processamento e equivalência C0 sem efeitos duplicados. Mantém três PIDs reais; um proxy de teste em thread segura o ACK, não integra a arquitetura de produção.
- **V07 ainda parcialmente aprovado** até execução real do novo ensaio. Mesmo se aprovado, não alegar suporte geral à concorrência/recuperação: serviços são HTTP seriais, sem replay/persistência.
- **Próximo comando no Windows:** sincronizar `tcc2/desenvolvimento`, rodar 39 `unittest`, executar `python -m c1.snapshot_race --output resultados-locais/c1-snapshot-http-<data>`, salvar `manifest.json`, `validation.json`, `timeline.jsonl`, logs, checksums e capturas.


## Encerramento funcional Etapa 07 — execução real 12/11/2026

**Situação mais recente:** Etapa 07 **concluída funcionalmente no escopo C0/C1**, com V01–V07 aceitos apenas para a fixture e testes locais especificados. Relatório de encerramento: `docs/tcc2/etapa-07-encerramento-funcional.md`. Não há prova de distribuição multinó, desempenho experimental, persistência ou recuperação de falhas.

- **Último commit efetivamente testado no Windows:** `be6b850d599504e9ea8166f02fd87b35313e5445`, branch `tcc2/desenvolvimento`, Python 3.13.9, compilação 0, `39/39 unittest OK em 11,152 s`, `V07-HTTP: 0` e `status=PASS` com 7 checks true.
- A confirmação de snapshot foi temporariamente retida por proxy de teste, uma alteração foi enviada por socket HTTP durante a espera e foi processada após a confirmação. Três PIDs reais: `1988`, `15164`, `18332`; dois efeitos nos passos 3/7, sem duplicações extras. **HTTP serializado**, não concorrência geral.
- Capturas E07-D19 a E07-D21: nomes, bytes, SHA-256 e resultados no relatório de encerramento. ZIP local `c1-snapshot-http-20261112-190909.zip`, SHA-256 exibido `E454D6051048C37CD2276BFF6ACADCFAC04E2FE03449ABCAFCCA217C07B6FBA1`; bytes do ZIP **não foram acessados nem auditados pela IA**.
- **Encaminhamento:** preservar ZIP e brutos, completar auditoria V11, confirmar com orientador uso de Python/3 serviços; **Etapa 08** a seguir (Docker/C2) com validação no Windows. Nenhuma alteração na `master` ou no código original, nenhum resultado de Kubernetes ou benchmark atribuído à Etapa 07.


## Última atualização — auditoria direta do ZIP C1 (12/11/2026)

- **Arquivo bruto recebido e auditado:** `c1-snapshot-http-20261112-190909.zip`, 5.867 bytes, SHA-256 `e454d6051048c37cd2276bff6acadcfac04e2fe03449abcafcca217c07b6fba1`, idêntico ao hash mostrado no PowerShell.
- Integridade: ZIP/CRC sem erros, **13 entradas**, sendo **12/12** arquivos efetivamente cobertos por `checksums.sha256` com hashes recalculados corretos. **20/20 verificações adicionais de consistência** dos logs, estados, eventos, manifestos e causalidade aprovadas.
- Conteúdo confirmado: commit `be6b850d599504e9ea8166f02fd87b35313e5445`, Python 3.13.9/Windows, três PIDs distintos, **5 notificações de atributo, 3 transições de condição, 2 efeitos** nos passos 3 e 7; igualdade exata entre `effects.jsonl` e `expected.jsonl`.
- Novo relatório: `docs/tcc2/etapa-07-auditoria-zip.md`. Declarações históricas de que o ZIP não havia sido inspecionado estão **superadas a partir deste envio**. O arquivo permanece anexado à conversa e no Windows do acadêmico, não no GitHub.
- **Etapa 07 funcionalmente concluída no escopo local C0/C1**; V11 reforçado para esta rodada, mas **parcial globalmente**. Sem novos testes da aplicação, benchmark ou execução de Kubernetes.


## 15/11/2026 — fechamento técnico da Etapa 08 (C2/Docker)

**Etapa 08 concluída para o escopo funcional Docker C2**, sem Kubernetes da aplicação nem medição de desempenho. Última execução Windows: branch `tcc2/desenvolvimento`, commit `2ea999a712032b2bf295362264e6a5a204b9986f`, 93/93 testes `unittest` OK (10,966 s, apenas duração da suíte), Git limpo; E08-D18G/H HTTP 409 esperados, ambos `PASS`, estados inalterados e zero efeitos extras. ZIP bruto `c2-v06-batch-20261115-184915.zip` auditado: 13.566 bytes, SHA-256 `24ff2fbc4aa28acfec0bad90c3677301cfadbce7efea51c9368b6e50953c1be1`, 27/27 entradas, CRC OK, 26/26 hashes internos. Laudo: `docs/tcc2/etapa-08-auditoria-v06-batch.md`; encerramento: `docs/tcc2/etapa-08-encerramento-tecnico.md`.

**Não repetir POSTs nem alterar/reiniciar bancadas V05/V06.** V07 global permanece **parcial** (concorrência durante snapshot C2/C3 não comprovada), V08/V09/V10/V12 ainda não executados no escopo Kubernetes/performance, V11 global parcial. **Próxima atividade: Etapa 09, diagnóstico do cluster existente e implantação C3/Kubernetes.** Preservar ZIPs originais fora do GitHub.


## 15/11/2026 — Etapa 09 Kubernetes C3 (marco E09-I03)

**Estado mais recente:** E09-D01 (diagnostico do cluster), E09-I01 (manifestos, dry-run), E09-I02 (implantacao) e E09-I03 (DNS HTTP e snapshot) **aprovados por saidas reais do Windows**. Relatorio atualizado: docs/tcc2/etapa-09-checkpoint.md.

- Cluster kind tcc2-pon: control-plane e worker Ready, ambos nos virtuais Docker/WSL2 no MESMO computador. Imagem C2 original carregada sem rebuild em ambos os nos; Docker image ID sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a.
- 8 recursos implantados no namespace tcc2-pon; tres Deployments 1/1, tres Pods Running 1/1 sem reinicios, tres Services ClusterIP. **Todos os Pods da aplicacao no no virtual tcc2-pon-worker**.
- E09-I03: DNS HTTP dos tres Services comprovado, antes do snapshot /health/live=200 e /health/ready=503; unico POST snapshot run_id=c3-e09-i03-v1 retornou HTTP 200 e duplicate=false; depois, tres /health/ready=200, watermarks zero, zero efeitos. Logs confirmam fluxo source→logic→executor. E09_I03_EXIT=0.
- V08 **parcial**: rollout, Service e snapshot validados, mas fixture integral C3 ainda pendente. V07 global parcial; V09 nao demonstrado (todos os Pods da aplicacao no mesmo no); V10 e V12 nao executados; V11 global parcial.
- E09-I04: runner de fixture e geracao de evidencias preparado em prova-conceito/c3/runner.py (nao executado). **Proxima acao: sincronizar branch de trabalho e executar uma unica vez** python -m c3.runner --output resultados-locais/c3-e09-i04-v1 a partir de prova-conceito, preservando ZIP/SHA, sem repetir snapshot. Nao reiniciar Pods nem executar outro POST se ocorrer falha: diagnosticar primeiro.


## 15/11/2026 — encerramento funcional da Etapa 09 (C3/Kubernetes)

**Etapa 09 concluida no escopo C3 minimo** com prova real de comunicacao por Services no cluster kind e comparacao funcional exata com o oraculo. Relatorios: docs/tcc2/etapa-09-checkpoint.md e docs/tcc2/etapa-09-auditoria-c3-zip.md.

- Execucao Windows na branch tcc2/desenvolvimento, commit testado 8669e8364118e30333c90fd798763c18a23fb1ea; E09-I03 snapshot unico validado, E09-I04 teste C3 executado uma unica vez: preflight PASS, 7/7 HTTP 200, validation.json 14/14 checks, E09_I04_EXIT 0.
- ZIP bruto c3-e09-i04-v1.zip realmente recebido e auditado: 27.165 bytes, SHA-256 aad71cea5e90b9c6a334f66180f54dc5609a024b907b7c7f121f6ed4d5855b83, 28/28 entradas, CRC OK, 27/27 hashes internos, 25/25 verificacoes documentais adicionais.
- Evidencia de 5 notificacoes de atributo, 3 transicoes de condicao e 2 efeitos exatamente nos passos 3 e 7 (C3 == C0 == oraculo == fixture manual), preservando ordenacao, multiplicidade, IDs e causalidade. Estado final atA=6, atB=1, sequencias (2,3), condition_sequence=3. 3 Pods UIDs/container IDs distintos e 0 restarts.
- **V08 aprovado para C3 funcional minimo**, sem distribuicao multinó: TODOS os tres Pods da aplicacao alocados ao no virtual tcc2-pon-worker. Um unico computador hospeda ambos os nos kind. **V09 nao demonstrado.** V07 global parcial, V10/V12 nao executados, V11 global parcial. Sem benchmark de latencia, CPU, RAM ou throughput.
- **Nao repetir** o snapshot ou a fixture sobre os Pods C3 atuais, nem reiniciar/alterar suas cargas. Preservar ZIP original e hashes fora do GitHub. Proximo: Etapa 10 — diagnostico dos taints do control-plane e nova bancada isolada C4 para execucao entre dois nos virtuais, sem alegar distribuicao fisica.


## 15/11/2026 — Etapa 10/C4: diagnostico e configuracao preparada (sem execucao)

**E10-D01 aprovado por diagnostico PowerShell:** nos kind control-plane e worker schedulable (unschedulable=false), mas control-plane com taint node-role.kubernetes.io/control-plane:NoSchedule. Worker sem taint efetivo identificado. Tres Pods C3 preservados Running 1/1, restarts=0, todos no worker; namespace tcc2-pon-c4 ausente no diagnostico.

**C4 apenas preparado no GitHub:** infraestrutura/kubernetes/c4/manifests.yaml define novo namespace tcc2-pon-c4, ConfigMap, tres Deployments/Services, image C2 inalterada; rule-executor e attribute-source agendados no worker, logic-engine no control-plane por nodeSelector + toleration local (sem remover taint). Ferramentas de rodada unica e evidencia em prova-conceito/c4/runner.py, reutilizando c3.runner com RUN_ID/NS/SCENARIO separados. Protocolo: docs/tcc2/etapa-10-checkpoint.md.

**Nao executado ainda:** dry-run C4, apply, rollouts, snapshot e fixture C4. V09 segue nao demonstrado ate comprovacao real de entrega de notificacoes em nos distintos. Todos os nos kind compartilham uma unica maquina fisica; nenhum benchmark, replay ou tolerancia a falhas comprovados. **Proxima acao:** sincronizar Git e executar validacao/aplicacao isolada C4 no Windows, uma unica rodada; nao tocar no C3 aprovado.


## 15/11/2026 — encerramento funcional da Etapa 10 (C4/kind multinó virtual)

**Estado MAIS RECENTE (substitui a situação pendente na seção anterior):** Etapa 10 concluída funcionalmente no escopo C4 mínimo, com **V09 APROVADO somente para dois nós Kubernetes virtuais no mesmo host físico**. Etapa 09/C3 também permanece aprovada em seu escopo. Fonte: docs/tcc2/etapa-10-checkpoint.md e docs/tcc2/etapa-10-auditoria-c4-zip.md.

- Windows real, commit executado f84c8384f33168219213757f9b2027216a2511e4, AST Python válida; dry-run 8 recursos, apply 8 recursos e 3/3 rollouts C4 OK no namespace tcc2-pon-c4. Worker: attribute-source e rule-executor; control-plane: logic-engine (toleration específica, taint do nó preservado). 3 Pods Running/Ready, UIDs/containers distintos, restarts=0. C3 preservado no namespace tcc2-pon, Running/Ready, sem reinícios.
- Snapshot único run_id=c4-e10-i02-v1, preflight de estado frio, inicialização 3/3 pronta e sem efeitos. Fixture 7/7 HTTP 200, 14/14 checks, exatamente 5 eventos de atributo e 3 condições correlacionados nos dois nós virtuais, 2 efeitos passos 3/7, equivalentes a C0/manual/oráculo. E10_C4_EXIT=0.
- ZIP bruto c4-e10-i02-v1.zip auditado diretamente: 36.370 bytes; SHA-256 8f77d981abb6977890f948168924b594398828ef3d843d7f38baf66d09acca7c; 16/16 entradas externas e 15/15 hashes, fixture.zip interno de 27.505 bytes SHA-256 21dcdc0239bb51d41e4148b8834e626c32dd5ac355f7fe4ba78a245dc3dfe2be, 28/28 entradas e 27/27 hashes corretos; ambos CRC OK. **48/48 auditorias documentais independentes aprovadas** sobre bytes reais, não 48 novas execuções.
- **Não alegar duas máquinas físicas:** ambos os nós kind rodam no mesmo host Windows/WSL2, sem captura de pacotes, benchmark, persistência, recuperação ou escala horizontal. V07 global parcial; V10 e V12 não executados; V11 parcial global.
- **Não repetir** snapshots/POSTs de C3 ou C4, não reiniciar/escalar seus Pods stateful e não modificar a master. Preservar ZIPs originais e hashes fora do GitHub. Próximo: Etapa 11, planejamento e instrumentação de experimentos quantitativos com novas bancadas independentes, sem inventar dados.

## 15/11/2026 — Etapa 11 iniciada: diagnóstico e proposta experimental (SEM BENCHMARK)

**Estado atual:** inspeção somente leitura de protocolo E05, auditorias C3/C4 e scripts C0–C4; estratégia de coleta e pendências documentadas em docs/tcc2/etapa-11-diagnostico-plano.md. Esta atualização registra planejamento, não aprovação definitiva de instrumentação, execução de carga ou qualquer série quantitativa.

**Achado metodológico:** c3/runner.py usa kubectl exec com Python novo por requisição; sua duração não mede apenas o processamento da aplicação. Recomenda-se driver de carga persistente, janela cronometrada separada de bootstrap/validação/ZIP e comparação primária de C2/C3/C4 com recursos equivalentes. CPU/memória via cgroup v2 permanecem instrumentos candidatos, sujeitos a sondagem real no Windows/WSL2/kind.

**Preservação:** C3 em tcc2-pon e C4 em tcc2-pon-c4 não devem sofrer novos eventos, escala, reinício ou remoção. Não foram criados namespaces, executados benchmarks ou alterados componentes funcionais. ZIPs C3/C4 originais e hashes permanecem referências funcionais, não medidas de desempenho.

**Próximo passo E11-D01:** executar apenas diagnóstico PowerShell não mutante de Git, ambiente Docker, cgroups e métricas no host do acadêmico; analisar a saída; fixar parâmetros e critérios antes de gerar scripts e qualquer piloto.


## 15/11/2026 — E11-D01 PowerShell recebido e diagnosticado

**Fonte:** saída textual do Windows fornecida pelo acadêmico, 21:02:01-03:00; arquivo TXT local não enviado para auditoria de bytes/hashes. Laudo: docs/tcc2/etapa-11-e11-d01-diagnostico-ambiente.md. **Aprovado como inventário, não como medição de desempenho**.

**Constatações:** branch local tcc2/desenvolvimento limpa em f84c8384f33168219213757f9b2027216a2511e4, anterior aos commits documentais E11; Windows 10/i5-9300H 4c/8t; Docker Desktop 4.99.0, Engine 29.9.3, 8 CPUs e 8245637120 bytes, cgroups v2; imagem C2 correta; dois nós kind v1.37.0 Ready no mesmo host WSL2. C3 e C4, seis Pods Running 1/1, 0 restarts, posições esperadas, preservados. metrics.k8s.io/v1beta1 retorna NotFound, sem fonte atual comprovada de métricas CPU/RAM por Pod. Nenhum benchmark executado, nenhum Pod alterado.

**Próximo E11-D02:** sincronizar a documentação por git pull --ff-only na branch de trabalho, verificar Kubelet Summary API e disponibilidade de arquivos cgroup v2 de nós kind **somente por leitura**; não executar GET/POST da aplicação nem iniciar novos contêineres. Só então fixar instrumentos, método e piloto.

## 15/11/2026 — E11-D02: Kubelet Summary API acessível

**Diagnóstico PowerShell por captura:** pull `--ff-only` realizado via Fast-forward, HEAD local `72957299fe9dbffb66c9f99681a54c5787459919` e Git limpo; mensagem vermelha `git : From...` é stderr informativo tratado pelo PowerShell como `NativeCommandError`, não falha do pull.

**Métricas:** `/api/v1/nodes/{node}/proxy/stats/summary` disponível em ambos os nós kind; seis contêineres C3/C4 vistos (5 worker, 1 control-plane), campos cumulativos CPU e workingSetBytes presentes com timestamp. `NETWORK=False` inconclusivo por consulta ao campo incorreto `network.interface.rxBytes` (verificar campos `network.rxBytes` / `network.interfaces` no coletor novo). Cgroups v2: `cpu.stat`, `memory.current`, `memory.peak` legíveis nas raízes dos nós kind, sem demonstrar ainda atribuição a contêineres individuais. **Nenhum benchmark executado; instrumentos ainda precisam ser calibrados**. C3/C4 preservados.

**Laudo:** `docs/tcc2/etapa-11-e11-d02-auditoria-instrumentacao.md`. **Próximo:** E11-I01/I02, implementar ferramenta de coleta persistente e verificações quantitativas em novas bancadas; não repetir sondagem por aparência vermelha do PowerShell.

## 15/11/2026 — E11-I01/I02: instrumentos experimentais PREPARADOS, ainda SEM validacao no Windows

**Commits de preparacao:** 2f517229e55992390502495aff17a6793f05346d (biblioteca instrumental), 34b40d419afc37fa97d3efc03c5892d9454a0047 (runner C3/C4 piloto), 2b1e8de13c95e4898f39c79778ea7e2de80dd0e2 (testes sintéticos), 8d0415f51cb2d97e3b607d5bba022172bd324c9d (documentacao). Consulte docs/tcc2/etapa-11-e11-i01-i02-preparacao.md.

**Arquivos novos:** prova-conceito/benchmark/{fixtures,client,collector,evidence,prepare,runner}.py e tests/test_benchmark.py. O núcleo funcional pon/ e c1/, imagem C2, namespaces e manifestos aprovados C3/C4 permanecem inalterados. Nenhuma execução na máquina do acadêmico desses scripts ainda foi observada; nenhum benchmark, PILOTO, criação de Pod/namespace ou medição científica deve ser declarado.

**Desenho:** cliente Python em Pod separado no worker e processo único para o lote, sem um kubectl exec por evento; Summary API candidata para CPU/memoria (calibracao pendente); manifests E11 apenas gerados em arquivos, não aplicados; runner sem --execute mostra somente plano, com --execute e MUTANTE numa NOVA bancada (um snapshot e uma rodada, sem retry). Quatro gates restantes: AST/unittest real, conferencia dos YAML e hashes, C2 equivalente antes das comparacoes definitivas, piloto e auditoria dos dados.

**Próximo E11-D03:** sincronizar branch, executar somente validacao sintatica/unittest, gerar fixtures/YAML com caminhos ineditos e imprimir plano sem --execute. Se houver falha, parar e corrigir codigo, preservando C3/C4. Nao rodar piloto ainda.

## 15/11/2026 — E11-D03 preparação validada no Windows COM RESSALVA

**Evidência textual recebida:** HEAD 00f69cd18ed02f4d65a6335e7078d15cad35dc50 e Git limpo; Push-Location falhou porque PowerShell já estava em prova-conceito, mas demais comandos continuaram. Compilação Python sem falha reportada, **6/6 unittest OK (0,052 s da suíte, NÃO benchmark)**. Três fixtures 100/1000/10000 geradas com hashes/contagens; dry-run C3/C4 9 recursos cada; PLAN_ONLY C3/100 execute:false. Sem kubectl apply real, snapshot, POST ou benchmark.

**Laudo:** docs/tcc2/etapa-11-e11-d03-auditoria-preparacao.md. SHA do TXT exibido no terminal, não auditado independentemente. C3/C4 funcionais preservados.

**Correções preventivas posteriores aos 6 testes, NÃO VALIDADAS NO WINDOWS:** benchmark/runner.py preserva saída/telemetria parcial e logs em falhas, compara fixture inteira com fonte canônica; tests/test_benchmark.py ganhou assert de adulteração. Núcleo PON, Docker C2 e manifests C3/C4 inalterados.

**Próximo E11-D04:** sincronizar branch e executar AST/unittest do controlador atualizado em PowerShell com reconhecimento automático da pasta prova-conceito. Liberar piloto isolado apenas depois. V12 NÃO EXECUTADO.

## 15/11/2026 — E11-P01 C3 piloto real e auditoria independente do RAR/ZIP

**Execução no Windows:** commit `b8b8a354e3207cc6eb04d7c61eff3913a6dec7f2`; nova bancada `tcc2-pon-e11-c3-p20261115-213740`; três serviços e cliente no worker virtual, Pods da aplicação com identidade e restartCount=0 estáveis. Snapshot único HTTP 200 `duplicate=false`, 3/3 serviços prontos. **100/100 HTTP 200, 86 alterações efetivas, 49 transições, 25 efeitos** iguais ao oráculo/esperado na ordem exata. Relatório `validation.json` PASS, **10/10 checks funcionais e 4/4 de transporte**. Pods C3 original e C4 original observados Running 1/1, 0 restarts, não foram reutilizados.

**Artefato enviado e realmente examinado:** `e11-p01-20261115-213740.rar`, 50.181 bytes, SHA-256 `8b8549faac1bb486dfec626fc64566937923dcb015d45bdd6276551c49d364df`; 28 entradas, das quais 24 arquivos com CRC válido. `run.zip` interno, 24.842 bytes, SHA-256 `ffa845a8ba7d88ac4fa27fd057d7b03f3f07509c01203d5f6b99a3c80e2ae064`, 19/19 entradas, CRC OK e 18/18 SHA-256 internos corretos. Equivalência JSON dos efeitos é semântica, NÃO identidade de bytes em arquivos JSONL (diferenças de ordem das chaves). Originais binários externos ao GitHub.

**Tempos OBSERVADOS APENAS NO PILOTO, não científicos definitivos:** lote 2,243528105 s, 44,57 req/s, latência mediana 21,08 ms e p95 51,02 ms, concorrência=1. 16 amostras Kubelet Summary API (4 por serviço + 4 cliente), sem erro; contador CPU monotônico presente, working-set amostrado. Entretanto janela de 3 segundos da coleta não está precisamente alinhada com lote de 2,244 s, de modo que **cpu_delta e working-set amostrado NÃO autorizam cálculo exato de CPU-segundos do lote nem pico real de memória**. `usable_cpu=true` no validador é apenas um teste de presença/monotonicidade, insuficiente para aprovar instrumentação quantitativa V12.

**Laudo completo:** `docs/tcc2/etapa-11-e11-p01-auditoria-c3-piloto.md`. **Decisão:** piloto funcional e arquivo de evidências APROVADOS; métrica CPU/memória AINDA NÃO CALIBRADA; séries estatísticas e V12 NÃO EXECUTADAS. **Não repetir snapshot/fixture nesta bancada**, não escalar, reiniciar ou remover Pods históricos C3/C4.

**Próximos:** endurecer teste de qualidade da amostragem/janela e registrar timestamps explícitos do cliente; planejar C4 piloto separado (mesma fixture), validar C2 comparável e realizar piloto de carga média antes de liberar baterias definitivas. Pesquisa Perplexity para metodologia de benchmark e confiabilidade da Summary API, com referências verificáveis.

## 15/11/2026 — E11-I03 instrumentação refinada (código preparado, testes Windows pendentes)

**Base empírica:** E11-P01 piloto C3/100 aprovado funcionalmente, mas janela de CPU (~3 s) não alinhada com lote (~2,244 s), por isso métricas de CPU/memória ainda não aceitas cientificamente. Laudo: docs/tcc2/etapa-11-e11-p01-auditoria-c3-piloto.md.

**E11-I03 preparado:** cliente registra início/fim UTC do lote adjacentes ao cronômetro monotônico; coletor distingue contadores monotônicos de cobertura temporal adequada (mínimo provisório 10 s de lote, pelo menos 5 timestamps, bordas a até 3 s e intervalos até 4 s); runner captura baseline pré-lote, gera CSV derivados e mantém JSONL brutos. Mesmo quando cobertura satisfatória, delta CPU por amostras de borda é estimativa com incerteza, nunca CPU exata do lote. C3/C4 e núcleo PON inalterados.

**Não executar piloto imediatamente:** rodar AST/unittest atualizados no Windows, conferir Git e revisar protocolo antes de nova bancada. Qualquer novo C4/C3 exige run_id e namespace inéditos; não repetir E11-P01. V12 global não aprovado.

## 15/11/2026 — E11-P02 C4 real auditado e prompt Perplexity preparado

**E11-D05:** HEAD affa6dfc1185c24b554235944c05fb9aeeb08ee3, sintaxe OK e 9/9 testes sintéticos OK (0,078 s, NÃO benchmark). **Piloto E11-P02:** novo namespace tcc2-pon-e11-c4-p20261115-220023; C4 com logic-engine no control-plane virtual e source/executor no worker; mesmo host físico. ZIP bruto enviado, 27.839 bytes e SHA256 d99e8b9c258ca7a0415dc2ca88d43119c47c5d4774945aacf4f011ae710a389d, CRC OK e 21/21 SHA internos. 100/100 HTTP 200, 86 mudanças, 49 notificações de condição e 25 efeitos semanticamente idênticos ao oráculo. 10/10 checks gerais e 4/4 de transporte PASS, Pods originais C3/C4 preservados.

**Tempo e vazão exploratórios, NÃO V12:** 2,095875392 s/lote, 47,71 requisições/s, mediana HTTP 19,78 ms e p95 50,24 ms. CPU e memória: 20 observações, 5 por contêiner incluindo cliente, sem erro de coleta declarado, porém cpu_window_adequate=false e memory_window_adequate=false. O contador do attribute-source assumiu dois valores sob timestamp igual a 01:00:36Z; isso indica ambiguidade de resolução, NÃO regressão comprovada. Não publicar CPU-segundos do lote ou picos reais. Laudo: docs/tcc2/etapa-11-e11-p02-auditoria-c4-piloto.md.

**Perplexity:** prompt de pesquisa metodológica versionado em docs/tcc2/etapa-11-pesquisa-perplexity-prompt.md. O resultado será recebido posteriormente em Markdown e BibTeX para verificação, síntese autoral e eventual LaTeX UTFPR; nenhum resultado científico ou referência externa foi acrescentado como verificado nesta atividade.

**Próximo:** corrigir distinção entre timestamp duplicado e regressão de CPU, validar em testes, preparar C2 e cargas médias em bancadas inéditas; não repetir o piloto C4 nem reutilizar C3/C4 históricos. V12 permanece NÃO APROVADO.

## 15/11/2026 — Etapa 11: auditoria seletiva da pesquisa Perplexity

**Recebidos:** pesquisa_metodologica_e11_perplexity.md (dossiê 586 linhas) e referencias_e11_perplexity.bib (14 entradas F01–F14). Triagem editorial e consulta externa a fontes primárias realizadas sem executar novos experimentos, modificar o núcleo funcional ou alterar o texto acadêmico aprovado.

**Escolha:** quatro estudos científicos centrais (F01 metodologia reprodutível, F02 variabilidade, F03 efeito da ordem, F05 inferência/IC) + quatro documentos técnicos oficiais candidatos (F09 cgroup v2, F10 Node metrics, F11 Kubelet Summary API, F13 kind). F04/F06/F07/F08 não entram automaticamente; F12/F14 reservados a decisões concretas de Docker/recursos. Todos os artigos centrais são em inglês, idioma permitido; futura redação será autoral em português, sem tradução literal/cópia massiva.

**Arquivos preparados:** docs/tcc2/etapa-11-auditoria-seletiva-perplexity.md e docs/tcc2/etapa-11-referencias-curadas-candidatas.bib. NÃO adicionar diretamente ao main.bib antes de revisão de duplicidades, integração ao estilo abntex2-alf e capítulo da metodologia. Referências técnicas já existentes sobre Docker/Kubernetes devem ser deduplicadas quando necessário.

**Impacto no protocolo:** definir lote como unidade independente, distribuição por blocos, desfecho primário tempo de lote, documentação de limites/gerador/warmup real e distinção de memória e CPU; nenhum número de repetições foi validado como suficiente de maneira universal. Resultados quantitativos continuam exclusivamente os pilotos observados; V12 NÃO CONCLUÍDO.

## 15/11/2026 — E11-I04: C2 experimental preparado e tratamento de timestamps CPU revisado

**Código em branch tcc2/desenvolvimento:** benchmark/collector.py distingue timestamp kubelet repetido com contador crescente de regressão real; contador monotônico é aferido na ordem das coletas, timestamps colapsados para no máximo uma observação temporal representativa e margens ambíguas bloqueiam atribuição de delta à janela de carga. Também valida consistência aproximada entre duração UTC e perf_counter_ns. Foram adicionados testes unitários de timestamp duplicado, regressão, borda ambígua e relógios incoerentes (não executados no Windows ainda).

**C2 piloto isolado preparado:** benchmark/docker_c2.py (PLAN_ONLY por padrão e MUTANTE somente com --execute) cria nova rede Docker bridge interna e contêineres exclusivos para source, logic, executor e cliente, usando imagem C2 funcional aprovada, teto nominal 0,5 CPU por contêiner, memória 256 MiB serviços / 128 MiB cliente; não publica portas. Cada rodada usa snapshot e lote únicos, preservando evidências e estados após falha. Arquivo tests/test_benchmark_docker_c2.py contém testes sintéticos sem acesso ao Docker. Não houve aplicação, nova rede/container ou benchmark realizados pela IA.

**Ressalva científica:** leituras CPU e memória propostas para C2 via docker exec dentro dos contêineres são intrusivas, interferem nos cgroups que observam e permanecem dados diagnósticos apenas. Não comparar CPU, memória ou percentuais de C2 à Summary API de C3/C4 antes de calibrar ou substituir o coletor. Rede bridge Docker e rede kind não isolam causalmente overhead do orquestrador.

**Documento:** docs/tcc2/etapa-11-e11-i04-bancada-c2.md. **Próximo E11-D06:** sincronizar Git, executar compileall/unittest para toda instrumentação e emitir plano C2 somente leitura para fixture 100 em diretório inédito; depois auditar falhas antes de liberar PILOTO C2. V12 segue pendente.

## 15/11/2026 — E11-D06: falha de asserção no teste Docker C2 (piloto não iniciado)

**Evidência PowerShell:** commit local `248f7b9425b5bfd089bc68885e852eb025e9909a`; `compileall` prosseguiu sem erro; **15 de 16** testes sintéticos passaram. A única falha foi `test_client_uses_same_image_but_different_entrypoint` porque `assertIn('time.sleep(86400)', cmd)` buscava item exato na lista de argumentos, mas o último item real era `'import time; time.sleep(86400)'`. Não há demonstração de erro na criação do cliente; trata-se de asserção escrita incorretamente.

**Segurança:** script de E11-D06/P03 interrompeu após erro de unittest e ANTES de `python -m benchmark.fixtures`, Docker network create, criação de contêineres, snapshot ou POST. Portanto piloto C2 NÃO executado; C3/C4 preservados.

**Correção commit `7f4d94cd45ae29ef2bb9aed3e9510d9cfad99347`:** validar `cmd[-3] == IMAGE_TAG`, `cmd[-2] == '-c'` e verificar substring `time.sleep(86400)` em `cmd[-1]`. Alterado somente `tests/test_benchmark_docker_c2.py`, sem alteração no runtime do controlador. **Ainda não validado no Windows** após commit.

**Próximo:** sincronizar branch com Git limpo, repetir suíte `test_benchmark*.py` e somente se PASS atualizar `expectedHead` do script do piloto para `7f4d94cd45ae29ef2bb9aed3e9510d9cfad99347`, rodando novamente o procedimento E11-D06/P03 uma única vez. Se qualquer verificação falhar, não criar bancada. V12 permanece pendente.

## 15/11/2026 — E11-D06 PASS e E11-P03 Docker C2: piloto funcional auditado

**Execução Windows:** HEAD `ad2092c085ec2379ba859b2007038a727664e9b5`; 16/16 testes E11-D06 PASS; Docker 29.9.3. Novo C2 em rede `tcc2-pon-e11-c2-p20261115-225314` com quatro contêineres exclusivos. 100/100 HTTP 200, 86 mudanças, 49 mudanças de condição, 25 efeitos iguais ao oráculo, zero divergência de resposta; 10/10 checks funcionais, 4/4 transporte, 0 reinícios.

**ZIP original auditado:** 27.261 bytes, SHA-256 `8f5d3336f1fe7d3d7ce052cd0d93381d9b5bd6f0b3db0db2d664df5da2b32a01`, 22 entradas com CRC válido, 21/21 hashes internos. Tempo exploratório: 2,867092063 s, 34,88 req/s, RTT mediana 19,99 ms e p95 101,22 ms. Uma única rodada — **não permite inferir vantagem C2/C3/C4**.

**Telemetria:** 16 amostras de cgroup via `docker exec` intrusivo, sem falha de coleta, porém `measurement_approved=false`; contador CPU e pico de memória não podem ser atribuídos exclusivamente ao lote nem comparados à Summary API do Kubernetes. Contadores `cpu_nr_throttled` cumulativos cresceram durante observação, com valores já positivos antes da carga. **V12 NÃO iniciada.**

**Laudo:** `docs/tcc2/etapa-11-e11-p03-auditoria-c2-piloto.md`. **Próximo:** coletor C2 de recursos não intrusivo, política de calibração, piloto médio 1000 em nova bancada, sem tocar em bancadas usadas/históricas.

## 15/11/2026 — E11-I05: sonda não intrusiva Docker Engine API preparada; E11-D07 pendente

**Motivação:** piloto C2/100 funcional E11-P03 aprovado, mas a telemetria de recursos via `docker exec` injeta processos nos mesmos cgroups, não permitindo atribuição limpa de CPU/memória do lote nem comparação direta com Summary API do Kubernetes. C3/C4 também ainda necessitam calibração temporal. V12 NÃO executada.

**Novo código:** `prova-conceito/benchmark/docker_engine_api.py`: sonda por requisições **somente GET** da Docker Engine API (`/containers/{id}/stats?stream=false&one-shot=true`) através de **named pipe Windows local**, sem executar processos dentro dos contêineres e sem TCP/SSH. Por padrão `PLAN_ONLY`; `--probe` consulta os 4 contêineres do piloto C2 antigo já gasto, com validação de nomes, IDs, imagem, label e restartCount. Gera JSONL/CSV, relatório e ZIP/SHA-256. `tests/test_benchmark_docker_engine_api.py` adiciona testes unitários de HTTP/1.1 chunked/Content-Length, sem Docker real. **Compatibilidade do named pipe e operação efetiva ainda não verificadas no Windows**.

**Limites:** `cpu_stats.cpu_usage.total_usage` é cumulativo em ns; `memory_stats.usage` é uso bruto, não `workingSetBytes`, e `usage - inactive_file` é valor derivado similar à CLI no cgroup v2, não pico/RSS. A coleta via daemon ainda perturba o host e exige ensaio de overhead. PASS_READ_ONLY significa campos disponíveis/monotônicos em repouso; jamais aprovação de métrica durante carga.

**Próximo gate E11-D07:** após Git limpo e `git pull --ff-only`, rodar `compileall` e `unittest discover -p test_benchmark*.py`, executar PLAN_ONLY e somente então `--probe` **de leitura** no C2 já usado `p20261115-225314`, preservando recursos e enviando novo ZIP/saída. Não executar snapshot nem novos pilotos até auditoria. Fontes técnicas: Docker Engine API e Docker Desktop FAQ.

## 15/11/2026 — E11-D07: sonda Docker Engine API SOMENTE LEITURA auditada

**Execução Windows:** Git HEAD `266b5872cd0cf6c8226ec830fc884fad6c4b1750`, 21/21 testes unittest aprovados; PLAN_ONLY passou, seguido de `--probe` SOMENTE leitura sobre quatro contêineres do E11-P03 C2 já gasto. A Docker Engine API 1.56 respondeu pelo named pipe local `npipe:////./pipe/dockerDesktopLinuxEngine`; não houve snapshot, benchmark, docker exec ou comandos mutantes no fluxo da sonda. `PASS_READ_ONLY` significa acesso a contadores, NÃO aprovação quantitativa de CPU/memória.

**RAR real recebido/auditado:** 7.223 bytes, SHA-256 `4417bab258fa48dd09fc42e73e9d0522dd299083e948208436abed34e043d4eb`; contém ZIP original 3.500 bytes SHA-256 `648bd8fb96384ec9495f10689522e0ca4f11a79b090ddb9e078d6ca1c11ed836`, 5 entradas, CRC 5/5 e 4/4 hashes internos válidos. `engine-stats.jsonl` / `.csv` consistentes: oito observações (duas por contêiner), CPU cumulativa sem regressão e memória bruta disponível; zero `issues`, zero `measurement_approved`. As duas leituras por papel distam ~1,57 s e aconteceram **em repouso após o piloto**, não delimitam carga. O segundo valor CPU client igual ao primeiro não prova ausência de trabalho em lote anterior.

**Laudo:** `docs/tcc2/etapa-11-e11-d07-auditoria-sonda-docker.md`. **Decisão:** sonda externa candidata APROVADA quanto à disponibilidade, mas NÃO calibrada quanto a efeito observador/tempo/definição da memória. Não executar 1.000 antes de E11-I06 integrar a coleta a bancada **nova** e validar mecanismos; preservar todos os experimentos históricos e pilotos. V12 pendente.

## 15/11/2026 — E11-I06: instrumento C2 externo integrado para lotes futuros

**Código publicado, ainda NÃO executado no Windows:** `benchmark/docker_engine_window.py` incorpora `EngineSampler` que usa somente Docker Engine API GET via Windows named pipe para estatísticas dos 4 contêineres C2; `benchmark/docker_c2.py` deixa de usar `cgroup_sample`/`Sampler` intrusivo e integra o monitor novo. Pré-voo da sonda antes de snapshot; baseline após snapshot; observações durante e após lote. `tests/test_benchmark_docker_engine_window.py` acrescenta 7 testes sintéticos. Não houve nenhuma nova carga ou modificação de namespaces/contêineres históricos na preparação.

**Gates instrumentais conservadores:** comparação UTC/perf_counter, frescor do relógio de origem Docker Engine, identidade do ID, monotonicidade CPU, >=10s de lote, >=5 fontes temporais, margens <=3s e gaps <=4s. `measurement_approved=false` e `memory_comparable_to_kubelet=false` SEMPRE até calibrar overhead e definir equivalência semântica de memória; deltas que englobam lote não equivalem a CPU exata.

**Documentação:** docs/tcc2/etapa-11-e11-i06-monitor-c2.md. **Próximo E11-D08:** sincronizar Git com branch limpa, verificar commit, executar Python compileall/unittest e emitir PLAN_ONLY em C2/1000 com fixture nova e sem `--execute`. Enviar saída para revisão antes de QUALQUER novo piloto mutante.

**Planejamento confirmado pelo documento original docs/tcc2/etapa-11-diagnostico-plano.md:** a Etapa 11 inclui E11-M01 (séries quantitativas controladas) e E11-A01 (auditoria dos ZIPs e completude) além da instrumentação e pilotos. Etapa 12 dedica-se à análise dos resultados. Ainda restam validação temporal/overhead, pilotos médios C2/C3/C4, protocolo congelado, séries estatísticas e auditoria final; sem prazo/porcentagem garantidos.

**Fortalecimento de segurança E11-I06:** a primeira leitura efetiva da Docker Engine API foi movida para ANTES do snapshot; falha de acesso à telemetria nesse ponto impede a primeira mutação. Continua necessária uma baseline posterior ao snapshot para delimitação do lote. Não há nova execução Windows comprovada.

## 15/11/2026 — E11-D08: validação sintética aprovada e C2/1000 liberado como piloto diagnóstico

**Evidência da execução PowerShell:** branch `tcc2/desenvolvimento`, HEAD `9d9e2998de46df2aa7ff5c0dfe73f59dba1309f5`; Python `compileall` PASS; **28/28** testes `unittest` PASS em **0,098 s** (duração da suíte, não do benchmark). `PLAN_ONLY` em C2 gerou plano para nova rede `tcc2-pon-e11-c2-p20261115-232603`, sem Docker run, snapshot ou POST. Nenhum benchmark foi realizado nesta validação.

**Fixture canônica 1000:** seed `20260502`, `run_id=e11-canonical-1000-20260502`; SHA-256 `inputs.jsonl` = `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, `expected.jsonl` = `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`. Composição: 1000 tentativas, 874 alterações, 126 no-ops, 500 transições de condição e 250 efeitos. Estado final esperado: `atA=10`, `atB=0`. Arquivo local: `prova-conceito/resultados-locais/e11-d08-20261115-232603/fixtures/s1000/inputs.jsonl`. O plano não é evidência de execução funcional da carga.

**Decisão:** liberar **somente um piloto diagnóstico E11-P04 C2/1000 em bancada NOVA**, com nova identificação `e11-c2-p...`, rede e contêineres inéditos e instrumento Docker Engine API (E11-I06) por GET externo. Gate no PowerShell: Git limpo/commit esperado, 28 testes, fixture SHA correto, PLAN_ONLY, Docker disponível e nomes nunca usados; somente então `--execute`. Em falha após esse ponto, preservar ZIP/rede/contêineres, **não repetir**. A nova coleta NÃO torna `measurement_approved` verdadeiro automaticamente.

**Pendências posteriores:** auditoria ZIP real E11-P04 e qualidade temporal de CPU; pilotos 1000 C3/C4 em novos namespaces; overhead, política de memória e aquecimento; congelamento do protocolo E11-M01; séries independentes controladas e auditoria E11-A01. V12 continua pendente.

## 15/11/2026 — E11-P04 C2/1000: auditoria ZIP real e qualidade instrumental

**PowerShell do usuário:** HEAD `52ec6e3fe609162b4b03aa3232dba5083c59402b`, 28/28 testes PASS, fixture/expected SHA canônicos válidos. Nova rede `tcc2-pon-e11-c2-p20261115-232946`, snapshot único e lote único de **1.000 operações**. ZIP real `run(2).zip` 189.105 bytes SHA-256 recalculado `cf6eb1acc121799e803f45322d671c1404afcfbd15401c52c4211dafdc8e3c19`; 24 entradas CRC OK, 23/23 hashes internos corretos. Reconstrução independente dos 1.000 HTTP 200 e logs: 874 notificações de atributos sem perdas, 500 condições, 250 efeitos iguais ao oráculo, estado final `atA=10,atB=0`, nenhum restart/fault. **PASS funcional**.

**Duração exploratória:** 20,210461674 s; 49,48 req/s; RTT mediana 19,11 ms; p95 nearest-rank 50,72 ms; apenas um lote. Telemetria Docker Engine API externa: **96 amostras** (24/papel), `cpu_window_adequate=true`, `cpu_counters_available=true`, `issues=[]`. CPU-s de bracketing: source 9,846899, logic 5,813650, executor 0,309241, client 0,838785 — **não exatos ou estatisticamente válidos como custo por lote**. Source: +175 períodos de throttling no bracket, 0,472 core médio com teto nominal 0,5 CPU; ponto de atenção para desenho experimental. Cada ronda de monitor demorou ~0,68 s com intervalo-alvo 1 s (efeito observador não calibrado). `measurement_approved=false`, `memory_comparable_to_kubelet=false`. CPU/memória como métrica secundária DEFINITIVA seguem bloqueadas.

**Laudo:** `docs/tcc2/etapa-11-e11-p04-auditoria-c2-1000.md`. Próximo: pré-verificações e pilotos C3/C4/1000 em novos namespaces, controle de instrumentação/ordem, plano congelado E11-M01 e auditoria E11-A01. NÃO reusar C2 piloto ou namespaces históricos. V12 não iniciada.

## 15/11/2026 — E11-D09: diagnóstico Kubernetes C3/C4/1000 preparado, não executado

**Ponto de partida:** E11-P04 C2/1000 PASS funcional, CPU temporalmente adequada mas ainda NÃO aprovada cientificamente (`measurement_approved=false`). C3/C4 1000 e E11-M01 não executados.

**Implementação:** `prova-conceito/benchmark/kube_preflight.py` prepara manifests locais novos para C3/C4 usando fixture canônica 1000, hashes, oráculo, namespace isolado e imagem C2 aprovada. Sem `--probe` é somente PLAN_ONLY. Com `--probe`, usa apenas `kubectl get` de nodes/namespaces/Kubelet Summary API para ambos os nós e `docker image inspect`, sem apply/create/exec/delete/snapshot/POST. Exige contexto kind-tcc2-pon, Ready, namespaces antigos presentes e futuros ausentes. Reporta timestamps Kubelet observados em dois instantes como disponibilidade e NÃO como medição sob carga. Produz YAML NOT-APPLIED, JSON, SHA-256 e ZIP.

**Testes:** `tests/test_benchmark_kube_preflight.py` cinco novos casos sintéticos: isolamento, validade de imagem, descoberta de namespaces, readiness, campos Kubelet e timestamps repetidos/regressivos. Não executados no Windows ainda; número esperado de testes totais 33, dependente da prova. Documento `docs/tcc2/etapa-11-e11-d09-diagnostico-kubernetes.md`.

**Próximo E11-D09:** Git pull limpo + compileall e unittest + `python -m benchmark.kube_preflight --label <novo> --fixture <fixture1000> --output <nova-pasta> --probe`. Revisar saída e ZIP antes de autorizar piloto C3/C4. Não aplicar manifests ou cargas nesta etapa; todas as bancadas históricas preservadas.

## 15/11/2026 — E11-D09 auditado: Summary API legível, sem avanço CPU entre consultas

**Evidência Windows + ZIP real:** 33/33 testes Python PASS; Git HEAD `70714f545a1dc4dc2b192a2833a446f2ef8b5462`, fixture/oráculo 1000 canônicos. `probe.zip` 15.632 bytes SHA-256 recalculado `3d348be564c20282473d120147a1d86f0347f8d7a47d2a5bb312b9c56e471636`, CRC 6/6, hashes internos 5/5. Nenhum apply, snapshot, benchmark.

**Planejamento:** C3 e C4 manifestos YAML inéditos isolados, 3 serviços + cliente em cada, namespaces candidatos `tcc2-pon-e11-c3-p20261115-234409` e `tcc2-pon-e11-c4-p20261115-234409` ausentes do cluster. Ambos nós kind Ready, namespaces históricos preservados, Docker image ID conferido.

**Resumo de Kubelet em repouso:** cinco contêineres históricos worker e um control-plane com CPU e memória válidas; em duas leituras espaçadas ~2,2 s, **0/5 e 0/1** com timestamps CPU novos e nenhum aumento de contadores (memória também com timestamps iguais). No worker idade das fontes CPU ~0,8 a 12,1 s; no control-plane **14,9 a 17,2 s**. Nenhuma regressão, mas **sampling_approved=false**, status `PASS_READ_ONLY_WITH_TIMESTAMP_WARNING`. Estes dados NÃO demonstram falha sob carga nem autorizam usar CPU/memória como métricas quantitativas confiáveis.

**Laudo:** `docs/tcc2/etapa-11-e11-d09-auditoria-kubernetes-readonly.md`. **Próximo:** E11-D10 de leitura com intervalo 10s e label/output novos para estimar atualização em repouso. Depois decidir se pilotos C3/C4 1000 avançam com foco na validade funcional/latência e CPU secundária exploratória, ou se exigem refinamento de instrumentação. Não aplicar manifests agora. V12 pendente.

## 15/11/2026 — E11-D10 aprovado: timestamps CPU avançam parcialmente com 10 s

**ZIP real auditado:** `probe(1).zip` 15.672 bytes, SHA-256 `dd5f29c050a985219d4d2a2bebb88d4004afa639fdf409fe0825bbbed4866d5a`, 6/6 CRC, 5/5 hashes internos. Git execução `3f8e80d6c44cdc8a3a4ffbde4e48a75ae27cf828`; `PASS_READ_ONLY`, sem apply/snapshot/benchmark. Ambos os nós kind Ready, históricos presentes, novos namespaces C3/C4 planejados ainda AUSENTES.

**Kubelet Summary em repouso, duas consultas separadas ~10,3 s:** worker 3/5 timestamps CPU novos, 2/5 ainda iguais; control-plane 1/1 novo, sem regressões. Worker com duas fontes na última captura **12,187 s e 17,187 s** antigas; control-plane ~7,289 s. Aumentar o intervalo de 2 para 10 s resolve parcialmente alerta de E11-D09, mas **não** estabelece atualizações uniformes durante carga nem aprovação de CPU/memória; `sampling_approved=false` permanece. Nenhum evento de aplicação introduzido.

**Laudo:** `docs/tcc2/etapa-11-e11-d10-auditoria-frescor-kubelet.md`. **Próximo E11-D11:** preparar C3/1000 somente em namespace NOVO, verificar imagem/nós/estado frio e cliente, sem snapshot/POST. Após auditoria, E11-P05 único; C4 somente depois. Preservar C3/C4 históricos e C2 pilotos. E11-M01 / A01 pendentes.

## 15/11/2026 — E11-D11: bancada C3/1000 criada e auditada, estado frio ainda não comprovado

**Execução local PowerShell:** Git HEAD `2d5b789ead6d73a2545c3453e31e7c654fdee9e9`, 33/33 testes PASS. Namespace Kubernetes **novo** `tcc2-pon-e11-c3-p20261115-235728` criado com 3 Deployments/Services e 1 Pod cliente; run_id reservado `e11-c3-p20261115-235728`. Rollouts concluídos; 4/4 Pods Ready no worker, 0 reinícios, imagem e limites corretos. Transcrição reporta UIDs históricos C3/C4 preservados.

**ZIP real auditado:** 31.500 bytes, SHA-256 `651c0c447e8ab5aea16fd2554436d1cf939108f09f52d49c06472673043f44db`; 8/8 CRC. Preflight ZIP interno 15.658 bytes, SHA-256 `bfb4551661eb8eb640863d9aecf7453716dafa93139d6ff5d5198501398c20a4`, 5/5 hashes de arquivos internos válidos. Manifest C3 SHA-256 `c1960450e1a9744dd983471aeee779f19a908b90fa6a10ae8c9ca094701aa09a`. `pods-c3.json` confirma quatro UIDs distintos e condições Running/Ready.

**Limitação:** arquivo ainda NÃO prova estado frio interno (sem `states-cold.json`, GET `/state` ou logs), nem snapshot ou carga executados. `PASS_READ_ONLY_WITH_TIMESTAMP_WARNING` no preflight de Kubelet histórico não autoriza CPU/memória científica. **E11-D11 aprovado apenas como preparo/isolamento da bancada.** No E11-P05, o `benchmark.runner` deve confirmar estado frio ANTES de snapshot; falha bloqueia mutações. Não repetir snapshot/carga no namespace após primeira tentativa. **Laudo:** `docs/tcc2/etapa-11-e11-d11-auditoria-preparacao-c3-1000.md`. E11-M01/A01 pendentes.

## 16/11/2026 — E11-P05: C3/1000 funcional PASS, CPU/memória reprovadas

**Fonte:** ZIP real `run(3).zip`, 178.711 bytes, SHA-256 recalculado `66e071c8c32130978cd220472cabb91029ab7b0e38a2bbd3f3c8fe2900ed0b09`, 22/22 CRC e 21/21 hashes SHA-256 internos. Transcrição: 33/33 testes Python PASS, HEAD `2dcdc230f0777a8b902298c4bd6c582539fe709a`, namespace novo `tcc2-pon-e11-c3-p20261115-235728`. ZIP comprova cold state real, snapshot único e três Pods de serviços estáveis no mesmo worker, 0 restarts.

**Auditoria independente:** 1.000/1.000 HTTP 200, 874 mudanças, 126 no-ops, 874 notificações atributos sem perdas, 500 transições sem perdas, 250 efeitos semanticamente idênticos ao oráculo. Estado final `atA=10,atB=0`; check_run 10/10, transporte 4/4. Lote 20,236690945 s (49,4152 req/s), mediana HTTP 18,4104 ms, p95 49,8723 ms. Apenas uma rodada exploratória, sem inferência comparativa C2/C3.

**Kubelet:** 76 observações JSONL (19 por papel incluindo cliente), 0 erros e clocks UTC/perf coerentes, mas fonte de CPU repetida: 3 timestamps distintos no source, 3 no logic, 2 no executor. Último timestamp de origem 03:06:41/42/30 UTC é anterior ao término do lote 03:06:43.953552, logo **sem bracketing completo**. `cpu_window_adequate=false`, `memory_window_adequate=false`, `usable_cpu=false`, `usable_memory=false` com seis alertas. Não converter métricas em custo científico. Valores working set são só amostras exploratórias.

**Laudo:** `docs/tcc2/etapa-11-e11-p05-auditoria-c3-1000.md`. **Decisão:** C3 agora gasto e intocável para novos snapshots/cargas. Próximo E11-D12: preparar nova bancada C4/1000, nova namespace, sem snapshot/benchmark. E11-P06 somente após auditoria de preparo. Ainda falta calibração de recursos, E11-M01 e E11-A01.

## 16/11/2026 — E11-D12 interrompido por PowerShell quoting; E11-R01 preparado

**PowerShell:** HEAD `dd47bb62e6ff1d4d61667e260d4f015be374f998`, 33/33 testes PASS. Namespace C4 NOVO `tcc2-pon-e11-c4-p20261116-001328` criado com todos os recursos; 4 Pods Ready, UID informado, sem snapshot/benchmark reportados. Falha exclusivamente na chamada `python -c $checkCold` com `NameError: name 'status' is not defined`, compatível com perda de aspas na passagem de script multiline do PowerShell; estado frio **não confirmado**. **Não repetir apply; não executar snapshot/carga.**

**ZIP realmente enviado:** somente `preflight.zip` ANTERIOR ao apply, 15.635 bytes SHA-256 `a48ef81ad9cd11db456387990b01e53579f2a5076e785b29f49315854568d02d`, 6/6 CRC e 5/5 hashes internos válidos. Não é o ZIP pós-apply, que não chegou a ser criado. Não confundir resultado do preflight com evidência do estado C4 após criação.

**Correção preparada:** `benchmark/kube_c4_recovery.py` (testes `test_benchmark_kube_c4_recovery.py` + cinco casos) consulta SOMENTE get/logs/GET /state, compara Pods com `pods-c4.json` salvo, compara históricos com `historical-before.json`, bloqueia UID/restart/imagem/node divergentes, identifica estado frio. Gera novo ZIP sem alterar recursos Kubernetes. Não executado no Windows ainda. Registro `docs/tcc2/etapa-11-e11-d12-erro-powerShell-recuperacao.md`.

**Próximo gate E11-R01:** git pull limpo, compileall, testes (esperados 38), rodar módulo com namespace/run já criados e pasta original E11-D12; enviar saída/ZIP para auditoria. Após PASS_COLD_READ_ONLY, preparar E11-P06 único. Nenhuma modificação em C2/C3 históricos.

## 16/11/2026 — E11-R01 auditado: C4/1000 em estado frio e com identidades intactas

**ZIP real recovery.zip auditado:** 10.840 bytes, SHA-256 recalculado 96cd8d47a3b4b64972a69d776077afd1e7e4b8156877a9f81e460a8cc3a18c62, 8/8 CRC válidos, 7/7 hashes internos. Execução HEAD 10c29585ef8846a402b302cc577d7538ee548ec0, 38/38 testes PASS.

**C4 namespace tcc2-pon-e11-c4-p20261116-001328:** 4/4 Pods Running/Ready no desenho virtual correto (logic no control-plane, os outros + cliente no worker), UIDs e containerIDs iguais aos da criação E11-D12, zero restart. Nenhuma mudança nos UIDs históricos C3/C4 originais e piloto C3. states-cold.json comprova ready=false e run_id=null nos três serviços, source atA/atB=0, logic attributes/condition=null, executor approved=null, sem ledgers/effects/fault. Sem snapshot, sem carga e sem apply na recuperação.

**Laudo:** docs/tcc2/etapa-11-e11-r01-auditoria-recuperacao-c4.md. Decisão: E11-R01 PASS_COLD_READ_ONLY, bancada liberável para UM piloto C4/1000 E11-P06 com preflight frio obrigatório antes de snapshot e guarda de IDs. A etapa de execução e resultados C4 ainda NÃO aconteceram. CPU/memória Kubelet continuarão exploratórias até qualidade temporal e calibração. E11-M01/A01 ainda pendentes.

**Instrumentação de continuidade E11-P06:** script versionado `prova-conceito/scripts/e11_p06_c4.ps1` publicado para o piloto C4/1000. Sem `-ExecuteOnce`, executa apenas testes, guardas, confirmação de imagem/Pods/fixture e PLAN_ONLY. Com `-ExecuteOnce`, revalida as identidades e chama o `benchmark.runner` uma única vez, que ainda confirma cold state/logs ANTES do snapshot. Requer Git sincronizado e recovery-report.json real do E11-R01 com hash auditado; nenhum `kubectl apply` ou recriação de namespace. **NÃO há evidência de E11-P06 realizado ainda.**

## 16/11/2026 — E11-P06 C4/1000: auditoria do ZIP real e fechamento dos pilotos médios

**Evidência efetiva** `run(4).zip`, 178.954 bytes SHA-256 recalculado `4a39d39b227ec8dd0a74a24233cf364cb165df2173655c54513361033f56c847`; 22/22 CRC e 21/21 hashes internos válidos. Git HEAD execução `5ae84606dde4262a0025ed8f8719a3a8d88b9d2f`, 38/38 unittest PASS, `PLAN_ONLY` e execução única em `tcc2-pon-e11-c4-p20261116-001328` (run_id `e11-c4-p20261116-001328`). ZIP confirma cold state verdadeiro, um único snapshot e topologia estável, 0 restarts; logic-engine no control-plane virtual e demais papéis/cliente no worker virtual, mesmo host físico.

**Reconstrução independente:** 1.000 HTTP 200/1.000 respostas canônicas, zero divergências; 874 mudanças e 126 no-ops, 874 notificações atributo e 500 condição recebidas sem perdas e em ordem, 250 efeitos iguais ao oráculo. Final `atA=10,atB=0`, sequências 374/500, condition_sequence=500, sem fault. `check_run` 10/10, transporte 4/4 PASS.

**Tempo exploratório (UMA rodada):** `T_batch=19,923379794 s`, `1000/T=50,1923 req/s`, RTT mediana 19,3446 ms, p95 nearest-rank 44,8173 ms, p99 94,8927 ms. Não inferir diferença estatística C2/C3/C4 com apenas um lote cada.

**Instrumental Kubelet reprovado:** 76 observações (19/papel), 0 erros, apenas **2 timestamps distintos CPU por serviço**, e nenhum timestamp da fonte posterior ao fim da carga. CPU/memória `window_adequate=false`, `usable_cpu=false`, `usable_memory=false`, seis alertas, sem bracketing nem pico exclusivo de lote. Working-set somente amostrado; métrica diferente da memória bruta Docker. CPU C2 coberta temporalmente mas ainda não aprovada cientificamente, com throttling em source.

**Laudo:** `docs/tcc2/etapa-11-e11-p06-auditoria-c4-1000.md`. **Decisão:** pilotos de 1.000 concluídos funcionalmente em C2/C3/C4, C4 agora gasto para novo snapshot/POST; não repetir. Próximos: fechar E11-M00 (protocolo/recursos/ordem/aquecimento/métricas), E11-M01 séries independentes com novas bancadas frias e E11-A01 auditoria integral; Etapa 12 análise. Não executar 10.000 até avaliar capacidade e medidas secundárias. V12 não iniciada.

## 16/11/2026 — E11-M00 ABERTO: proposta de fechamento metodológico, SEM experimentos

**Origem verificada:** branch `tcc2/desenvolvimento` estava exatamente no commit `27132a9bd155a9b5639c5a2cdb1502692a5282f9` antes deste registro. Consultados os laudos E11-P04 (C2), E11-P05 (C3), E11-P06 (C4), a Etapa 05 e o plano inicial da Etapa 11. Os três pilotos de 1.000 são PASS funcionais (1.000 HTTP 200, 874 mudanças, 500 transições, 250 efeitos por cenário), mas representam apenas uma rodada cada. CPU/memória continuam **NÃO APROVADAS para comparações científicas**.

**Entregável novo:** `docs/tcc2/etapa-11-e11-m00-plano-fechamento-metodologico.md`, commit `75caabc6434b9608653d76f140a91a917f3ee734`. Documento registra **PROPOSTAS, ainda NÃO congeladas**: matriz primária C2/C3/C4 com fixture canônica de 1.000, n=10 por cenário (30 rodadas independentes planejadas), dez blocos de ordem alternada, nova bancada fria/run_id/snapshot único por rodada, GETs de aquecimento não mutante, quotas documentadas e comparação primária por `T_batch`/RTT/vazão. Carga 100 apenas para sanidade; 10.000 condicionada a aditamento prévio. CPU e memória apenas exploratórias até calibração e semântica comum; cronometração primária proposta sem sonda periódica de recursos no lote, exigindo preparo do harness.

**Gates pendentes do E11-M00:** validar política de interrupção e substituições, confirmacão de limites comparáveis e condições do host, modo sem sampler em C2/C3/C4, decisão sobre instrumentação secundária, revisão com orientador se pertinente e congelamento versionado `E11-M00-v1` com `READY_FOR_M01` ou `BLOCKED`. **E11-M01, E11-A01 e V12 ainda NÃO executados/aprovados.**

**Integridade operacional:** somente documentação versionada; nenhum benchmark, snapshot, POST, apply, criação, limpeza ou modificação das bancadas históricas. As redes/contêineres/namespaces dos pilotos C2/C3/C4 e demais históricos permanecem protegidos.

## 16/11/2026 — E11-M00A: matriz e estimandos definidos (SEM experimentos)

**Documento versionado:** `docs/tcc2/etapa-11-e11-m00a-matriz-quantitativa.md`, commit `320cfd94f85518a66b9a65451e9c5b9c073351e1`. A E11-M00A foi **definida documentalmente**, sem congelar E11-M00 completo nem autorizar E11-M01.

**Matriz:** contraste C2 Docker, C3 kind em um nó virtual e C4 kind em dois nós virtuais no **mesmo host físico**; fixture determinística `N=1000`, seed `20260502`, hash canônico aprovado `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, oráculo 250 efeitos; dez rodadas novas/frias por cenário, total de 30, em dez blocos pré-especificados e aproximadamente contrabalanceados. Pilotos E11-P04/05/06 NÃO são réplicas definitivas. Não atribuir diferenças ao Kubernetes isoladamente.

**Desfecho:** `T_batch` com `perf_counter_ns` no cliente único Python, incluindo serialização e laço de envio/recebimento (protocolo HTTP/1.0, sem garantia de TCP keep-alive), e vazão derivada. Unidade experimental = rodada/bancada, não 1.000 RTTs independentes. Contrastes temporais pareados por bloco, relatório descritivo e sem inferência confirmatória antecipada. Carga de 10.000 fora da campanha principal, condicionada a avaliação separada.

**Pendentes para E11-M00B/C:** política de aquecimento realmente reprodutível, limites/quotas equivalentes e pressão do host, instrumentação primária sem efeito observador não calibrado, CPU/memória comparativas BLOQUEADAS, guardas de identidade e histórico, política de interrupções/substituições, congelamento da versão E11-M00-v1. E11-M01/A01 e V12 permanecem não executados. **Nenhum benchmark, snapshot, POST, `kubectl apply`, alteração/exclusão de bancadas históricas ou medição nova foi executado nesta atividade.**

## 16/11/2026 — E11-M00B: instrumentação sem sonda preparada, validação real PENDENTE

**Inspeção do código e laudos:** C2 sondava Docker Engine API durante o lote com potencial efeito observador (duração de ronda ~0,685 s e throttling no source), e C3/C4 sondavam Kubelet Summary com atualização de timestamps insuficiente; CPU/memória seguem NÃO APROVADAS para comparações definitivas. Tempo primário do cliente é `perf_counter_ns` interno; amostras de CPU/RAM não substituem RTT/tempo.

**Código de harness PREPARADO e versionado na branch:** `prova-conceito/benchmark/measurement_profile.py`, `benchmark/resource_contract.py`, alterações restritas em `benchmark/docker_c2.py` e `benchmark/runner.py`. Novo `--measurement-mode timing_only` desativa construção/início/fim do sampler em todos os cenários C2/C3/C4; grava modo e `metric_quality=NOT_COLLECTED` com contagens ausentes (`null`), sem inventar consumo zero. `resources_diagnostic` continua padrão por compatibilidade, mas permanece apenas diagnóstico. Modo temporal exige label `m...` e `run_id=e11-cX-{label}`, segregados dos pilotos `p...`. Kubernetes acrescentou guard fail-closed de requests/limits dos três Pods e Deployments + cliente, somente contrato declarado, não equivalência física de cgroups.

**Testes sintéticos criados, NÃO executados na máquina Windows:** `tests/test_benchmark_measurement_profile.py` e `tests/test_benchmark_resource_contract.py`. Nenhum compileall/unittest, validação real do novo modo, PLAN_ONLY, Docker/Kubernetes, snapshot, benchmark ou remoção foram realizados nesta atividade. A aprovação operacional do harness depende das evidências reais de execução de regressão no Windows.

**Documento:** `docs/tcc2/etapa-11-e11-m00b-controle-instrumental.md` (commits preparatórios de código e testes incorporados; HEAD de consolidação neste status). E11-M00B classificado como `PREPARED_NOT_EXECUTED`. Ainda pendentes: registrar/avaliar pressão e quotas efetivas do host, definir aquecimento final e política de falha/replicação, validar os guardas no Windows sem `--execute`, congelar E11-M00-v1 em M00C. **E11-M01, E11-A01, V12 não iniciados. Bancadas históricas preservadas sem tocar em estados, rede ou Pods.**

## 16/11/2026 — E11-M00B: PowerShell 38/38 PASS, porém sobre HEAD anterior

**Evidência recebida:** transcrição PowerShell informa branch `tcc2/desenvolvimento`, HEAD **`5ae84606dde4262a0025ed8f8719a3a8d88b9d2f`**, `Ran 38 tests in 0.096s`, `OK`, sem erros exibidos. Tempo de **suite Python**, NÃO benchmark. Arquivo TXT bruto/hash não fornecido; `compileall` sem marcador independente de exit code, embora nenhum erro tenha sido exibido.

**Auditoria de versão:** comparação GitHub entre o SHA reportado e a branch mostrou **17 commits à frente**, incluindo instrumentação e testes E11-M00B. Os módulos novos `test_benchmark_measurement_profile.py` e `test_benchmark_resource_contract.py` **NÃO aparecem** entre os 38 casos listados. **Decisão:** `LEGACY_REGRESSION_PASS` somente para código anterior, `M00B_NEW_CODE_NOT_TESTED` para a revisão atual; **NÃO liberar E11-M01**. Esperam-se 48 testes caso sejam descobertos os 10 casos novos sem outras alterações, **contagem ainda não executada**.

**Laudo:** `docs/tcc2/etapa-11-e11-m00b-auditoria-regressao-head-antigo.md`, commit `1776d4ced6a7693794fc09856041ee97bf35e47c`. Próximo gate seguro: sincronizar clone com `git pull --ff-only` **somente após confirmar working tree limpa**, confirmar HEAD atualizado, repetir `compileall`/`unittest` e enviar transcrição. Não usar `--execute`, alterar bancadas históricas ou realizar nova carga. E11-M00C/M01/A01/V12 permanecem pendentes.

## 16/11/2026 — E11-M00B: falha de compilação no novo harness e correção pontual

**Nova evidência primária (captura PowerShell do acadêmico):** clone já atualizado em `b20919f0bb8d405aeea54762ee22aec57e1ed92c`; `python -m compileall -q benchmark tests` falhou com `IndentationError: unexpected indent`, `benchmark/docker_c2.py`, linha 21. Os testes de unidade subsequentes **NÃO foram executados** porque o script interrompeu no `throw "Falha na compilação"`. Este erro é do harness adicionado na E11-M00B, não da aplicação distribuída nem das bancadas.

**Causa confirmada por inspeção do GitHub:** a edição do cabeçalho do executor C2 removeu acidentalmente o prefixo `from c0.io import`, deixando a linha incorreta ` read_jsonl, validate_input`. **Correção pontual versionada:** restaurada a linha `from c0.io import read_jsonl, validate_input`, commit **`b74b66a2204a20e13b806f77ae022024c4d75ebf`**, alterado exclusivamente `prova-conceito/benchmark/docker_c2.py`. Não houve execução de compilação no Windows após essa correção; **PASS ainda não demonstrado**.

**Próximo gate:** `git pull --ff-only origin tcc2/desenvolvimento` com working tree limpa, depois `compileall` e `unittest discover` (incluindo os 10 testes sintéticos novos). Não usar `--execute`, não tocar nos ambientes históricos. E11-M00C e E11-M01 continuam BLOQUEADOS até evidência de validação.

## 16/11/2026 — E11-M00B 48/48 PASS e E11-M00C PROTOCOLO V1 CANDIDATO BLOQUEADO

**Evidência primária do acadêmico recebida:** PowerShell efetuou `git pull --ff-only` para `2d237ba8f91cd5ba7d7f6c65a451d45bb7c1d21c`, mostrou `COMPILACAO: PASS`, `Ran 48 tests in 0.121s`, `OK`, `TESTES: PASS`. Foram listados e aprovados os 10 testes sintéticos adicionais (`MeasurementProfileTests` e `ResourceContractTests`). **Tempo de suíte, não benchmark**. Não se recebeu arquivo bruto de log nem saída explícita do `git status --porcelain` final. Sem evidência de erro no compileall/unittest desta revisão.

**Decisão técnica:** `E11-M00B_STATIC_REGRESSION_PASS` no SHA acima; correção prévia de `IndentationError` confirmada sintaticamente. **Não** equivale a verificação dinâmica C2/C3/C4 ou calibração do host. Laudo: `docs/tcc2/etapa-11-e11-m00b-auditoria-regressao-48-tests.md` (commit `3db2a87962d695432dd052f3d55132b4bcde4965`).

**E11-M00C avançado documentalmente:** arquivo `docs/tcc2/etapa-11-e11-m00c-protocolo-v1-candidato-bloqueado.md` (commit `442ac9c031c40efb15388f9f193018134c30636d`) registra candidata v1 com matriz C2/C3/C4, 10 blocos, `timing_only`, GET não mutante, controle de host, timeout 10 s/600 s, critérios funcionais, tentativas preservadas e proposta prospectiva de até **2 blocos completos substitutivos** exclusivamente por falha operacional exógena elegível, nunca por tempo lento nem falha sistemática.

**Status:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`. Faltam PLAN_ONLY C2/C3/C4 com fixture canônica e labels inéditos; inventário read-only de host/WSL2/Docker/kind, verificação de disponibilidade/quotas/imagens/identidades históricas; homogeneização do pré-aquecimento, registro de environment/backup e aprovação do procedimento final. **Não houve novo experimento, snapshot, POST, apply, execução de software no Windows pelo assistente ou modificação de bancadas históricas. E11-M01/A01/V12 NÃO iniciados.**

## 16/11/2026 — E11-M00C: três PLAN_ONLY PASS e inventário preliminar verificado

**Evidência PowerShell recebida:** `git pull --ff-only` com HEAD local `707d456f83dadbcea088924ed60e33dc8f3720a6`; Docker `desktop-linux`, cgroup `v2`, `NCPU=8`, `MemTotal=8245637120` B (~7,68 GiB anunciados pelo daemon), WSL2, ambos os nós kind `tcc2-pon-worker` e `tcc2-pon-control-plane` Ready, Kubernetes `v1.37.0`, runtime containerd `2.3.4`. Esse é inventário parcial, não recurso livre comprovado.

**Fixture gerada localmente, SEM execução de carga:** inputs SHA `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551` e expected SHA `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`, n=1.000, seed 20260502, 874 mudanças/126 no-ops/500 transições/250 efeitos. Os **três planos** C2/C3/C4 retornaram `PLAN_ONLY`, `timing_only`, `resource_sampling_during_batch=false`, `execute=false` com labels `m01-b01` e `run_id` respectivos; **não há novas medições**.

**Laudo** `docs/tcc2/etapa-11-e11-m00c-auditoria-plan-only-inventario.md` (commit `ef20465b81d16d1fde7683c8502ee7190feb3502`); candidata v1 atualizada para reconhecer gates PASS (commit `688ccb70fdf45a5bf327cf717900c4345efa7cf8`).

**Decisão:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`. Faltam consulta read-only de disponibilidade e identidades reais (imagem/rede/namespace), quotas efetivas e capacidade/pressão/disco, fechamento de política uniforme de preflight e backup, aceite dos critérios de falha/reposição, congelamento versionado. A confirmação sintática de nomes não é confirmação de inexistência de recursos. Bancadas históricas preservadas; **nenhum snapshot, POST, benchmark, apply, restart, delete ou limpeza foi realizado** nesta etapa. E11-M01/A01/V12 continuam pendentes.

## 16/11/2026 — E11-M00C: imagem e IDs da campanha confirmados somente leitura

**Fonte:** captura PowerShell do acadêmico após fast-forward para `5365ee4f13ffe76608f27b6e8edbaa6a501f6adf`. `docker image inspect` exibiu imagem aprovada `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`. Tabela de inexistência de `tcc2-pon-e11-c2-m01-b01` (rede), `tcc2-pon-e11-c2-m01-b01-*` (contêineres), namespaces `tcc2-pon-e11-c3-m01-b01` e `tcc2-pon-e11-c4-m01-b01`: **quatro `False`** no momento da consulta. Os dois nós kind reportaram cada um `CPU_ALLOC=8`, `MEM_ALLOC=8052380Ki`, **não somar** os nós virtuais como se fossem computadores físicos independentes. Saída de `git status --porcelain` sem alterações visíveis.

**Ausências:** os comandos Windows de RAM física e disco aparecem na captura, mas seus resultados **não são exibidos**; portanto não há validação de RAM host, espaço em disco, pressão ou cgroup quota/period efetivos. `allocatable` não é CPU/RAM livre. Não comprovar limite de contêineres que ainda não existem.

**Documentos:** `docs/tcc2/etapa-11-e11-m00c-auditoria-imagem-identidades-readonly.md` (commit `02c64c46f004fef010020363143deb12bae99d89`) e apêndice ao protocolo candidato (commit `45ea5f1ccbe911299a2d01251ed9920f44c6acf5`). **Estado:** gates de identidade e imagem `PASS`, inventário apenas parcial, protocolo `E11-M00-v1-CANDIDATE/BLOCKED_FOR_M01`. **Sem POST, snapshot, benchmark, apply, restart, delete ou mutação de histórico**; E11-M01/A01/V12 ainda não iniciados.

## 16/11/2026 — E11-M00C: capacidade Windows observada, pressão de RAM exige gate

**Fonte:** saída PowerShell fornecida pelo acadêmico: `RAM_HOST_TOTAL_GiB=15,84`, `RAM_HOST_LIVRE_GiB=2,73`, `DISCO_C_TOTAL_GiB=930,59`, `DISCO_C_LIVRE_GiB=65,03`. Correspondem a **17,2% de RAM física e 7,0% de disco C livres**, aproximadamente, na coleta pontual. O dado complementa o inventário anterior Docker `MemTotal=8245637120` bytes (~7,68 GiB no daemon), cgroup v2 e dois nós kind virtuais no mesmo host, sem provar capacidade livre real para ensaios.

**Avaliação de risco:** memória Windows disponível é relativamente restrita para múltiplas camadas (host/WSL2/Docker/kind e históricos). Por bancada, os quatro papéis têm **limites nominais agregados de 896 MiB** (3 × 256 MiB serviços + 128 MiB cliente), NÃO uso medido nem total dos componentes da infraestrutura; com 2,73 GiB livres não é possível concluir aprovação ou reprovação automática. Disco disponível 65,03 GiB, mas orçamento de 30 ZIPs e retenção ainda precisa ser documentado. **Não executar bancadas C2/C3/C4 simultaneamente**; preservar ambientes históricos e coletar pressão de host/WSL/Docker por pré-voo fora da janela de medição.

**Laudo novo:** `docs/tcc2/etapa-11-e11-m00c-auditoria-capacidade-windows.md` (commit `47b8ec22f08f6bd93d558810318e3cc5315eed46`). Protocolo candidato recebeu avaliação de capacidade e regras prospectivas (commit `75c9a4e5692319c458133faaf59e8112d5457f58`). **Status:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01` até verificar pressão/quotas, GETs e `environment.json`, preservação e freeze. Sem teste, POST, snapshot, apply, remoção ou alteração histórica.

## 16/11/2026 — E11-M00C: inventário Docker de repouso e risco de acumular bancadas

**Fonte:** transcrição PowerShell do acadêmico (`docker stats --no-stream`, `docker system df`, RAM livre Windows). **RAM Windows livre = 2,42 GiB** (antes, em consulta separada, 2,73 GiB; não inferir tendência). `docker stats` listou **22 contêineres ativos**: 20 históricos da aplicação/cliente e 2 nós kind (control-plane 870,2 MiB, CPU 14,30%; worker 930,4 MiB, CPU 7,37% em instantâneo). Esses contêineres kind compartilham host WSL2/Docker e a soma não equivale ao consumo exclusivo do Kubernetes nem à RAM livre da máquina. `docker system df`: imagens 10/3 ativos 3,859 GB, contêineres 23/22 ativos 4,78 MB, volumes 4/2 ativos 2,564 GB, build cache 65/0 ativos 3,027 GB; **reclaimable não autoriza limpeza**.

**Risco operacional:** 30 rodadas com 4 papéis cada, em cenários sucessivos, **não podem ser planejadas com todas as novas bancadas simultaneamente ativas** sem demonstrar capacidade. Embora a execução seja serial por cenário, reter cada nova bancada em execução produziria acumulação crescente e viés temporal. Somar limites nominais (896 MiB por bancada) não é prever consumo observado. Os 2,42 GiB de RAM livre são instantâneos; não autorizam automaticamente novas cargas.

**Decisão documental:** `docs/tcc2/etapa-11-e11-m00c-auditoria-pressao-docker-repouso.md` (commit `dd9caa0e3f0c864ebdd545bd2dc2438ee9eb9ed1`) e apêndice `## 12` no protocolo candidato (commit `e5ceece21aeeffd60eaa116e315f855d623bb5e7`). Proposta de protocolo: uma nova bancada por vez, arquivar e verificar ZIP+SHA fora da bancada, e definir mecanismo auditável de encerramento/remoção **APENAS de recursos novos M01** com allowlist e validação de identidade, mantendo históricos permanentemente preservados. **Nenhuma limpeza foi autorizada ou realizada**, nem `docker prune` ou `kubectl delete`.

**Estado atual:** `E11-M00-v1-CANDIDATE/BLOCKED_FOR_M01`; pendentes ciclo de vida seguro (ou STOP por capacidade), requisitos `environment.json`, GET/preflight uniforme, verificação prospectiva de quotas/capacidade e aprovação/freeze. **Sem experimento novo, snapshot, POST, apply, restart ou alteração de histórico**.

## 16/11/2026 — E11-M00C: GET uniforme, environment e auditoria ZIP PREPARADOS (SEM experimentos)

**Implementação no GitHub (somente harness):** criados `prova-conceito/benchmark/campaign_controls.py` (preflight final uniforme read-only), `benchmark/environment_snapshot.py` (metadados de host em `environment.json` antes de snapshot) e `benchmark/lifecycle_audit.py` (auditoria ZIP SHA-256/CRC e revisão de nomes de bancadas novas sem comandos destrutivos), além de integração `timing_only` em `benchmark/docker_c2.py` e `benchmark/runner.py`. Código da aplicação, Dockerfile, imagens, manifests de produção e bancadas históricas NÃO alterados.

**GET final uniforme proposto:** em cada cenário e papel uma chamada GET `/health/live`, uma GET `/state`, uma leitura de logs, verificação de inicialização fria e zero mutações antes de snapshot; grava `preflight-uniform.json`. Incide apenas em futuras execuções `timing_only`, não reabre pilotos. **GETs não aquecem cadeia funcional com POST**, e o histórico de readiness nativo de C2/C3/C4 ainda não é idêntico.

**Ambiente:** `environment.json` deverá conter Git SHA, SO/Python, Docker context e cgroup, RAM/CPUs anunciadas, imagem aprovada, disco e RAM Windows e nós kind quando aplicável. É leitura pontual pré-snapshot e NÃO aprova quotas/CPU/RAM comparativas.

**Arquivo e ciclo de vida:** `lifecycle_audit.py` deverá verificar ZIP, CRC e SHA por membro, status funcional `PASS`, IDs de campanha `m...` e presença de `environment.json`/`preflight-uniform.json`; `retirement_review_only()` devolve **`commands=[]`, `delete_authorized=false`**, nunca executa stop/delete. A política de remoção segura (apenas novos recursos com UID/ID e allowlist/backup) **não foi implementada nem autorizada**; se a capacidade impedir a campanha, STOP.

**Testes:** criados `tests/test_benchmark_campaign_controls.py`, `tests/test_benchmark_environment_snapshot.py`, `tests/test_benchmark_lifecycle_audit.py` com **15 casos sintéticos planejados**, ainda **NÃO executados** no Windows. Total esperado da suíte = **63**, apenas previsão (os 48 anteriores foram executados no SHA `2d237ba8...`). Requer `compileall` e `unittest` novos para detectar regressões, incluindo possível `powershell.exe` no Windows. Nenhum teste novo relatado como PASS.

**Documento detalhado:** `docs/tcc2/etapa-11-e11-m00c-preflight-ambiente-retencao-preparados.md` (commit `a3b02b640c3f49c6c4ada4f076a8367552f8cd58`), protocolo candidato M00C atualizado (commit `98be892d77fa33fb9d064fe2ad17e479d430f64f`).

**Estado formal:** `E11-M00-v1-CANDIDATE/BLOCKED_FOR_M01`. Pendentes regressão sintética, verificação real read-only do baseline em Windows, ownership/backup e tratamento seguro de novas bancadas, limites de pressão/STOP, teste de quotas efetivas antes de POST, aceite e congelamento do protocolo. **NENHUM snapshot, POST, benchmark, apply, rm/prune, restart, remoção ou alteração de qualquer bancada histórica nesta atividade.**

## 16/11/2026 — E11-M00C: 63 testes PASS no SHA antigo; preflight corrigido pelo contrato real

**Evidência do acadêmico:** após fast-forward para `4ba69a3464cb6c2e0d225875ea753a6133da1a18`, PowerShell reportou `COMPILACAO: PASS`, `Ran 63 tests in 0.284s`, `OK` e `TESTES: PASS`, incluindo 15 novos testes sintéticos E11-M00C. Esses 63 são PASS **exclusivamente na revisão testada**; `0.284s` é a duração da suite, NÃO do benchmark.

**Achado de revisão do código real:** `prova-conceito/c1/state.py` antes de snapshot retorna `LogicEngine.attributes=None`, `LogicEngine.condition=None` e `RuleExecutor.approved=None` (fonte tem atributos/contadores zerados). O preflight novo havia usado mocks com esses campos já inicializados e **rejeitaria indevidamente uma bancada realmente fria**. Corrigido `benchmark/campaign_controls.py`, ajustados fixtures sintéticos e adicionados dois testes, incluindo um usando diretamente os três objetos de estado de `c1.state` sem rede. C2/C3/C4 passaram a fazer a rodada final realmente ordenada por papel GET live, GET state, logs, também sem mutação.

**Auditoria:** `docs/tcc2/etapa-11-e11-m00c-auditoria-63-tests-e-ajuste-estado-frio.md` (commit `5db9baafebf8bae19120a5f9911876de97801351`). O código atualizado após correção **AINDA NÃO FOI COMPILADO OU TESTADO NO WINDOWS nesta versão**; total esperado = **65 casos**, apenas projeção. Requer atualização Git + compileall + unittest (sem `--execute`) e validação read-only de `environment.json` antes de congelar v1. **Sem experimentos, snapshots, POST, apply, rm, restart ou mutações nos históricos**. E11-M01/A01/V12 BLOQUEADOS.

## 17/11/2026 — E11-M00C: 65/65 testes PASS e inventário read-only 3/3 validado

**Evidência primária:** transcrição PowerShell enviada pelo acadêmico como arquivo `Texto colado(1).txt` nesta conversa. Fast-forward da branch `tcc2/desenvolvimento` e SHA reportado `f8b12606616fd6e13249a730a0ef8dbad4508d80`. Compilação: `COMPILACAO: PASS`. Suíte: **`Ran 65 tests in 0.311s` / `OK` / `TESTES: PASS`**, incluindo dois testes novos (estado frio real e objetos `c1.state` sem rede), além dos 63 anteriores. **0,311 s é tempo de suíte e não execução experimental**.

**Inventário real somente leitura executado pelo acadêmico:** `capture_environment` retornou `C2: ENVIRONMENT_READ_ONLY_PASS`, `C3: ENVIRONMENT_READ_ONLY_PASS` e `C4: ENVIRONMENT_READ_ONLY_PASS`; Windows reportou RAM livre de **2.159.898.624 bytes (~2,01 GiB)** e disco livre na localização do projeto de **72.307.068.928 bytes (~67,34 GiB)**. JSON temporário `tcc2-m00c-ambiente-20261117-192218.json`, SHA-256 reportado `7962B6F10BE59D93989AB064BA58C1E1449AFB94BCF6BEF29C9728CE3C8B7F9D` (arquivo JSON **não enviado nem hash recalculado aqui**). Dados pontuais sem demonstração de quotas efetivas, de consumo sob carga ou de capacidade livre garantida.

**Laudo:** `docs/tcc2/etapa-11-e11-m00c-auditoria-65-tests-environment-readonly.md` (commit `643fcb6e755124f70680530c79d89ab366ceb735`); protocolo candidato atualizado (commit `2e74c2db49b65d23131d1cdcc9ec2e91eb64889f`).

**Decisão:** `M00C_STATIC_TESTS_PASS` e `M00C_ENVIRONMENT_READONLY_PASS_C2_C3_C4`. Permanecem pendentes: política operacional segura de ciclo de vida de **somente novas bancadas** com backup/ownership/allowlist e resultado `PASS/FAIL` retido; confirmação de quotas efetivas antes de primeiro POST; limiares prospectivos e controles de pressão/STOP, orçamento de disco/retentativas, aceite e congelamento E11-M00-v1. **E11-M01/A01/V12 NÃO liberados**. Não houve novo benchmark, snapshot, POST, `kubectl apply/delete`, `docker rm/prune`, reinício ou alteração dos históricos neste registro.

## 17/11/2026 — E11-M00-v1: desenho pré-registrado, gates operacionais preparados, M01 BLOQUEADO

**Evidência anterior confirmada:** 65/65 testes sintéticos PASS, `compileall` PASS e `capture_environment` read-only C2/C3/C4 3/3 no commit **`f8b12606616fd6e13249a730a0ef8dbad4508d80`**, transcrição PowerShell do acadêmico. Os novos módulos/alterações desta atividade **não** foram testados na máquina Windows; não estender o PASS anterior aos arquivos modificados.

**Desenho prospectivo `DESIGN_FROZEN` documentado:** `docs/tcc2/etapa-11-e11-m00-v1-pre-registro-e-gates-m01.md` (commit `27e440db92dc11e4b04bf53dfe4958fafb508394`). Matriz fixa C2/C3/C4, n=10/10/10 com 10 blocos, fixture de 1.000/seed 20260502, duração `T_batch` e throughput, uma bancada nova por rodada; política de falha/retenção e até 2 blocos completos substitutivos somente por interrupção exógena documentada, sem rejeição oportunista de tempos lentos. CPU/RAM comparativas permanecem `NOT_APPROVED`. Pré-registro não é aprovação do orientador nem autorização para `--execute`.

**Novos controles de harness versionados:** `prova-conceito/benchmark/runtime_gate.py` e `benchmark/campaign_exclusivity.py`, com integrações `timing_only` em `benchmark/docker_c2.py` e `benchmark/runner.py`. Um único cenário M01 ativo por vez; gate de capacidade de **3 GiB RAM Windows livres e 15 GiB disco** (limiares conservadores operacionais, NÃO evidências científicas); aferição pré-snapshot de cgroup V2 em **somente quatro contêineres/Pods NOVOS**: `cpu.max=500m`, `memory.max=256MiB` por serviço e `128MiB` por cliente, `memory.swap.max=0`, `memory.current` válido e `oom/oom_kill=0`. Falhas = STOP, sem snapshot/POST, sem ajuste retroativo de quotas. O último valor real de RAM livre reportado foi **~2,01 GiB**, abaixo do piso de segurança: neste estado **M01 não poderia começar**.

**Evidência/retencão:** `lifecycle_audit.py` agora exige `capacity-gate.json`, `effective-quotas.json` e `campaign-exclusivity.json` no ZIP com status PASS, além dos anteriores. Nenhum mecanismo de cleanup foi implementado: `retirement_review_only()` continua com `commands=[]`, `delete_authorized=false`. Bancadas antigas `p...`/v03/v05/v06/c2/namespaces históricos continuam estritamente preservadas. Retirada futura só de bancada NOVA depende de backup externo íntegro, identificação imutável de recursos/UID, allowlist positiva, teste sacrificial e aceite explícito; caso contrário STOP por capacidade.

**Testes pendentes no Windows:** adicionados `tests/test_benchmark_runtime_gate.py` (**10 casos**), `tests/test_benchmark_campaign_exclusivity.py` (**5 casos**) e **um caso** em `tests/test_benchmark_lifecycle_audit.py`; a suíte passaria de 65 para **81 casos** se tudo carregar corretamente, **contagem prevista, não executada**. Validar `compileall` e `unittest` no SHA novo; registrar divergências e não executar benchmarks. Os novos gates de cgroup real só podem ser testados em novos recursos futuros, antes de snapshot, sem tocar históricos.

**Status operacional:** `DESIGN_FROZEN / IMPLEMENTATION_UNVALIDATED / M01_BLOCKED`. A próxima ação é regressão sintética (sem cargas). Ainda pendentes: aprovação formal de ciclo de vida de recursos **novos** e backup, prova de margens físicas, verificação efetiva dos cgroups quando houver um recurso novo autorizado e aceite final. **Nenhum Docker/Kubernetes foi executado ou mutado pelo assistente, nenhum POST/snapshot/benchmark/cleanup efetuado nesta atividade.**

## 17/11/2026 — E11-M00-v1: regressão 81/81 PASS no SHA e6e83ff, E11-M01 ainda bloqueado

**Evidência primária recebida:** transcrição de PowerShell `Texto colado(2).txt` do acadêmico; `git pull --ff-only` fast-forward até `e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`. `ARQUIVOS: PASS`, `COMPILACAO: PASS` e `Ran 81 tests in 0.314s` / `OK` / `TESTES: PASS`; todos os casos listados com `ok`, incluindo 10 `RuntimeGateTests`, 5 `CampaignExclusivityTests` e 1 novo `LifecycleAuditTests`. Duração **0,314s da suíte unitária, não benchmark**. O `git status --porcelain` final não aparece no trecho recebido; não declarar árvore limpa a partir dessa ausência.

**Veredito:** `E11_M00_V1_SYNTHETIC_REGRESSION_PASS` no SHA exato; anteriores 65 testes PASS no SHA `f8b1260...`. Registro documental `docs/tcc2/etapa-11-e11-m00-v1-auditoria-regressao-81-tests.md` (commit `edf4f413b30ee41628f99b670bb61353cee40693`). Pré-registro E11-M00-v1 atualizado com gate sintético fechado e pendências de liberação (commit `e95508221c927a47d99192fdcb07346cff204a81`).

**Bloqueios ainda materiais:** memória livre Windows última observada ~2,01 GiB, abaixo do limite operacional pré-registrado de 3 GiB; cgroups reais `cpu.max=500m`, `memory.max=256/128Mi` e `memory.swap.max=0` não verificados em **bancadas novas**; ciclo de vida M01 com controle de ownership, IDs/UID, backup externo e autorização específica não implementado/aprovado; sem mecanismo seguro não é possível acumular novas bancadas respeitando exclusividade. Os dois nós kind compartilham host WSL2; CPU/RAM comparativas permanecem `NOT_APPROVED`.

**Decisão:** `DESIGN_FROZEN / SYNTHETIC_REGRESSION_PASS / OPERATIONAL_READINESS_BLOCKED`; **E11-M01/A01/V12 NÃO iniciados**, sem registro de 30 execuções novas. Nenhum comando mutante Docker/Kubernetes, snapshot, POST, restart, stop, rm/prune ou delete ocorreu nesta revisão documental; recursos históricos preservados.

## 17/11/2026 — E11-M00D: ownership de recursos novos e backup em modo review-only preparados

**Etapa atual (sem experimento):** pacotes `benchmark/ownership.py` e `benchmark/backup_integrity.py` implementados e versionados no GitHub. O primeiro comprova, com consultas exclusivamente read-only, labels positivas da nova campanha `m01`, exato `run_id`, IDs imutáveis de rede/4 contêineres C2 ou UID de namespace/4 Pods C3/C4. O segundo valida ZIP original + cópia de local distinto por CRC, SHA-256 de todos membros e hash byte a byte, indicando se o filesystem é volume distinto. **Não cria cópia, não remove evidências e não garante independência física só por volume distinto.** Não houve execução dessas rotinas no computador Windows do acadêmico nesta etapa.

**Integração prospectiva:** `benchmark/docker_c2.py` adiciona labels `tcc2.e11/campaign=m01` e `tcc2.e11/run-id=...` exclusivamente nos `docker run` e `network create` de bancadas `m...` futuras; `benchmark/prepare.py` rotula só Namespace gerado de C3/C4 com label `m...`, sem editar históricos ou imagens. `benchmark/runner.py` e `docker_c2.py` passam a registrar `ownership-start.json` pré-snapshot. `benchmark/lifecycle_audit.py` exige tal arquivo na evidência PASS e possui `review_retirement_packet` com validação combinada ZIP/UID/backup — retorna **sempre `commands=[]`, `delete_authorized=false`**, nenhuma rotina de cleanup implementada.

**Testes preparados, NÃO executados:** 8 novos `tests/test_benchmark_ownership.py`, 5 `tests/test_benchmark_backup_integrity.py` e 2 adicionais `tests/test_benchmark_lifecycle_audit.py`: estimativa **96 testes** (81 da regressão anterior no SHA `e6e83ffa64e5074b6bcb80635dd472a2f3cf2401` + 15 novos), a ser confirmada no Windows com `compileall` e `unittest` na revisão HEAD nova. Nenhum PASS atribuído antecipadamente.

**Documento:** `docs/tcc2/etapa-11-e11-m00d-ciclo-vida-ownership-backup-reviewonly.md` (commit `fb8eaad935a083b9c11259ed8fd72bd2e66eb54a`) e aditamento §8 do pré-registro E11-M00-v1 (commit `c8ef30355b58b7c6d694cd57db3fa724a8299068`).

**Estado:** `DESIGN_FROZEN / M00D_IMPLEMENTED_UNTESTED / M01_BLOCKED`. Última RAM livre Windows real ~2,01 GiB, abaixo da margem de 3 GiB; quotas reais C2/C3/C4 ainda não comprovadas em bancada M01 nova; política destrutiva deliberadamente inexistente, com testes sacrificiais/aceite e backup real pendentes. **Nenhum novo benchmark, snapshot, POST, apply, stop, delete, rm, prune ou alteração de bancadas históricas.**

## 17/11/2026 — E11-M00D: compilação, 96/96 testes e GIT LIMPO na versão e86d2e8

**Evidência PowerShell (arquivo anexo `Texto colado(3).txt`):** `git pull --ff-only` fast-forward `e6e83ff` → **`e86d2e884f0bb70a22de4ba6409e8fe98713b40c`**, `COMPILACAO: PASS`, **`Ran 96 tests in 0.352s`**, **`OK`**, `TESTES: PASS`, **`GIT: LIMPO`**. Todos os 96 casos listados `ok`, inclusive 8 `OwnershipTests`, 5 `BackupIntegrityTests` e 2 novos `LifecycleAuditTests`, relativos a identidades/UIDs de bancadas novas, labels e SHA/CRC de ZIPs e à recusa de autorização automática para apagar recursos. **0,352 s é tempo da suíte unittest, NÃO tempo de benchmark.**

**Veredito:** `E11_M00D_SYNTHETIC_REGRESSION_PASS` no SHA testado. Laudo `docs/tcc2/etapa-11-e11-m00d-auditoria-regressao-96-tests.md` (commit `4b2b175b6795f603eb4c81dd954ff05a95e6af1c`). Nenhum novo benchmark, POST, snapshot, limpeza, `docker run` ou `kubectl apply/delete` demonstrado. Alterações futuras de código exigem nova regressão.

**Pendências explícitas:** RAM Windows >=3 GiB antes de criar bancada nova (última leitura reportada ~2,01 GiB; sem atualização nesta rodada), disco >=15 GiB, comprovação de quotas/swap em NOVOS cgroups antes de POST, cópia real/externa do ZIP, provenance UID/ID real e teste seguro de ciclo de vida de recursos **exclusivamente novos** com aprovação específica. Nenhuma rotina de stop/rm/delete foi implementada ou autorizada. Ambientes históricos permanentemente preservados neste escopo. `E11_M01_BLOCKED`; campanha definitiva 30 rodadas não iniciada.

## 17/11/2026 — E11-M00E: precheck de capacidade Windows PASS; Docker/kind ainda nao reconfirmados

**Evidência primária:** captura de tela PowerShell fornecida pelo acadêmico. Após `Get-CimInstance Win32_OperatingSystem` e `Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"`, output **`RAM livre: 9,11 GiB`**, **`Disco livre: 67,43 GiB`**, **`CAPACIDADE: PRECHECK PASS`**; supera os pisos operacionais prospectivos de 3 GiB RAM física disponível no Windows e 15 GiB disco. Esses números são amostras pontuais e não demonstram desempenho nem garantem capacidade durante a campanha. No início da sessão houve erros de digitação `cd..cd` e PSReadLine, sem impacto visível na posterior medição do bloco de capacidade. O PowerShell estava em `C:\Windows\system32`, não na pasta da prova de conceito.

**Atenção causal:** a RAM livre anteriormente reportada (~2,01 GiB) aumentou para 9,11 GiB; **não afirmar que Docker/WSL/kind continuam em execução** sem nova consulta, nem atribuir a melhora a um evento desconhecido. Antes de qualquer bancada sacrificial, verificar read-only `docker info`, `docker ps`, `kubectl --context kind-tcc2-pon get nodes`, namespaces e recursos históricos sem modificá-los. Conferir RAM de novo **com Docker e kind confirmadamente ativos**. Esta captura NÃO verifica a disponibilidade do Docker, quotas em novos cgroups, backup externo, ownership real ou política de retirada segura de novas bancadas.

**Decisão:** `E11_M00E_HOST_CAPACITY_PRECHECK_PASS_AT_OBSERVATION` e `E11_M01_BLOCKED`. E11-M00D já possui 96/96 testes sintéticos PASS e GIT LIMPO no SHA `e86d2e884f0bb70a22de4ba6409e8fe98713b40c`; nenhuma mudança de código foi necessária para registrar esta evidência. **Nenhum POST, snapshot, benchmark, criação, encerramento, limpeza ou mutação de históricos é alegado.**

## 17/11/2026 — E11-M00E: Docker e kind Ready, capacidade PASS, discrepância de contêineres históricos

**Evidência primária recebida do acadêmico:** consulta PowerShell `docker context show` → `desktop-linux`, `docker info` → `CPUs=8 RAM=8245641216 Cgroup=2`, `DOCKER: PASS`, `kubectl --context kind-tcc2-pon get nodes -o wide` → nodes `tcc2-pon-control-plane` e `tcc2-pon-worker` **Ready**, Kubernetes `v1.37.0`, Debian trixie, WSL2, containerd `2.3.4`. Endereços observados: control-plane `172.18.0.3`, worker `172.18.0.2`; não pressupor que IPs/UIDs históricos se mantiveram. Windows reportou `RAM_WINDOWS_LIVRE_GiB=8,81` e `DISCO_C_LIVRE_GiB=67,43`, com `CAPACIDADE: PRECHECK PASS`, acima dos pisos operacionais de 3/15 GiB. Capacidade é fotografia em repouso, não autorização para criar/executar bancada.

**Risco novo, NÃO RESOLVIDO:** o `docker ps --format '{{.Names}}'` mostrou **somente dois contêineres ativos**, os nodes kind. Consulta anterior `docker stats --no-stream` havia listado **22 contêineres em execução** (20 históricos de aplicação/pilotos e 2 nodes kind). A ausência de nomes em `docker ps` não prova exclusão: podem existir em `docker ps -a` como parados. **Não afirmar que foram removidos, reiniciados, nem assumir motivo da redução de memória.** Consultar em leitura `docker ps -a`, `docker network ls`, `kubectl get namespaces/pods -A` e conferir nome/status/identidade, sem iniciar/parar/deletar, snapshot ou POST. Histórico de pilotos continua intocável e não deve ser usado como bancada substitutiva.

**Decisão:** `E11_M00E_DOCKER_KIND_CAPACITY_PASS_AT_OBSERVATION` e `HISTORICAL_RUNTIME_STATE_REQUIRES_AUDIT`. Mesmo que histórico esteja intacto, a primeira bancada sacrificial NOVA ainda depende de aprovação operacional específica, checklist de unicidade/ownership/quotas, política de backup e encerramento seguro. **E11-M01 segue BLOCKED**. Nenhum experimento, criação, cleanup, restart ou mutação histórica é alegado nesta análise.

## 17/11/2026 — E11-M00E: 20 históricos Exited 137; históricos kind com reinícios; clientes Unknown

**Nova evidência primária PowerShell:** `docker ps -a` lista **20 contêineres históricos da aplicação/cliente com `Exited (137) 27 hours ago`** (8 dos dois pilotos E11-C2 e 12 das famílias C2/V03/V05/V06). Os contêineres continuam cadastrados, com IDs abreviados; há também um `tcc2-python-validacao` com `Exited (0)` e dois nós kind `Up 3 hours`. Redes Docker específicas de C2/V03/V05/V06/pilotos **ainda presentes**. `Exited 137` é compatível com SIGKILL, **não prova OOM sem `State.OOMKilled` ou eventos**. Não atribuir causalidade à memória ou a ações do acadêmico sem evidências.

**Kubernetes:** namespaces `tcc2-pon`, `tcc2-pon-c4` e 4 pilotos C3/C4 continuam `Active`; seus serviços de aplicação estão `Running`, mas **têm 1 restart** (aprox. 3h3m antes da consulta). Os quatro Pods `e11-benchmark-client` estão **`0/1 Unknown`**, não saudáveis. Componentes `kube-system` possuem múltiplas reinicializações (CoreDNS/kindnet etc.). Logo, o runtime histórico foi interrompido/reiniciado e **não se encontra no estado de execução dos pilotos anteriores**. Objetos/namespaces ainda existentes não significam continuidade do estado em memória.

**Impacto científico:** resultados pilotos anteriormente documentados não são automaticamente invalidados; manter artefatos e hashes, porém não executar POST/snapshot/recovery ou novas medições sobre histórico nem afirmar identidade temporal de ambiente. Campanha de 30 novas rodadas depende de condições revalidadas, sem mistura de épocas de host. Em auditoria M00E, investigar somente leitura `docker inspect .State` (OOMKilled/ExitCode/FinishedAt/Error) e `kubectl get pods -A -o json` (lastState/restarts). **Não iniciar, remover, recriar, reiniciar ou limpar históricos**.

**Documento:** `docs/tcc2/etapa-11-e11-m00e-auditoria-preservacao-historicos-apos-interrupcoes.md` (commit `d2edd6fe8251be4605db021fa1a29a975bb31785`), com fonte e ressalvas. **Status** `E11_M00E_HISTORICAL_RUNTIME_CHANGED_ROOT_CAUSE_UNKNOWN`; **E11_M01_BLOCKED**. Último precheck de capacidade passou com nodes kind ativos, RAM 8,81 GiB e disco 67,43 GiB, mas não libera série, novas bancadas ou quotas. Nenhuma mutação de histórico foi executada nesta atividade.
