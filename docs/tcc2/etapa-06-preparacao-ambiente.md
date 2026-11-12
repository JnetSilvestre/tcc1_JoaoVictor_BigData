# TCC2 — Etapa 06: preparação do ambiente (registro parcial)

**Situação:** em andamento; não declarar conclusão da Etapa 06.  
**Data das evidências:** 11/11/2026 (horário local GMT-3), com saídas HTTP/logs em UTC já em 12/11/2026.  
**Branch exclusiva:** `tcc2/desenvolvimento`; não modificar `master`.  
**Referências metodológicas:** `docs/tcc2/etapa-04-arquitetura-distribuida.md` e `docs/tcc2/etapa-05-protocolo-experimental.md`.

## 1. Escopo e decisão

O alvo experimental permanece uma prova Python PON com `attribute-source`, `logic-engine` e `rule-executor`, uma réplica por papel e comunicação HTTP/JSON (ainda não implementados). Para preparar o ambiente foi escolhida a opção **kind com um control-plane e um worker virtuais**, no mesmo Windows/WSL2/Docker. Escolha feita sem segunda medição com aplicativos fechados, a pedido do acadêmico; não apresentá-la como medição realizada. Os nós virtuais compartilham CPU e RAM físicas. A arquitetura definitiva e a inclusão de figuras na monografia dependem das Etapas 07–10/13, conforme Etapas 04/05.

## 2. Inventário registrado pelas capturas do PowerShell

- Windows 10 Home 64 bits, build 19045; Intel Core i5-9300H, 4 núcleos físicos e 8 processadores lógicos.
- RAM utilizável 15,84 GB; disponível na primeira coleta 4,87 GB, e em coleta posterior com Docker ativo 3,30 GB (outros aplicativos abertos, condições não controladas).
- Armazenamento inicialmente: C: 69,44 GB livres, D: 69,40 GB livres; E: sem capacidade reportada. Valores instantâneos, não medições durante o experimento final.
- Virtualização habilitada conforme Gerenciador de Tarefas; WSL2 disponível, `docker-desktop` em execução ao validar Docker.
- Python 3.13.9; Git 2.45.0.windows.1; `kubectl` cliente v1.34.1; kind v0.33.0; Docker Desktop 4.99.0, Engine 29.9.3, Linux/amd64; `containerd` v2.2.4 no cluster; Kubernetes dos nós v1.37.0. Compatibilidade entre versões e suporte do Windows 10 Home devem permanecer registrados como restrição, não ser presumidos.
- Docker Engine reportou 8 CPUs lógicas e 8.245.633.024 bytes de memória em uma coleta; memória do Engine não representa memória livre. `docker system df` apontou imagens 2,33 GB, volumes 212 MB e cache de construção 2,85 GB (categorias podem compartilhar armazenamento).

## 3. Validações realizadas e evidência visual recebida

1. `docker run --name tcc2-teste-docker hello-world`: download e saída 'Hello from Docker!'; contêiner com `Exited (0)` e logs consultados. `docker rm tcc2-teste-docker` posteriormente concluiu e `docker ps -a` ficou sem contêineres na coleta.
2. Criação do arquivo `kind-config.yaml` com control-plane + worker. `kind create cluster --name tcc2-pon --config .\\kind-config.yaml --wait 180s` concluiu como `Ready after 9s`, usando provider Docker. O cluster recebeu a imagem de nó `kindest/node:v1.37.0`; a saída mostrou `kind-tcc2-pon` como contexto.
3. `kubectl get nodes -o wide` indicou control-plane `tcc2-pon-control-plane` (172.18.0.3) e worker `tcc2-pon-worker` (172.18.0.2), ambos `Ready`, Debian GNU/Linux 13, kernel WSL2 e containerd 2.2.4.
4. `kubectl get pods -n kube-system -o wide` mostrou CoreDNS, kube-proxy e componentes de controle `Running`, sem reinícios na coleta. Um comando de consulta JSONPath falhou com `unclosed action` por problema de escape; corrigido com `kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU:.status.allocatable.cpu,MEMORY:.status.allocatable.memory`.
5. Recursos alocáveis anunciados por *cada nó*: CPU 8, memória 8052380Ki; `MemoryPressure=False`, `DiskPressure=False`, `PIDPressure=False`. Não somar capacidades virtuais como recursos físicos independentes.
6. Namespace `tcc2-infra-test` criado. Pod `servidor-teste` com Nginx criado no worker, inicialmente `ContainerCreating`, depois `Ready` e `Running` (1/1), IP 10.244.1.2, sem reinícios; logs mostraram Nginx/1.27.5 inicializado.
7. Service ClusterIP `servidor-teste` recebeu IP 10.96.76.28 e EndpointSlice apontou para 10.244.1.2:80. Pod `cliente-teste` no control-plane, IP 10.244.0.5, `Running` (1/1), sem reinícios.
8. Dentro do cliente, `curl -sS -i --max-time 10 http://servidor-teste:80/` e `curl -sS -i --max-time 10 http://10.244.1.2:80/` retornaram HTTP 200 OK e a página padrão do Nginx. Logs do servidor registraram duas requisições GET oriundas de 10.244.0.5 com código 200, 615 bytes. Evidência de conectividade HTTP entre Pods em nós *virtuais* distintos via Service/DNS e IP direto; NÃO demonstra ainda a comunicação da aplicação PON.
9. Consulta posterior `kubectl get pods -n tcc2-infra-test -o wide`, `kubectl get svc,endpointslice -n tcc2-infra-test -o wide`, `kubectl get nodes -o wide` e `kubectl get all -n tcc2-infra-test` confirmou dois nós Ready, dois Pods Running 1/1 com 0 reinícios, Service/EndpointSlice coerentes.

