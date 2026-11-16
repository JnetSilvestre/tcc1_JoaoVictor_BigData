# TCC2 — Etapa 11 / E11-P06 — Auditoria independente do piloto Kubernetes C4 / 1.000

**Execução reportada:** 16/11/2026 ~00:33 America/Sao_Paulo. Janela do cliente: `2026-11-16T03:33:59.693377+00:00` até `2026-11-16T03:34:19.616775+00:00`. **Fonte primária:** arquivo real `run(4).zip` enviado pelo acadêmico, lido diretamente com ZIP/JSONL/CSV, e transcrição PowerShell. **Resultado:** PASS funcional e integridade PASS. **CPU e memória NÃO são métricas comparativas aprovadas**. Nenhuma nova execução ou modificação de recursos Kubernetes foi realizada durante a auditoria.

## 1. Proveniência e integridade SHA-256

- ZIP recebido `run(4).zip`: **178.954 bytes**, SHA-256 recalculado `4a39d39b227ec8dd0a74a24233cf364cb165df2173655c54513361033f56c847`, exatamente o registrado no PowerShell.
- **22 nomes distintos**, 22/22 testes CRC do ZIP OK, **21/21 hashes SHA-256 individuais** em `checksums.sha256` corretos (exceto o próprio manifesto de hashes, sem autorreferência).
- Git HEAD da execução `5ae84606dde4262a0025ed8f8719a3a8d88b9d2f`; **38/38 testes** Python PASS em 0,148 s (tempo da suíte, não benchmark).
- `manifest.json`: cenário C4, namespace `tcc2-pon-e11-c4-p20261116-001328`, run ID `e11-c4-p20261116-001328`, fixture canônica 1.000 com SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, seed `20260502`, imagem idêntica aprovada `tcc2-pon:c2-e08-dbefcd2cf3d2`, Docker imagem `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`. A versão rebaseada da fixture tem SHA próprio.

## 2. Estado frio, snapshot único e topologia C4

- `states-cold.json` contém os 3 serviços antes de qualquer inicialização: `ready=false`, `run_id=null`, `snapshot_version=null`, fonte `atA=0`, `atB=0`, sequências zero; logic `attributes=null`, `condition=null`, zero eventos; rule executor `approved=null`, zero effects, sem fault.
- `snapshot-response.json`: HTTP 200, `duplicate=false`, `ready=true`; versão `e11-c4-p20261116-001328:snapshot:0`. Os logs de cada serviço têm **um único evento de mutação `/init/snapshot`** correspondente. Estados posteriores ao snapshot (`states-after-snapshot.json`) mostram os 3 serviços prontos, mesmo `run_id` e versão.
- `topology-start.json` e `topology-end.json` possuem Pods, UIDs, IPs, container IDs, image IDs, nós e serviços **idênticos**. Contadores de reinício zero. Worker contém `attribute-source`, `rule-executor` e cliente; control-plane contém `logic-engine`. Ambos nós Ready.
- Os nós são **virtuais de kind na mesma máquina física**; não inferir comportamento de duas máquinas físicas, paralelismo de processamento ou overhead causal puro de Kubernetes.

## 3. Auditoria independente de funcionalidade

- `inputs.jsonl` = 1.000 entradas, `client.stdout.jsonl` = 1.000 respostas individuais mais um resumo final. Cada resposta foi reconstituída a partir dos estados esperados e conferida para `step`, HTTP 200, `changed`, `sequence`, `event_id` e `duplicate_request=false`: **0 discrepâncias**.
- **874 mudanças efetivas e 126 no-ops**. `attribute-source-logs.jsonl` -> `logic-engine-logs.jsonl`: **874/874** notificações de atributo com mesmo payload e mesma ordem. `logic-engine-logs.jsonl` -> `rule-executor-logs.jsonl`: **500/500** notificações de condição preservadas.
- Efeitos `effects.jsonl`: **250/250** semanticamente idênticos a `expected.jsonl` e aos eventos de efeito do executor; passos `3,7,11,...,999`, sem efeitos extras ou faltantes.
- Estado final: `atA=10`, `atB=0`; sequências `atA=374`, `atB=500`; condição final `approved=false`; 500 transições e 250 efeitos, nenhum `faulted`. Todas as 10 checagens gerais e quatro de transporte em `validation.json` são verdadeiras, status global PASS.

## 4. Tempos HTTP — rodada exploratória SEM inferência

| Medida | E11-P06 C4/1000 |
|---|---:|
| `T_batch` monotônico no cliente Pod | **19,923379794 s** |
| Throughput `1000/T_batch` | **50,1923 req/s** |
| RTT médio dos 1.000 POSTs | **19,8974 ms** |
| RTT mediano | **19,3446 ms** |
| RTT p95 (nearest-rank) | **44,8173 ms** |
| RTT p99 (nearest-rank) | **94,8927 ms** |
| RTT máximo | **178,4491 ms** |

