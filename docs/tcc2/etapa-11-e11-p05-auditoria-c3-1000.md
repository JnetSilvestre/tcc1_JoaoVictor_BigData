# TCC2 — Etapa 11 / E11-P05: auditoria independente do piloto Kubernetes C3 / 1000

**Data:** 16/11/2026, ~00:06–00:07 America/Sao_Paulo; lote `2026-11-16T03:06:23.716827+00:00` a `03:06:43.953552+00:00`. **Fonte:** ZIP original real `run(3).zip` recebido na conversa, auditado diretamente com Python/zipfile sem repetir a execução, e transcrição PowerShell. **Status:** PASS funcional; CPU/memória INADEQUADOS para comparações quantitativas científicas; série E11-M01/V12 não iniciada.

## 1. Integridade, proveniência e topologia

- Arquivo ZIP original **178.711 bytes**, SHA-256 recalculado `66e071c8c32130978cd220472cabb91029ab7b0e38a2bbd3f3c8fe2900ed0b09`, coincide com terminal. **22 arquivos únicos**, 22/22 CRCs ZIP válidos, **21/21 hashes internos** em `checksums.sha256` conferidos. Não há falha de extração.
- Git HEAD executado `2dcdc230f0777a8b902298c4bd6c582539fe709a`; 33/33 testes Python aprovados, 0,101 s de suíte (NÃO duração de benchmark). `manifest.json` confirma fixture canônica 1.000/seed 20260502, hash `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`, image ID Docker aprovado `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Namespace isolado `tcc2-pon-e11-c3-p20261115-235728`, run ID `e11-c3-p20261115-235728`. Topologia start/end idêntica para os três serviços; todos no `tcc2-pon-worker`, zero reinícios, nomes, UID, IP, containerID, serviços e imageID estáveis. Nós virtuais worker/control-plane Ready; não existem hosts físicos independentes.
- `states-cold.json`: três serviços não prontos, `run_id=null`, atributos iniciais `atA=0,atB=0`, watermarks zero, sem effects, sem fault. `snapshot-response.json`: HTTP 200, duplicate=false, ready=true, versão `e11-c3-p20261115-235728:snapshot:0`. `states-after-snapshot.json` e `states-final.json` consistentes. Foi uma tentativa única segundo o fluxo e logs; não executar novamente.

## 2. Oráculo e causalidade reconstruídos independentemente

- 1.000 registros `request` + um resumo `summary` em `client.stdout.jsonl`, 1.000/1.000 HTTP 200, sem erros, todos com `step` correspondente à fixture; reconstituição independente dos campos `changed`, `sequence`, `event_id`, `duplicate_request` a partir dos 1.000 inputs resultou em **0 divergências**.
- 874 alterações verdadeiras, 126 no-ops; 874 payloads `AttributeChanged` enviados pela fonte e recebidos pelo motor lógico em ordem e conteúdo idênticos; 500 payloads `ConditionChanged` emitidos e recebidos pelo executor com a mesma ordem/conteúdo.
- 250 objetos `effects.jsonl` **semanticamente idênticos** aos 250 de `expected.jsonl` e aos 250 logs de efeito do rule-executor. Passos esperados 3,7,11,...,999. Não houve efeito perdido ou extra detectado.
- Estado final em três serviços: `atA=10,atB=0`, sequências `atA=374`, `atB=500`, condição final `approved=false`, 500 transições, 250 efeitos e sem fault. `validation.json`: 10/10 checks gerais PASS, 4/4 transporte PASS, `status=PASS`.

## 3. Tempo HTTP — uma rodada exploratória

| Indicador | C3/1000 E11-P05 | Comentário |
|---|---:|---|
| Duração do lote monotônico | **20,236690945 s** | `time.perf_counter_ns` dentro do cliente Pod |
| Throughput | **49,4152 req/s** | 1000 / duração |
| RTT médio | **20,2110 ms** | N=1000 |
| RTT mediana | **18,4104 ms** | N=1000 |
| RTT p95 nearest-rank | **49,8723 ms** | N=1000 |
| RTT p99 nearest-rank | **104,6951 ms** | N=1000 |
| RTT máximo | **144,1052 ms** | N=1000 |
| RTT mediana com mudança | **18,9398 ms** | N=874 |
| RTT mediana no-op | **1,2516 ms** | N=126 |

- Tempo UTC entre marcas é 20,236725 s; diferença de ~0,034055 ms relativa a `perf_counter_ns`, `clock_coherent=true`. Essa coerência interna não demonstra sincronismo entre relógio do Pod e relógio Kubelet.
- C2/1000 E11-P04 teve ~20,21046 s e 49,4793 req/s; NÃO inferir equivalência, vantagem ou significância com base em apenas uma rodada de cada e instrumentos/ambientes diferentes.

## 4. Qualidade instrumental reprovada: causa real

- `metrics-samples.jsonl` **76 registros**, correspondentes a 19 observações por papel (3 serviços + cliente). `metrics-errors.json=[]`. Consistência CSV/JSONL conferida (76 linhas). Há timestamps de CPU e memória válidos e contadores sem regressão, mas a Summary API retorna dados defasados e repetidos.
- Para os três SERVIÇOS, os 19 registros por papel produzem apenas **3 timestamps de CPU distintos** em `attribute-source` (16 duplicatas), **3** no `logic-engine` (16 duplicatas) e **2** no `rule-executor` (17 duplicatas). Nenhuma duplicata ambígua do contador e nenhuma regressão. O gate exige no mínimo 5 timestamps distintos, gaps <=4 s e uma amostra de fonte que delimite o fim do lote.
- Últimos timestamps da fonte: `attribute-source=03:06:41 UTC`, `logic-engine=03:06:42 UTC`, `rule-executor=03:06:30 UTC`. O lote terminou em **03:06:43.953552 UTC**; **não existe amostra de origem posterior ao fim** para nenhum serviço. Portanto não é possível calcular um delta de CPU bracketing e **`cpu_window_adequate=false`**. A memória também carece de fronteiras/frequência adequadas: `memory_window_adequate=false`.
- `metric_quality`: `cpu_counter_present_monotonic=true`, `clock_coherent=true`, `sample_count=76`, `cpu_window_adequate=false`, `memory_window_adequate=false`, `usable_cpu=false`, `usable_memory=false`, seis issues (CPU e memória por cada papel). Valores máximos de working set AMOSTRADOS e não aprovados: source 62,3867 MiB, logic 61,4297 MiB, executor 20,7305 MiB. Não somar como pico simultâneo nem comparar a memória bruta Docker como a mesma métrica.
- Importante: o coletor utilizou consultas GET `kubectl` aos dois nós, sem erros reportados, mas o refresh interno do Kubelet foi mais lento/irregular que as consultas. Não afirmar que 76 observações equivalem a 76 amostras novas, nem preencher lacunas interpolando contadores.
- A reprovação instrumental NÃO invalida a evidência de viabilidade funcional nem o tempo HTTP do cliente, mas limita a comparação de recursos. Este piloto não deve ser usado como ponto de custo computacional de CPU/RAM definitivo.

## 5. Decisão e seguimento

1. **E11-P05 concluído, funcionalmente PASS auditado, integridade PASS.** Marcar namespace `tcc2-pon-e11-c3-p20261115-235728` como GASTO para mutações. Preservar Pods, logs, ZIP e UIDs; não reenviar snapshot nem lote.
2. Prosseguir E11-D12 com **preparação de nova bancada C4/1000**, separada de namespaces históricos, com gate de preflight/cold state antes de qualquer snapshot. E11-P06 só após auditoria E11-D12.
3. Na escrita científica, RTT/throughput são métricas primárias exploratórias, com replicação estatística futura. CPU e memória via Kubelet Summary API permanecem diagnósticas/reprovadas até adequação temporal ou método alternativo calibrado. Não 'relaxar' requisitos de frescor ad hoc para declarar CPU válida.
4. Próximos gates: C4/1000 funcional, desenho de redução de interferência observador e seleção de métricas secundárias, protocolo congelado E11-M01, séries repetidas com controle de ordem/aquecimento, E11-A01 auditoria dos dados. Etapa 12 analisa e discute; não iniciar V12 agora.

**Auditoria baseada em arquivos reais, sem execuções adicionais na infraestrutura.**
