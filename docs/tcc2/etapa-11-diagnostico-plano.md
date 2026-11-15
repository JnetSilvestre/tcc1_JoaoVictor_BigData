# TCC2 — Etapa 11: diagnóstico e proposta de protocolo quantitativo

**Data:** 2026-11-15  
**Branch exclusiva:** tcc2/desenvolvimento  
**Ponto de partida documental:** d761b59424ae56dd8243ef840ff8e02c11003501  
**Situação:** PLANO PRELIMINAR; ainda não congelado, sem execução de benchmark, sem resultados quantitativos.

## 1. Evidências e limites herdados

- Referências primárias: STATUS_ATUAL_TCC2.md (última seção cronológica); docs/tcc2/etapa-05-protocolo-experimental.md; docs/tcc2/etapa-09-auditoria-c3-zip.md; docs/tcc2/etapa-10-auditoria-c4-zip.md; docs/tcc2/etapa-10-checkpoint.md.
- C0/C1, C2, C3 e C4 aprovados apenas nos respectivos testes funcionais realizados. C3: três Pods no worker virtual. C4: source e executor no worker, logic no control-plane; V09 aprovado apenas para dois nós kind no mesmo host físico.
- C3 ZIP: 27165 bytes; SHA-256 aad71cea5e90b9c6a334f66180f54dc5609a024b907b7c7f121f6ed4d5855b83.
- C4 ZIP: 36370 bytes; SHA-256 8f77d981abb6977890f948168924b594398828ef3d843d7f38baf66d09acca7c.
- Não há benchmarks validados. Tempos de unittest, timestamps de log e duração dos runners funcionais não constituem métricas quantitativas da aplicação.
- C3 e C4 já exercitados contêm estado em memória. Não reenviar snapshot, mudanças, reiniciar, escalar, alterar ou remover seus namespaces/Pods. Não alterar master nem JnetSilvestre/codigoPon.
- A aplicação é uma prova de conceito Python com três serviços HTTP/JSON síncronos/seriais; não equivale ao NOP Query completo em C++ nem a consulta real de vídeo.

## 2. Diagnóstico do código disponível

- prova-conceito/c0/runner.py: verifica fixture, compara núcleo com oráculo e grava hashes. O tempo total do runner inclui I/O, oráculo e validação; não é benchmark.
- prova-conceito/c0/pon_execution.py e c0/oracle.py: cadeia PON local e oráculo independente reutilizáveis para validar fixtures maiores. Oráculo não deve entrar na janela cronometrada do C0.
- prova-conceito/c1/service.py: HTTPServer serial, encaminhamento síncrono e logs JSONL; c1/state.py mantém estados/ledgers em memória, sem replay persistente.
- prova-conceito/c1/client.py: cliente urllib simples com timeout de 5 segundos.
- prova-conceito/c2/runner.py: execução funcional Docker com verificações e coleta, sem instrumentação quantitativa.
- prova-conceito/c3/runner.py: cada operação HTTP lança kubectl exec e um Python curto no Pod; NÃO medir duração do runner como latência da aplicação.
- prova-conceito/c4/runner.py: reutiliza C3, prepara snapshot C4 de uso único e audita equivalência; NÃO reutilizar sobre C4 aprovado.
- infraestrutura/kubernetes/c3/manifests.yaml e c4/manifests.yaml: três Deployments/Services, requests de 100m/128Mi e limits 500m/256Mi por Pod; limites foram definidos para funcionamento, ainda não para experimento.
- Não foi identificado gerador de carga quantitativa, sampler reproduzível de CPU/memória ou consolidador de resultados neste inventário. A API de kubectl top estava indisponível no diagnóstico anterior: disponibilidade atual permanece a verificar.

## 3. Pergunta e desenho comparativo PROPOSTOS

Pergunta adicional à funcional: com carga, semântica, código de serviço e recursos documentados, como variam o tempo de resposta, a vazão, CPU e memória da prova de conceito ao passar da execução local para comunicação entre serviços e orquestração em kind?

- **Faixa de referência C0:** núcleo de execução local; baseline algorítmico. Não interpretar C0 versus C4 como efeito causal isolado de Kubernetes, pois muda também o transporte e possivelmente o SO/runtime.
- **Faixa HTTP C1/C2/C3/C4:** três serviços e uma réplica por papel; injeção serial (concorrência=1), uma chamada por alteração. C1 Windows multiprocesso serve como referência adicional, com diferença de SO explicitada.
- **Comparação principal recomendada:** C2 versus C3 versus C4, com mesma imagem de serviços, mesma sequência de solicitações, mesma semântica e políticas equivalentes de recursos. Diferenças de rede, camada de execução e posicionamento permanecem fatores correlacionados; não afirmar causalidade isolada quando não controlados.
- C5 é a variação de volume aplicada aos cenários, não uma nova arquitetura. Não experimentar escalonamento horizontal nem tolerância a falhas como parte desta primeira série.