- Marcadores UTC apontam intervalo de 19,923398 s, diferença de apenas ~0,018206 ms relativa ao monotônico (`clock_coherent=true`). Isto NÃO comprova sincronismo entre Pod e Kubelet nem possibilita latências entre nós por subtração de timestamps.
- `client.stderr.log` vazio, 1.000 respostas HTTP 200. Todos os dados são de **uma única rodada C4**.

## 5. CPU/memória REPROVADAS por falta de frescor e bracketing

- `metrics-samples.jsonl` = **76 observações**: 19 consultas amostradas por papel (source, logic, rule-executor e cliente). CSV tem 76 linhas. `metrics-errors.json=[]` e contador sem regressão, mas a Summary API repetiu timestamps e valores de origem.
- **Somente DOIS timestamps de CPU distintos para cada um dos três serviços** (17 observações repetidas por papel). Fonte `attribute-source`: 03:33:45 e 03:34:03 UTC; logic-engine: 03:33:52 e 03:34:07; rule-executor: 03:33:58 e 03:34:14.
- O último timestamp da fonte para os três serviços é ANTERIOR ao final do lote, `03:34:19.616775 UTC`, respectivamente por ~16,617 s (source), ~12,617 s (logic) e ~5,617 s (executor); nenhum contador observado delimita a fronteira final.
- `cpu_counter_present_monotonic=true`, `clock_coherent=true`, mas `cpu_window_adequate=false`, `usable_cpu=false`. A cobertura requer bordas adequadas, >=5 timestamps distintos e gaps <=4s; dados não passam. `memory_window_adequate=false`, `usable_memory=false` para todos os serviços. Não interpolar lacunas nem forçar valores de CPU-segundos como se fossem exatos.
- Máximos de memória de **working set** AMOSTRADOS e **não aprovados como pico de lote**: source 59,0820 MiB, logic 57,7188 MiB, executor 21,4414 MiB; cliente 19,9688 MiB. Instantes assíncronos; não somar. Docker C2 reporta memória bruta, métrica semanticamente distinta.
- **Causa operacional da reprovação**: 19 consultas per papel não significam 19 atualizações de origem; refresh Kubelet muito mais lento do que período requisitado de 1 s. Nenhum erro HTTP foi registrado nas consultas, mas não há resolução temporal para atribuir custo de CPU ou pico de memória ao lote.

## 6. Consolidado dos pilotos 1000 — SOMENTE DESCRITIVO

| Cenário | Piloto | `T_batch` (s) | Vazão (req/s) | RTT mediana (ms) | RTT p95 (ms) | Funcional | CPU/memória |
|---|---|---:|---:|---:|---:|---|---|
| C2 Docker | E11-P04 | 20,210462 | 49,4793 | 19,1079 | 50,7198 | PASS | CPU cobertura provisória, medição não aprovada; memória não comparável |
| C3 kind/1 nó virtual | E11-P05 | 20,236691 | 49,4152 | 18,4104 | 49,8723 | PASS | Cobertura CPU/memória reprovada |
| C4 kind/2 nós virtuais | E11-P06 | 19,923380 | 50,1923 | 19,3446 | 44,8173 | PASS | Cobertura CPU/memória reprovada |

**Estes três pilotos são uma única observação por configuração**, em períodos sequenciais com instrumentalidade diferente e sem desenho de ordem balanceada. Proibido apresentar as diferenças numéricas como speedup, superioridade, equivalência estatística, robustez a falha ou escalabilidade horizontal física. O experimento primário utiliza injeção serial/concorrência 1 e cadeia HTTP/JSON síncrona.

## 7. Decisão e próximos passos

1. **E11-P06 auditado: funcional PASS, integridade PASS, CPU/memória INADEQUADAS.** A bancada `tcc2-pon-e11-c4-p20261116-001328` está **gasta para novos snapshots ou POSTs** e deve ser preservada íntegra, como C2/1000 e C3/1000 anteriores.
2. **Pilotos C2/C3/C4 de 1.000 concluídos funcionalmente**; não existe série estatística quantitativa independente. O desenho para as métricas primárias pode prosseguir, mas precisa ser **congelado antes de produzir dados definitivos**, incluindo n=10 proposto, ordem de execução, limites/quota, aquecimento, coleta, tolerância a falhas, host compartilhado e exclusões pré-registradas.
3. Replanejar observabilidade secundária **sem reajustar critérios retroativamente**: caracterizar efeito observador do Docker Engine API; CPU C2 teve throttling; avaliar leitura externa de contadores por cgroups/CRIs Linux com correspondência de Pod/container ID, com acesso SOMENTE READ-ONLY. Não assumir que o método alternativo exista ou esteja validado.
4. Considerar piloto de 10.000 requisições apenas após avaliação de capacidade (memory/CPU/throttling), timeout e evidências do ambiente; não derivar duração garantida de extrapolação linear do piloto 1.000. Pod stateful exige **nova instância fria a cada execução**.
5. Próximos entregáveis E11-M00 (fechamento metodológico) -> E11-M01 (séries repetidas controladas) -> E11-A01 (auditoria integral dos ZIPs) -> Etapa 12 (análise estatística).

**Não houve nova atividade experimental no Kubernetes/Docker por esta auditoria. ZIP bruto fornecido continua preservado fora do GitHub.**
