# E11-M01 — Execução definitiva integrada dos 30 slots, sem repetição da B01/C2

**Data:** 18/11/2026 (America/Sao_Paulo). **Status:** orquestrador versionado, execução no host acadêmico pendente; dados reais existem apenas para **B01/C2 (slot 1 de 30)**, cujo journal está `COMPLETE/M01_RUN_PASS_BACKED_UP`, ZIP e backup SHA-256 `8197a3f08b0c8c8575e11bc87970289255c74f836d865b52b6e051c2cd8c3650`, bancada C2-B01 preservada.

## Objetivo e relação com planejamento

Evitar múltiplos turnos manuais de regressão, preparação e cópia de saída: a partir do `179/179 PASS` e `B01/C2 RUN PASS` reportados pelo acadêmico no HEAD `eecc15e3bb1c36c9ee51b3165f882d76a0c6ed9b`, consolidar todas as operações em **um único comando local** de execução sequencial, sem alterar a matriz pré-registrada (10 blocos; três cenários; 30 slots; 1.000 POSTs sequenciais por rodada; seed 20260502; `timing_only`; mesmo host físico; dois nós kind virtuais no C4).

O script `prova-conceito/benchmark/m01_campaign.py` usa exclusivamente funções já implementadas no controlador `m01_lifecycle.py` e a matriz de `m01_readiness.full_schedule()`. Nenhuma qualificação sacrificial S01 participa da série principal.

## Procedimento único

```powershell
Set-Location "C:\Users\João Victor\tcc2\etapa07\tcc2-trabalho\prova-conceito"
git pull --ff-only origin tcc2/desenvolvimento
$sha = (git rev-parse HEAD).Trim()
$fixture = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl"
python -u -m benchmark.m01_campaign --fixture $fixture --backup-root "D:\TCC2-Backup" --approved-head $sha
```

**O comando real deverá fixar SHA completo esperado na versão publicada e confirmar Git limpo antes de entrar no executor.** Ele não é executado pelo assistente porque o Windows/Docker/Kubernetes e os volumes C/D não estão conectados à sessão.

Por padrão, `--until-position 30` percorre todos os slots. Para limitar a sessão a um subconjunto e poder retomar mais tarde, acrescentar `--until-position N` com `1<=N<=30`. Na próxima execução, os slots com RUN e RETIRE completos são auditados e pulados; um journal de RUN já existente (B01/C2) **nunca dispara novamente snapshot/POST**.

## Portões de segurança de cada slot

1. Checar branch Git limpa/HEAD exato, posição em matriz congelada, release autorizado, ausência de estados futuros inesperados e status do ambiente.
2. Se journal `RUN` existir, exigir `COMPLETE/M01_RUN_PASS_BACKED_UP`, ZIP funcional PASS, CRC/SHA para todos os membros, backup byte a byte em outro volume e SHA idêntico ao journal; **jamais relançar RUN**.
3. Antes de desmobilizar a bancada já existente, revalidar em modo **somente leitura** o UID/IDs completos e labels originais de rede, quatro containers ou Namespace/Pods a partir de `ownership-start.json` no ZIP; nenhuma bancada M01 concorrente ou recurso terceiro é permitido; a saída do review mantém `delete_authorized=false`.
4. Exigir aceite humano independente por operação e ID, por exemplo `AUTORIZO_RETIRE_E11_C2_M01_B01` para finalizar a primeira bancada. A retirada C2 atua somente nos quatro IDs completos e na rede de nova criação; a retirada C3/C4 usa `DeleteOptions.preconditions.uid` para o Namespace recém-criado. **Nenhum recurso histórico será alvo**.
5. Após journal de `RETIRE` `COMPLETE/M01_RETIREMENT_COMPLETE`, reauditar ZIP e backup e somente então avançar para a posição seguinte.
6. Para slot ainda não iniciado, executar preflight SOMENTE LEITURA com RAM/disco mínimos e exclusividade, solicitar aceite `AUTORIZO_RUN_E11_C3_M01_B01` (exemplo do slot 2), criar **uma** bancada, executar exatamente um snapshot e 1.000 POSTs `timing_only`, auditar ZIP, copiar D e conferir bytes e SHA e registrar `RUN_PASS_BACKED_UP`; só então pedir autorização específica de RETIRE.
7. Qualquer STOP, falta de aceite ou interrupção deixa recursos e evidências preservados, sem retry automático, sem `docker prune`, sem `kubectl delete --all` e sem criar bancada substituta. Se um journal indicar `INTERRUPTED_DO_NOT_RETRY`, o orquestrador recusa retomar até investigação documental.

## Ordem e limites da autorização

`MAIN_CAMPAIGN_ENABLED=True` e allowlist `RELEASED_OPERATIONS` passaram a abranger os 30 slots da matriz. Isso é uma **liberação de código para solicitar consentimento**, não uma execução independente nem uma autorização prévia e irrestrita para remover recursos. `RUN` e `RETIRE` requerem **confirmações distintas por slot**, mesmo na execução integrada. Os artefatos dos 30 slots continuam fora do repositório, em `%USERPROFILE%\TCC2-Evidencias\E11-M01` e `D:\TCC2-Backup\E11-M01`. O script não cria nova fixture e não altera fontes da PoC.

A saída final `M01_CAMPAIGN_SEGMENT_COMPLETE`, `all_30_completed=true` somente deverá aparecer após cada slot chegar a `RUN_PASS_BACKED_UP` **e** `RETIREMENT_COMPLETE`, com ZIPs e cópias íntegros. Não inferir números de T_batch, RTT, throughput, CPU ou RAM da mera conclusão. Resultados estatísticos e gráficos exigem leitura real dos ZIPs após a série.

## Integridade científica e limites reais

Os **179/179 testes anteriores** e o RUN real B01/C2 foram comprovados pela saída do acadêmico; o orquestrador integrado desta revisão **não foi executado no host Windows nesta mensagem**. Não afirmar conclusão das 29 rodadas restantes. A regressão automatizada pode ser mantida em CI para verificações de código, mas não substitui as verificações Docker/Kubernetes, executadas localmente pelo próprio controlador. Qualquer correção no código durante uma campanha requer registro de SHA por rodada e avaliação sobre comparabilidade antes de continuar.

**Estado:** `E11_M01_1_OF_30_RUN_PASS_AND_BACKED_UP / B01_C2_RETIRE_PENDING / CAMPAIGN_ORCHESTRATOR_PREPARED_NOT_RUN`.
