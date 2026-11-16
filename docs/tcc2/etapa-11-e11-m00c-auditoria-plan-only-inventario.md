# TCC2 — E11-M00C: auditoria dos três PLAN_ONLY e inventário preliminar do host

**Data documental:** 16/11/2026 (America/Sao_Paulo); **branch:** `tcc2/desenvolvimento`.  
**Origem:** transcrição PowerShell fornecida pelo acadêmico nesta conversa. A saída não inclui um ZIP de evidências ou log original com SHA-256 preservado.  
**Classificação:** `PLAN_ONLY_C2_C3_C4_PASS`, `CANONICAL_FIXTURE_PASS`, `ENVIRONMENT_INVENTORY_PARTIAL`, **`E11_M01_BLOCKED`**.

## 1. Evidência observada

A transcrição confirma `git pull --ff-only origin tcc2/desenvolvimento` com fast-forward `2d237ba...` -> **`707d456f83dadbcea088924ed60e33dc8f3720a6`**. Ela mostra em seguida:

- Docker context = `desktop-linux`.
- Docker daemon = **cgroup v2**, `NCPU=8`, `MemTotal=8245637120` bytes (**~7,68 GiB**, memória anunciada pelo daemon, não memória livre ou capacidade física total do computador).
- WSL status: distro padrão `docker-desktop`, versão padrão 2.
- kind: `tcc2-pon-control-plane` (control-plane, 172.18.0.2) e `tcc2-pon-worker` (172.18.0.3), ambos `Ready`, `v1.37.0`, Debian GNU/Linux 13 trixie, Linux `6.18.58.1-microsoft-standard-WSL2`, containerd 2.3.4; **ambos são nós virtuais no mesmo host físico**. Dados fornecidos são fotografia de inventário, não avaliação de carga.

A geração local da fixture de **1.000 entradas** reportou:
- `seed=20260502`, `run_id=e11-canonical-1000-20260502`.
- SHA-256 inputs: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`.
- SHA-256 oráculo: `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`.
- 1.000 requisições, 874 mudanças e 126 no-ops, 500 transições de condição, 250 efeitos; entidades atA=375 e atB=625, estado final atA=10/atB=0. **São dados de caracterização gerados, não execuções distribuídas.**

Os três comandos `python -m benchmark.docker_c2` (C2) e `python -m benchmark.runner --scenario C3/C4` (todos **sem `--execute`**) retornaram JSON com:
- `status=PLAN_ONLY`, `measurement_mode=timing_only`, `resource_sampling_during_batch=false`, `resource_metrics_comparable=false`, `execute=false`;
- o mesmo tamanho e os mesmos contadores funcionais esperados;
- C2: rede/contêineres propostos `tcc2-pon-e11-c2-m01-b01[-papel]`, `run_id=e11-c2-m01-b01`;
- C3: namespace proposto `tcc2-pon-e11-c3-m01-b01`, `run_id=e11-c3-m01-b01`;
- C4: namespace proposto `tcc2-pon-e11-c4-m01-b01`, `run_id=e11-c4-m01-b01`.

**O que NÃO foi verificado:** `PLAN_ONLY` valida argumentos, fixture, labels, IDs e saída de plano **local**, mas não consulta existência real de rede/namespace proposto, não verifica disponibilidade de image ID/identidades de contêineres/Pods, não prova aderência dos limites/cgroups no runtime e não reserva recursos. `kubectl get nodes` verifica readiness dos dois nós, não CPU/RAM livre disponível nem adequação de host. A saída final de `git status --porcelain` não está explícita na transcrição; não afirmar árvore limpa exclusivamente por ausência de mensagem. Nenhuma calibração de observador/custos foi feita.

## 2. Critérios de aceitação confrontados com E11-M00C candidato

| Gate do candidato | Evidência recebida | Decisão |
|---|---|---|
| SHA fixture e oráculo | Os dois SHA-256 coincidem | `PASS` |
| C2 PLAN_ONLY timing_only | JSON `PLAN_ONLY`, `execute=false` | `PASS` |
| C3 PLAN_ONLY timing_only | JSON `PLAN_ONLY`, `execute=false` | `PASS` |
| C4 PLAN_ONLY timing_only | JSON `PLAN_ONLY`, `execute=false` | `PASS` |
| Identidades inéditas previstas | Labels `m01-b01` válidas, nomes consistentes | `SINTAXE_PASS; EXISTENCIA_PENDENTE` |
| Docker/context/WSL2/kind | Contexto, cgroup, CPUs/memória total, nós e versões | `INVENTARIO_PARCIAL` |
| Requests/limits reais, cgroup quota/period e swap, pressão e disco | Não observados nesta transcrição | `PENDENTE` |
| Imagem digest e existência de namespace/rede real | Não observados nesta transcrição | `PENDENTE` |
| Preflight/GETs uniformes e logs arquivados | Propostos, sem execução no cluster real novo | `PENDENTE` |
| Políticas de falha, substituições/retensão | Propostas documentalmente | `ACEITE_E_CONGELAMENTO_PENDENTES` |
| Duração/custo CPU/RAM | Nenhum novo experimento | `NOT_MEASURED` |

## 3. Próximo gate seguro (somente leitura)

A próxima atividade deve consultar, sem `exec` nos serviços e sem alteração do cluster: imagem Docker `tcc2-pon:c2-e08-dbefcd2cf3d2` e seu ID, nomes das redes/contêineres existentes, namespaces existentes, `allocatable` dos dois nós, capacidade livre de disco e RAM total do host Windows. Registrar também se o contexto kind é o mesmo e se a árvore Git está limpa. **Não executar `docker run`, `kubectl apply`, POST/snapshot, scale, delete, restart ou operações em históricos.**

A matriz/ordem de dez blocos e o modo `timing_only` mantêm-se como definidos, porém o protocolo permanece `E11-M00-v1-CANDIDATE/BLOCKED_FOR_M01` até confirmação dos gates reais, política uniforme de GET, preservação de evidências e congelamento explícito. CPU e memória seguem fora das métricas comparativas v1.

**Integridade:** esta auditoria não executou comandos de infraestrutura. Nenhuma bancada histórica foi modificada, excluída, reiniciada ou reusada por esta atividade.
