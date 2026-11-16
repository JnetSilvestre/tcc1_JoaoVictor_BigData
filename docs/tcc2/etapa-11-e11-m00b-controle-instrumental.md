# TCC2 — E11-M00B: controle instrumental, recursos e guardas da série

**Data:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Status:** **IMPLEMENTAÇÃO PREPARADA, NÃO VALIDADA NA MÁQUINA DO ACADÊMICO**.  
**Proibido até E11-M00C:** executar `--execute`, benchmarks, POSTs, snapshots ou criar/remover/reiniciar recursos nas bancadas históricas. A etapa E11-M01 continua bloqueada.

## 1. Fontes e motivação factual

Fontes: `STATUS_ATUAL_TCC2.md`, `docs/tcc2/etapa-05-protocolo-experimental.md`, `docs/tcc2/etapa-11-e11-m00a-matriz-quantitativa.md`, laudos E11-P04/P05/P06, `benchmark/docker_c2.py`, `benchmark/runner.py`, `benchmark/client.py`, `benchmark/docker_engine_window.py`, `benchmark/collector.py`, `benchmark/prepare.py`, `c3/runner.py` e manifestos C3/C4.

Auditorias dos pilotos: todos funcionais com 1.000 requisições e 250 efeitos, uma rodada por cenário; **CPU e RAM não aprovadas cientificamente**. Em C2, 24 rodadas do monitor consumiram em média ~0,685 s de tempo decorrido para consultar sequencialmente quatro papéis, com +175 períodos de throttling da fonte no bracket. Em C3/C4, as consultas Kubelet retornaram timestamps repetidos e não delimitaram o fim da carga. `memory_stats.usage` Docker não tem mesma semântica que `workingSetBytes` Kubelet.

## 2. Duas modalidades explícitas de coleta — código preparado

Os executores `benchmark/docker_c2.py` (C2) e `benchmark/runner.py` (C3/C4) agora aceitam:

- `--measurement-mode timing_only`: **não cria, não inicia nem encerra monitor periódico** de recursos na janela do lote. As medições de CPU/RAM são explicitamente marcadas `NOT_COLLECTED` em `validation.json > validation > metric_quality` e não há criação de arquivos CSV/JSONL de amostras com zeros fictícios. `metrics-status.json` registra o modo. O tempo do cliente (`perf_counter_ns`) e as validações funcionais permanecem os mesmos.
- `--measurement-mode resources_diagnostic`: preserva o funcionamento de sondagem dos pilotos anteriores; **não atribui aprovação quantitativa automática** à CPU/RAM. Continua como padrão por compatibilidade com os scripts antigos, mas **M01 exigirá a opção explícita `timing_only`**, sujeita ao congelamento de M00C.

A biblioteca pura `benchmark/measurement_profile.py` fornece escolha `select_sampler`, metadados e tratamento fail-closed de modo inválido. Os testes `tests/test_benchmark_measurement_profile.py` foram preparados, mas **NÃO executados no Windows nem considerados aprovados**.

Nota: o modo sem sonda elimina **o polling periódico instrumentado pelo próprio harness**, não elimina outras atividades do host/WSL/Docker/kind. `docker exec`/`kubectl exec` ainda inicia o cliente, mas o tempo externo desses comandos não está no `T_batch` interno.

## 3. Segregação de IDs e proteção da história

A execução futura em `timing_only` exige identificadores **novos com prefixo `m`** para o label; o `run_id` deve corresponder exatamente a `e11-{cenario_minúsculo}-{label}`. Exemplos apenas documentais, NÃO executados:

- C2: `--label m01-b01 --run-id e11-c2-m01-b01`
- C3: `--label m01-b01 --run-id e11-c3-m01-b01`
- C4: `--label m01-b01 --run-id e11-c4-m01-b01`

Os pilotos receberam identificadores `p...`. C2 mantém o guard que recusa rede/nomes Docker existentes; C3/C4 preservam a exigência de estado frio `ready=false`, `run_id=null` e ausência de mutações antes de snapshot. **Identificador com prefixo m não substitui preflight completo**, nem prova inexistência prévia do namespace. Em qualquer conflito, falhar sem novas mutações. Manter históricos intactos, sem qualquer limpeza genérica.

## 4. Recursos: limites declarados e comparabilidade ainda condicionada

| Papel | C2 Docker | C3/C4 kind |
|---|---|---|
| Três serviços | `--cpus 0.5`, `--memory 268435456`, `--memory-swap 268435456` | request `100m/128Mi`, limit `500m/256Mi` por Pod |
| Cliente | `--cpus 0.5`, `--memory 134217728`, `--memory-swap 134217728` | request `100m/64Mi`, limit `500m/128Mi` |
| Réplicas | 1 por papel | 1 por papel |
| Rede | bridge interna Docker | Service ClusterIP e rede kind |
| Local | mesmo host físico | dois nós kind virtuais no mesmo host físico |

