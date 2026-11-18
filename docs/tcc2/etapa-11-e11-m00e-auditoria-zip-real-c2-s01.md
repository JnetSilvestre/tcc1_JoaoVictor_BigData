# TCC2 — E11-M00E — Auditoria independente do ZIP real da qualificação C2-S01

**Data da coleta:** 2026-11-18 01:36:44–01:37:02 UTC (2026-11-17, aproximadamente 22:36–22:37 BRT).  
**Data documental:** 2026-11-17 (America/Sao_Paulo). **Branch/revisão executada:** `tcc2/desenvolvimento`, `87a07cdab4e5fb649e3dec735e1c6ead5ac597f5`.  
**Fonte primária:** arquivo binário `C2-m01-s01.zip` **enviado pelo acadêmico nesta conversa** e saída PowerShell transcrita; auditoria no ambiente de análise do assistente por leitura direta de ZIP com Python `zipfile`/`hashlib`/`json`/`statistics`, sem execução Docker ou Kubernetes. O ZIP binário não foi comitado no GitHub nesta ação; cópia original deve continuar retida no computador do acadêmico.

## 1. Identidade, checksums e integridade física da evidência

- Nome do ZIP: `C2-m01-s01.zip`. SHA-256 do arquivo **recalculado localmente**: **`6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6`**, coincidindo com hash reportado pelo executor e por `Get-FileHash` do usuário.
- Arquivo possui **26 membros** e teste CRC `ZipFile.testzip() = None`, sem erro. O membro `checksums.sha256` lista os **25 outros membros**; hashes SHA-256 foram recalculados sobre os bytes de cada membro, sem divergência ou membros faltantes, com nomes únicos.
- `manifest.json`: `scenario=C2`, `run_id=e11-c2-m01-s01`, `measurement_mode=timing_only`, `seed=20260502`, `requests=1000`, `fixture_sha256=26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; imagem imutável `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Canonical `expected.jsonl` contém 250 linhas; `inputs.jsonl` contém exatamente **1000** linhas, com `step=1..1000` e IDs da rodada. O arquivo `effects.jsonl` tem 250 linhas. Os 250 objetos JSON de efeitos **coincidem na sequência** com os 250 objetos do oráculo (a igualdade de bytes não ocorre devido à ordenação de chaves JSON distinta, o que não é erro funcional).

## 2. Resultado funcional comprovado

- `validation.json`: `status=PASS`, `phase=complete`, `started_snapshot=true`, `started_changes=true`; dez verificações em `checks` e quatro em `transport`, todas `true`.
- `client.stdout.jsonl`: **1000 registros de requisição** e uma linha final `summary`; 1000 respostas `status=200`, sem `duplicate_request` e com `step` de 1 até 1000, em ordem.
- Alterações efetivas: **874**; sem mudança: **126**. Logs mostram **874 emissões de notificação de atributo** e **500 emissões de notificação de condição**; os **250 efeitos esperados** constam em `effects.jsonl` e nos logs. Valores finais: `atA=10`, `atB=0`.
- `snapshot-response.json`: `ready=true`, `duplicate=false`, versão `e11-c2-m01-s01:snapshot:0`. `states-cold.json` apresenta os três papéis `ready=false` e `run_id=null`; após snapshot e ao final `ready=true`, `run_id=e11-c2-m01-s01` nos três papéis.
- `topology-start.json` e `topology-end.json` são idênticos byte a byte; identidades e limites de rede/contêineres estáveis, sem reinício no contexto da validação executada.

## 3. Duração e métricas (EXCLUSIVAMENTE qualificação)

- `batch-summary.json`: `elapsed_ns=17931810239` => **`T_batch=17.931810239 s`**; throughput aritmético **`1000 / T_batch = 55.7668181 req/s`**.
- Duração inclui laço do cliente e comunicação HTTP, não prova ganho ou custo de Docker/Kubernetes sem contrafactual. **Não incluir este tempo na série científica principal**.
- Registros de RTT por 1000 solicitações têm **mediana ~17.52725 ms** e média ~17.90806 ms; estas 1000 observações são dependentes dentro de **uma única rodada**, portanto não constituem n=1000 independentes.
- `metrics-status.json`: `timing_only`, `resource_sampling_during_batch=false`, `resource_metrics_comparable=false`. `validation.metric_quality.status=NOT_COLLECTED`, `sample_count=null`, `usable_cpu=false`, `usable_memory=false`, `measurement_approved=false`. **Não inferir custos CPU/RAM a partir de `memory_current` pré-lote.**

