# TCC2 — E11-M00C — Preparação técnica dos controles finais (sem carga)

**Registro:** 16/11/2026 (America/Sao_Paulo); **branch:** `tcc2/desenvolvimento`.  
**Estado:** `IMPLEMENTED_STATICALLY_NOT_VALIDATED_ON_WINDOWS / BLOCKED_FOR_M01`. A versão E11-M00-v1 permanece **candidata, NÃO congelada**. Os controles técnicos preparados aqui não autorizam nenhum `--execute`.

## 1. Base documental e razão técnica

Fonte: `etapa-11-e11-m00c-protocolo-v1-candidato-bloqueado.md`, `STATUS_ATUAL_TCC2.md`, auditorias E11-P04/P05/P06, M00A/M00B e inventários M00C Windows/Docker. Foram auditados dois pontos:
- C2 tinha polling de readiness, `states-cold.json` e logs; C3/C4 tinham verificação de frio semelhante, mas não a mesma leitura final uniforme.
- Nenhum executor registrava automaticamente um arquivo `environment.json` com condições do host; os ZIPs precisavam de verificação integral antes de qualquer deliberação sobre descarte de **bancadas novas**.

A memória Windows livre reportada recentemente foi `2,42 GiB`; havia 22 contêineres ativos, inclusive históricos. Assim, **não é adequado acumular 30 bancadas em funcionamento**. Qualquer política de encerramento de recursos novos depende de controle de identidade e evidências, sem atingir os históricos.

## 2. Módulos preparados no GitHub

### 2.1 `benchmark/campaign_controls.py` — GETs finais uniformes

`final_readonly_cold_check(get_health, get_state, get_logs)` faz **uma rodada final idêntica por papel** nos cenários C2/C3/C4 em `timing_only`, com:
- 1 `GET /health/live`, 1 `GET /state` e 1 leitura de logs por papel (3 papéis; 9 leituras);
- conferência de `live=true`, `ready=false`, `run_id=null`, atributos/sequências zerados, ausência de notificações/mutações antigas, estado lógico sem efeitos/ledgers/faults e source sem pending;
- `preflight-uniform.json` com UTC de início/fim, leitura final de estados e resumo dos logs, **antes** de qualquer snapshot. Falha implica `STOP`, sem tentar corrigir/repetir snapshot.

A sequência de bootstrap/readiness anterior **ainda difere** entre Docker e Kubernetes: o que foi uniformizado é a **passada final não mutante**, não a história de caches/probes. Nenhum `POST` de aquecimento foi introduzido e não se deve chamar essas leituras de aquecimento funcional.

### 2.2 `benchmark/environment_snapshot.py` — baseline `environment.json`

A função `capture_environment(scenario,run_id)` faz leituras não mutantes **fora de `T_batch`**: Git HEAD, SO/Python, CPU lógica, espaço total/livre do disco do projeto, Docker context e cgroup/CPU/RAM anunciadas, SHA-ID da imagem aprovada; em Windows, RAM total/livre via `Get-CimInstance` em PowerShell; em C3/C4, `kubectl ... get nodes -o json` com UID, `allocatable` e Ready.

Os dois executores C2 e C3/C4 agora chamam essa função no modo `timing_only`, antes de seu primeiro snapshot. Falha no baseline impede a mutação daquele executor e gera registro de falha quando possível. O JSON contém `BASELINE_READ_ONLY_NOT_CAPACITY_APPROVAL` e não marca CPU/RAM comparativas como aprovadas. **Não mede quota/period/swap efetivos de contêineres novos e não verifica memória disponível durante o lote**.

### 2.3 `benchmark/lifecycle_audit.py` — provas de arquivamento, nenhuma exclusão

`audit_archive(zip_path, scenario, label, run_id)` foi preparado para ZIPs de futuras rodadas `timing_only`, exigindo: nomes sem duplicatas, arquivos obrigatórios incluindo `environment.json` e `preflight-uniform.json`, CRC do ZIP, SHA-256 de **cada** membro listado, correspondência ao `run_id`, `manifest.json`, resultado `validation.json` `PASS` e registro de snapshot e mudanças efetivas. O laudo retorna `delete_authorized=false`.