`benchmark/docker_c2.py` já verificava os limites Docker pelo `docker inspect`. Agora, `benchmark/resource_contract.py` prepara checagem **estática e fail-closed** de requests/limits declarados dos três Pods, templates dos três Deployments e Pod cliente. A função `verify_kube_resources` foi integrada ao preflight Kubernetes; um `resource-contract.json` deve registrar o resultado após uma execução futura. Cinco testes sintéticos foram preparados em `tests/test_benchmark_resource_contract.py` (não executados).

**Não declarar equivalência física apenas por limites nominais.** Em E11-M00C ou preflight não mutante futuro, verificar se CPU quota/period, memory limit, cgroups, swap/WSL2, scheduler, pressão física e regras de throttling são suficientemente controlados. O `attribute-source` C2 mostrou incidência de throttling e isso integra a interpretação; não elevar quotas retroativamente em resposta ao desempenho dos pilotos.

## 5. Aquecimento e condições de host — política candidata para congelamento

1. Estado experimental = **aplicação fria por rodada**, mas serviços já Running/Ready, com rotas GET e logs lidos somente para preflight. Sem POST de aquecimento na mesma bancada, pois consumir a sequência/estado alteraria o estimando. GET não é prova de aquecimento equivalente da cadeia.
2. Não inferir que C2 (múltiplas verificações readiness) e C3/C4 (probes Kubernetes) têm exatamente o mesmo histórico de cache e GET. E11-M00C deve fixar um ciclo final idêntico de verificações não mutantes e registrar número, timestamps e ausência de mudanças.
3. No host Windows, registrar CPU/RAM física disponível, modo de energia, temperatura/throttling se houver instrumento, Docker Desktop/WSL2/kind, processos concorrentes relevantes, uptime, capacidade do disco, versões e horário por bloco. Minimizar interferências sem interromper bancadas históricas. Os estados históricos em execução podem usar CPU/RAM: registrar, não desligar.
4. Fixar timeout por requisição/lote e intervalo entre blocos prospectivamente; referenciais atuais do runner: 10 s por HTTP e 600 s por lote. Não inferir tempo de 10.000 a partir de 1.000.
5. O modo `timing_only` produz evidências primárias temporais; **não** autoriza comparar CPU/RAM. Uma pesquisa secundária de cgroup/CRI, se possível, terá protocolo/ambientes novos próprios e calibração separada; nunca intercalar sondagem diferenciada entre os cenários principais.

## 6. Gates de qualidade e validação pendentes

**A fazer em Windows sem mutações de infraestrutura** (na pasta `prova-conceito`, após atualizar o repositório e conferir branch limpa):

```powershell
git branch --show-current
git status --porcelain
git rev-parse HEAD
python -m compileall -q benchmark tests
if ($LASTEXITCODE -ne 0) { throw "compileall reprovado" }
python -m unittest discover -s tests -p "test_benchmark*.py" -v
if ($LASTEXITCODE -ne 0) { throw "unittest reprovado" }
git status --porcelain
```

**Orientação:** `git pull --ff-only` pode ser executado, se necessário, no clone correto **antes** do preflight; nenhum dos comandos acima chama `--execute` ou qualquer POST. Registar stdout/stderr e SHA-256 de capturas/artefatos. O resultado da suíte é **desconhecido nesta data**: não chamar de PASS até receber evidência.

Após a regressão sintética, realizar uma revisão de `PLAN_ONLY` com `--measurement-mode timing_only` e fixture canônica, **sem `--execute`**, em caminhos de saída inexistentes. Verificar a seleção e proteção de IDs; o output de PLAN_ONLY não valida Docker/Kubelet em execução, quotas físicas nem integridade de benchmark.

**Não executar uma calibração real, nem séries E11-M01, enquanto E11-M00C não aprovar formalmente os gates**. Se a verificação falhar, corrigir apenas o harness/testes e versionar a justificativa, sem tocar imagens ou runtime dos três serviços.

## 7. Estado e decisão

- **E11-M00A:** matriz/estimandos documentalmente definidos.
- **E11-M00B:** `PREPARED_NOT_EXECUTED` — opções e guardas versionados; validação sintética no Windows, qualidade dos preflights e equivalência operacional pendentes.
- **CPU/RAM científica:** `BLOCKED`; quando não coletadas, `NOT_COLLECTED` em vez de 0.
- **E11-M00C:** próxima fase — política final de aquecimento, substituições, níveis de qualidade, metadados e congelamento v1.
- **E11-M01/V12:** não iniciados; não autorizados por este documento.

**Integridade e escopo:** modificados somente scripts `benchmark/`, testes e esta documentação. Não houve novo snapshot, benchmark, POST, docker run, kubectl apply, remoção de serviços, ou acesso mutante a bancada antiga. Não afirmar testes executados.
