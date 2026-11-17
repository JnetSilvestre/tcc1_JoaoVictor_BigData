# TCC2 — E11-M00-v1 — Pré-registro metodológico e bloqueios operacionais

**Data:** 17/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Situação formal:** **`DESIGN_FROZEN / IMPLEMENTATION_UNVALIDATED / M01_BLOCKED`**.

Esta versão fixa **prospectivamente** as decisões do desenho experimental e os limites operacionais, para evitar mudanças oportunistas após observar tempos de execução. **Não** equivale a aprovação do orientador, aprovação de implementação nova, comprovação de capacidade física ou autorização para iniciar E11-M01. Os critérios foram estabelecidos antes dos 30 lotes definitivos; os pilotos anteriores não compõem a amostra.

**Base aprovada/inspecionada:** `docs/tcc2/etapa-05-protocolo-experimental.md`, `docs/tcc2/etapa-11-e11-m00a-matriz-quantitativa.md`, `docs/tcc2/etapa-11-e11-m00b-controle-instrumental.md`, `docs/tcc2/etapa-11-e11-m00c-protocolo-v1-candidato-bloqueado.md` e laudos E11-P04/P05/P06/M00C. Evidência de testes disponíveis até agora: **65 testes PASS** e inventários read-only 3/3 no commit `f8b12606616fd6e13249a730a0ef8dbad4508d80`. Alterações de harness realizadas DEPOIS desse commit **não foram validadas no Windows**.

## 1. Cenários, fenômeno medido e limite científico

- C2: três serviços Python em contêineres Docker isolados, comunicação síncrona HTTP/JSON; cliente separado.
- C3: mesmos três papéis em Kubernetes kind no nó worker virtual.
- C4: logic-engine no control-plane virtual, source/executor e cliente no worker virtual.
- Dois nós kind no **mesmo host físico**. Comparações caracterizam este ambiente virtual específico; não há prova de escalabilidade em múltiplos servidores reais nem de overhead atribuível exclusivamente ao Kubernetes. A aplicação é a PoC Python dos mecanismos de notificação, **não** o NOP Query C++ completo.

## 2. Matriz quantitativa pré-fixada

Uma sequência de 1.000 requisições HTTP POST seriais por rodada, concorrência=1; seed canônica `20260502`, entrada SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, oráculo SHA-256 `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c` (250 efeitos).

**10 blocos completos, 30 rodadas principais, uma bancada inédita/friamente inicializada e um único snapshot/lote por tentativa:**

| Bloco | 1º | 2º | 3º |
|---|---|---|---|
| B01 | C2 | C3 | C4 |
| B02 | C3 | C4 | C2 |
| B03 | C4 | C2 | C3 |
| B04 | C4 | C3 | C2 |
| B05 | C3 | C2 | C4 |
| B06 | C2 | C4 | C3 |
| B07 | C2 | C3 | C4 |
| B08 | C3 | C4 | C2 |
| B09 | C4 | C2 | C3 |
| B10 | C4 | C3 | C2 |

A ordem é fixa e aproximadamente contrabalanceada, **não randomizada**. Cada tentativa tem `run_id=e11-cX-m01-bNN` e label `m01-bNN`; a ordem decide qual cenário vem a seguir e os IDs devem ser sempre checados contra recursos realmente existentes. Não reutilizar IDs, redes, namespaces, Pods, contêineres ou snapshots após uma tentativa concluída/incerta.

**Primário** = `T_batch` (s) pelo `time.perf_counter_ns` do cliente entre início e fim do lote, incluindo laço Python, preparo de JSON e trocas HTTP/1.0, excluindo criação, snapshot, `docker exec`/`kubectl exec` externo e compactação. **Secundários** = throughput `1000/T_batch`, RTT mediana/p95/p99 por rodada, contrastes por bloco em tempo C3-C2, C4-C3 e C4-C2 e razões relativas. Unidade estatística é **uma rodada**, não 1.000 RTTs independentes. Relatar todos os 10 valores por cenário, mediana, IQR, mínimo/máximo, diferenças e dispersão; sem teste de hipótese confirmatório ou alegação de equivalência baseada apenas em n=10.