## 4. Cargas e repetições CANDIDATAS — não aprovadas

- Fixture mínima de sete passos continua como teste de sanidade, não como amostra de desempenho.
- Cargas propostas da Etapa 05: 100, 1000 e 10000 requisições de alteração, com sementes 20260501/20260502/20260503; confirmar a semântica de cada semente, proporção de no-op, mudanças efetivas, transições e efeitos antes de congelar os arquivos.
- O gerador deverá construir JSONL determinístico; o oráculo independente criará os efeitos esperados, e cada carga terá SHA-256 versionado. O run_id varia a cada rodada; comparar a carga canônica separadamente do arquivo rebased por rodada.
- Primeiro piloto 100 e 1000 para validar tempo, volume de log, CPU/memória e limites; 10000 só entra após aprovação do piloto e risco de OOM/timeout. Esses limites podem ser revisados antes do congelamento, nunca retroativamente em função dos resultados.
- Dez repetições independentes por cenário/carga após aquecimento são o alvo inicial herdado da Etapa 05, não garantia de poder estatístico; decidir manutenção com base no piloto e no tempo de execução.
- Cada repetição exige nova instância com estado frio, run_id exclusivo, snapshot exclusivo, prova de 3/3 ready e zero eventos antes da injeção. Aquecimento apenas com GETs não mutantes antes do snapshot ou em bancada descartável, sempre identificado.
- Intercalar a ordem dos cenários por blocos quando factível; manter configurações do host estáveis, registrar apps concorrentes e recursos compartilhados.

## 5. Métricas e pontos exatos de medição

**Primárias:**
1. T_batch (s): tempo monotônico no MESMO cliente persistente desde imediatamente antes do primeiro POST até receber o último HTTP 200; EXCLUI criação dos serviços, snapshot, geração de dados, oráculo, leitura final de estado e empacotamento.
2. RTT por requisição (ms): perf_counter_ns imediatamente antes/depois do POST síncrono. Registrar tipo no-op/mudança/efeito, tamanho do payload e status; o ACK do código atual é propagado sincronicamente pela cadeia quando há notificação.
3. Vazão: N_requisições/T_batch e N_mudanças_efetivas/T_batch, com unidades e denominadores distintos.
4. Correção: contagens de requisições, mudanças, condições e efeitos; comparação exata por ordem/causalidade com oráculo; 0 erros, 0 perdas e 0 duplicações não previstas são pré-condições da validade do benchmark.

**Secundárias condicionais à sondagem real:**
5. CPU-segundos por papel: diferença de contador cumulativo em janela delimitada; tentar cgroup v2 cpu.stat usage_usec nos Linux containers, verificando isolamento/escopo antes de usar. Em C0, process_time_ns do processo medido. Não misturar denominadores ou CPU% instantâneo.
6. Memória por papel: máximo **amostrado** de memory.current (cgroup v2, inclui componentes além de RSS), com cadência e perdas informadas; memory.peak é pico desde criação/reset do cgroup, não presumir pico exclusivo da janela. Documentar separadamente métricas de memória da CLI docker stats, que desconta cache.
7. Rede: contadores brutos por interface/contêiner somente se comprovados e atribuíveis, não estimar bytes com base apenas em número de eventos.

**Não disponíveis automaticamente:** latência entre nós por diferença de timestamps, RSS/pico preciso, CPU de máquinas físicas independentes, energia, velocidade de escalabilidade e recuperação após falha. kubectl top/metrics-server não será fonte única de série temporal.

## 6. Instrumentação a implementar SEM alterar o núcleo funcional

- prova-conceito/benchmark/fixtures.py — gerar e validar cargas determinísticas e metadados; sem simular resultados.
- prova-conceito/benchmark/client.py — driver persistente com mesmo protocolo HTTP, sem kubectl exec a cada POST; intervalos monotônicos, uma requisição por vez, timeout/erro registrados, sem retry automático.
- prova-conceito/benchmark/runner.py — escolher cenário, isolar bancada, preflight obrigatório, snapshot único, aquecimento não mutante, medição, drain, auditoria e ZIP; falhas interrompem novas mutações.
- prova-conceito/benchmark/metrics.py — sondagem de cgroup v2, contadores CPU/memória e metadados; recurso opcional explicitamente indisponível caso falhe.
- infraestrutura/kubernetes/benchmark/ — novos namespaces e manifests/JOBs de gerador exclusivos, usando placement C3/C4 conforme cenário; nunca reutilizar os namespaces já validados.
- infraestrutura/docker/benchmark/ (se necessário) — rede Docker e três contêineres exclusivos, mesma imagem e políticas equivalentes.
- prova-conceito/benchmark/validate.py — confrontar efeitos, causalidade, counters, integridade e arquivos SHA-256; não selecionar apenas execuções rápidas.
- prova-conceito/benchmark/aggregate.py — gerar resumo de CSV de rodadas apenas após validação. Scripts de análise final e gráficos ficam sob Etapa 12.

