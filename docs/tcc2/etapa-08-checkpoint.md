# Checkpoint compacto — Etapa 08 (13/11/2026)

## Estado funcional comprovado
- Branch de trabalho: `tcc2/desenvolvimento`; preservar `master` e `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.
- Etapa 07: C0/C1 mínimos comprovados; efeitos nos passos 3 e 7 para fixture de sete entradas; 39 testes da etapa.
- E08-I01: Git/Docker/WSL2 diagnosticados e válidos no Windows.
- E08-I02: parâmetros de hostname/interface de escuta aprovados por 42 testes `unittest` no Windows, commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`.
- E08-I03: **aprovado em E08-D08**. Build de `tcc2-pon:c2-e08-dbefcd2cf3d2` a partir do código `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` completou com `Build: 0`, resolução do digest específica `Registro: 0`, Python 3.13.18, UID 10001, imports e CLI retornando 0; Linux/amd64, 176 MB. Evidências E08-D08a/b recebidas; SHA-256 no documento de diagnóstico.

## Próximo incremento: E08-I04 / E08-D09
- Configurar rede Docker interna `tcc2-pon-c2`, sem portas publicadas e sem tocar no cluster kind.
- Iniciar três contêineres independentes a partir **da mesma imagem testada**: `tcc2-c2-rule-executor`, `tcc2-c2-logic-engine`, `tcc2-c2-attribute-source`; porta interna 8080, DNS por aliases iguais aos nomes dos papéis.
- Exigir evidência real de `docker ps`, `docker network inspect`, IDs distintos, três logs `listening` e GET HTTP interno `/health/live` de origem→avaliador e avaliador→executor.
- Deixar estados não inicializados (readiness 503), sem enviar fixture nesta rodada. Não concluir equivalência C2 nesta etapa parcial.
- **E08-D09 primeira tentativa falhou antes de criar recursos:** `docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'` retornou `template parsing error: function "org" not defined` no PowerShell. Captura `image(20261113-210012).png`, SHA-256 `4eaf907129c646850fe36ca5335c71f9073c398b0c17ce1e92e705885f796b18`. Correção: ler JSON completo com `ConvertFrom-Json`, depois comparar label. E08-D09 permanece pendente.

## E08-D09 aprovado em 13/11/2026
- Captura `image(20261113-210408).png`, SHA-256 `53ecd7f79bc5fe5c35282f3ec4ce70a55fad6f94af90581a9f6703e5228d49c1` (PNG original ainda fora do repositório).
- Rede `tcc2-pon-c2` bridge interna, três contêineres Running com IDs diferentes e sem portas publicadas. `SOURCE -> LOGIC` e `LOGIC -> EXECUTOR` responderam HTTP 200 (`live=true`); três estados `ready=false` antes do snapshot; logs listening na porta 8080.
- E08-I04 aprovado exclusivamente para implantação Docker, saúde, DNS e transporte HTTP; notificações e equivalência não verificadas.

## Próximo E08-D10
- Confirmar contêineres ativos e estados ainda não inicializados; enviar uma única inicialização `POST /init/snapshot` ao produtor e conferir encadeamento até executor.
- Exigir `ready=true` nos três, mesma versão de snapshot, valores e watermarks iniciais, zero efeitos. Não aplicar fixture ainda. Se falhar parcialmente, preservar contêineres e logs antes de outra tentativa.

## E08-D10 aprovado (13/11/2026)
- Captura original `image(20261113-210955).png`, SHA-256 `fb949fba22f6b79796adaded539f8f92a890ba3bee36b8a553ed07cab15c29af` (não versionada).
- Rede interna preservada. Três serviços passaram de `ready=false` para `ready=true` com mesmo `run_id=c0-minimo-v1` e versão `c0-minimo-v1:snapshot:0`. Atributos/seq. iniciais 0, condição false, executor sem efeitos; logs de snapshot send/mutation/ack e contêineres Up.
- **Não reenviar snapshot.** C2 não passou pela fixture.

## Próximo E08-D11
- Verificar pré-condições de zero mutações de `/attributes/change` via logs, estados iniciais e contêineres. Executar sete passos sequenciais da fixture versionada e preservar HTTP, logs, estados, SHA-256 e manifesto.
- Comparar efeitos/ordem/causalidade com `fixtures/c0_esperado.jsonl`, C0 e oráculo independente. Se falhar parcialmente, bloquear reexecução automática.

## Limitações e preservação
- Uma rede Docker/contêineres no mesmo Windows/WSL2 não constitui multinó físico.
- C2 funcional, V02/V04/V05–V07 via Docker, métricas, figuras finais e Kubernetes estão pendentes.
- Não apagar kind, contêineres anteriores ou evidências; não executar `docker system prune`.
- Documentação detalhada: `docs/tcc2/etapa-08-diagnostico-rede.md`.

## E08-D11 — ferramenta de ensaio publicada, ainda sem teste no Windows
- `prova-conceito/c2/runner.py` usa a biblioteca padrão e `docker exec` por argumentos (sem problemas de aspas PowerShell) para aplicar 7 passos somente após preflight de snapshot e logs limpos; não reinicia contêineres.
- `prova-conceito/tests/test_c2_runner.py` adiciona 3 testes de pré-condição. Esperados **45 testes** totais (42 anteriores + 3), não realizados ainda no host.
- Em caso de erro, salva logs e `validation.json` FAIL; não reexecutar a fixture automaticamente. Efeitos, C0/oráculo, estados, entradas e hashes são coletados para auditoria após o ensaio.

## E08-D11 — execução REAL aprovada no Windows (13/11/2026)

