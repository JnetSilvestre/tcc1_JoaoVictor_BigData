# TCC2 — Etapa 11 / E11-M00 — Plano de fechamento metodológico

**Data de abertura:** 16/11/2026 (America/Sao_Paulo).  
**Branch:** `tcc2/desenvolvimento`. **Base verificada:** `27132a9bd155a9b5639c5a2cdb1502692a5282f9`.  
**Estado deste documento:** **PROPOSTA PARA FECHAMENTO, NÃO PROTOCOLO CONGELADO**. Não autoriza E11-M01 nem qualquer POST, snapshot, benchmark, apply ou exclusão.

## 1. Evidências e precedência

Fontes consultadas: `STATUS_ATUAL_TCC2.md` (registros finais 15–16/11/2026), `docs/tcc2/etapa-05-protocolo-experimental.md`, `docs/tcc2/etapa-11-diagnostico-plano.md` e laudos `etapa-11-e11-p04-auditoria-c2-1000.md`, `etapa-11-e11-p05-auditoria-c3-1000.md`, `etapa-11-e11-p06-auditoria-c4-1000.md`.

- E11-P04, P05 e P06: C2/C3/C4 **PASS funcional** cada um com 1.000 HTTP 200, 874 mudanças, 126 no-ops, 874 notificações de atributos, 500 notificações de condição e 250 efeitos iguais ao oráculo. Integridade dos ZIPs auditada.
- Existe **apenas uma rodada exploratória por cenário**. Tempos e vazões dos pilotos não permitem inferência estatística.
- CPU/memória dos três pilotos **NÃO foram aprovadas para contraste quantitativo**: C2 tem bracketing provisório, mas sondagem com potencial efeito observador e throttling; C3/C4 têm timestamps de origem Kubelet insuficientes e ausência de bracketing final; `memory_stats.usage` (Docker) não equivale a `workingSetBytes` (Kubelet).
- A prova de conceito é Python/HTTP/JSON síncrona e serial, **não** a aplicação NOP Query C++ integral. Dois nós kind compartilham um único computador físico. O objetivo principal aprovado é viabilidade técnica da distribuição, **não** ganho obrigatório de desempenho.
- Todas as redes/contêineres/namespaces usados anteriormente, incluindo os três pilotos de 1.000, são **históricos, gastos e intocáveis para novas mutações ou exclusões**. Proibido reenviar snapshot, POST, benchmark, reiniciar, reescalar ou aplicar manifestos neles.

## 2. Organização enxuta de E11-M00 — proposta

**E11-M00A — matriz e estimando (decisão documental):** fechar comparação principal, unidade experimental, ordem, repetições, carga, semântica do cliente e condições de host. Não executar experimentos.

**E11-M00B — instrumentação e segurança (preparação controlada):** conferir por inspeção de código os guardas; definir separação entre cronometração primária e sondagens secundárias; se indispensável, preparar apenas mudanças no harness/infraestrutura nova e testes sintéticos, nunca no núcleo aprovado nem nas bancadas históricas. Qualquer calibração real posterior exige autorização específica e bancada descartável inédita.

**E11-M00C — revisão e congelamento (documental):** registrar critérios de aceitação, falhas e documentação; atribuir versão imutável ao protocolo e hashes de scripts/fixtures, validar reprodutibilidade planejada e declarar explicitamente `READY_FOR_M01` ou `BLOCKED`. Sem execução quantitativa nesta abertura.

## 3. Matriz experimental candidata

Comparação principal: **C2 Docker vs C3 Kubernetes com três serviços no worker virtual vs C4 Kubernetes com logic-engine no control-plane virtual e os demais papéis no worker**. Em todos, um serviço/réplica por papel, cliente persistente, concorrência = 1, mesma imagem e sequência; C0/C1 são referências funcionais, não fatores da comparação principal.