Somente `--measurement-mode timing_only` poderá ser usado nos lotes principais. Não coletar CPU/RAM periodicamente no lote. CPU/RAM comparativas seguem **`NOT_APPROVED`**; suas ausências devem ser `NOT_COLLECTED`, não zero. Carga 100 é apenas sanidade de bancada sacrificial, 10.000 e experimentos F1/V10 exigem aditamento antes de execução.

## 3. Estado inicial e gates obrigatórios PRE-snapshot

Antes de enviar o primeiro `/init/snapshot` de **qualquer bancada inédita**:

1. `PLAN_ONLY`, hash fixture/oráculo, nome de recurso/namespace, Git branch limpa e revisão/imagem aprovada, topologia e ausência de recursos históricos como destino; o plano não é prova de inexistência real — reconsultar imediatamente antes de criar.
2. Verificar **exclusividade M01** por `docker ps` e `kubectl get namespaces`: **no máximo uma bancada NOVA ativa**. C2 não pode coexistir com outro C2 ativo nem com namespace M01 C3/C4; C3/C4 só permitem o namespace atual; histórico p... e namespaces antigos são intocáveis.
3. Registrar `environment.json` sem modificar recursos: Git SHA, Windows/WSL2/Docker, cgroup v2, CPUs/RAM do daemon, RAM Windows física livre, disco livre do projeto, imagem SHA aprovada, nós kind/UID/allocatable para C3/C4. Não somar allocatable de nós kind como capacidade física independente.
4. **Margem operacional deliberadamente conservadora (não validada por artigo nem derivada estatisticamente): pelo menos 3,00 GiB de RAM física Windows livre e 15,00 GiB no volume do projeto**. Se abaixo, `STOP` sem snapshot/POST, registrar dados reais e reprogramar sem mudar a cota com base nos tempos observados. `2.159.898.624` bytes de RAM livres foram reportados no inventário de 17/11 (~2,01 GiB), **abaixo** deste limiar; a próxima tentativa encontra-se `BLOCKED_BY_CAPACITY` caso a leitura se repita. O limite não garante que host não sofrerá OOM.
5. Limites declarados e **cgroups V2 efetivos** dos quatro papéis novos: CPU `500m` por contêiner (relação `cpu.max` quota/period=0,5), memória `256 MiB` para cada serviço, `128 MiB` cliente e **`memory.swap.max=0`**. Verificar `memory.current` dentro do teto e ausência de `oom`/`oom_kill` preexistentes; registrar `memory.events`. `kubectl exec`/`docker exec` empregam `python -c` somente para leitura de cgroup no novo recurso, **sem chamadas à aplicação**. Divergência/ausência provoca STOP; não alterar limites para obter PASS.
6. Executar a última rodada uniforme de leituras sem mutações por papel: `GET /health/live`, `GET /state`, leitura de logs; `AttributeSource` fria tem zero/zero, `LogicEngine` ainda sem atributos/condição (`null`) e `RuleExecutor.approved=null`. Ledger vazio, sem faults/mutações. Registrar `preflight-uniform.json`. GET não é aquecimento funcional com POST, e a história de polling Kubernetes/Docker não é idêntica.
7. Persistir `campaign-exclusivity.json`, `capacity-gate.json` e `effective-quotas.json`, bem como `environment.json`, antes do snapshot. A aprovação de quotas é **por contêiner novo criado**, não substitui as quotas físicas do host nem permite comparações científicas de consumo.

**Política de instrumentos:** a leitura de cgroup V2 acontece **antes do lote**; sem sampler durante `T_batch`. O preflight C2 verifica RAM antes de criar a rede, C3/C4 após a criação dos Pods e antes de snapshot. Uma perda posterior de margem é risco residual a ser reportado, não prova de equivalência.

## 4. Segurança, falhas e reposições — regra prospectiva