`retirement_review_only(...)` limita-se a **exibir** os nomes esperados de recursos novos `m...` sob `status=REVIEW_ONLY_NO_ACTION`; a propriedade da evidência deve corresponder aos IDs e cenários e sempre devolve `commands=[]`, `delete_authorized=false`. **Este módulo não importa Docker/kubectl/subprocess, não para e não exclui nada.** Não usar a checagem de ZIP como autorização suficiente de destruição: ainda serão necessários UID/ID reais do runtime, ownership, cópia redundante segura, allowlist e aceite formal.

Uma execução com erro/timeout **permanece preservada e registrada**, inclusive se seu ZIP não satisfizer os requisitos de sucesso; não substituir nem eliminar resultados falhos.

## 3. Integração restrita ao harness

Arquivos alterados (sem alterações em `pon/`, `c1/`, imagem Docker ou serviços):
- `benchmark/docker_c2.py`: baseline antes de criar rede nova e rodada uniforme após inicialização e antes do snapshot, **somente** com `--measurement-mode timing_only`. Modo diagnóstico legado não se altera.
- `benchmark/runner.py`: baseline e rodada uniforme após preflight C3/C4 e **antes** de snapshot, **somente** em `timing_only`. Nenhum manifesto aplicado por esta modificação.

O `archive(output)` existente já inclui arquivos extras gerados na pasta de saída, de modo que, no fluxo `timing_only` futuro, os novos `environment.json` e `preflight-uniform.json` passam a constar no ZIP e `checksums.sha256` gerado, sem editar runtime de aplicação.

## 4. Testes sintéticos preparados — NÃO executados ainda

Novos módulos `tests/test_benchmark_campaign_controls.py`, `tests/test_benchmark_environment_snapshot.py` e `tests/test_benchmark_lifecycle_audit.py` contêm **15 casos** para: conferir sequência e quantidade de GETs, estado frio/estado previamente mutado, host/imagen/cluster injetados, SHA-256 e integridade ZIP, falha funcional, label histórico e revisão `REVIEW_ONLY` sem comandos.

A suíte já verificada no Windows antes dessas alterações tinha **48 testes PASS no SHA `2d237ba8...`**, não no HEAD atual; a descoberta atual deverá apresentar **63 casos se todos forem carregados**, contagem ainda **NÃO EXECUTADA**. Sintaxe, testes e interação integrada com ambiente real permanecem pendentes. Não reportar PASS até a evidência do acadêmico.

## 5. Validação segura seguinte (no Windows) e estado

Na pasta `prova-conceito`, após assegurar árvore Git limpa, `git pull --ff-only origin tcc2/desenvolvimento`, verificar SHA, então:

```powershell
python -m compileall -q benchmark tests
if ($LASTEXITCODE -ne 0) { throw "compileall reprovado" }
python -m unittest discover -s tests -p "test_benchmark*.py" -v
if ($LASTEXITCODE -ne 0) { throw "unittest reprovado" }
git status --porcelain
```

Tudo acima é **somente compilação e testes locais sintéticos**, sem criação de namespace/rede, snapshot, POST, benchmark ou remoção de histórico.

**Outros gates antes da autorização de E11-M01:** ensaio de `PLAN_ONLY` se houver novas flags, preflight de quotas/cgroup reais em bancadas novas **antes** do primeiro POST (em fase autorizada), política com regra auditável de ownership e retenção limitada de *somente* bancadas novas, limites de pressão/STOP prospectivos, aceitação das reposições e congelamento E11-M00-v1. CPU/RAM comparativas ainda bloqueadas.

**Decisão:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`. Nenhum experimento executado e nenhuma bancada histórica alterada, reiniciada ou excluída nesta atividade.