| Fator | Proposta | Situação |
|---|---|---|
| Carga principal | **1.000 requisições**, fixture canônica seed `20260502`, SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551` | Herda fixture já auditada; conferir hash novamente antes da série |
| Repetições | **10 rodadas independentes por cenário**, cada rodada em bancada nova, fria, `run_id` próprio; **30 rodadas completas previstas** | Proposta herdada da Etapa 05; não é garantia de poder estatístico |
| Carga 100 | Sanidade/preflight e inspeção de segurança, **não entra** no n=10 nem na inferência principal | Proposta de delimitação |
| Carga 10.000 | **Fora da série inicial**; decidir por aditamento prévio, após capacidade/CPU/quota/timeout e sem extrapolação linear garantida | Condicional, não autorizada |
| Limites | Manter como referência **0,5 CPU / 256 MiB por serviço**, cliente 128 MiB, somente se equivalência efetiva C2/C3/C4 for verificada; registrar requests/limits e quota cgroup separadamente | Configuração observada no piloto, decisão quantitativa ainda sujeita a gate |
| Estado | Uma única sequência snapshot em estado comprovadamente frio; sem mutação de aquecimento da carga na mesma bancada | Regra de segurança já estabelecida |

Comparar cenários significa comparar **pilhas de execução e posicionamentos observados** sob esta configuração. Não atribuir diferenças exclusivamente ao Kubernetes, à distância física entre nós, ao PON isoladamente ou a speedup por paralelismo.

### Ordem proposta dos dez blocos

Cada bloco contém **uma rodada de cada cenário**, em bancadas novas, com a ordem fixada antes de E11-M01. Distribuição aproximada das posições (3/3/4 por cenário) para reduzir tendência temporal; nenhum ajuste de ordem por resultado.

| Bloco | 1ª | 2ª | 3ª |
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

## 4. Definições de medidas e hipótese

**Desfecho quantitativo primário proposto:** `T_batch` (s), obtido no mesmo cliente persistente com relógio monotônico `perf_counter_ns`, imediatamente antes do primeiro POST até a resposta do último POST. Exclui preparação, snapshot, oráculo, leitura final e ZIP. O tempo de iniciar `docker exec` / `kubectl exec` fica fora da janela interna do cliente.

Desfechos derivados por rodada: vazão `1000/T_batch` em requisições/s; latências RTT (ms) com mediana, p95 e p99 nearest-rank; taxas distintas de requisições, alterações efetivas e efeitos sempre com denominadores explícitos. O ACK síncrono não prova latência de propagação entre máquinas físicas; não subtrair clocks entre Pods/nós.

**Unidade amostral:** a execução independente completa em bancada nova (n=10 por cenário), **não** cada um dos 1.000 RTTs como réplica independente. Reportar por cenário mediana, IQR, amplitude, dispersão e diferenças por bloco; IC bootstrap por bloco apenas se a adequação amostral for defendida, sem reivindicar potência estatística ou causalidade isolada. Registrar todos os blocos, inclusive falhas e valores extremos.

## 5. Aquecimento, host e intervenção do monitor

- **Aquecimento não mutante por bancada:** confirmar prontidão/rotas com GETs de health e state, antes do snapshot, registrando quantidade/horário e provando que `ready=false`, contadores/ledgers/efeitos continuam intocados. Isto é **pré-aquecimento de infraestrutura**, não aquecimento da cadeia com carga POST; o desfecho mede uma carga a partir de estado de aplicação inicial fixo.
- **Aquecimento de carga verdadeiro**, se necessário, só em **bancada descartável nova, separada e não contabilizada**, previamente especificada. Nunca aproveitar a bancada que receberá a medição nem reutilizar redes/Pods históricos.
- Em cada bloco anotar SO, versões, contexto Docker/kind, imagem/digest, cgroup/quotas, CPU e RAM disponíveis do host, modo de energia, processos concorrentes relevantes, uso de disco, horários UTC e colocação dos Pods. Evitar tarefas pesadas concorrentes. Toda mudança de contexto requer registro; bloquear se recursos/topologia divergirem dos limites congelados.
- **Proposta prioritária para cronometração comparativa:** não usar consultas periódicas de CPU/memória dentro da janela cronometrada, em nenhum dos três cenários, até caracterizar e controlar o efeito observador. O `benchmark.runner` Kubernetes atual aciona `Sampler` durante o lote e **não apresenta flag de desativação**; preparar/validar alteração restrita ao harness antes de E11-M01, sem mudar comportamento dos serviços.
- **CPU/memória secundárias:** jamais misturar Docker `memory_stats.usage` com Kubelet `workingSetBytes`. Só autorizar comparação com fonte/semântica comum, correspondência inequívoca Pod/container/cgroup, resolução e atualização suficientemente densas, janela delimitada (inclusive amostra originada depois do fim), monitor calibrado e efeito observador documentado. Critérios provisórios já usados pela auditoria Kubelet: ≥5 timestamps distintos por serviço, gaps ≤4 s, bracketing efetivo; não afrouxar retroativamente.
- Se uma fonte comum não for validada, **CPU/RAM ficam exclusivamente como observações exploratórias e limitação**, não como resultados quantitativos comparativos. Throttling sob quota fixa deve ser registrado quando observável, não omitido nem utilizado para alterar o limite depois de ver resultados.

## 6. Gate por rodada e exclusões pré-especificadas

**Antes de qualquer mutação:** branch e Git limpos, scripts e imagem aprovados, fixtures/hash/seed e run_id exclusivos, namespace/rede **inéditos**, recursos e placement corretos, identidades históricas preservadas, serviços Ready e estados `ready=false`/sem eventos, preflight PLAN_ONLY. Falha: STOP, sem retry de evento incerto.

**Durante/após execução:** um único snapshot inicial e um único lote; exatamente 1.000 HTTP 200/respostas canônicas, 874 mudanças e 126 no-ops, 874 notificações de atributos e 500 de condição com ordem/payload conservados, 250 efeitos iguais ao oráculo, topologia estável, 0 reinícios/faults, `check_run` e transporte PASS, clocks monotônicos coerentes, logs e ZIP íntegros com CRC/SHA-256. Qualquer discordância suspende a aprovação funcional; conservar tentativa como falha.

**Validade quantitativa:** cronometração primária só inclui lotes completos, sem timeout/erro funcional/restart nem perturbação de ambiente previamente definida como impeditiva. Falhas e timeouts **não são apagados nem convertidos em sucesso**; relatar denominadores de tentativas e falhas. Não excluir outlier apenas por ser lento. Repetição substitutiva, se previamente permitida no congelamento, deve usar outra bancada nova e manter a tentativa original registrada, com motivo explícito e teto de substituições definido **antes** da campanha.

**Após conclusão:** arquivar `manifest.json`, `environment.json`, topologias/IDs, estados frio/pós-snapshot/final, inputs/oráculo, JSONL de HTTP/logs/efeitos, validação, saídas do monitor (ou null/unavailable explicito), checksums e ZIP externo; nenhum arquivo bruto é sobrescrito. Só descartar **bancadas novas da campanha** mediante política futura de allowlist e depois de integridade/arquivamento, nunca históricas.

## 7. Gates para declarar E11-M00 fechado

1. Matriz, n=10, bloco/ordem, fixture, parâmetros de carga e estimando aceitos no registro (incluindo resolução sobre carga 10.000).
2. Guardas do preflight e modo **sem sonda de recursos na janela primária** preparados/avaliados por inspeção e testes sintéticos; nenhum experimento real necessário para este registro inicial.
3. Confirmar quotas/limites efetivos iguais ou documentar ajustes **antes** da primeira série; calibrar/descartar análise CPU/RAM como comparativa sem flexibilizar a qualidade de dados.
4. Formalizar aquecimento, interrupções e teto de substituições, esquema de identificadores, rotina de backup, hashes e análise por bloco. Discutir orientações relevantes com o orientador antes de atribuir aprovação acadêmica.
5. Publicar protocolo versão `E11-M00-v1` com estado explícito `READY_FOR_M01` após os gates; se faltarem, registrar `BLOCKED`. **Este arquivo ainda não é esse congelamento.**

**Próxima ação autorizada por este documento:** somente revisão documental/inspeção do harness e discussão das decisões. **Nenhuma bancada histórica será tocada e nenhum experimento novo foi executado na abertura de E11-M00.**