- **Qualidade funcional obrigatória por rodada:** 1.000 HTTP 200, 874 mudanças e 126 no-ops, 874 notificações de atributo, 500 de condição e 250 efeitos, oráculo, sequência/causalidade, estado, nenhum restart/fault, identidade/placement/limites estáveis e `ZIP` com CRC/SHA íntegros.
- Timeouts nominalmente fixos: **10 s por solicitação e 600 s pelo lote**. Em POST/snapshot de confirmação incerta, **NUNCA retry**; preservar a bancada/bytes/logs/erro, interromper e investigar.
- Registrar tentativas `FUNCTIONAL_PASS`, `FUNCTIONAL_FAIL`, `PRECHECK_BLOCKED` e `TIMING_ELIGIBLE`, publicando todos os resultados e motivos de exclusão; tempo alto **não** justifica descarte. O status `NOT_COLLECTED` de CPU/RAM não desqualifica duração temporal.
- Meta 10 blocos completos. Apenas após falha operacional exógena comprovada e autorização documentada, admite-se até **2 blocos substitutivos completos** (máximo 6 rodadas extras), com novas identidades; ordens B11 `C2,C4,C3` e B12 `C3,C2,C4`. Falha funcional sistemática ou apenas maior duração não gera substituição automática. Arquivar cada tentativa frustrada, sem apagar seu resultado.
- Congelar host, imagens e limites; se mudanças de configuração se tornarem inevitáveis, **aditamento versionado ANTES de novas medidas** e análise estratificada; nunca mesclar valores de ambientes diferentes sem ressalvas. Não comparar CPU/RAM dos pilotos à duração futura.

## 5. Política de arquivo e ciclo de vida

- Após qualquer tentativa, gravar a evidência completa e o ZIP fora do contêiner/namespace, com `manifest.json`, `validation.json`, `inputs.jsonl`, `expected.jsonl`, `states-cold.json`, `preflight-uniform.json`, `environment.json`, `campaign-exclusivity.json`, `capacity-gate.json`, `effective-quotas.json`, estado de snapshot/lote/final, logs, `checksums.sha256` e ZIP SHA-256.
- O `benchmark/lifecycle_audit.py` verifica CRC e SHA-256 de cada membro, identidade do `run_id`, cenário, funcionalidade PASS e os três gates adicionais. **Não** decide sozinho se uma bancada pode ser removida.
- Preservar **permanentemente neste escopo** todas as bancadas históricas (incluindo `p...`, `tcc2-pon`, `tcc2-pon-c4`, `tcc2-v03/v05/v06`, `tcc2-c2`), imagens e volumes antigos. **Proibidos** `docker system prune`, `kubectl delete`, `docker rm` genéricos e reinicialização de histórico.
- **Não existe implementação nem autorização de cleanup.** `retirement_review_only()` só devolve `commands=[]`, `delete_authorized=false`. Retirada futura só de recursos NOVOS M01 exigirá: (a) ZIP íntegro + cópia independente validada; (b) lista positiva com ID imutável do contêiner/rede ou UID de namespace; (c) prova de origem/ownership da rodada; (d) comparação explícita contra lista negativa histórica; (e) aceite específico do operador; (f) testes da rotina em ambiente sacrificial novo. Sem todos, **STOP por capacidade** em vez de acumular 30 bancadas.
- Tentativas `FAIL` e parciais são arquivadas e mantidas, mesmo que `audit_archive()` não autorize aposentadoria. Não escolher apenas dados rápidos/funcionais por conveniência. Planejar capacidade de disco pelo conjunto de ZIPs e backup, sem usar `RECLAIMABLE` do Docker como autorização de apagar artefatos existentes.

## 6. Base do código e condição para liberar o E11-M01

**Revisão de implementação do pacote após 65 testes anteriores:** commit `592da6314d629ae833c53f5b39df97bd8e446580` precede a redação deste pré-registro; integrações adicionais ocorreram no mesmo ramo e devem ser identificadas por seus SHA de conteúdo após a publicação do protocolo.

