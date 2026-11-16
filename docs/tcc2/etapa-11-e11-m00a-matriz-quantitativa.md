# TCC2 — E11-M00A — Matriz quantitativa e plano de análise por blocos

**Data de registro:** 16/11/2026 (America/Sao_Paulo).  
**Ramo:** `tcc2/desenvolvimento`. **Base documental:** `STATUS_ATUAL_TCC2.md`, `etapa-05-protocolo-experimental.md`, `etapa-11-diagnostico-plano.md`, `etapa-11-e11-m00-plano-fechamento-metodologico.md` e auditorias E11-P04, E11-P05 e E11-P06.

**Estado:** **E11-M00A DEFINIDO DOCUMENTALMENTE**; as decisões sobre a matriz e estimandos abaixo orientam a preparação de E11-M00B. **E11-M00 global NÃO CONGELADO**, **E11-M01 NÃO AUTORIZADO**; sem execução experimental, mudança do runtime ou ação em bancadas históricas. Orientador ainda não indicado como aprovador deste desenho.

## 1. Escopo científico preservado

Avalia-se uma prova Python baseada nos mecanismos de notificações do PON, formada pelos serviços `attribute-source`, `logic-engine` e `rule-executor` por HTTP/JSON síncrono e serial. Isso NÃO equivale ao NOP Query C++ completo. O estudo principal é a viabilidade técnica de implantação, comunicação, isolamento e distribuição; o contraste temporal quantitativo é complementar e **não exige melhoria de desempenho**.

- C2: os três serviços em contêineres Docker independentes numa rede interna.
- C3: Kubernetes kind; três serviços no **worker virtual**.
- C4: Kubernetes kind; `logic-engine` no **control-plane virtual**, `attribute-source`, `rule-executor` e cliente no worker virtual.
- Os dois nós kind residem no **mesmo host físico**. A diferença C3/C4 compreende o posicionamento entre nós virtuais, mas não mede o ganho de hardware distribuído nem identifica isoladamente um overhead causal do Kubernetes. C0/C1 permanecem referências semânticas, não entram nos 30 ensaios quantitativos principais. C5 é variação de carga, não nova arquitetura; F1/V10 continuam separados.

Os pilotos E11-P04/05/06 foram auditados apenas como **uma execução por cenário**, com 1.000 HTTP 200, 874 mudanças, 126 no-ops, 500 transições e 250 efeitos por lote; NÃO integrar seus tempos ao conjunto inferencial. CPU e memória dos pilotos **NÃO APROVADAS como comparativas**.

## 2. Matriz, carga e unidade de repetição

