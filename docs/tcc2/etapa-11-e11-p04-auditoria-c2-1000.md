# TCC2 — Etapa 11 / E11-P04 — Auditoria independente do piloto Docker C2 / 1.000

**Escopo:** auditoria de arquivo real, sem nova execução mutante, sem Docker/Kubernetes nesta análise. **Data do piloto local:** 15/11/2026 ~23:29 America/Sao_Paulo; `batch_started_utc` 2026-11-16T02:30:01.243398+00:00, `batch_finished_utc` 2026-11-16T02:30:21.453914+00:00. **Status: piloto funcional PASS, janela CPU adequada segundo critérios provisórios; medição científica NÃO aprovada.** V12 ainda não iniciada.

## 1. Evidência recebida e integridade

- Arquivo bruto fornecido: `run(2).zip`; **189.105 bytes**, SHA-256 recalculado `cf6eb1acc121799e803f45322d671c1404afcfbd15401c52c4211dafdc8e3c19`, exatamente igual ao valor exibido no PowerShell.
- ZIP: **24 entradas distintas; CRC 24/24 válido; 23/23 hashes** listados no `checksums.sha256` verificam exatamente os conteúdos individuais. Não há arquivos não listados além do próprio manifesto de hashes.
- Git HEAD do piloto: `52ec6e3fe609162b4b03aa3232dba5083c59402b`; compilação sintática PASS; **28/28 testes** do controlador PASS em 0,109 s (**tempo da suíte, não benchmark**). Docker Engine 29.9.3. Imagem de runtime fixa: `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, aplicada nos quatro contêineres.
- Bancada C2 nova: rede interna `tcc2-pon-e11-c2-p20261115-232946`, `run_id=e11-c2-p20261115-232946`; source/logic/executor/client com IDs distintos, **0 restartCount** e topologias inicial e final idênticas; sem portas publicadas. Teto por contêiner de 0,5 CPU; 256 MiB de memória para cada serviço, 128 MiB para cliente. São limites NOMINAIS, não observações da CPU física.
- Fixture canônica 1.000: semente `20260502`, SHA-256 do arquivo canônico `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; oracle canônico `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`. Inputs rebased no ZIP diferem em bytes por possuírem novo `run_id`; não é corrupção.

## 2. Correção e conservação semântica

- `client.stdout.jsonl`: 1.000 registros `request` + 1 `summary`, **1.000/1.000 HTTP 200**, sem erros. Auditoria independente reconstruiu `changed`, `sequence`, `event_id`, `duplicate_request` e ordem dos 1.000 passos: **0 divergências**.
- 874 mudanças efetivas / 126 no-ops. Logs comparados sem recorrer apenas ao `validation.json`: **874 notificações de atributos enviadas e recebidas** com payloads iguais e mesma ordem, **500 notificações de condição enviadas e recebidas** com payloads iguais e mesma ordem.
- **250 efeitos** em `effects.jsonl` exatamente iguais aos 250 objetos do `expected.jsonl`, e também iguais aos eventos de efeito do executor. Passos 3, 7, 11, ..., 999.
- Estado frio anterior ao snapshot confirmado nos três papéis; os três prontos após snapshot com mesmo `run_id`. Estado final `atA=10`, `atB=0`; sequências `atA=374`, `atB=500`; 500 transições de condição, executor `approved=false`, 250 efeitos e nenhum `faulted`.
- `validation.json` confirma **10/10 checks gerais, 4/4 transporte**, status PASS. A reconstrução independente é compatível com todos os checks.

## 3. Tempo e respostas — SOMENTE UMA RODADA EXPLORATÓRIA

| Métrica | Resultado observado | Definição |
|---|---:|---|
| Tempo de lote | **20,210461674 s** | `perf_counter_ns` do cliente; exclui preparação e leitura final |
| Vazão | **49,4793 requisições/s** | 1.000/T do lote |
| RTT mediano HTTP | **19,1079 ms** | 1.000 respostas, serial |
| RTT médio HTTP | **20,1835 ms** | incluiu no-ops e mutações |
| RTT p95 (nearest-rank) | **50,7198 ms** | N=1.000 |
| RTT p99 (nearest-rank) | **98,7868 ms** | N=1.000 |
| RTT máximo | **163,2814 ms** | não atribuir causalidade individual |
| Coerência UTC vs duração monotônica | **diferença ~0,054 ms** | marcadores UTC aproximados |

**Não comparar diretamente a vazão com o piloto C2/100 ou C3/C4/100 para deduzir speedup:** número de requisições, custo fixo, coleta, potencial aquecimento, diferenças de rede e ordem experimental mudaram. Os resultados de 1.000 em C3/C4 AINDA NÃO existem.

