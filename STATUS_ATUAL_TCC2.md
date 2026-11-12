# STATUS ATUAL — TCC2

Atualizado em: 2026-11-11

## Etapas
- Etapa 02: concluída, conforme informação do acadêmico.
- Etapa 03: concluída; referência `2eb080b93a38db47ea1149bb660a5379c6478bd4`.
- Etapa 04: concluída como **especificação arquitetural**; nenhuma implementação distribuída comprovada.
- Etapa 05: **protocolo experimental e esqueleto LaTeX documentados**; sem execução de testes.
- Etapa 06: **infraestrutura básica concluída e validada em ambiente local**; limitações e dependências restantes documentadas.
- Próxima: **Etapa 07 — Implementação e validação local da prova de conceito**.

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

## Próxima etapa — 06: Preparação do ambiente
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
