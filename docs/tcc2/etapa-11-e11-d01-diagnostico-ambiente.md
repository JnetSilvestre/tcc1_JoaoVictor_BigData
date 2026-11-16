# TCC2 — Etapa 11 / E11-D01: diagnóstico do ambiente de medição

**Recebido:** 15/11/2026, execução local declarada às 21:02:01-03:00.  
**Origem:** transcrição textual do PowerShell fornecida pelo acadêmico nesta conversa.  
**Natureza da evidência:** diagnóstico somente leitura; o arquivo TXT bruto local ainda não foi recebido para auditoria binária/hash.  
**Estado:** E11-D01 aprovado quanto ao inventário solicitado; instrumentação por contêiner e protocolo quantitativo permanecem pendentes. **Nenhum benchmark executado.**

## 1. Git e proveniência

- Branch local reportada: tcc2/desenvolvimento.
- HEAD local reportado: f84c8384f33168219213757f9b2027216a2511e4.
- Saída de git status --short sem entradas: indica árvore de trabalho aparentemente limpa.
- **Observação:** o HEAD local é anterior ao commit documental da Etapa 11 71675c0fd2d95fadfd715bd08c5db3608385389d, confirmado como HEAD remoto da branch em leitura posterior. Não é indicação de execução de código desatualizado da prova: o descompasso identificado corresponde aos commits documentais publicados após o encerramento C4. Antes de novos procedimentos, usar git pull --ff-only origin tcc2/desenvolvimento, após confirmar branch/árvore limpa.

## 2. Host e Docker/WSL2

- Windows 10 Home, 10.0.19045.
- Intel Core i5-9300H @2.40 GHz: 4 núcleos físicos, 8 processadores lógicos.
- TotalVisibleMemorySize=16614052 KiB (reportado pelo WMI, não a quota Docker).
- WSL versão padrão 2; distribuição padrão docker-desktop.
- Docker client/server 29.9.3; Docker Desktop 4.99.0 (245822); contexto desktop-linux.
- Engine Linux/amd64, containerd 2.4.2, runc 1.5.2.
- CgroupVersion=2 no daemon Docker; NCPU=8; MemTotal=8245637120 bytes. **Não inferir que cada nó kind tem recursos físicos próprios.**
- Imagem C2 local com ID sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a, consistente com as auditorias C3/C4.

## 3. Kubernetes e preservação

- Cluster kind tcc2-pon: dois nós Ready; Kubernetes v1.37.0; Debian GNU/Linux 13; kernel 6.18.58.1-microsoft-standard-WSL2; runtime containerd 2.3.4.
- tcc2-pon-control-plane, IP 172.18.0.2; tcc2-pon-worker, IP 172.18.0.3. São nós virtuais no mesmo host.
- C3, namespace tcc2-pon: attribute-source, logic-engine, rule-executor 1/1 Running, RESTARTS=0, todos no worker. Os três Pods mantêm os mesmos nomes identificados nos artefatos da Etapa 09.
- C4, namespace tcc2-pon-c4: attribute-source e rule-executor no worker, logic-engine no control-plane, 1/1 Running, RESTARTS=0. Nomes/IPs coincidem com o artefato C4 auditado.
- Não há relato de alteração, novo evento, restart, escala ou exclusão dos Pods C3/C4 nesta sondagem.

## 4. API de métricas e implicação

- A chamada kubectl --context kind-tcc2-pon get --raw /apis/metrics.k8s.io/v1beta1 retornou HTTP NotFound (“server could not find the requested resource”).
- **Interpretação estrita:** a API metrics.k8s.io/v1beta1 não está disponível neste diagnóstico. Isso **não prova**, isoladamente, ausência do binário Metrics Server ou dos contadores internos do kubelet.
- O host usa cgroups v2 (confirmado no Docker), mas isso **não comprova** que os contadores por contêiner estejam disponíveis/isolados dentro dos Pods kind nem valida precisão/amostragem.
- Próximo diagnóstico instrumental: avaliar Kubelet Summary API por nó (somente GET, sem requisições ao aplicativo), verificar presença de usageCoreNanoSeconds e memory.workingSetBytes por contêiner, timestamps e intervalo de atualização. A API Summary é distinta de metrics.k8s.io e pode existir sem Metrics Server.
- Se Kubelet Summary indisponível/inadequado, avaliar acesso seguro a cpu.stat e memory.current/peak dos cgroups de **novas bancadas** após instrumentação; não executar novos comandos nos Pods C3/C4.
- Docker stats não é equivalente a cgroup memory.current, e amostras do nó kind não podem ser atribuídas às aplicações específicas.

## 5. Decisões e pendências

**Aceito em E11-D01:** inventário do hardware, software, versão de cgroup do Docker, imagem C2 e topologia preservada; registro da indisponibilidade da API metrics.k8s.io.

**Não aceito/pendente:** API Summary, fontes confiáveis de CPU por papel, memória por papel, janela temporal, cadência, overhead do coletor, limites finais, gerador persistente, plano de aquecimento, fixtures de carga e séries experimentais.

**Próximo E11-D02:** uma sondagem PowerShell curta, somente leitura, para Kubelet Summary API e cgroup v2 dos contêineres de nó kind; saída textual sem dump de métricas extensas; sincronizar documentação via fast-forward sem tocar em master. Após a sondagem, aprovar ou descartar instrumentos e implementar benchmark em bancada própria.

**Advertência:** CPU/latência/vazão e memória científica **ainda não foram medidas**. Não converter uptime, tempo de testes funcionais ou idade dos Pods em resultados de desempenho.
