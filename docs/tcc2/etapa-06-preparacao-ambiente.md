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