### Evidências identificadas durante acompanhamento

- E06-01 criação do cluster; E06-02 topologia e nós Ready; E06-03 componentes do kube-system; E06-04 capacidade/condições dos nós; E06-05 criação do primeiro Pod; E06-06 Nginx Ready e logs; E06-07 Service/EndpointSlice; E06-08 cliente e servidor em nós distintos; E06-09 duas requisições HTTP 200 e logs; E06-10 verificação de topologia estável após a comunicação.
- **As capturas foram fornecidas na conversa; não foram transferidas para este repositório nem convertidas em resultados de execução por um script.** Manter prints originais para anexação manual ao pacote de evidências, com origem, data e sem credenciais. O nome E06-10 é registro documental desta última verificação.

## 4. Reproduzir a infraestrutura de teste

Pré-requisitos: Docker Desktop Engine funcionando, kind, kubectl, WSL2 e recursos disponíveis. Executar no PowerShell a partir da raiz do repositório; garantir que não exista cluster homônimo antes de criar:

```powershell
kind get clusters
kind create cluster --name tcc2-pon --config .\\infraestrutura\\kind\\kind-config.yaml --wait 180s
kubectl --context kind-tcc2-pon get nodes -o wide
kubectl --context kind-tcc2-pon create namespace tcc2-infra-test
kubectl --context kind-tcc2-pon apply -f .\\infraestrutura\\kind\\testes\\pod-servidor-teste.yaml
kubectl --context kind-tcc2-pon apply -f .\\infraestrutura\\kind\\testes\\service-servidor-teste.yaml
kubectl --context kind-tcc2-pon apply -f .\\infraestrutura\\kind\\testes\\pod-cliente-teste.yaml
kubectl --context kind-tcc2-pon wait --for=condition=Ready pod/servidor-teste -n tcc2-infra-test --timeout=120s
kubectl --context kind-tcc2-pon wait --for=condition=Ready pod/cliente-teste -n tcc2-infra-test --timeout=120s
kubectl --context kind-tcc2-pon get pods -n tcc2-infra-test -o wide
kubectl --context kind-tcc2-pon get svc,endpointslice -n tcc2-infra-test -o wide
kubectl --context kind-tcc2-pon exec -n tcc2-infra-test cliente-teste -- curl -sS -i --max-time 10 http://servidor-teste:80/
kubectl --context kind-tcc2-pon exec -n tcc2-infra-test cliente-teste -- curl -sS -i --max-time 10 http://10.244.1.2:80/
kubectl --context kind-tcc2-pon logs servidor-teste -n tcc2-infra-test --tail=20
```

**Limpeza somente depois de arquivar evidências e concluir validações**: `kubectl --context kind-tcc2-pon delete namespace tcc2-infra-test` remove exclusivamente os recursos do namespace de teste. Não executar `kind delete cluster` por rotina antes das próximas verificações.

## 5. Pendências — NÃO concluídas