## 4. Telemetria externa Docker Engine API / cgroup

- `engine-context.json`: Docker Engine API 1.56 via `npipe:////./pipe/dockerDesktopLinuxEngine`, sem processo `docker exec` usado para coleta dos serviços. Cliente de lote ainda é executado por `docker exec -i` dentro do contêiner cliente, não dentro dos papéis observados.
- `metrics-engine.jsonl`: **96 observações = 24 por papel**; 24 rodadas da sonda, antes e durante o lote e depois; `metrics-errors.json=[]`. O CSV deriva dos mesmos 96 registros e confere em identidade e CPU. Todas as fontes mostram 24 timestamps próprios distintos por papel, sem regressão de contador ou timestamp, nem borda de tempo ambígua.
- `metric_quality`: `cpu_counters_available=true`, `cpu_window_adequate=true`, `clock_coherent=true`, `issues=[]`. Fonte temporal com gaps máximos entre ~1,06 e ~1,16 s e margens nas fronteiras (abaixo de ~0,64 s); duração 20,210 s excedeu mínimo provisório 10 s.
- **Aprovação SCIENTÍFICA ainda é `measurement_approved=false`**; `memory_window_adequate=false`; `memory_comparable_to_kubelet=false`. Não converter adequação instrumental em autorização para publicar CPU/memória como custos por lote causalmente exatos.

| Papel | Delta de CPU por bracketing (CPU-s) | Máximo AMOSTRADO de memória bruta Docker (MiB) | Variação de períodos de throttling no bracket |
|---|---:|---:|---:|
| attribute-source | 9,846899 | 64,359 | +175 |
| logic-engine | 5,813650 | 61,887 | +7 |
| rule-executor | 0,309241 | 21,699 | +0 |
| cliente | 0,838785 | 20,066 | +1 |

**Ressalvas fundamentais:**
- Os intervalos de bracketing duram ~20,85–20,87 s, **mais que** os 20,210 s de lote; os CPU-s incluem tempo de borda e não identificam exatamente o custo das 1.000 requisições.
- CPU do `attribute-source` no bracket ≈0,472 core médio equivalente sobre a janela de ~20,875 s, perto do teto **nominal** de 0,5 CPU; o aumento do contador de `throttled_periods` em +175 dentro desse bracket indica incidência de limitação por quota na observação. Isso é **indício de pressão de CPU sob configuração adotada**, NÃO prova isolada de gargalo causal, nem motivo para alterar o limite após ver tempos.
- Uma rodada de leitura **sequencial dos 4 contêineres** levou mediana ~0,678 s e média ~0,685 s, com período-alvo de 1 s. Esse é tempo decorrido da consulta (não CPU próprio do monitor), mas pode representar efeito observador relevante na máquina que hospeda o Docker Desktop; exige calibração separada.
- O uso de memória é `memory_stats.usage` (bruto), **não** `workingSetBytes` do Kubernetes. Os máximos por papel ocorreram em instantes possivelmente diferentes, portanto **não somar como pico simultâneo**. Não existe memória de pico exclusivo da janela aprovada.
- O cenário C2, C3 e C4 usa **um mesmo host físico** (kind com nós virtuais); não afirmar escalabilidade horizontal entre máquinas ou overhead isolado de Kubernetes.

## 5. Decisões, pendências e próximos passos

1. **E11-P04 PASS funcional** e integridade do ZIP verificada. A **fonte CPU temporalmente adequada nesse lote**, com 24 timestamps por papel e nenhuma regressão.
2. **Não classificar medições secundárias como aprovadas**: coleta tem custo de observação e memória não é semanticamente equivalente à Summary API. Esses são impeditivos para conclusões comparativas diretas.
3. Preservar rede `tcc2-pon-e11-c2-p20261115-232946` e quatro contêineres e todos os namespaces C3/C4 históricos. **Não reenviar snapshot nem fixture**.
4. Próximo E11-D09: preparar somente PLAN_ONLY e pré-verificações C3/1000 e C4/1000 em namespaces NOVOS; calibrar cadência da Summary API e checar se haverá timestamps distintos suficientes. Pilotos após revisão, não permitir criação accidental em históricos.
5. Antes da série definitiva E11-M01, aprovar protocolo de aquecimento, limite de CPU (throttling C2 significativo), réplica = rodada, randomização de ordem, metadados de host e política explícita para medidas secundárias (possivelmente exploratórias apenas). E11-A01 auditar todos os ZIPs; Etapa 12 analisar, **não antecipar inferência estatística**.

**Integridade científica:** análise feita somente sobre os arquivos reais e logs reportados; nenhuma nova execução experimental, modificação de runtime, imagem, contêiner ou cluster por este registro. ZIP original permanece externo ao repositório.