Implementar primeiro os instrumentos e testes sintéticos explicitamente rotulados, depois uma única rodada piloto por configuração candidata. Evitar instrumentação invasiva do runtime aprovado. Se a coleta de CPU/memória exigir mudança de código de serviço, justificar e validar invariância antes de considerar.

## 7. Artefatos mínimos por rodada

Pasta exclusiva experimentos/<run_id>/ contendo:
- manifest.json e environment.json: Git SHA, versões, clocks, imagem/digest, limites, cenário, nó, Pod/container IDs, parâmetros e motivo de exclusão.
- inputs.jsonl e expected.jsonl, checksums de carga canônica e arquivo rebaseado;
- requests.jsonl (um registro por POST com monotonic duration e status), effects.jsonl, events.jsonl/logs dos três serviços, states-before/after;
- cpu-before.json, cpu-after.json, memory-samples.csv quando instrumentos aprovados; métricas ausentes como null/unsupported com justificativa, nunca zero inventado;
- validation.json, checksums.sha256 e ZIP imutável com SHA-256 externo.
Guardar ZIPs brutos fora do GitHub, sem credenciais. Versionar código, manifests, critérios e relatório auditável; não versionar grandes resultados binários.

## 8. Gate de validade e estatística

- Piloto só passa se preflight de código/imagem/recursos, estado frio, inicialização, topologia, preservação de C3/C4, integridade do gerador, oráculo, contadores e ZIP forem verificáveis.
- Status HTTP inesperado, Pod reiniciado, CPU throttling relevante não documentado, erro de clock, métricas inválidas ou erro funcional invalidam ou suspendem a rodada conforme política previamente congelada; registrar todas as falhas sem sobrescrever dados.
- Não repetir POST incerto. Investigar a bancada e preservar evidências; para uma nova rodada, criar nova bancada.
- Resumir repetições por mediana, IQR, mínimo/máximo e incerteza, sem descartar outliers arbitrariamente. Distribuição de latências por requisição não equivale a repetição experimental independente.
- Não afirmar speedup por paralelismo nem superioridade do Kubernetes sem dados e identificação adequada dos fatores de confusão.

## 9. Sequência eficiente de trabalho

E11-D01: uma coleta PowerShell somente leitura de ambiente, Git, Docker/kind, cgroup, capacidade e API de métricas.  
E11-I01: fechar método, prioridades, cargas, critérios de aceitação e referências metodológicas (Perplexity como pesquisa auxiliar, com checagem independente).  
E11-I02: implementar driver + gerador + monitor + validadores em incremento único, com testes que não fazem POST em C3/C4.  
E11-P01: piloto isolado em novas bancadas, uma execução por configuração, arquivar e auditar antes de avançar.  
E11-M01: congelar protocolo e executar séries balanceadas/repetições definidas; preservar todos os brutos.  
E11-A01: auditar ZIPs, hashes, completude, falhas e organizar insumos para Etapa 12, sem antecipar conclusões.

## 10. Decisões ainda pendentes

1. Confirmar capacidade e cgroups reais com leitura na máquina Windows; se necessário, reduzir instrumentação secundária.
2. Fixar especificação exata das fixtures e hashes, não apenas tamanho e semente.
3. Fixar limites CPU/RAM equivalentes para C2/C3/C4 (500m/256Mi são configuração funcional, não decisão experimental automática) e validar ausência de OOM/throttling impeditivo.
4. Fixar local do gerador por cenário, duração/intervalo das leituras, timeout por request/rodada, aquecimento e política de falha.
5. Aprovar a interpretação dos contrastes C0/C1 versus C2/C3/C4 diante de diferentes SOs e níveis de virtualização.
6. Confirmar desenho e prioridade do estudo com orientador e buscar referências metodológicas no Perplexity; não incluir bibliografia sem validar documentos.
7. Após obter resultados, usar Etapas 12–15 para análise e construção/revisão do projeto LaTeX UTFPR em Work/Overleaf, preservando os arquivos acadêmicos existentes e conferindo pré-textuais, referências e PDF compilado.

**Entregável desta revisão:** somente diagnóstico e protocolo preliminar versionado. **Não foram executados benchmarks, criados novos namespaces, alterados Pods ou coletadas medições.**