- Validar ambiente Python `venv`, `pip` e dependências necessárias (não instalar bibliotecas sem inspeção do código-base).
- Construir/executar uma imagem própria de teste, sem antecipar a implementação definitiva da aplicação PON.
- Verificar métricas viáveis e overhead: `kubectl top` requer Metrics Server; logs, `docker stats`, `kubectl get/describe/logs` já são candidatos. Não declarar medições de CPU/RAM/latência feitas.
- Verificar Git remoto, versão/revisão do `codigoPon`, integridade de arquivos e documentação para reprodução completa; observar hardware em condições experimentais futuras.
- C0–C5 e F1 do protocolo são cenários da aplicação PON e **não estão aprovados** por este teste Nginx/curl. V08/V09 da aplicação também permanecem pendentes.
- Ajustar `capitulos/cap-metodologia-tcc2.tex` apenas na consolidação acadêmica apropriada, sem antecipar texto de experimento final ou as duas figuras arquiteturais.

## 6. Próximo passo

Concluir validação de Python e construção de imagem de teste; coletar versões e evidências com comandos reais, registrar eventuais limitações, então atualizar `STATUS_ATUAL_TCC2.md` ao término da Etapa 06. A Etapa 07 corrigirá o núcleo PON e validará C0/C1 conforme protocolo.


## 7. Verificações finais realizadas após o registro inicial

### Python e Git
- Ambiente Windows Python 3.13.9, pip 25.2, Git 2.45.0.windows.1; módulo `venv` disponível.
- `python -m venv .venv` executado em `$HOME\tcc2\python-testes`. O Python do ambiente virtual reportou 3.13.9 e pip 25.2. Não foram instaladas dependências PON.
- `git ls-remote --heads https://github.com/JnetSilvestre/tcc1_JoaoVictor_BigData.git tcc2/desenvolvimento` identificou o commit `93cdba227074dca8e23831653ed4294caf107bcf` naquele instante.
- `git ls-remote https://github.com/JnetSilvestre/codigoPon.git refs/heads/main` identificou `c2d525b5c675820806af34348e259bff32a6bc5f`, mesma revisão da Etapa 04.
- Inspeção somente de código-fonte da revisão acima: `main.py` e módulos `pon/*.py` importam módulos internos e bibliotecas padrão `json`/`asyncio`; não há `requirements.txt` no inventário do commit. **Isso não comprova compatibilidade funcional Python 3.13** e não substitui testes da Etapa 07.

### Imagem Docker própria (E06-11 e E06-12)
- Arquivos reproduzidos em `infraestrutura/docker/teste-python/`: `Dockerfile` e `teste.py` (teste isolado, NÃO aplicação PON).
- O usuário executou `docker build -t tcc2-python-teste:etapa06 .` em `$HOME\tcc2\docker-testes`. Build finalizou `8/8 FINISHED`; imagem Linux/amd64, identificador apresentado `sha256:797d88a1b943...`, tamanho listado 176 MB.
- `docker run --name tcc2-python-validacao tcc2-python-teste:etapa06` retornou `Python: 3.13.18`, `Sistema: Linux`, `Arquitetura: x86_64`, `Status: EXECUCAO CONCLUIDA`. `docker ps -a` confirmou `Exited (0)`; `docker logs` reproduziu a saída; `docker run --rm --entrypoint python tcc2-python-teste:etapa06 --version` retornou `Python 3.13.18`.
- Python do host = 3.13.9 e Python da imagem = 3.13.18. A base foi especificada por tag, que é mutável; para experimentação final congelar digest da imagem e dependências. A imagem de teste não contém dependências da aplicação.

### Instrumentos de observação (E06-14)
- `kubectl --context kind-tcc2-pon top nodes` e `top pods -n tcc2-infra-test`: `Metrics API not available`.
- `kubectl --context kind-tcc2-pon get apiservice v1beta1.metrics.k8s.io`: `NotFound`. Logo, `kubectl top` **não está disponível**; optou-se por não instalar Metrics Server na Etapa 06.
- `docker stats --no-stream` retornou para `tcc2-pon-control-plane`: CPU 42,79%, memória 614,7MiB/7,679GiB, rede 21,8MB/4,44MB, block I/O 1,01MB/800MB, 273 PIDs; para `tcc2-pon-worker`: CPU 6,38%, memória 154,5MiB/7,679GiB, rede 34,7MB/1,99MB, block I/O 373kB/269MB, 106 PIDs.
- **Leitura pontual não é medição do PON.** Os contêineres representam nós virtuais, não necessariamente métricas individuais dos Pods; rede e I/O são contadores reportados pela ferramenta. Definir metodologia de coleta por serviço para C5/V12 nas Etapas 09–11 e medir sobrecarga.

