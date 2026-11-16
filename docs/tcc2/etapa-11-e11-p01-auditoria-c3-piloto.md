# TCC2 — Etapa 11 | Auditoria independente do piloto C3 E11-P01

**Data da rodada:** 15/11/2026, aproximadamente 21:37 (America/Sao_Paulo), segundo os artefatos; UTC final do lote: 2026-11-16T00:37:56.309669+00:00.
**Natureza:** análise dos bytes do arquivo RAR bruto recebido nesta conversa, com extração e validação independente do ZIP interno `run.zip`. Os resultados são **de piloto instrumental**, NÃO compõem a série estatística V12.
**Branch/commit do código executado:** `tcc2/desenvolvimento`, `b8b8a354e3207cc6eb04d7c61eff3913a6dec7f2`.
**Scenario/namespace:** C3, `tcc2-pon-e11-c3-p20261115-213740`. **run_id:** `e11-c3-p20261115-213740`.

## 1. Proveniência e integridade

- Arquivo bruto enviado: `e11-p01-20261115-213740.rar`, **50.181 bytes**, SHA-256 calculado **`8b8549faac1bb486dfec626fc64566937923dcb015d45bdd6276551c49d364df`**.
- Contém 28 entradas: 24 arquivos e 4 diretórios. Todas as 24 entradas de arquivo foram extraídas por biblioteca de leitura RAR5 e tiveram CRC32 recalculado compatível com o registro do RAR; nenhuma divergência detectada.
- ZIP interno bruto `run.zip`: **24.842 bytes**, SHA-256 recalculado **`ffa845a8ba7d88ac4fa27fd057d7b03f3f07509c01203d5f6b99a3c80e2ae064`**, compatível com o valor mostrado no terminal Windows. O ZIP contém 19 arquivos, 19 nomes distintos e **zero erro CRC**; os outros **18 arquivos têm 18/18 hashes SHA-256 correspondentes** ao `checksums.sha256`. Os bytes das 19 entradas internas correspondem aos mesmos arquivos presentes separadamente no RAR.
- Hash da fixture canônica `fixtures/s100/inputs.jsonl`: **`e2ee29163bed0755dee2e44c3c17929b7bcb6039cbdf8c16d5907988d2489d14`**; do oráculo esperado canônico `expected.jsonl`: **`441849d87d3d2d6d56365fa1614dd89445530bd63cc9ec87eda1244e7a46cc3b`**. Correspondem aos valores do preparo E11-D03 e manifesto da rodada.
- O RAR original e o ZIP bruto **não** foram versionados como binários no GitHub. Preservar originais e cópias imutáveis externas.

## 2. Topologia, estado frio e correção funcional

