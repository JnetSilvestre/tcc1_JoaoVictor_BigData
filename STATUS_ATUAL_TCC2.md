# STATUS ATUAL — TCC2

Atualizado em: 2026-11-13

## Leitura rápida — última situação verificada

- **Etapa 07 concluída funcionalmente em C0/C1:** 39 testes reais aprovados no Windows, V01–V07 nos casos ensaiados; código testado em `be6b850d599504e9ea8166f02fd87b35313e5445`. O ZIP V07 foi auditado diretamente (12/12 hashes internos, 20/20 checagens).
- **Etapa 08 aberta em 13/11/2026:** E08-D01/D02 comprovam branch limpa e Docker/WSL2 operacionais; E08-D03 comprova atualização fast-forward ao HEAD `3dadef829846fdf5f0bcf0c47c956b44eb89d821`, compilação 0 e 39/39 testes OK em 10,813 s na máquina do acadêmico. Capturas e SHA-256 em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I01 e E08-I02 aprovados no Windows (E08-D04):** commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, `compileall=0`, 42/42 testes OK em 11,564 s (duração da suíte, não benchmark), `Testes: 0` e Git limpo. Capturas/hashes em `docs/tcc2/etapa-08-diagnostico-rede.md`; os testes de DNS usam mocks, não rede Docker.
- **E08-D05 aprovado no Windows:** `python:3.13-slim` Linux/amd64, Python 3.13.18 executado com `--network none`; digest exato `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`, Git limpo e kind preservado. Print e SHA-256 registrados em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I03 concluído no Windows (E08-D08, 13/11/2026):** no commit `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`, resolução do manifesto `linux/amd64` corrigido (`Registro: 0`), build (`Build: 0`), imports (`Imports: 0`) e CLI (`CLI: 0`) aprovados; imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`, Python 3.13.18, UID 10001, Git limpo. Dois PNGs originais e hashes SHA-256 registrados em `docs/tcc2/etapa-08-diagnostico-rede.md`.
- **E08-I04 aprovado e E08-D10 aprovado no Windows (13/11/2026):** três contêineres em bridge interna comprovados (E08-D09). Snapshot `c0-minimo-v1:snapshot:0` propagado por HTTP/ACK nos três (E08-D10): `ready=true`, estado inicial/seq. coerentes, nenhum efeito; print original e SHA-256 em `docs/tcc2/etapa-08-diagnostico-rede.md`. **E08-D11 preparado, sem execução real:** executor `prova-conceito/c2/runner.py` e 3 testes de preflight em `tests/test_c2_runner.py` foram adicionados na branch; requer compilação e regressão no Windows antes de executar a fixture C2. Compara resultados com C0 e oráculo, captura logs/manifesto/hashes, bloqueia replay da fixture caso mudanças já constem nos logs. **Pendentes:** notificações e equivalência C2, desempenho e Kubernetes.
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