Blobs de referência inspecionados:
- `benchmark/docker_c2.py`: `725072b7d60a8067a40bf47908aca6267d89bc29`;
- `benchmark/runner.py`: `2dca160f1a3d4a8337067f31bb85e0943562b542`;
- `benchmark/runtime_gate.py`: `f75ff260554c3b79d956f43be943a33a34ce489d`;
- `benchmark/campaign_exclusivity.py`: `d0d5fd8b5fb7036b615b36c940adc84bb4ece826`;
- `benchmark/lifecycle_audit.py`: `a0d6014cb9b019a44bcf032b68d30fefc7bba7f7`.

**Observe:** os blobs listados foram inspecionados no pacote de implementação em formação, não são garantia de que o commit final do ramo tenha esses mesmos SHAs após toda revisão. **Sempre registrar HEAD exato testado, e não interpretar apenas o SHA deste documento como resultado de teste.**

**Gates pendentes antes de `READY_FOR_M01`:**
1. `compileall` e suíte `test_benchmark*.py` da revisão **atual do harness**, com resultados e SHA reais do Windows; os 65 PASS anteriores não cobrem os novos módulos/gates.
2. Confirmação read-only da semântica do `cpu.max`, `memory.max`, `memory.swap.max` em recursos **novos não históricos**, antes de qualquer snapshot/POST; mock de cgroup não aprova quotas reais.
3. Comprovar margem física de RAM/disco, exclusividade e identidade; última RAM reportada ~2,01 GiB implicaria STOP pelo piso escolhido de 3 GiB.
4. Planejar/validar procedimento de isolamento e encerramento de recursos M01 **somente novos**, com UID/ID/allowlist, backup, autorização explícita, e critérios de STOP; enquanto pendente, não iniciar série de 30.
5. Registro da revisão acadêmica/orientador quando exigida; nenhuma aprovação externa está implícita neste documento.

**Decisão:** o **DESENHO** experimental de E11-M00-v1 está pré-registrado para impedir alterações oportunistas, porém a **EXECUÇÃO** não foi autorizada. E11-M01 permanece **`BLOCKED`**. Nenhum benchmark, POST, snapshot, `kubectl apply/delete`, stop, rm, prune ou manipulação das bancadas históricas foi realizado ao criar este documento. Qualquer alteração de regras após início da coleta deverá constar em aditamento versionado e não pode ser escolhida com base nos tempos.

## 7. Atualização após regressão Windows do pacote v1

**Evidência:** `docs/tcc2/etapa-11-e11-m00-v1-auditoria-regressao-81-tests.md` (commit `edf4f413b30ee41628f99b670bb61353cee40693`) registra o texto fornecido pelo acadêmico em 17/11/2026: HEAD **`e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`**, `ARQUIVOS: PASS`, `COMPILACAO: PASS`, `Ran 81 tests in 0.314s`, `OK`, `TESTES: PASS`. São 81/81 casos sintéticos e **não** 81 execuções da aplicação. Novo pacote de quotas/host, exclusividade e auditoria de ZIP está **regressionado estaticamente neste SHA**.

**Gates agora fechados:** compilação e unittest Windows para o SHA indicado. **Permanecem abertos:** disponibilidade efetiva de RAM Windows `>= 3 GiB` (último valor observado ~2,01 GiB), comprovação de `cpu.max`/`memory.max`/`memory.swap.max` nos quatro contêineres/Pods de uma **bancada nova e autorizada**, política de backup e encerramento restrita ao novo recurso com IDs/UID imutáveis e allowlist positiva, análise de resultados de falha e autorização de execução; evitar acumular 30 bancadas novas. Qualquer alteração de código após o SHA acima exige nova regressão da versão modificada.

**Estado atualizado:** `DESIGN_FROZEN / SYNTHETIC_REGRESSION_PASS / OPERATIONAL_READINESS_BLOCKED`. **E11-M01 NÃO AUTORIZADO**. Não transformar a aprovação de testes mock em certificação de quota física nem tocar em históricos.