- Nova bancada C3: três Deployments/Pods/Services da aplicação, todos no worker virtual `tcc2-pon-worker`, mais um Pod `e11-benchmark-client`. Versão da imagem C2 `tcc2-pon:c2-e08-dbefcd2cf3d2`; ID Docker declarado no manifesto `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Topologia inicial e final dos **três Pods da aplicação** mantêm UIDs, container IDs, nodes e restartCount=0. Ambos os nós virtuais permanecem no mesmo host físico WSL2, sem distribuição entre máquinas físicas.
- Estados antes do snapshot: `ready=false` e `run_id=null` em três serviços. Snapshot único: HTTP 200, `duplicate=false`, versão `<run_id>:snapshot:0`; estados após snapshot 3/3 `ready=true`.
- **100/100 POSTs HTTP 200**, IDs de requisição distintos, 86 alterações efetivas e 14 sem mudança. O `attribute-source` registra 100 mutations incrementais + 1 snapshot.
- **86/86 AttributeChanged** enviados/recebidos com objetos JSON iguais, na ordem correta; **49/49 ConditionChanged** enviados/recebidos, com correlação preservada; **25/25 efeitos** iguais ao oráculo e aos logs de execução. Passos dos efeitos: 3, 7, 11, 15 ... 99.
- Estado final `atA=5`, `atB=1`, sequências `atA=37`, `atB=49`, `condition_sequence=49`, condição/aprovação verdadeiras, sem falhas.
- O `validation.json` registra **10/10 checks gerais** e **4/4 checks de transporte** verdadeiros. Não confundir estes 14 checks com repetições independentes.
- Os arquivos `effects.jsonl` e `expected.jsonl` possuem **JSON semanticamente igual e mesma ordem**, mas não bytes idênticos (ordem das chaves difere). Aceitação correta é por objetos, incluindo multiplicidade, ordem e causalidade.
- Captura PowerShell adicional confirma Pods C3 funcional em `tcc2-pon` e C4 funcional em `tcc2-pon-c4` Running 1/1, restarts=0; não houve POST para namespaces antigos nesta rodada.

## 3. Tempo, latência e vazão OBSERVADOS APENAS NO PILOTO

| Indicador | Medida observada | Interpretação |
|---|---:|---|
| Duração do lote (relógio monotônico no cliente) | **2,243528105 s** | Não inclui implantação, snapshot, validação e ZIP |
| Vazão global | **44,57 requisições/s** | 100/duração; concorrência=1 |
| Vazão de mudanças efetivas | **38,33 mudanças/s** | 86/duração |
| Vazão de efeitos | **11,14 efeitos/s** | 25/duração |
| RTT mediano (todas as requisições) | **21,08 ms** | Cliente no worker, HTTP/1.0, não latência isolada PON |
| RTT p95 (nearest-rank, N=100) | **51,02 ms** | Apenas estatística descritiva deste lote |
| RTT máximo | **105,40 ms** | Sem inferência sobre variabilidade entre execuções |
| RTT mediano sem alteração (N=14) | **1,84 ms** | Caminho no-op |
| RTT mediano com alteração (N=86) | **21,85 ms** | Caminho com propagação, heterogêneo |

**Advertência:** trata-se de **uma rodada piloto**, excluída das estimativas científicas finais, não se calcula intervalo de confiança entre rodadas ou significância. O tempo inclui transporte HTTP cliente→source e comunicação síncrona entre três serviços; não separa custo intrínseco do NOP nem latência entre nós.

## 4. Métricas Kubelet Summary API: coletadas, mas calibração incompleta

- `metrics-errors.json` = lista vazia. `metrics-samples.jsonl` contém **16 observações**, 4 por cada um dos três contêineres da aplicação + 4 do Pod cliente. Quatro instantes UTC por papel (`00:37:53Z`, `:54Z`, `:55Z`, `:56Z`).
- `metric_quality.usable_cpu=true` no runner significa **presença de contador monotônico com timestamps distintos**; não significa que os pontos delimitam precisamente a janela de carga.

| Papel | Variação observada do contador CPU (primeira→última amostra) | Maior working set amostrado |
|---|---:|---:|
| attribute-source | 1,090192 CPU-s | 56,65 MiB |
| logic-engine | 0,668313 CPU-s | 47,86 MiB |
| rule-executor | 0,031209 CPU-s | 20,97 MiB |
| e11-benchmark-client | 0,405435 CPU-s | 17,86 MiB |

**Limitação crítica:** os 4 timestamps da Summary API abrangem aproximadamente 3 s, enquanto a janela cronometrada do lote tem 2,244 s e não há amostras com fronteiras exatamente coincidentes com seu início/fim. Diferenças de CPU incluem componentes temporais externos ao lote e não podem ser usadas como consumo exato da aplicação neste piloto. Working-set máximo AMOSTRADO não é pico exato de RSS ou uso físico total; não somar recursos dos nós kind como se fossem físicos independentes. A rede é medida por Pod, não por contêiner. O cliente de carga divide o worker e pode competir por recursos.
- Houve bytes de rede disponíveis no JSON da Summary API; ainda não são uma métrica causal isolada por serviço ou por ligação.

## 5. Classificação de aceitação

- **Piloto funcional C3/100: APROVADO no escopo ensaiado**, com transporte e oráculo íntegros.
- **Instrumentação de RTT/vazão: OPERACIONAL em uma rodada**, mas sem repetição, aquecimento padronizado e política estatística congelada.
- **Instrumentação de CPU e memória: disponibilidade comprovada e amostragem inicial operacional; ADEQUAÇÃO QUANTITATIVA AINDA PENDENTE.** Corrigir a interpretação permissiva de `usable_cpu` no validador, exigir janelas suficientemente longas, distinguir timestamps e registrar overhead da coleta.
- **V12 global: NÃO APROVADO, ainda em preparação.** Não interpretar 44,57 req/s como desempenho definitivo, speedup, escalabilidade ou vantagem de Kubernetes.
- **Preservação:** não repetir snapshot/fixture em `tcc2-pon-e11-c3-p20261115-213740`; manter C3/C4 históricos intocados. Qualquer nova rodada exige novo namespace e run_id.

## 6. Próximos incrementos recomendados

1. Reforçar o coletor/validador: distinguir `cpu_counter_present_monotonic` de `cpu_window_adequacy`, registrar primeira/última amostra e timestamps explícitos do cliente. Completar evidências de falha/timeout, sem modificar runtime PON.
2. Antes de pilotar C4, revisar os testes atualizados e dry-run em namespace C4 novo. Piloto C4/100 com **mesmo dataset canônico e mesma imagem**, excluído da análise estatística.
3. Planejar piloto de carga média (1000) em bancada nova para testar frescor dos contadores, memória sob carga e timeout, sem executar 10000 até analisar risco de OOM/retentativas.
4. Implementar C2 com gerador, limites e instrumentação equivalentes; fixar política de aquecimento, recursos, amostragem e repetição antes da série quantitativa V12.
5. Solicitar ao Perplexity pesquisa dirigida de fontes metodológicas reais sobre benchmarking de microsserviços, confiabilidade de amostras da Summary API, efeitos do gerador e comparações de ambientes; verificar cada DOI e texto original antes de citar na monografia.

**Entregável:** laudo documental. Os dados originais brutos permanecem externos ao GitHub, sem criação de resultados artificiais.