## 4. Gates de ambiente observados na evidência

- `capacity-gate.json`: `CAPACITY_SAFETY_GATE_PASS_NOT_PERFORMANCE_APPROVAL`, RAM Windows livre **9038450688 bytes (~8.42 GiB)** e disco livre no projeto **72409292800 bytes (~67.44 GiB)**, ultrapassando limites de segurança **3 GiB** e **15 GiB** respectivamente (valores de gate coletados antes do snapshot e distintos da leitura PowerShell do precheck).
- `environment.json`: Windows, Python **3.13.9**, Docker `desktop-linux`, cgroup v2, 8 CPUs anunciadas, RAM daemon **8245641216 bytes**, imagem e Git HEAD conferidos.
- `campaign-exclusivity.json`: `ONE_NEW_CAMPAIGN_BENCH_ONLY` e listas vazias de outros novos recursos no instante do preflight.
- `ownership-start.json`: `NEW_BENCH_OWNERSHIP_READONLY_PASS`, IDs imutáveis de rede e dos quatro contêineres novos sob `tcc2-pon-e11-c2-m01-s01`; **`delete_authorized=false`, `commands=[]`**.
- `preflight-uniform.json`: `PASS_COLD_READ_ONLY`, três GETs de health, três GETs de state e três leituras de logs, uma sequência final por papel antes do snapshot, sem POST de aquecimento.
- `effective-quotas.json`: `EFFECTIVE_LIMITS_ALL_FOUR_PASS` para quatro papéis. Cada um possui `cpu.max=50000 100000` (0,5 CPU); três serviços `memory.max=268435456` bytes (256 MiB), cliente `memory.max=134217728` bytes (128 MiB); `memory.swap.max=0`; `memory.events.oom=0` e `oom_kill=0` na leitura **pré-snapshot**, não durante todo o lote.

## 5. Conclusão, limites e bloqueios

**Veredito técnico:** `E11_M00E_C2_S01_QUALIFICATION_PASS_EVIDENCE_AUDITED`.

A qualificação sacrificial demonstra integração funcional, identidade, isolamento de novo cenário Docker, quotas efetivas pré-snapshot e integridade da coleta de tempo/artefatos para **C2 no host e período observados**. Não demonstra C3/C4, estabilidade entre 30 ensaios, independência de nós kind, comparabilidade de CPU/RAM, nem qualidade do processo de backup em outro volume. Nenhuma rodada B01–B10 foi iniciada.

**Próximas condições obrigatórias, sem executar limpeza:**
1. Executar/verificar cópia de ZIP em outro volume de filesystem, com verificação SHA/CRC byte a byte; **não remover o ZIP original**.
2. Homologar procedimento de encerramento/desmobilização com *allowlist* por IDs imutáveis da bancada nova, teste sacrificial e autorização específica do operador; jamais tocar nos históricos C2/Kubernetes.
3. Não executar C3/C4 `m...` enquanto a bancada C2-S01 permanecer e a regra de exclusividade do protocolo estiver em vigor. NÃO reiniciar nem remover o C2-S01 prematuramente.
4. Fazer qualificações próprias C3 e C4 antes da liberação de 30 rodadas, caso exigidas pelo protocolo final, mantendo exclusão dos dados da análise.
5. Critérios de memória/disco deverão ser verificados novamente imediatamente antes de cada bancada nova.

**Integridade e causalidade:** o ZIP foi auditado no ambiente do assistente, sem executar contêineres, aplicações, snapshot, POST ou remoção. O resultado do lote foi executado no computador do acadêmico e suportado por evidência binária verificável. **Os arquivos binários devem ser preservados pelo acadêmico**; não presumir backup independente realizado.
