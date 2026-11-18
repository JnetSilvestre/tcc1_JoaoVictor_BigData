# TCC2 — E11-M00E — Qualificação real sacrificial C2-S01 (pré-registro antes de executar)

**Data:** 17/11/2026, America/Sao_Paulo. **Branch:** `tcc2/desenvolvimento`.  
**Estado:** `QUALIFICATION_PROCEDURE_DEFINED / NOT_EXECUTED / M01_MAIN_SERIES_BLOCKED`.

## 1. Contexto e separação amostral

O acadêmico confirmou várias ações de desligar/religar o computador. A nova consulta read-only mostrou **20 contêineres históricos C2/v03/v05/v06 `Exited (137)` ao redor de `2026-11-16T21:59:09Z`**, todos com `OOMKilled=False`, sem mensagem de `State.Error` reportada. Os objetos Kubernetes históricos permanecem, mas seus serviços têm `LastReason=Unknown`, `LastExit=255` e reinícios, enquanto os clientes dos pilotos estão `Failed`. Essa evidência é **compatível com interrupções Docker/WSL2 por desligamento**, porém não prova isoladamente causalidade. Não religar, recriar, remover ou executar novos testes nos históricos.

O último preflight reportou Docker `desktop-linux`, `CPUs=8`, `Cgroup=2`, Kubernetes v1.37.0 com ambos os nós kind Ready; RAM física Windows livre **8,81 GiB** e disco C livre **67,43 GiB**. Esses valores são pontuais, não garantias futuras.

**Próxima operação proposta:** **uma única rodada real SACRIFICIAL C2**, com 1.000 requisições, `seed=20260502`, por meio do executor já regressionado em 96 testes. Essa qualificação é teste de integração dos gates e mecanismo de evidências, **não** uma das 30 rodadas principais B01–B10 e não será usada na análise quantitativa. O protocolo primário permanece inalterado.

## 2. Identidade exclusiva, requisitos e operação

- Label: `m01-s01` (prefixo `m...` exigido pelo harness, sufixo `s01` sinaliza SACRIFICIAL); `run_id=e11-c2-m01-s01`. **Nunca reusar**.
- Rede futura `tcc2-pon-e11-c2-m01-s01`; quatro contêineres futuros `...-attribute-source`, `...-logic-engine`, `...-rule-executor`, `...-benchmark-client`.
- Uso de diretório de evidências fora do Git, sem sobrescrita, por exemplo `$env:USERPROFILE\TCC2-Evidencias\E11-M00E`, fixture gerada com `python -m benchmark.fixtures --output ... --sizes 1000`.
- Validar SHA-256 `inputs.jsonl` = `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; hash expected = `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`.
- Antes de executar, confirmar `git status --porcelain` limpo, branch, modo `timing_only`, Docker/kind disponíveis, nenhum recurso novo com prefixo `m...` já ativo e nome do C2 sacrificial inexistente; medir novamente RAM Windows disponível >= **3 GiB** e disco no projeto >= **15 GiB**. **Se qualquer gate falhar, STOP antes de --execute.**
- A operação `python -m benchmark.docker_c2 ... --measurement-mode timing_only --execute` **é mutante SOMENTE em rede/contêineres novos**: cria rede/4 contêineres, faz UM snapshot inicial e 1.000 POSTs seriados na aplicação sacrificial; coleta evidências/ZIP. O executor é fail-closed nos gates de memória/disco, imagem SHA, ownership e cgroup. Não usar esse comando sobre namespaces/contêineres antigos, nem repetir se a primeira tentativa ficar parcialmente mutada.

## 3. Resultado e retenção

Após executar, registrar explicitamente `STATUS: PASS/FAIL`, `ZIP`, `ZIP_SHA256`, `validation.json` e `batch-summary.json`. A entrada na série principal continua BLOQUEADA mesmo com PASS sacrificial.

- Se `FAIL`, preservar integralmente diretório, ZIP, rede e 4 contêineres criados se existirem; **não repetir**, não tentar consertar com reset ou reinício; diagnosticar mensagem e etapa.
- Se `PASS`, verificar integridade com `audit_archive(..., "C2","m01-s01","e11-c2-m01-s01")` (não modifica ZIP). A qualificação **não entra** na matriz C2-B01.
- Em seguida, copiar ZIP para outro volume de filesystem e verificar com `backup_integrity.compare_backup_pair`; sem volume adicional, registrar limitação e NÃO autorizar remoção de recursos da bancada.
- **Nenhum cleanup implementado/autorizado**; a bancada sacrificial será preservada, mesmo que bloqueie futuras bancadas pelo gate de exclusividade, até desenvolver/testar e aprovar rotina de encerramento **somente de recursos novos com IDs imutáveis/allowlist**. Não usar `docker system prune`, `docker rm`, `docker stop` ou `kubectl delete` genéricos.

**Limites científicos:** obter `T_batch` nesta qualificação não torna tempo válido para as 30 medições principais (viés/efeito de teste). C3/C4 não foram validados por esta execução de C2, nem CPU/RAM comparativas. Será necessário concluir qualificação/retirada de recursos antes de iniciar os blocos B01–B10.

## 4. Decisão documentada

`E11_M00E_C2_S01_QUALIFICATION_PERMITTED_CONDITIONALLY`: permissão para **no máximo uma bancada nova sacrificial** após os gates locais explicitados e fora da série. **E11_M01_MAIN_SERIES_BLOCKED**. A própria criação/execução ocorrerá pelo acadêmico no PowerShell, não pelo assistente. Nenhum POST, snapshot, `docker run` ou alteração de históricos foi executado durante a criação deste documento.
