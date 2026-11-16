# TCC2 — Etapa 11 / E11-P02 — Auditoria de piloto C4 multinó virtual

**Data local do piloto:** 15/11/2026, aproximadamente 22:00 (America/Sao_Paulo). **Fonte primária:** ZIP bruto run.zip enviado na conversa, verificado diretamente em ambiente de análise, além da transcrição PowerShell. **Classificação:** PILOTO FUNCIONAL APROVADO; métricas de CPU/memória ainda não aprovadas; V12 permanece pendente.

## 1. Ambiente e proveniência
- Commit executado: affa6dfc1185c24b554235944c05fb9aeeb08ee3 na branch tcc2/desenvolvimento. E11-D05: nove testes unitários relatados como OK (0,078s de suíte, NÃO benchmark), sintaxe sem erro.
- Namespace exclusivo: tcc2-pon-e11-c4-p20261115-220023. Run ID: e11-c4-p20261115-220023. Imagem tcc2-pon:c2-e08-dbefcd2cf3d2, ID esperado sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a.
- Localização: attribute-source, rule-executor e cliente de carga em tcc2-pon-worker; logic-engine em tcc2-pon-control-plane. São dois nós virtuais kind no mesmo host físico WSL2. Não foi testado cluster com computadores físicos independentes.
- Topologia de Pods de aplicação antes/depois: UID, containerID, IP e nó consistentes; restartCount=0. Três Services ClusterIP. Client Pod consta na topologia inicial, mas não na chave client_pod do JSON final (registrada null pelo runner), sem afetar a comprovação de estabilidade dos três Pods de aplicação.
- Saída PowerShell mostra C3 histórico tcc2-pon e C4 histórico tcc2-pon-c4 ainda Running, 1/1, zero reinícios. Não foi reenviado snapshot ou carga a esses namespaces.

## 2. Integridade do ZIP fornecido
- run.zip: **27.839 bytes**, SHA-256 calculado diretamente: **d99e8b9c258ca7a0415dc2ca88d43119c47c5d4774945aacf4f011ae710a389d**; idêntico ao SHA-256 da saída PowerShell.
- 22 entradas únicas e nenhuma falha na verificação CRC; checksums.sha256 contém 21 hashes SHA-256, **21/21 verificados** sobre os demais arquivos do ZIP.
- Hash da fixture canônica declarado no manifesto: e2ee29163bed0755dee2e44c3c17929b7bcb6039cbdf8c16d5907988d2489d14, mesmo hash da fixture de carga 100 da preparação. Inputs rebaseados por run_id têm hash próprio e distinto (normal).
- O conteúdo JSON dos 25 efeitos esperados e produzidos é semanticamente igual e está na mesma ordem; os bytes do JSONL não são iguais por ordem de chaves distinta.

## 3. Correção funcional verificada independentemente
- 100/100 respostas HTTP 200, nenhuma resposta divergente dos campos changed, sequence, event_id, duplicate_request e step. 86 alterações efetivas e 14 no-op.
- Oráculo independente reexecutado sobre inputs.jsonl: **25 efeitos idênticos** a expected.jsonl e effects.jsonl, nos passos 3,7,11,...,99.
- Mudanças com notificação de atributos: **86 envios = 86 recebimentos**, payloads idênticos em ordem. Condição: **49 envios = 49 recebimentos**, payloads idênticos em ordem.
- Snapshot único: HTTP 200, duplicate=false e snapshot_version do run_id. Estados frios ready=false, run_id=null; estados após snapshot prontos; estados finais atA=5, atB=1, sequências atA=37/atB=49; condition_sequence=49, approved=true, sem falhas/pending.
- validation.json PASS: **10/10 verificações gerais e 4/4 de transporte**, sem confundir checks com repetições experimentais.

## 4. Descrições de latência e vazão do PILOTO (não estatística definitiva)

| Indicador | Observado no C4 piloto |
|---|---:|
| Tempo de lote perf_counter_ns | **2,095875392 s** |
| Vazão de requisições | **47,71 req/s** |
| Vazão de alterações efetivas | **41,03 mudanças/s** |
| Vazão de efeitos | **11,93 efeitos/s** |
| Mediana RTT HTTP, N=100 | **19,78455 ms** |
| Percentil 95 RTT, nearest rank | **50,2415 ms** |
| Máximo RTT HTTP | **78,4466 ms** |
| Mediana RTT com mudança, N=86 | **20,4607 ms** |
| Mediana RTT sem mudança, N=14 | **1,2930 ms** |

- batch-summary.json registra batch_started_utc=2026-11-16T01:00:37.012977+00:00 e batch_finished_utc=2026-11-16T01:00:39.108872+00:00; relógio monotônico do MESMO cliente gerou a duração do lote. UTC é apenas marca de alinhamento aproximado.
- **NÃO concluir que C4 superou C3**: há apenas um piloto por cenário, sem repetição estatística, bloqueio de ordem ou controle suficiente de ruído/condições. Números piloto devem permanecer fora de V12 e da inferência final.

## 5. CPU e memória: limitação instrumental
- metrics-samples.jsonl possui **20 amostras = 5 por contêiner (três serviços + cliente)**. metrics-errors.json=[] (nenhum erro de coleta declarado).
- metric_quality.cpu_window_adequate=false, memory_window_adequate=false, usable_cpu=false e usable_memory=false. A duração 2,096 s não alcança mínimo candidato 10 s.
- No attribute-source há duas observações com timestamp cpu_time_utc 01:00:36Z e contador usageCoreNanoSeconds distinto. O validador marca cpu_counter_present_monotonic=false por ambiguidade de registros no mesmo segundo. Não é evidência de regressão real no contador; a precisão de timestamp não distingue tais coletas.
- Nos outros dois serviços cpu_counter_present_monotonic=true, mas ainda sem janela suficiente. Os valores de working set são máximos AMOSTRADOS, não pico preciso de RAM; sem afirmação de consumo CPU por lote.
- O coletor deve distinguir repetição de timestamp com contador crescente (granularidade) de regressão real em timestamps sucessivos e tornar o resultado explícito. Testar em nova bancada. Não reprocessar dados antigos como se fossem precisos.

## 6. Decisões e próximos passos
1. E11-P02 aprovado funcionalmente, integridade ZIP aprovada, métricas de RTT/vazão operacionalmente disponíveis em uma única rodada exploratória.
2. CPU/memória ainda não aprovadas como métrica quantitativa; V12 NÃO executado/encerrado. Nenhum resultado do piloto é estimativa estatística definitiva.
3. Não repetir snapshot ou POST sobre tcc2-pon-e11-c4-p20261115-220023, nem sobre namespaces C3/C4 históricos.
4. Próximo incremento: ajustar tratamento de timestamp duplicado no coletor, reforçar delimitação e duração das janelas e planejar piloto médio de 1000 requisições em namespace NOVO. Priorizar equivalência instrumental C2 antes da série estatística.
5. Pesquisa metodológica Perplexity deve trazer fontes reais verificáveis e exportação em Markdown/BibTeX para revisão e futura redação LaTeX da monografia UTFPR.

**Evidência bruta:** ZIP recebido em conversa (não commitado como binário); hashes documentados neste laudo. Dados narrados no PowerShell não substituem o ZIP.
