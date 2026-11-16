# TCC2 — Etapa 11 / E11-P03: auditoria independente do piloto Docker C2

**Data da execução:** 15/11/2026, aproximadamente 22:53 (America/Sao_Paulo). **Amostra:** 100 requisições, concorrência 1. **Natureza:** piloto de integridade funcional e de instrumentação, NÃO parte da série estatística definitiva V12. **Fonte primária:** ZIP bruto `run(1).zip` recebido nesta conversa, aberto e analisado diretamente; transcrição Windows PowerShell.

## 1. Proveniência e integridade

- Git SHA efetivamente executado: `ad2092c085ec2379ba859b2007038a727664e9b5` em `tcc2/desenvolvimento`, conforme manifesto do ZIP e terminal. **E11-D06:** syntax compileall OK, 16/16 testes unitários OK (0,072 s de unittest, NÃO benchmark), Docker Engine 29.9.3.
- Bancada: rede interna `tcc2-pon-e11-c2-p20261115-225314`, run ID `e11-c2-p20261115-225314`; quatro contêineres novos, três serviços mais cliente. Imagem aprovada `tcc2-pon:c2-e08-dbefcd2cf3d2`, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a` em todos os papéis.
- `run.zip`: **27.261 bytes**, SHA-256 recalculado `8f5d3336f1fe7d3d7ce052cd0d93381d9b5bd6f0b3db0db2d664df5da2b32a01`, correspondente exatamente ao hash do PowerShell. **22 entradas únicas; CRC ZIP sem falhas; 21/21 hashes internos corretos** em `checksums.sha256`.
- Manifesto inclui SHA-256 da fixture canônica 100 `e2ee29163bed0755dee2e44c3c17929b7bcb6039cbdf8c16d5907988d2489d14`, mesma fixture-base dos pilotos C3/C4; inputs rebaseados têm `run_id` próprio e portanto bytes distintos. Arquivo binário original permanece externo ao GitHub.

## 2. Correção e causalidade observadas

- `client.stdout.jsonl`: **100 requests + 1 summary**, 100/100 respostas HTTP 200, 86 alterações verdadeiras, 14 no-op. Sem erro no cliente ou no transporte declarado.
- Cálculo independente das respostas sequenciais com a especificação dos atributos: **zero divergências** nos campos `changed`, `sequence`, `event_id`, `duplicate_request` e `step` em todas as requisições.
- Logs verificados separadamente: **86 AttributeChanged enviados = 86 recebidos** por lógica com payloads idênticos, ordenados; **49 ConditionChanged enviados = 49 recebidos** pelo executor, também ordenados; **25 efeitos produzidos** e logados na sequência dos passos 3,7,11,...,99. `effects.jsonl` e `expected.jsonl` têm 25 JSON objetos semanticamente idênticos, não bytes idênticos (ordem de chaves).
- Estado antes de snapshot: três serviços `ready=false`, `run_id=null`. Após snapshot, três prontos no mesmo run_id. Estado final: `atA=5`, `atB=1`, sequências `atA=37`, `atB=49`, condition_sequence=49, approved=true, 25 efeitos, nenhum fault.
- `validation.json` status PASS, **10/10 verificações gerais** e **4/4 verificações de transporte**, incluindo identidade estável dos contêineres. `topology-start.json` e `topology-end.json` são exatamente iguais, quatro IDs distintos, quatro restartCount=0.
- Topologia e recursos nominais reportados por contêiner: 500 millicpus (Docker NanoCpus=500000000), 256 MiB serviços / 128 MiB cliente, memory-swap combinado igual ao limite de memória. Rede Docker bridge interna, sem portas publicadas. São atributos do manifesto/inspeção, não prova de isolamento físico perfeito.

## 3. Latência e vazão OBSERVADAS EM UMA RODADA PILOTO

| Métrica | Observação C2 | Nota |
|---|---:|---|
| Duração perf_counter_ns | **2,867092063 s** | Apenas lote, não provisionamento ou coleta posterior |
| Vazão HTTP | **34,8785 requisições/s** | 100/duração |
| RTT mediano | **19,9902 ms** | HTTP/1.0; 1 cliente serial |
| RTT médio | **28,6432 ms** | Sensível a cauda |
| RTT p95 nearest-rank | **101,2198 ms** | N=100, indicativo |
| RTT máximo | **176,3203 ms** | Sem atribuição causal isolada |
| RTT mediano com alteração (N=86) | **20,9218 ms** | Caminho com propagação |
| RTT mediano sem alteração (N=14) | **1,2647 ms** | No-op |

**Alinhamento do cliente:** batch_started_utc=2026-11-16T01:53:30.000098+00:00, batch_finished_utc=2026-11-16T01:53:32.867644+00:00. Relógio monotônico `perf_counter_ns` determinou o tempo; datas UTC apenas referência temporal aproximada.

**Comparação meramente descritiva:** piloto C3 2,243528105 s / 44,57 req/s / mediana 21,08 ms / p95 ~51,02 ms; C4 2,095875392 s / 47,71 req/s / mediana 19,78 ms / p95 ~50,24 ms; C2 2,867092063 s / 34,88 req/s / mediana 19,99 ms / p95 101,22 ms. **Não concluir superioridade, overhead causal nem diferença estatisticamente identificada**: apenas uma rodada por configuração, sem blocos de ordem balanceados, e instrumentação distinta/intrusiva de C2.

## 4. Telemetria C2: disponibilidade comprovada, ADEQUAÇÃO REPROVADA

- `metrics-cgroup-intrusive.jsonl`: **16 amostras**, quatro para cada um dos três serviços e quatro para cliente. Erros de leitura reportados `[]`. A sequência das coletas é serial entre contêineres, por processos `docker exec` que também consomem recursos dos cgroups observados; as séries não representam instantes simultâneos. Abrangência global de marcas `capture_utc` de ~6,37 s, maior que o lote 2,867 s.
- `metric_quality.measurement_approved=false` no relatório, com justificativa explícita: **intrusão por `docker exec` e janelas temporais não calibradas**. Acesso a cgroup v2 por dentro dos próprios contêineres NÃO constitui ainda leitura limpa do custo da aplicação.
- Deltas cumulativos entre a **primeira e última amostra** (que NÃO delimitam exatamente o lote, e INCLUEM os processos de medição): attribute-source ~1,547108 CPU-s, logic-engine ~1,166852 CPU-s, rule-executor ~0,485845 CPU-s, cliente ~0,892765 CPU-s. **Não publicar essas diferenças como CPU do lote**.
- Os dados contêm `cpu_nr_throttled` já positivo antes da carga e crescente em amostras posteriores; não atribuir causalidade exclusiva das 100 operações. `memory_peak_lifetime_bytes` representa pico vitalício do cgroup, não pico somente da janela de 100 requisições; `memory.current` não é igual ao workingSetBytes da Summary API.
- As amostras expõem também efeitos de concorrência do amostrador e do cliente no mesmo Docker Desktop. Não somar picos de papéis observados em instantes diferentes como pico simultâneo do aplicativo.

## 5. Decisão e próximos passos

1. **E11-D06 PASS real (16 testes); E11-P03 C2 piloto funcional PASS auditado.** Integridade do ZIP confirmada, oráculo/causalidade e identidade dos quatro contêineres preservados.
2. **Instrumentação HTTP cliente de carga: operacional** nos três pilotos, mas insuficiente para declarar superioridade/overhead. **CPU/memória C2 NÃO ACEITAS para comparação** com Kubelet C3/C4. V12 continua NÃO EXECUTADA.
3. A bancada `tcc2-pon-e11-c2-p20261115-225314` está gasta para mutações; NÃO reenviar snapshot/fixture, NÃO reiniciar/remover recursos históricos. Preservar os arquivos e registro de evidências.
4. Priorizar E11-I05: monitor C2 **não intrusivo** acessando `/sys/fs/cgroup` por fonte externa ao contêiner observado (com prova de identificação de cgroup correto), ou medir overhead da coleta em experimento controlado; revisar limites/posicionamento do gerador e planejar janela maior.
5. E11-P04: piloto diagnóstico de 1000 requisições em bancada **completamente nova** só após aprovação E11-I05 e verificação de duração, memória, timeout e recursos; sem 10.000 nem repetição estatística definitiva antes de congelar metodologia. Métodos fundamentados em 4 artigos principais selecionados do dossiê Perplexity.

**Documento de auditoria:** criado com base no ZIP recebido e nas transcrições. O ZIP original não foi adicionado como binário ao GitHub.