### Limpeza controlada (E06-15)
- Antes da exclusão, `kubectl get all -n tcc2-infra-test` mostrou dois Pods Running e um Service ClusterIP.
- `kubectl --context kind-tcc2-pon delete namespace tcc2-infra-test --wait=true --timeout=120s` retornou `namespace "tcc2-infra-test" deleted`.
- Consulta posterior do namespace retornou `NotFound`; `kind get clusters` ainda listou `tcc2-pon` e `kubectl get nodes` mostrou os dois nós `Ready` v1.37.0.
- Uma tentativa extra de comando colado concatenou `--timeout=120sWrite-Host`, gerando `invalid argument`; isso **não invalida** a exclusão já confirmada. Nenhuma exclusão do cluster foi executada.
- O contêiner local `tcc2-python-validacao` ainda não teve remoção comprovada. A imagem construída foi preservada para inspeção. Não usar `docker system prune` indiscriminadamente.

## 8. Compatibilidade com os cenários da Etapa 05 e limitações

| Cenário | Condição após a Etapa 06 |
| --- | --- |
| C0 / C1 | Python/venv operacionais; implementação e oráculo PON ainda pendentes da Etapa 07 |
| C2 | Docker e build/execução Python mínima validados; os **três serviços PON** ainda não foram conteinerizados |
| C3 | Cluster Kubernetes multinó disponível; implantação real dos três serviços ainda pendente |
| C4 | Nós virtuais distintos e comunicação HTTP entre Pods de teste demonstradas; distribuição **física em máquinas independentes não testada**; aplicação PON entre nós pendente |
| C5 | Docker stats disponível apenas como leitura pontual dos nós; Metrics API ausente, carga/medidas da aplicação não realizadas |
| F1 | Reinício/replay da aplicação não implementado nem testado |

Para V01–V12, manter todos os testes funcionais da aplicação PON como **não executados** nesta etapa. Testes Nginx/curl são exclusivamente de infraestrutura. As requests/limits de Nginx/curl são exemplares dos manifests de teste, não parâmetros finais dos serviços PON. Não foram mensuradas latências nem contabilizadas séries históricas de CPU/memória de aplicação.

**Suporte e operação:** Windows 10 Home com Docker Desktop 4.99.0 é uma condição potencialmente não suportada nas matrizes atuais; observar atualizações e estabilidade. As leituras de recursos com múltiplos aplicativos abertos não equivalem a benchmark controlado. Não somar recursos alocáveis dos nós kind como recursos físicos independentes.

**Cuidado com capturas:** evidências E06-01 a E06-15 foram recebidas na conversa como prints e interpretadas; os arquivos PNG originais **não foram publicados neste repositório**. Reproduzir as capturas importantes em pasta de evidências de projeto quando disponível, preferencialmente com hash, data e comando associado. Não apresentar diagramas ilustrativos como captura de execução real.

## 9. Reproduzir o Docker de teste

```powershell
Set-Location .\infraestrutura\docker\teste-python
docker build -t tcc2-python-teste:etapa06 .
docker run --name tcc2-python-validacao tcc2-python-teste:etapa06
docker ps -a --filter "name=tcc2-python-validacao"
docker logs tcc2-python-validacao
docker run --rm --entrypoint python tcc2-python-teste:etapa06 --version
```

Não repetir com o mesmo nome de contêiner sem remover ou renomear o anterior. Teste de Docker em Python não implica aprovação do núcleo PON.

## 10. Encerramento técnico e transição

**Infraestrutura básica da Etapa 06 validada** com evidências observadas para Python, Docker, kind, Pods, DNS/Service e comunicação HTTP entre nós virtuais. As limitações de medição e do hardware foram identificadas, mas o hardware não foi submetido a teste de carga controlado. Os artefatos reprodutíveis de teste estão versionados.

**Próxima Etapa 07:** preservar `codigoPon` em `c2d525b5c675820806af34348e259bff32a6bc5f` como base; corrigir e testar `Condition`, `Rule`/asyncio e IDs; definir ambiente de dependências, oráculo determinístico e contratos HTTP/JSON de `attribute-source`, `logic-engine`, `rule-executor`, executar C0/C1 e V01–V07 **antes** de avançar para Docker da aplicação. Não afirmar que o código Python é equivalente à implementação NOP Query C++.