| Item | Decisão E11-M00A |
|---|---|
| Cenários principais | C2, C3, C4 (uma réplica por papel) |
| Carga principal | `N=1000` POSTs seriais `/attributes/change`, concorrência=1 |
| Fixture canônica | `seed=20260502`; `run_id=e11-canonical-1000-20260502`; SHA-256 de `inputs.jsonl`: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551` |
| Oráculo | `expected.jsonl` SHA-256 `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`; efeitos esperados: 250 |
| Repetições planejadas | 10 bancadas/rodadas **novas e frias** por cenário; 30 tentativas principais planejadas, antes de eventuais falhas |
| Blocos | 10 blocos temporais, cada um contendo C2, C3 e C4 exatamente uma vez |
| Estado | `run_id` exclusivo, snapshots únicos por bancada fria, sem retry de evento incerto; não reutilizar estado |
| Cliente | **um processo Python** por lote, protocolo HTTP/1.0, sem garantia de conexão TCP keep-alive |
| Carga de 100 | Sanidade / calibração somente em bancada inédita, não considerada réplica de n=10 |
| Carga de 10.000 | Fora da campanha inicial; exige aditamento prospectivo após verificação de capacidade, risco de quota/OOM, tempo de execução e armazenamento |
| Recursos | Referência inicial: 0,5 CPU e 256 MiB por serviço, cliente 128 MiB. **Equivalência real de limites/quota e requests C2/C3/C4 ainda é gate de E11-M00B**, não assumida aprovada |

A fixture é gerada por `benchmark/fixtures.py` com ciclo de oito solicitações e semente fixa. A versão `rebased` altera identificadores da execução, sem alterar a sequência semântica; registrar seu hash específico. A descrição acima usa hashes obtidos dos laudos existentes e requer reconfirmação no preflight de cada rodada futura, **não foi executada nova geração neste registro**.

**Unidade experimental pretendida:** rodada completa em nova instância fria. Isso evita pseudorrepetição dos RTTs individuais, embora todas as rodadas compartilhem host e possam sofrer autocorrelação temporal. Portanto, não declarar independência estatística perfeita ou inferência a hardware físico diferente.

## 3. Ordem pré-especificada e contrabalanceamento

**Ordem operacional determinada antes das séries**, sem seleção em função do tempo observado:

| Bloco | Primeiro | Segundo | Terceiro |
|---|---|---|---|
| 01 | C2 | C3 | C4 |
| 02 | C3 | C4 | C2 |
| 03 | C4 | C2 | C3 |
| 04 | C4 | C3 | C2 |
| 05 | C3 | C2 | C4 |
| 06 | C2 | C4 | C3 |
| 07 | C2 | C3 | C4 |
| 08 | C3 | C4 | C2 |
| 09 | C4 | C2 | C3 |
| 10 | C4 | C3 | C2 |

Frequência das posições (inspeção combinatória da matriz, **não resultado experimental**):

| Cenário | Primeiro | Segundo | Terceiro | Total |
|---|---:|---:|---:|---:|
| C2 | 3 | 3 | 4 | 10 |
| C3 | 3 | 4 | 3 | 10 |
| C4 | 4 | 3 | 3 | 10 |

Cada cenário ocupa cada posição 3 ou 4 vezes (máxima aproximação possível ao equilíbrio em 10 blocos). Nos seis primeiros blocos ocorrem as seis permutações. A sequência é **determinística e aproximadamente balanceada**, NÃO randomizada. Registrar hora de início/fim, uso compartilhado do host e qualquer interrupção, sem trocar ordem depois de ver resultados. Um bloco planejado corresponde a três tentativas; qualquer desvio deve permanecer auditável.

**Disciplina de infraestrutura futura:** bancadas da campanha serão sempre inéditas; a política de remoção de *apenas* recursos temporários criados nessa campanha, após evidências arquivadas, será definida em E11-M00B/C. Redes, contêineres, Pods e namespaces históricos de C2/C3/C4 e anteriores jamais serão modificados, reiniciados, usados novamente ou excluídos.

## 4. Desfechos e definição operacional fiel ao código

**Primário: duração do lote `T_batch` (segundos) por rodada completa.** No `benchmark/client.py` inspecionado, o cliente registra `begin = time.perf_counter_ns()` **antes do laço** de 1.000 iterações e `elapsed` ao sair dele, no `finally`. Assim, o valor inclui preparação individual do JSON/corpo HTTP, laço Python, envios e recebimentos e suas operações locais, mas exclui criação da bancada, preparação do snapshot, execução externa `kubectl exec`/`docker exec` em si, impressões finais em stdout, auditoria e ZIP. O cliente executa em processo único; o servidor é HTTP/1.0 e o cliente não garante reutilização TCP.

**Secundários derivados da mesma rodada:** (i) vazão `1000/T_batch` (requisições por segundo), (ii) RTT por POST em ms, mediana, p95/p99 nearest-rank e amplitude, (iii) quando útil, `874/T_batch` como taxa de mudanças efetivas e `250/T_batch` como efeitos confirmados por segundo, com denominador explícito. HTTP 200 não substitui auditoria semântica; o cliente mede o ACK síncrono da implementação, não latência causal de comunicação de múltiplos computadores físicos.

**CPU e memória:** NÃO integram os desfechos comparativos desta definição. Exigem uma fonte equivalente entre C2/C3/C4, precisão temporal, bracketing do lote, calibragem do efeito do observador e correção da diferença `memory_stats.usage` vs `workingSetBytes`. Até comprovação, serão exploratórias/restritas ou indisponíveis, **jamais assumidas como zero**.

## 5. Contrastes e tratamento estatístico planejado

Contrastes principais definidos **sem direção esperada**: (C3 − C2), (C4 − C3) e (C4 − C2), sempre usando a duração `T_batch` em segundos. Para cada bloco completo calcular:

- diferença assinada `D_BA = T_B - T_A` (s);
- razão `R_BA = T_B/T_A`, quando `T_A > 0`;
- diferença relativa `100*(R_BA-1)` (%; valor positivo indica B mais lento que A).

Relatar por cenário, sobre as **10 rodadas completas previstas**, mediana, quartis/IQR, mínimo/máximo, valores individuais e ordem dos blocos. Para contrastes, relatar as dez diferenças e razões por bloco e respectivas estatísticas descritivas. Gráficos e consolidação só serão construídos na Etapa 12 com dados auditados. Bootstrap de blocos pode ser explorado conforme adequação efetiva, mas **não há justificativa atual para poder estatístico, significância confirmatória ou equivalência**. Os 1.000 RTT de cada lote são medições internas correlacionadas, não n=1.000 réplicas independentes.

Se ocorrer falha em uma tentativa ou bloco, preservar todos os registros, identificar n válido por cenário, justificar qualquer análise parcial e evitar viés por escolher apenas rodadas rápidas. **Não substituir automaticamente** a execução nem modificar limites em função do resultado. Política de reposições e interrupções será fixada em E11-M00C *antes* de executar E11-M01.

## 6. Critérios de qualidade a completar em M00B/C

**Qualidade funcional por rodada:** 1.000 respostas HTTP 200/canônicas, 874 mudanças e 126 no-ops, 874 notificações de atributos e 500 de condição com ordem/payload coerentes, 250 efeitos corretos, igualdade ao oráculo, sem perda/duplicação, sem fault/restart, preflight frio antes de snapshot, somente um snapshot/lote, IDs e topologia estáveis, dados brutos íntegros e checks de transporte/validação PASS.

**Controle do host:** antes de cada bloco registrar configuração Docker/WSL2/kind, versão/commit/imagem, limits e quota realmente observáveis, energia, pressão do host, horários e presença de serviços históricos que consomem recursos. Não confundir múltiplos nós virtuais kind com hosts físicos independentes.

**Aquecimento:** GETs não mutantes são apenas preparação de infraestrutura e **não aquecem a cadeia por carga POST**. Se um aquecimento real da cadeia for necessário, deverá ocorrer apenas em bancada descartável inédita distinta das rodadas medidas; regra uniforme e documentada no M00B antes de executar.

**Instrumentação:** avaliar o modo de cronometração primária **sem sampler periódico de CPU/RAM durante o lote**, dado o efeito observador ainda não quantificado e o refresh irregular do Kubelet, em implementação de harness validada por testes sintéticos. Não modificar runtime dos três serviços aprovados. Calibração de instrumento em infraestrutura nova somente depois de protocolo e autorização separados.

**Preflight e falhas:** recusar identidades históricas/duplicadas, reuso de rede/namespace, estado não frio, recurso/imagem divergente ou Git sujo; modo PLAN_ONLY anterior à mutação, sem retry automático de snapshot/POST incerto. Tentativas incompletas arquivadas e rotuladas separadamente.

## 7. Decisão de encerramento da fase A

- **E11-M00A:** `DECIDED_DOCUMENTED` — matriz e estimandos fixados para a preparação seguinte.
- **E11-M00B:** `PENDING` — avaliar harness, controle de instrumentos/quotas/host, aquecimento e segurança de novas bancadas.
- **E11-M00C:** `PENDING` — fechar exclusões/retentativas, decisões finais, protocolo imutável e eventual validação do orientador.
- **E11-M01:** `NOT_AUTHORIZED` — nenhum benchmark ou nova rodada deve iniciar a partir deste registro.

**Integridade:** este é um documento de planejamento; nenhum teste, snapshot, execução Docker/Kubernetes, modificação de imagens ou exclusão foi feito.
