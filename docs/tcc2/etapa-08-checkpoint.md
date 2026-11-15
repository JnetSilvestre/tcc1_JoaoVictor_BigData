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