- Código do runner testado: `5eee8e7a7c931491d3668cc9472a46191de6180c`, build da imagem mantido `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- `Compilacao: 0`, 45 testes OK em 11,028 s (não benchmark), `Testes: 0`, rodada C2 `PASS` e `C2: 0` com 11 checks verdadeiros.
- Dois efeitos de regra em passos 3 e 7, igualdade sinalizada com manual/oráculo/C0; cinco eventos de atributo e três de condição verificados pelo runner nos logs no âmbito da fixture; três contêineres Up.
- Pasta de evidências no Windows: `prova-conceito/resultados-locais/c2-20261113-182248` (ignorada pelo Git). Capturas originais `image(20261113-212344).png`, `image(20261113-212359).png`, `image(20261113-212416).png`, SHA-256 no diagnóstico Etapa 08.

## Próximo E08-D12 — auditoria por bytes

- **Não rerodar o runner** nem reenviar passos ou snapshot na mesma rodada. Preservar os contêineres e seus logs.
- Verificar no Windows as 13 entradas de `checksums.sha256` e empacotar a pasta de execução em ZIP. Enviar ZIP e seu SHA-256 para inspeção independente. Prints só comprovam as saídas exibidas, não substituem análise dos arquivos completos.
- Depois decidir se é necessária rodada separada e limpa para casos Vxx adversariais, sem avançar para Kubernetes.

## E08-D12 — auditoria independente aprovada (15/11/2026)
- ZIP `c2-20261113-182248.zip`, 7.417 bytes, SHA-256 `e90a3b1741b6b68d89ca0ea3fecb1583ab869e8cdfca0938db8bceeb8567de6e` (original enviado nesta conversa; ainda não versionado no repositório).
- Integridade: ZIP/CRC correto; **14/14 arquivos**, **13/13 hashes SHA-256 internos corretos**, sem entradas extras/duplicadas; JSONs lidos. Conteúdo igual ao da fixture/esperado versionados após normalizar CRLF→LF.
- Auditoria sem executar a aplicação: **7** chamadas, **5** notificações de atributo, **3** notificações de condição, **2** efeitos passos **3 e 7**, logs 21/15/7; verificações de causa, ordem, ACK e estados finais exatas. `validation.json`: PASS, 11/11 verdadeiros. Equivalência limitada à fixture ensaiada.
- Screenshot Docker Desktop de 15/11: três C2 ativos e kind ativo; não inferir benchmark dos totais de CPU/RAM. Possível reinício recente; não pressupor estado anterior persistente.
- Laudo completo: `docs/tcc2/etapa-08-auditoria-zip.md`. **Próximo E08-D13**: preflight somente leitura e preparação de testes adversariais em rodada separada, sem repetir D11 nem avançar ao Kubernetes.

## E08-D13 — estado frio observado após nova inicialização (15/11/2026)
- Git no Windows em `f6e087f974d1359b63606077ce538c4542d5dcc4`, limpo; rede `tcc2-pon-c2` bridge e interna; mesmos IDs dos três contêineres, Running=true.
- `StartedAt` em 15/11 às 14:16:06–14:16:08 UTC e `RestartCount=0`; sem evidência da causa. HTTP `/state` retornou `ready=false`, `run_id=null`, versão do snapshot nula, sequências 0, sem efeitos. Processo iniciado novamente com estado vazio (não prova recuperação funcional).
- Captura original `image(20261115-143451).png`, 110952 bytes, SHA-256 `241be744c5cfe522993163a064e236f0be86477d398e3e50d6c4a23d7a643e1e`.
- E08-D11/D12 preservados no ZIP auditado (não repetir). Próximo E08-D14: preparar nova sessão separada para V03 (HTTP 4xx sem mutação), depois V05/V06, e V07 adicional somente se instrumentado.

## E08-D14A aprovado — bancada isolada para V03 (15/11/2026)
- Screenshot `image(20261115-144612).png`, tamanho 100603 bytes, SHA-256 `44ceda0a52fb8ed5094fa27257bb877d23f99353637fdbfd7d4ba140264bc7c0`.
- Git Windows em `2cf3b9c5ab862ec2f705f705be9ff4a18cf1c4ac`; rede `tcc2-pon-c2-v03` bridge interna; novos `tcc2-v03-*` Running, três IDs distintos, ausência de portas host e estados frios. A bancada principal C2 e kind não foram usados.
- Próximo E08-D14B: `python -m c2.v03_cold --output resultados-locais/c2-v03-cold-<timestamp>`, após compileall e os 45 testes de regressão. Checa 10 respostas 4xx, estado invariável dos três serviços e logs/hashes. Ferramenta publicada, **ainda não testada no Windows**.

## E08-D14B-R1 — falha de preflight sem execução adversarial (15/11/2026)
- Prints reais: `image(20261115-165837).png` SHA-256 `185ca95442ef430207cf56c5adef6a7bc2f4378527294c4861050969afe28993`; `image(20261115-165903).png` SHA-256 `e9d673524b13fde486e6c7ea95012fb33807b9fb63fcbe30f301f5072dfb8031`.
- Git em `e2b9d6c4d4abeff4d19d8da9055d8847b848af49` limpo, compilação 0, 45 testes OK (11,039 s); runner `V03: 1`, `FAIL`, 0/10 casos; erro `atributos alterados: logic-engine` no preflight.
- Código real `c1/state.py`: LogicEngine frio apresenta `attributes=null`, `condition=null`; RuleExecutor frio apresenta `approved=null`, enquanto AttributeSource possui valores iniciais zerados. O executor tinha expectativa errada; nenhum teste HTTP adversarial executado.
- Corrigido apenas `c2/v03_cold.py` e acrescentado `tests/test_c2_v03_cold.py` com 5 testes sem Docker. **Próxima rodada E08-D14B-R2**: `compileall`, 50 testes esperados, execução única em pasta de evidência nova se tudo passar; preservar três contêineres V03 e rodada R1.

## E08-D14B-R2 — PASS no Windows (15/11/2026)
- Git `66dfef80d7c9bf17e4343d6087c8d51e397ae523`, compilação 0, 50 testes OK em 11,077 s, `Testes: 0`.
- Runner V03 frio: `PASS`, 10/10 casos, `V03: 0`, pasta `resultados-locais/c2-v03-r2-20261115-140543`. Prints `image(20261115-170706).png` SHA `87ffe23584d5fe656acf6497baf4edc83ced36454827d163d005bc52e712cfa3`; `image(20261115-170715).png` SHA `a0586d2f9f7f9ee63671185c2379e0f934b639bf004838882abd58faf691fc21`.
- Tabela PowerShell das respostas veio sem linhas: consultar `http-cases.json` diretamente e auditar os bytes do ZIP antes de registrar integridade independente. Execução real aprovada no escopo V03 frio, auditoria binária pendente.
- Próximo E08-D15: leitura só de arquivos, validação de hashes e ZIP; **não reexecutar mensagens/fixture, nem tocar no kind**.

## E08-D15 aprovado — leitura dos 10 registros V03 (15/11/2026)
- Screenshot `image(20261115-171137).png`, 71293 bytes, SHA-256 `d098d72e6da1d1a99c490d41dd25c14f2fe016403fe98475a99af5ad1db1a62e`.
- Leitura direta de `http-cases.json` no Windows: `TOTAL: 10`; S01–S10 com status observado igual ao esperado (422, 422, 422, 400, 415, 422, 422, 422, 422, 404), `state_unchanged=True` em todos. Hash de `http-cases.json` **exibido no PowerShell** `95cd9cc95a4dd03bd83113cd6380f4897bb64fd989bc2850791190389a050113`, ainda não recalculado independentemente por IA.
- Problema de formatação da tabela anterior esclarecido, nenhum POST adicional. **Próximo E08-D16:** verificar 8 hashes internos, empacotar 9 arquivos em ZIP e enviar para auditoria binária; não rerodar V03, nem tocar em kind ou contêineres C2.

## E08-D16 — auditoria V03 aprovada (15/11/2026)
- Após duas falhas de procedimento no arquivamento (R1 array JSON no PowerShell, R2 quoting de Python `-c`), R3 gerou ZIP sem tocar nos serviços. Captura `image(20261115-172900).png`, SHA-256 `f324e12b8fe9f8ac1bc6fc639e2a6720ff68013f83b207990dd52b300ada2d86`.
- ZIP `c2-v03-r2-20261115-140543.zip`, **4.489 bytes**, SHA-256 `718213c176dbb7dbf7982f9615d5f31b5955739b992edb8e1326cdac4749ab9c` auditado por bytes; 9/9 entradas/CRC válidos, 8/8 hashes internos, 10/10 HTTP status corretos, resposta com erro por caso, estados antes/depois iguais, logs compatíveis (9 rejeições com evento + 404 de rota desconhecida sem evento).
- **Aceite:** V03 frio aprovado nos casos ensaiados; integridade independente aprovada, porém verificação por caso de estado intermediário depende do runner, já que snapshots por caso não foram persistidos.
- Laudo: `docs/tcc2/etapa-08-auditoria-v03.md`. **Próximo E08-D17:** planejar e executar V05/V06 em sessão isolada, registrar evidências reais e auditar ZIP; não implantar no Kubernetes nesta etapa.

## E08-D17 — planejamento V05/V06 conferido (15/11/2026)
- Protocolo Etapa 05 e `c1/state.py`/`c1/protocol.py`/`c1/service.py` consultados. V05 espera ACK `duplicate=true` sem novo efeito e conflitos com HTTP 409; V06 espera rejeição explícita HTTP 409 de lacunas/out-of-order com estado preservado.
- Novo documento `docs/tcc2/etapa-08-v05-v06-plano.md` detalha as duas bancadas separadas, testes, riscos e auditoria. **Próximo E08-D17A:** criar rede `tcc2-pon-c2-v05` e contêineres `tcc2-v05-*`, sem qualquer snapshot ou mensagem. Agir somente na branch `tcc2/desenvolvimento` e não alterar imagem, master, origem codigoPon ou kind.
- V05 e V06 ainda não executados no host. E08-D16 permanece aprovado e auditado.

## E08-D17A/D17B — infraestrutura e estado frio V05 aprovados (15/11/2026)
- E08-D17A: saída PowerShell e Docker Desktop mostraram 3 contêineres V05 com IDs Docker diferentes, imagem C2 aprovada, rede `tcc2-pon-c2-v05` bridge e `Internal=true`, sem portas publicadas, logs `listening` porta 8080. Git `8812cf05bb54dbdda968b607ee8a5fd9eb278c02` limpo.
- E08-D17B: screenshot `image(20261115-174707).png`, 93.598 bytes, SHA-256 recalculado `514ec8a34b30ec28d4afb95c65908b548ac559e124144c0e6a7b2fbfac9b3582`. `LIVE: OK` + `COLD STATE: OK` nos 3; fonte atA/atB 0, sequências zero, sem pendência, `ready=false`/`run_id=null`; avaliador attributes=null, condition=null, received_ids/condition_events vazios, faulted=false; executor approved=null, effects/received_ids vazios, faulted=false. Git final sem modificações.
- **D17C próximo:** somente snapshot V05 distinto, validar `ready=true` nos 3, `run_id=v05-dedup-v1`, `snapshot_version=v05-dedup-v1:snapshot:0`, estado inicial sem efeitos. Não executar notificações duplicadas antes do aceite. Não repetir POST se houver erro parcial: preservar logs.

## E08-D17C — snapshot V05 validado no Windows (15/11/2026)
- Screenshot `image(20261115-175306).png`, **142.516 bytes**, SHA-256 `3b03035b4e1fa64c24750f9de658aa06ef67b76693a5430d58d1dce91fa92e0c` (recalculado do PNG recebido). Original permanece na conversa, não versionado no GitHub.
- Git Windows fast-forward ao HEAD `5800839e1ff7589b188d925541824fb53a558e2a`, limpo ao fim; 3/3 preflights de estado frio aprovados antes da operação.
- Único POST de snapshot em `tcc2-v05-attribute-source`: HTTP **200**, `ready=true`, `duplicate=false`, `snapshot_version=v05-dedup-v1:snapshot:0`.
- Três estados HTTP finais: `ready=true`, `run_id=v05-dedup-v1`, versão idêntica, atributos/sequências zero na fonte e avaliador, `condition=false`, `approved=false`, nenhuma notificação, nenhum efeito, `faulted=false`. Logs dos três demonstram envio, ACK e aceitação do snapshot propagado por rede interna.
- **E08-D17C aprovado exclusivamente para inicialização.** Deduplicação V05 pendente; nenhum evento de atributo, notificação duplicada ou conflito foi enviado nessa execução.
- **Próximo E08-D17D:** preflight da bancada pronta, um só POST de `atA=5` com `request_id=v05-req-atA-1`; esperar sequência 1 e nenhum efeito. Capturar o payload exato em `send /notifications/attribute` para uso posterior, especialmente `emitted_at`. Não repetir automaticamente POST se falhar.

## E08-D17D — primeiro AttributeChanged validado (15/11/2026)
- Captura PowerShell `image(20261115-175816).png`, 166635 bytes, SHA-256 recalculado `a22f086a610d52e024a97fce1c8ec107036f882a403db7072b5037bf269f71c1`. O arquivo original está na conversa, não no repositório.
- HEAD Windows `7f6294431a97a49388518e817cf153b9edfee73f`, branch `tcc2/desenvolvimento`, Git limpo. Estados antes 3/3 aprovados.
- POST único `/attributes/change` em `tcc2-v05-attribute-source` com `run_id=v05-dedup-v1`, `request_id=v05-req-atA-1`, `entity_id=atA`, `value=5`, `step=1`: HTTP 200, `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atA:1`, `sequence=1`.
- GET `/state` depois: fonte/avaliador atributos `atA=5,atB=0`, sequências `atA=1,atB=0`; avaliador `received_ids=["v05-dedup-v1:atA:1"]`, `condition=false`, `condition_sequence=0`, `condition_events=[]`; executor `approved=false`, `received_ids=[]`, `effects=[]`. Sem falhas.
- Logs reais: produtor `send /notifications/attribute` e `ack` com resposta `{accepted:true,duplicate:false}`, avaliador `mutation /notifications/attribute` status 200 com payload original e ACK correspondente. Nenhum evento de condição ou efeito esperado.
- **E08-D17D aprovado**, mas **não houve replay** e V05 deduplicação permanece pendente.
- **Próximo E08-D17E:** capturar os logs originais e validar por leitura o evento `send` único, sem gerar novo timestamp. Guardar arquivo de payload original e seu SHA-256 para futuro replay único E08-D17F. Não reiniciar os contêineres e não alterar a imagem.

## E08-D17E — evento original capturado no Windows (15/11/2026)

- Print real `image(20261115-180441).png` enviado: 94724 bytes, SHA-256 recalculado `88eceb148d582b57a27f37a72113a4c2c0d1dde76ce95a7c4fa64d6d7d2e1141`. Original permanece na conversa, não no repositório.
- Git Windows em `600fa9e636611d7e5c52c0a9a7a18590388ec5cf`, limpo ao final. O script somente leu logs `docker logs`, sem enviar qualquer POST.
- Saída real: `EVENTO ORIGINAL: OK`, `ENVIO: 1`, `ACK: 1`, `RECEBIMENTO: 1`, `PAYLOADS IDENTICOS: True`, `EFEITOS: 0`, `HASHES: 5` e `E08-D17E: CAPTURA CONCLUIDA`.
- Evento: `event_id=v05-dedup-v1:atA:1`, `request_id=v05-req-atA-1`, `run_id=v05-dedup-v1`, `source=attribute-source`, `entity_id=atA`, `value=5`, `sequence=1`, `step=1`, `schema_version=1`, `emitted_at=2026-11-15T17:57:08.636308+00:00` (UTC original capturado, não reproduzir com novo timestamp).
- Evidências locais: `prova-conceito/resultados-locais/c2-v05-original-20261115-150412`: três logs, `attribute-event-original.json`, `capture-summary.json`, `checksums.sha256` (5 hashes referenciados no manifesto).
- **E08-D17E aprovado como captura/consistência de payload**; replay idempotente ainda NÃO executado, não há resultado V05 de deduplicação.
- **E08-D17F preparado, não executado:** `prova-conceito/c2/v05_duplicate.py`, replay único com pré-condições de estado, imagem e logs, verificação de SHA-256 do payload original, um único `POST /notifications/attribute` ao avaliador, comparação de estados e logs antes/depois, registro SHA-256 e teste local. `tests/test_c2_v05_duplicate.py` contém 7 testes unitários, ainda pendentes de validação no Windows.
- Não reconstruir imagem, não reinicializar V05, não repetir `/attributes/change`, não tocar em V03, C2 principal nem cluster kind.

## E08-D17F — replay idempotente do atributo aprovado no Windows (15/11/2026)

- Prints originais recebidos na conversa: `image(20261115-181207).png` **85.792 bytes**, SHA-256 **`076be5e983dd8327a73b0afea7eba77725a602bc824e0a39e589d87d6c254938`**, e `image(20261115-181217).png` **58.509 bytes**, SHA-256 **`d318ab4b2ccde10908c44327ca4d7d12ec390ba9e8d526493e82f929e8cb898e`**. Hashes calculados dos PNGs enviados; originais permanecem anexados à conversa, não ao Git.
- Windows: fast-forward para HEAD `cb212667616b5e94128b1337f7a12b6d499891e8`, `Compilacao: 0`, **57/57 testes OK em 11.260 s**, `Testes: 0`, branch e Git final limpos. Tempo é da regressão, não benchmark.
- Arquivo original em `resultados-locais/c2-v05-original-20261115-150412/attribute-event-original.json`; SHA-256 **`b325a023eac2609601307a84aab0d1d8d30ecd21b8211a5f4b0ab4ea5c7c2e25`** exibido pelo PowerShell; não reconstituído de memória.
- Execução única `python -m c2.v05_duplicate`: `scenario=C2`, `criterion=V05`, `increment=E08-D17F`, **`status=PASS`**, `replay_attempted=true`, `event_id=v05-dedup-v1:atA:1`, `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`, `V05: 0`.
- Resposta HTTP efetivamente exibida: **200**, `body={"accepted":true,"duplicate":true}`. `new_logic_mutations=1` significa **um evento adicional do logger HTTP do avaliador**, não alteração do estado PON, conforme `states-before.json` e `states-after.json` comparados pelo executor. Os logs da fonte e do executor permaneceram sem acréscimos segundo o executor.
- Evidências locais da rodada: `prova-conceito/resultados-locais/c2-v05-duplicate-20261115-151112` com `manifest.json`, `event-original.json`, `request-intent.json`, `replay-response.json`, `states-before.json`, `states-after.json`, `validation.json`, três pares de logs antes/depois e `checksums.sha256` (**13 arquivos listados no manifesto + manifesto = 14 arquivos esperados**).
- **Conclusão:** E08-D17F **aprovado operacionalmente na única duplicação de atributo ensaiada**. Os bytes da pasta, incluindo hashes internos, **não foram ainda auditados independentemente**; só se verificaram os hashes exibidos na captura. A pasta de evidências deve ser empacotada e enviada em ZIP antes de declarar integridade independente.
- **Próximo E08-D17G:** realizar apenas verificações de hashes e arquivamento ZIP; não repetir `/notifications/attribute`, `/attributes/change` ou reiniciar contêineres. Após auditoria, abordar event_id conflitante (HTTP 409), duplicação de ConditionChanged e V06 em rodada separada. Sem Kubernetes/benchmark nesta etapa.

## E08-D17G — auditoria do replay V05 aprovada (15/11/2026)
- Binário ZIP `c2-v05-duplicate-20261115-151112.zip`: 7163 bytes, SHA-256 independente `532281718862cc28bd17654721b6d01d0a78d8d9cc9c7283730e8c943b9ca3cb`; captura `image(20261115-182817).png`: 98401 bytes, SHA-256 `fca5defd9745c52a91604034e8938be44401a645dbf0b190c0eac5c604d5fdcc`.
- 14 entradas ZIP, CRC OK, 13 SHA-256 internos verificados com o conteúdo real: **13/13 corretos**. `states-before.json` e `states-after.json` iguais em bytes (SHA `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`).
- `request-intent.json` registra 1 tentativa sem retry; resposta `HTTP 200 / accepted=true / duplicate=true`. Log source 7→7, logic 5→6 com único `mutation` duplicado 200 e payload exato, executor 2→2; `rule-executor.effects=[]`. Deduplicação do evento `v05-dedup-v1:atA:1` comprovada **no caso ensaiado**.
- Laudo: `docs/tcc2/etapa-08-auditoria-v05-atributo.md`. ZIP e captura originais pertencem à conversa/host Windows; não foram versionados como binários.
- **Próximo E08-D17H:** preparar teste HTTP 409 para `event_id` igual e payload divergente, guardar estados/logs e ZIP, sem repetir D17F; posteriormente deduplicação de condição, V06, V07 e documentação final. Não executar Kubernetes agora.

## E08-D17H — executor de conflito preparado (ainda NÃO executado)

- O contrato em `c1/state.py` rejeita o mesmo `event_id` com payload diferente (`ContractError(status=409)`, `error="event_id reutilizado com payload diferente"`). `c1/protocol.py` permite `value=6` para `atA`.
- Preparado `prova-conceito/c2/v05_conflict.py`: valida SHA-256 E17E/E17F, topologia, estado atual, logs anteriores (original e único replay), registra intenção antes do POST; altera apenas `value=5 → 6` em cópia do payload original, preservando ID e timestamp; exige HTTP 409, estado global imutável, um registro 409 novo no avaliador, nenhuma mudança nos logs de fonte/executor; salva evidências e checksums SHA-256. **Sem retry.**
- Adicionados 7 testes locais (sem Docker): `prova-conceito/tests/test_c2_v05_conflict.py`. Pendentes compilação/regressão no Windows. A nova suíte esperada é de **64 testes** (57 prévios + 7), não resultado medido.
- Próximo: sincronizar branch, compilar, executar regressão, executar uma vez `python -m c2.v05_conflict --capture ... --previous ... --output ...`, preservar qualquer `FAIL` sem reenvio, auditar novo ZIP antes de novos ensaios.

## E08-D17H — conflito de event_id aprovado operacionalmente (15/11/2026)

- Capturas originais enviadas nesta conversa: `image(20261115-184410).png` (94.191 bytes, SHA-256 `2b1a2ada040bede5e617cd081fe1e98bfff72be05cc2848f190df1b863066c5b`), `image(20261115-184423).png` (76.959 bytes, SHA-256 `b558ed6efcfc82dc685a7417634cdc0825701330816ab2f9071d32bb7bd7e727`). Hashes calculados diretamente sobre os PNGs montados, que não foram versionados no Git.
- HEAD executado no Windows: `5787a095045d37d24b2b141070823676277d90f0`; compilação `0`; suíte de **64 testes aprovada em 11,012 s** (tempo da suíte, não benchmark); Git final limpo.
- Rodada `E08-D17H`, cenário `C2`, critério `V05`, relatório `status=PASS`, `attempted=true`; `event_id=v05-dedup-v1:atA:1`; `expected_http=409`, `observed_http=409`; `state_unchanged=true`, `new_logic_mutations=1`, `new_effects=0`; código de saída `V05 conflito: 0`.
- Resposta HTTP observada: status 409, `body.error="event_id reutilizado com payload diferente"`. O teste alterou `value` de 5 para 6 preservando `event_id` segundo o executor; verificar evento original e conflito diretamente após receber o ZIP.
- Pasta de evidências no host: `prova-conceito/resultados-locais/c2-v05-conflict-20261115-154229`, incluindo `event-original.json`, `event-conflict.json`, `conflict-response.json`, estados/logs antes/depois, `request-intent.json`, `validation.json`, `manifest.json`, `checksums.sha256`.
- **Aceite operacional E08-D17H** baseado em saída real. O relatório de estado inalterado foi emitido pelo executor, ainda sem comparação binária externa; auditoria independente de integridade **pendente**.
- **E08-D17I próximo:** somente empacotar arquivos e verificar hashes SHA-256; arquivo esperado 15 entradas = 14 arquivos de dados listados no manifesto + `checksums.sha256`. Não repetir o POST 409. Após upload, auditar ZIP e então prosseguir V05 condição.

## E08-D17I — auditoria direta ZIP V05 conflito aprovada (15/11/2026)
- ZIP recebido e auditado: `c2-v05-conflict-20261115-154229.zip` (7683 bytes, SHA-256 `4aef50d86c83feceb8c007dfa959e82a5e57a9ced23df2ef827a7d39839f327b`), 15/15 entradas, `testzip()` CRC OK, 14/14 hashes internos conferidos com bytes. Captura `image(20261115-184927).png` (92871 bytes, SHA-256 `379d4257acef5be2875696e1ce6512085bba5017c5d7e379fc73765db33c91de`). Originais na conversa/host, não no GitHub.
- Confronto JSON: evento base `v05-dedup-v1:atA:1` com `value=5`; novo conflito idêntico exceto `value=6`. HTTP 409, corpo `event_id reutilizado com payload diferente`; estados antes/depois iguais em bytes (SHA `648e82a9e90f1962ce7a47d2785c1b8b3a738ddd79a6c3c7cfde8a09c5316778`), incluindo 0 efeitos; fonte 7→7, logic 6→7 com um registro HTTP 409 e executor 2→2.
- Resultado **E08-D17I APROVADO** no caso ensaiado. Laudo `docs/tcc2/etapa-08-auditoria-v05-conflito.md`. E08-D17H deixou de estar pendente de auditoria de bytes.
- Próximo E08-D17J: preflight frio/ready da condição na mesma bancada V05, sem POST, e somente após aceite avançar para `atB=1`. Não repetir conflito E08-D17H, não reiniciar serviços, não modificar imagem/codigoPon/master/kind.

## E08-D17J — preflight V05 para condição aprovado no Windows (15/11/2026)

- Captura real `image(20261115-185446).png` recebida: **102.442 bytes**, SHA-256 recalculado `198375f957fb03bbcae26e36ae32310e91abba0d8e18dc67eed1f215599c7c96`, resolução 1920×1080; original permanece na conversa.
- HEAD Windows `7e4069c0df5f93ab4313d4968e65375c72ef40b6` após fast-forward, branch `tcc2/desenvolvimento` e Git final limpo. Rede `tcc2-pon-c2-v05` driver=bridge `Internal=true`.
- `/health/live`: 3/3 `LIVE: OK`. `/state`: 3/3 `STATE: OK`, `ready=true`, `run_id=v05-dedup-v1`, `snapshot_version=v05-dedup-v1:snapshot:0`. Fonte e avaliador `atA=5,atB=0` com sequências `1,0`; avaliador `condition=false`, `condition_sequence=0`, `received_ids=["v05-dedup-v1:atA:1"]`; executor `approved=false`, `condition_sequence=0`, `received_ids=[]`, `effects=[]`. Três contêineres V05 UP. Nenhum POST nesta etapa.
- **E08-D17J APROVADO como preflight, não como transição ou deduplicação de condição**.
- **E08-D17K preparado no repositório, ainda NÃO executado no Windows:** `prova-conceito/c2/v05_condition_first.py` para um único `POST /attributes/change` com `atB=1`, `request_id=v05-req-atB-1`, `step=2`, após verificar hashes/estado/topologia/logs, com evidências pré/pós e captura do `ConditionChanged` original. `tests/test_c2_v05_condition_first.py` adiciona 8 testes locais, que ainda não foram executados no Windows.
- Esperado, não medido: condição `true`, sequência 1, aprovação da regra `true` e 1 efeito, `event_id=v05-dedup-v1:cn1:1` causado por `v05-dedup-v1:atB:1`; capturar a mensagem com timestamp original para ensaio de replay posterior. Não repetir POST em caso de falha.

## E08-D17K — transição de condição e primeiro efeito V05 aprovados operacionalmente (15/11/2026)

- Evidência primária: três capturas PowerShell recebidas na conversa (binários não versionados em Git): `image(20261115-190447).png`, 87305 bytes, SHA-256 `f82580a41fd28ed2b23cecf411d6438a7f682941d599bf3fef4c7b4d1364f3e5`; `image(20261115-190457).png`, 70254 bytes, SHA-256 `d61c84381b94ee931bc04f907eb0047f4d785f19a32e45950815d8bf3f656e80`; `image(20261115-190509).png`, 65438 bytes, SHA-256 `73c096f0d318483945f579c93a2727b99c1818102639d8049eb7a2becab27ea4`.
- Branch `tcc2/desenvolvimento`, HEAD Windows `ba200b85bfe24f81b15a3f1ec838480a6cc10e49` após fast-forward, Git final limpo. Compilação `0`; **72/72 testes automatizados aprovados em 10,837 s** (tempo da regressão, **não** benchmark).
- Executor `c2.v05_condition_first`: `scenario=C2`, `criterion=V05`, `increment=E08-D17K`, `status=PASS`, `attempted=true`, `condition_sequence=1`, `effects_count=1`, retorno `V05 condicao: 0`.
- Envio único planejado e registrado pelo executor: `POST /attributes/change`, `{"run_id":"v05-dedup-v1","request_id":"v05-req-atB-1","entity_id":"atB","value":1,"step":2}`. Resposta HTTP observada **200**, corpo `changed=true`, `duplicate_request=false`, `event_id=v05-dedup-v1:atB:1`, `sequence=1`.
- No `/state` exibido dos três serviços: `atA=5,atB=1`, sequências `1/1`, avaliador `condition=true`, `condition_sequence=1`, `condition_events` contém **um** evento `ConditionChanged` `v05-dedup-v1:cn1:1`, `approved=true`, `caused_by=v05-dedup-v1:atB:1`; executor `approved=true`, sequência 1, `received_ids=["v05-dedup-v1:cn1:1"]`, **um efeito** `event_id=v05-dedup-v1:rl1:1`, `caused_by=v05-dedup-v1:cn1:1`, `attribute_event_id=v05-dedup-v1:atB:1`, `step=2`.
- Evento de condição original exibido: `emitted_at=2026-11-15T19:03:59.142115+00:00`. SHA-256 de `condition-event-original.json` mostrado pelo PowerShell: `04687836e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`. **Ainda não foi recalculado independentemente**, pois a pasta binária não foi enviada.
- Pasta local da rodada: `prova-conceito/resultados-locais/c2-v05-condition-first-20261115-160357`. O código do executor prevê 14 arquivos de dados mais `checksums.sha256` (total **15**), desde que não tenha ocorrido erro; verificar inventário real.
- Os três contêineres `tcc2-v05-*` constam `Up` na saída. Não ocorreu modificação do código PON, da imagem Docker ou do cluster kind.
- **Classificação:** E08-D17K **aprovado operacionalmente** com base nos prints e no relatório do executor; integridade do ZIP e validação independente dos bytes dos estados/logs **pendentes**. A transição `atB:1 → cn1:1 → rl1:1` fornece material de rastreabilidade para diagrama de sequência futuro, **sem mensuração de latência/desempenho**.
- **Próximo E08-D17L:** apenas conferir SHA-256, conteúdo funcional, empacotar pasta em ZIP e verificar 15 entradas antes de enviar para auditoria independente. **Não repetir o POST `atB=1` nem reiniciar os serviços.** Após auditoria, preparar replay idempotente exato de `ConditionChanged` no `rule-executor`.

## E08-D17L-R2 — auditoria da primeira transição ConditionChanged aprovada (15/11/2026)

- O ZIP `c2-v05-condition-first-20261115-160357.zip` foi recebido e auditado diretamente: **8.840 bytes**, SHA-256 recalculado `46787fb0ac9d7ae068aa9e13ef3cf3977bfdf84017acd1f61e8868709a52b587`; captura `image(20261115-191445).png` **86.408 bytes**, SHA-256 `e4c148bfe59c029e23e780151069469b3a1180ed2ba3c4f6b4b3f68340b567c8`. O print confirmou Git limpo no HEAD `f6293046a405aa76de672a7807b5e6ac80a422a5`, `Real=Manifesto: True` no diagnóstico anterior e `E08-D17L-R2: ARQUIVAMENTO CONCLUIDO`.
- Integridade: **15/15 entradas**, CRC OK, **14/14 SHA-256** coincidentes com bytes extraídos. Condição original SHA-256 `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54`; o valor manual do primeiro comando estava errado (`04687836` vs `04687b36` no início), sem alteração do dado original.
- Dados auditados: HTTP 200 `changed=true`, `duplicate_request=false`; atributos `atA=5,atB=0` → `atA=5,atB=1`; condição `false→true`, sequência 0→1, payload `v05-dedup-v1:cn1:1` `approved=true`; executor `approved=false→true`, produz **um** efeito `v05-dedup-v1:rl1:1`. Logs: fonte **7→10**, avaliador **7→10**, executor **2→4**, todos os prefixos anteriores preservados; novos payloads e confirmações coerentes com cadeia causal.
- **E08-D17L-R2 aprovado independentemente.** Relatório `docs/tcc2/etapa-08-auditoria-v05-condicao-inicial.md`. As notas anteriores de auditoria pendente de E08-D17K estão superadas.
- **Próximo E08-D17M:** reenvio idêntico de `condition-event-original.json` ao executor, apenas uma tentativa HTTP, após verificações preventivas de estado/topologia/logs e evidências; exigir ACK `duplicate=true`, nenhum efeito adicional e estados idênticos. Não repetir alteração `atB=1`.

## E08-D17M — replay de ConditionChanged preparado, ainda não executado
- Código `prova-conceito/c2/v05_condition_replay.py` preparado com preflight completo: SHA-256 do evento de condição aprovado em E08-D17L-R2; integridade de 14 arquivos anteriores; estado e logs atuais **iguais aos arquivos auditados**; os três IDs e horários de inicialização dos contêineres e a topologia Docker coerentes. Exige o `run_id=v05-dedup-v1`.
- Após esse preflight, faz **um único** `POST /notifications/condition` ao `rule-executor` com o payload original íntegro, incluindo `emitted_at`. Exige HTTP 200 `accepted=true,duplicate=true`, todos os estados idênticos, **zero efeito adicional** e um único novo registro HTTP no executor; logs source/logic invariáveis.
- Evidências: manifesto de imagem, IDs e hashes anteriores, intenção de envio escrita antes do POST, respostas, estados/logs pré/pós, `validation.json` e `checksums.sha256`. Em caso de falha após envio, preservar os arquivos, **NÃO repetir**.
- Adicionados **8 testes unitários preparados** em `tests/test_c2_v05_condition_replay.py` (ainda não executados no Windows). Total esperado na próxima suíte: **80** (72 anteriormente aprovados + 8 novos), não uma medição atual.
- Não houve reconstrução de imagem nem reimplantação de serviços, alteração de núcleo PON, de `master` ou do cluster kind.

## E08-D17M — replay exato de ConditionChanged V05 aprovado operacionalmente (15/11/2026)

- Capturas PowerShell fornecidas pelo acadêmico: `image(20261115-192312).png` (87.353 bytes; SHA-256 recalculado `ac0515c61ea42ca9d590e86d97f0f59281bb9467b93c631bcdef5219f892e6fa`) e `image(20261115-192356).png` (71.569 bytes; SHA-256 `405c09d2d24927fc287345355b2cef2bdd3b7d5d5ae9cc50f945ce40c5c9dfb6`). Arquivos de imagem anexados à conversa, não versionados no GitHub.
- Branch `tcc2/desenvolvimento`, HEAD Windows `a654453c284563ec3324a1c1b3462f759e9d10ec` após `git pull --ff-only`; compilação código 0; **80 testes automatizados OK em 11,065 s** (duração da regressão, **não** métrica de desempenho experimental); Git final sem alterações exibidas.
- Executor `c2.v05_condition_replay` reportou `scenario=C2`, `criterion=V05`, `increment=E08-D17M`, `status=PASS`, `replay_attempted=true`, `event_id=v05-dedup-v1:cn1:1`, `expected_http=200`, `observed_http=200`, `duplicate=true`, `state_unchanged=true`, `new_effects=0`, `new_executor_mutations=1`, retorno `V05 replay: 0`.
- Resposta HTTP exibida: `{"status":200,"body":{"accepted":true,"duplicate":true}}`. Três serviços `tcc2-v05-attribute-source`, `tcc2-v05-logic-engine`, `tcc2-v05-rule-executor` exibidos em estado `Up`. Sem novo evento `atB=1`, sem reinicialização ou alteração de imagem demonstrada.
- Pasta de evidências no Windows: `prova-conceito/resultados-locais/c2-v05-condition-replay-20261115-162246`; o print apresenta `checksums.sha256` com **13 arquivos listados**, mais o próprio manifesto (inventário total esperado: **14**). **Ainda não recebemos ZIP; CRC, 13 SHA-256 internos e consistência independente dos bytes de logs/estados permanecem pendentes**.
- Classificação: **E08-D17M aprovado operacionalmente pelos prints e relatório**, não auditado independentemente até receber ZIP.
- Próximo **E08-D17N**: somente leitura e empacotamento da pasta de evidências V05: validar `validation.json`, `replay-response.json`, igualdade exata `states-before.json`/`states-after.json`, logs fonte/avaliador invariáveis e um novo log de `mutation` no executor com `duplicate=true` (nenhum novo `effect`), checar 13 SHA-256 locais, empacotar 14 entradas e conferir conteúdo ZIP/CRC. **Não repetir POST** ou reiniciar contêineres.

## E08-D17N — auditoria independente de deduplicação ConditionChanged APROVADA (15/11/2026)
- Arquivo real recebido e inspecionado: `c2-v05-condition-replay-20261115-162246.zip`, **8703 bytes**, SHA-256 recalculado `0378c162b45bd44b316754023577daec5b41a19583dbef68c0f0d8b6340bfb42`, coincidindo com print do PowerShell; duas capturas `image(20261115-192914).png` SHA-256 `be019d1eda8515f840822f28d95106ad0207ae8ec09ce2ad9ca02b66ab730e1d` (91684 bytes) e `image(20261115-192920).png` SHA-256 `322b901d40a75320b2ec9a2d1d3047e00a3f382412081ce655107b0d313131fa` (29822 bytes). Originais no Windows/conversa, não no GitHub.
- ZIP/CRC sem erros, **14/14 entradas** e **13/13 hashes internos recalculados** corretos. Condição original SHA-256 `04687b36e59e61a38081828100ae1c5ea64d767e7358ddf16a52b0806f7d6c54` e **idêntica byte a byte** à do ZIP E08-D17K. `manifest.previous_validation_sha256` igual ao hash da `validation.json` anterior. IDs/horários dos três contêineres, imagem e rede iguais aos da rodada de transição.
- `states-before.json` do replay igual byte a byte a `states-after.json` da rodada original e também a `states-after.json` do replay (SHA `2a53df80250bc2b72fd614c20b586108550d84a71f6347baaa3ca0dfb805ae0f`). Logs atuais pré-replay iguais aos finais da rodada original. Fonte e avaliador logs **10→10**, sem mudanças; executor **4→5** com exatamente um novo `mutation /notifications/condition` para payload idêntico, HTTP 200 `accepted=true,duplicate=true`, **zero efeitos novos**; permanece 1 efeito pré-existente.
- **E08-D17M e arquivamento E08-D17N auditados e aprovados no caso ensaiado**; laudo: `docs/tcc2/etapa-08-auditoria-v05-condicao-replay.md`. 80 testes na execução Windows (11,065 s) não caracterizam benchmark.
- Próximo E08-D17O: preflight **somente leitura** na bancada V05 para testar futuramente conflito de `ConditionChanged.event_id` (payload diferente, HTTP 409, estados inalterados). V06 em bancada nova e revisão V07 permanecem pendentes. Não repetir POST anterior e não reiniciar V05.

## E08-D17O / E08-D17O-R1 — preflight V05 (15/11/2026)

- Print E08-D17O exibiu falha **antes de qualquer POST**: \`ValueError: inventario anterior divergente\`, porque a lista \`EVIDENCE_FILES\` do E08-D17K (14 arquivos de dados) foi aplicada indevidamente à pasta E08-D17M (13 arquivos de dados).
- A correção E08-D17O-R1 ajustou o inventário **sem modificar evidências ou serviços**. Print recebido \`image(20261115-194634).png\`: **13/13 hashes**, evento original íntegro, relatório E08-D17M PASS, topologia e 3/3 contêineres corretos, estados HTTP 3/3, **1 efeito**, logs fonte 10, avaliador 10 e executor 5; \`Nenhum evento HTTP POST enviado.\` Git limpo, HEAD Windows \`5d52a1043f67dfbed1e6a7ca50d658b5f9195a76\`.
- **E08-D17O-R1 aprovado como preflight somente leitura.** Nenhum resultado de conflito HTTP 409 foi produzido até aqui.

## E08-D17P — conflito de ConditionChanged preparado, PENDENTE de execução Windows

- Publicados \`prova-conceito/c2/v05_condition_conflict.py\` e \`tests/test_c2_v05_condition_conflict.py\` com 8 novos casos unitários; **88 testes previstos** (80 anteriores + 8), ainda sem execução na máquina do acadêmico.
- Preflight exige inventário E08-D17M correto (13 arquivos), SHA-256/JSON/relatório PASS, topologia e IDs/horários idênticos, estados e logs idênticos aos auditados, 1 único efeito prévio.
- Faz uma única alteração sobre payload real \`v05-dedup-v1:cn1:1\`: **\`approved=true → false\`**; preserva \`event_id\`, \`emitted_at\`, \`sequence\`, \`run_id\` e demais campos. Envia no máximo **um POST** \`/notifications/condition\` ao \`rule-executor\`, sem retry.
- Resultado **esperado, não observado**: HTTP 409, \`{"error":"event_id reutilizado com payload diferente"}\`, estados idênticos, logs fonte/avaliador inalterados, exatamente 1 novo registro HTTP no executor e **0 novos efeitos**. Evidências JSON/JSONL e SHA-256 preservadas; não repetir em falha ou timeout.
- Nenhum Dockerfile, imagem, kernel PON, código original, \`master\` ou recurso Kubernetes modificado.

## E08-D17P/Q — conflito de ConditionChanged e auditoria independente APROVADOS (15/11/2026)

- **E08-D17P e E08-D17Q aprovados em 15/11/2026 (V05 encerrado nos casos previstos):** execução Windows do conflito de `ConditionChanged` no HEAD `0b647d64b1f8a66d6b5f1cb01f3692ebfc2f7286` com compilação 0, 88/88 testes OK (11,246 s), HTTP 409, estado inalterado, zero efeitos novos, executor 5→6 registros e Git limpo. Auditoria direta do ZIP `c2-v05-condition-conflict-20261115-171101.zip`: **9.296 bytes**, SHA-256 `2c9b1dc47cb59a8d403dc8ad8c3cd9c12a967f6ac6dfe10f0f753ad0662d3640`, CRC OK, **15/15 arquivos, 14/14 hashes internos**, evento original idêntico às duas rodadas anteriores, somente `approved:true→false`, estados byte a byte iguais, logs fonte/avaliador 10→10 e executor 5→6, continuidade de IDs dos 3 contêineres, imagem e rede. Laudo `docs/tcc2/etapa-08-auditoria-v05-conflito-condicao.md`. Próximo **E08-D18A: diagnóstico V06 somente leitura**, em bancada separada. V07 e encerramento Etapa 08 ainda pendentes; sem Kubernetes, benchmark ou distribuição física.

- Rastreabilidade: `conflict-response.json` HTTP 409; `event-original.json` byte-idêntico aos originais D17K/D17M; `states-before.json` e `states-after.json` byte-idênticos (SHA `2a53df80250bc2b72fd614c20b586108550d84a71f6347baaa3ca0dfb805ae0f`); todos os 3 logs pré-conflito iguais aos finais do replay; último log executor registra erro 409. Captura `image(20261115-202708).png`, 93.002 bytes, SHA-256 `00462f5ea25bf6025f0c1cf0ed6e124b58c12488ee21fdd270758ecf759bc323`.
- Registro de decisão: V05 completo somente **nos casos serializados ensaiados** (atributo replay e conflito, condição transição, replay e conflito); não atribuir a V05 métricas de desempenho, cluster Kubernetes ou execução multi-host. Laudo detalhado no link acima.
- **E08-D18A** reservado ao diagnóstico apenas de leitura da bancada futura V06; criar infraestrutura e executar eventos **somente após validação** da etapa inicial. Não modificar/reiniciar V05.

## E08-D18A — diagnóstico de infraestrutura V06 (15/11/2026): APROVADO

- Fonte: captura real PowerShell `image(20261115-203614).png`, enviada nesta conversa; sem inspeção independente do daemon, apenas registro da saída exibida. Branch `tcc2/desenvolvimento`, Git limpo, HEAD Windows `1364bda7623467934dd897f016fe038dc0b75956` após `git pull --ff-only`.
- Docker context `desktop-linux`, Linux/x86-64; imagem aprovada `tcc2-pon:c2-e08-dbefcd2cf3d2` com ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, revisão OCI `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Rede `tcc2-pon-c2-v06` e nomes `tcc2-v06-attribute-source`, `tcc2-v06-logic-engine`, `tcc2-v06-rule-executor`: inexistentes e disponíveis na consulta. Bancada V05: três contêineres `Running=true` (não remover/reiniciar).
- E08-D18A executado **somente leitura**, sem POST, criação de rede, contêiner, imagem ou snapshot. Aprovado para avançar **E08-D18B: provisionar V06**, mantendo imagem existente e rede bridge internal=true separada; executar apenas um papel por contêiner, sem portas publicadas e com aliases privados. Critério D18B restrito à infraestrutura (três Running, IDs distintos, rede correta, logs listening, sem snapshot), **não** valida V06 funcional.
- Etapas posteriores: D18C = preflight de estado frio e DNS/HTTP interno (somente GET); D18D = snapshot controlado (POST único) e então ensaios V06 de lacunas/ordem com evidências. Não executar ações adversariais antes dos aceites prévios. Kubernetes apenas Etapas 09/10.
