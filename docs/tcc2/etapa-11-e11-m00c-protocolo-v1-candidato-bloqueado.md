# TCC2 — E11-M00C — Protocolo quantitativo v1 (candidato, não congelado)

**Data:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Estado formal:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`. **NÃO é versão congelada nem autorização para E11-M01.**  
**Vinculações:** `etapa-05-protocolo-experimental.md`; `etapa-11-e11-m00-plano-fechamento-metodologico.md`; `etapa-11-e11-m00a-matriz-quantitativa.md`; `etapa-11-e11-m00b-controle-instrumental.md`; auditorias pilotos E11-P04/05/06 e regressão M00B de 48 testes.

## 1. Evidências confirmadas e limites

**Confirmado por transcrição PowerShell:** no SHA `2d237ba8f91cd5ba7d7f6c65a451d45bb7c1d21c`, `compileall` aprovado e `48/48 unittest` em 0,121 s, incluindo cinco casos `MeasurementProfileTests` e cinco `ResourceContractTests`. Isso demonstra correção sintática e comportamento unitário simulado do harness, **não** funcionamento de bancada experimental. A execução anterior no SHA `b20919f...` teve `IndentationError`, corrigido no commit `b74b66a...`; não ocultar esse histórico.

**Confirmado pelos laudos anteriores:** os pilotos C2/C3/C4 de 1.000 são PASS funcionais (uma rodada por cenário); CPU e memória não aprovadas para comparação científica. Não reaproveitar piloto nem ambiente histórico.

**Limitações intrínsecas:** PON PoC em Python com HTTP/JSON, não o NOP Query C++; C4 são nós kind virtuais no mesmo host físico. Não alegar medição de distribuição em dois computadores físicos, speedup obrigatório, escalabilidade horizontal ou efeito causal exclusivamente do Kubernetes.

## 2. Matriz principal e estimando — decisão proposta preservada de E11-M00A

- **Cenários:** C2 (Docker), C3 (Kubernetes com três serviços no worker virtual), C4 (logic-engine no control-plane virtual e outros serviços/cliente no worker).
- **Carga:** 1.000 POSTs seriais de `benchmark/fixtures.py` (seed `20260502`), canônico `inputs.jsonl` SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; oráculo 250 efeitos com SHA registrado na documentação M00A.
- **10 blocos pré-especificados de três cenários**, conforme tabela imutável em `etapa-11-e11-m00a-matriz-quantitativa.md`. Uma bancada inédita e fria por tentativa, um snapshot e uma carga por bancada; `run_id` único com label `m...`.
- **Primário:** `T_batch` medido pelo processo cliente `time.perf_counter_ns` da primeira iteração até saída do laço, incluindo preparo da solicitação e HTTP/1.0, excluindo `docker exec`/`kubectl exec` externo, snapshot e empacotamento. Sem sonda periódica de recursos nos três cenários: **`--measurement-mode timing_only` explícito**.
- **Secundários de tempo:** `1000/T_batch` req/s, mediana/p95/p99 RTT por lote, razões e diferenças assinadas C3-C2, C4-C3, C4-C2 por bloco. Relatar mediana/IQR/mínimo/máximo por cenário e por contraste, todas as tentativas e denominações válidas. Não tratar RTTs individuais como réplicas independentes.
- **CPU/RAM:** fora dos contrastes quantitativos principais enquanto semântica/cobertura/calibração não forem aprovadas. `NOT_COLLECTED` = não observado, **NÃO zero**; dados de Docker Engine e Kubelet Summary antigos continuam exploratórios e incomparáveis diretamente.
- Carga 100 = sanidade opcional, em bancada nova fora dos 30 lotes. Carga 10.000, F1/replay e escalonamento = fora desta versão; eventual aditamento **anterior** à nova aquisição, nunca inserção pós-hoc.

## 3. Estado inicial, aquecimento e observação não mutante

**Procedimento candidato único (congelar após revisar implementação):** antes da primeira mutação em bancada inédita, serviços/Pod cliente disponíveis, contêineres sem reinícios e imagem aprovada. Para os três papéis, uma verificação final por `GET /health/live` e `GET /state`, com registros de horários UTC e estado frio `ready=false`, `run_id=null`, contadores/efeitos zerados e ausência de mutações nos logs; como a prontidão inicial pode ter polling/probes próprios diferentes, registrar essas consultas extras. **Nenhuma carga `POST` de aquecimento na mesma bancada**.

Não chamar isso de aquecimento funcional: é verificação não mutante/estabilização de infraestrutura. Se necessário calibrar aquecimento real de aplicação, fazê-lo somente em bancada de sacrifício separada e nova, fora da matriz. **Implementação uniforme dos GETs finais e comprovação de estado frio ainda dependem de revisão do harness**, que no momento usa preflights C2 e Kubernetes com padrões ligeiramente diferentes.

Após snapshot único inicial, registrar estado inicial dos três serviços e ausência de efeitos; depois lançar lote uma só vez. Não reusar recursos após qualquer tentativa, mesmo que falhe antes de terminar ou que nunca tenha enviado mutações.

## 4. Controle de recursos e host

- Referência nominal já documentada: C2 `--cpus 0.5` e 256 MiB por serviço (128 MiB cliente), C3/C4 requests `100m/128Mi` por serviço e `100m/64Mi` cliente, limits `500m/256Mi` e `500m/128Mi` respectivamente. Não equiparar requests Kubernetes a quotas Docker; documentar a diferença. CPU quota 0,5 core em C2 versus limit 500m em kind é **igualdade nominal de teto**, não prova de equivalência do host/cgroup.
- Antes do primeiro bloco, inventariar read-only: CPU/RAM física, Windows/WSL2/Docker/kind, espaço em disco, contexto/versões, cgroup/version/quota/period/limites/swap aplicáveis, nós e recursos allocatable, imagem/digest e modo de energia. Repetir campos mutáveis por bloco, anotando pressão/concorrrência externa e possíveis serviços históricos ainda ativos; **não desligar histórico para "estabilizar"**.
- O throttle observado no source do piloto C2 (+175 períodos) é um fator interpretativo já existente; não mudar limites por causa da medição piloto. Se igualdade nominal, disponibilidade física ou estabilidade do host forem insuficientes, **parar antes da série** e registrar o motivo.
- Fixar limites antes dos dados, e preservar a configuração por toda a série; qualquer alteração controlada de variável exige nova versão de protocolo, não uma correção silenciosa.
- **Ações read-only e PLAN_ONLY não equivalem a prova de que recursos poderão ser criados nem que quotas efetivas são equivalentes.**

## 5. Timeouts, falhas e integridade — política de reposições proposta antes da série

**Proposta fixa:** timeout por POST de 10 s, timeout externo do lote de 600 s, concorrência=1. Uma falha de transporte, timeout ou confirmação de POST/snapshot incerta produz **STOP imediato**, sem retry automático; a bancada é preservada e não reutilizada. Guardas de estado, recurso, imagem, namespace/rede, label, versão, ausência de histórico e capacidade devem passar antes de qualquer mutação.

**Por tentativa, três etiquetas diferentes:**

- `FUNCTIONAL_PASS`: 1.000 HTTP 200 e payload canônico, 874 mudanças, 126 no-ops, 874 notificações de atributo, 500 notificações de condição e 250 efeitos iguais ao oráculo; contadores/ordem, estado, logs e integridade ZIP PASS; não houve restart/fault ou mudança de placement.
- `FUNCTIONAL_FAIL`: divergência do contrato, timeout, perda, duplicação, restart/fault ou estado de mutação incerto. Preservar tudo, suspender a campanha, investigar; não excluir silenciosamente falhas funcionais da conclusão de viabilidade.
- `TIMING_ELIGIBLE`: somente `FUNCTIONAL_PASS` com `T_batch > 0`, payload/ordem corretos e host dentro dos controles antes declarados; **tempo lento por si só NÃO causa exclusão**. Falha instrumental de recursos `NOT_COLLECTED` não é impedimento para `T_batch`.

**Reposição candidata:** alvo inicial de dez **blocos completos**. Em caso de interrupção operacional exógena documentada ou falha pré-lote sem mutações, manter o bloco original no relatório, paralisar e investigar; substituir somente por um **bloco completo novo** (C2/C3/C4 em bancadas inéditas), limitado a **2 blocos extras (máximo 6 tentativas adicionais)**, com ordens pré-fixadas B11 `C2,C4,C3` e B12 `C3,C2,C4`. **Não** substituir com base em `T_batch` lento/alto, nem usar essa regra para "corrigir" falha funcional sistemática. Se ocorrer segunda falha do mesmo tipo, mudança de ambiente não resolvida, necessidade de mais de dois blocos extras ou quebra de controles, **STOP e aditamento/revisão**. O teto e a definição de elegibilidade só terão efeito após aprovação/congelamento E11-M00-v1. É obrigatório publicar número de tentativas, blocos válidos/invalidos, motivos e resultados incompletos.

**Risco de viés:** substituir blocos após falha pode selecionar condições mais favoráveis; apresentar análise com todas tentativas e sensibilidade de contrastes; não anunciar potência estatística, significância confirmatória ou resultados causais isolados.

## 6. Plano seguro de execução e arquivamento (não executar nesta fase)

- Identidades futuras: `e11-c2-m01-b01`, `e11-c3-m01-b01`, `e11-c4-m01-b01` com `label=m01-b01` são **exemplos**. `timing_only` restringe sintaxe `m...`, mas ainda exige verificação real de inexistência do namespace e preservação histórica; prefixos não garantem exclusividade por si só.
- Para cada tentativa: diretório de saída **inexistente**, outputs e ZIP sem sobrescrita, `manifest.json`, `environment.json` (ainda precisa ser produzido/arquivado na futura série), recursos/topologia, identidades, seed/hash fixture/rebased, snapshots/estados, logs por serviço, HTTP JSONL, effects, `batch-summary.json`, `metrics-status.json`, `validation.json`, checksums SHA-256 e ZIP externo. Capturar metadados antes/durante/depois por interface read-only fora da janela `T_batch`.
- Primeiro validar `PLAN_ONLY` para C2/C3/C4 com fixture correta e flags exatas, **sem `--execute`**. Confirmar ausência de targets históricos e de alterações do código da aplicação. Nunca aplicar manifesto no namespace histórico e nunca executar limpeza genérica (`docker rm`, `docker network rm`, `kubectl delete`, `kind delete`, `git reset --hard`).
- Preparar cópia íntegra dos arquivos brutos com SHA e inventário das bancadas novas antes de qualquer política de limpeza futura. **Política de limpeza ainda não aprovada**; por padrão, preservar todas as bancadas da série até auditoria E11-A01 e autorização explícita de uma allowlist concreta. Historicamente existentes permanecem permanentemente protegidas neste escopo.

## 7. Checkpoint de congelamento — critérios objetivos

| Gate | Situação agora | Para liberar |
|---|---|---|
| Matriz, 1.000, n=10, ordem/estimando | `DECIDED_DOCUMENTED` em M00A | Reconfirmar hashes e escopo |
| Compilação e regressão estática | `PASS` em SHA `2d237ba8...` por transcrição (48/48) | Regressão novamente se harness sofrer alterações |
| Modo `timing_only` | `STATIC_TESTS_PASS` | `PLAN_ONLY` C2/C3/C4 real, sem `--execute` |
| Recursos | Requests/limits declarados e mock-test PASS | Inventário real read-only de host/WSL/Docker/kind; verificação de topologia e quotas/limites |
| Aquecimento/preflight final uniforme | `PROPOSED` | Revisão/homogeneização documental ou code/test antes de M01 |
| Política de falhas/reposições | `PROPOSED` neste documento | Aceite explícito + congelamento prospectivo |
| Evidência/backup/metadados | `PROPOSED` | Preparar/check de `environment.json`, cópia/sha e exclusividade de IDs |
| CPU/RAM comparativas | `NOT_APPROVED` | Manter fora do escopo v1 ou instrumentar nova fase calibrada |
| Revisão do orientador | `NOT DOCUMENTED` | Registrar consulta/decisão se exigida pelo fluxo acadêmico |

**Decisão E11-M00C neste checkpoint:** `BLOCKED_FOR_M01`. O candidato pode orientar as verificações seguintes **somente leitura e geração de PLAN_ONLY**, mas **não** congela E11-M00-v1 nem libera nenhum `--execute`. Publicar protocolo imutável e `READY_FOR_M01` só após gates remanescentes efetivamente comprovados.

## 8. Próxima verificação mínima autorizada

No PowerShell do clone já em `prova-conceito`, após conferir working tree/branch e o SHA da revisão:

```powershell
git branch --show-current
git status --porcelain
git rev-parse HEAD

# Saidas apenas de consultas ao ambiente, sem mutacoes:
docker context show
docker info --format 'CgroupVersion={{.CgroupVersion}} NCPU={{.NCPU}} MemTotal={{.MemTotal}}'
wsl --status
kubectl --context kind-tcc2-pon get nodes -o wide
```

Se qualquer comando falhar, guardar a mensagem exata; **não corrigir automaticamente por restart, apply, load, criação ou exclusão**. Fixture/PLAN_ONLY C2/C3/C4 poderão ser preparados sem acesso aos cenários antigos, como passo separado.

**Não foram executados novos benchmarks, snapshots, POSTs, `kubectl apply`, ações Docker/cluster mutantes ou exclusões neste registro.**

## 9. Atualização da matriz de gates: PLAN_ONLY e inventário recebidos

**Fonte:** `etapa-11-e11-m00c-auditoria-plan-only-inventario.md`, versão textual de PowerShell fornecida pelo acadêmico após `git pull --ff-only` para `707d456f83dadbcea088924ed60e33dc8f3720a6`.

**Gates agora comprovados por transcrição:** SHA-256 da fixture e do oráculo, três `PLAN_ONLY` C2/C3/C4 com `timing_only` e `execute=false`, labels válidas `m01-b01`, Docker `desktop-linux` com cgroup v2, CPU 8, RAM anunciada 8245637120 bytes, WSL2, dois nós kind `Ready` e Kubernetes v1.37.0. Esses dados são **preflight planejado e inventário**, não experimentação ou validação de quotas físicas.

**Gates que permanecem pendentes antes de congelar:** (i) consulta read-only de namespace/rede já existentes e confirmação de inexistência para IDs novos; (ii) image ID do runtime, recursos `allocatable` por nó, disponibilidade efetiva do host/disco, quotas e swap; (iii) critério final de GETs/estabilização comum aos cenários, `environment.json` e política de preservação; (iv) aceitação formal prospectiva das regras de falha/reposição; (v) protocolo versionado `E11-M00-v1` com SHA dos scripts e status deliberado. **O método `--execute` continua BLOQUEADO.**

**Decisão mantida:** `BLOCKED_FOR_M01`. Não confundir três `PLAN_ONLY` PASS com três novos experimentos.
