# TCC2 — E11-M00H — C4-S01 qualificada, evidência preservada e retirada por UID preparada

**Data:** 18/11/2026 (America/Sao_Paulo).  
**Status:** `C4_S01_REAL_QUALIFICATION_PASS / C4_S01_RETIREMENT_PREPARED_UNTESTED / E11_M01_MAIN_SERIES_BLOCKED`.  
**Base primária:** saída PowerShell real enviada pelo acadêmico. Nenhuma ação Docker ou Kubernetes foi executada pelo assistente nesta preparação.

## 1. Qualificação SACRIFICIAL real concluída em C4

No commit `3221696c10faec8131dacb900209bd6b2669ebb9`, o acadêmico realizou preflight e execução em C4:

- `Ran 129 tests in 0.272s`, `OK`, `REGRESSAO: 129/129 PASS`.
- Imagem Docker observada e aprovada idênticas: `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Fixture canônica observada: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`. RAM Windows livre: **7,53 GiB**; C **64,89 GiB** e D **69,53 GiB**.
- Após autorização expressa `AUTORIZO_EXECUTAR_QUALIFICACAO_C4_S01`, o manifesto do namespace novo `tcc2-pon-e11-c4-m01-s01` passou em dry-run e foi realmente aplicado. Três Deployments terminaram rollout e Pod cliente ficou Ready. **Nenhum namespace histórico foi utilizado como alvo**.
- `python -m benchmark.runner` em C4-S01 retornou `STATUS: PASS`, `ETAPA: complete` para 1000 POSTs seriados predefinidos, `timing_only`. O auditor local retornou `ZIP_INTEGRITY_VERIFIED_NOT_DELETION_AUTHORIZATION`, **27 membros**, `functional_pass_verified=true`, `delete_authorized=false`.
- ZIP original: `C:\Users\João Victor\TCC2-Evidencias\E11-M00H\C4-m01-s01\resultado.zip`.
- Backup validado localmente: `D:\TCC2-Backup\E11-M00H\C4-m01-s01.zip`.
- SHA-256 reportado dos ZIPs: **`8e2f5a0918bcfe398e3d76b737973a08f35c59d62bfc9c03eea1939b29883f27`**.
- Journal da qualificação: `D:\TCC2-Backup\E11-M00H\C4-m01-s01-journal.jsonl`.
- **UID do namespace novo:** `08c6e166-4fc3-4aaf-b1d4-67ac5f628a30`.

**Conclusão científica limitada:** a qualificação C4-S01 comprova o funcionamento da prova de conceito nessa execução no cluster kind, mas **não integra a amostra de 30 rodadas E11-M01** e não autoriza inferências sobre ganho de desempenho, CPU/RAM comparativos ou dois hosts físicos. O ZIP binário C4 ainda **não foi enviado diretamente** ao assistente para recálculo independente; a auditoria e backup acima foram reportados pelo ambiente do acadêmico.

## 2. Encerramento específico C4-S01 — preparação, não execução

Preparado `benchmark/retirement_execute_c4_s01.py`, especializado a partir da rotina C3 já executada e comprovada, com substituições explícitas **sem alterar hashes por substituição indiscriminada de `c3` por `c4`**. Constantes congeladas:

- `NS=tcc2-pon-e11-c4-m01-s01`;
- `UID=08c6e166-4fc3-4aaf-b1d4-67ac5f628a30`;
- `ZIP_SHA=8e2f5a0918bcfe398e3d76b737973a08f35c59d62bfc9c03eea1939b29883f27`;
- `RUN_ID=e11-c4-m01-s01`;
- `APPROVAL=AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C4_M01_S01`.

**Sem `--execute`:** a ferramenta executa **somente leitura**, revalida ZIP principal/cópia por CRC+SHA, UID e labels do namespace, UIDs e containerIDs dos quatro Pods contra `ownership-start.json`, inventário fechado dos recursos do namespace e exclusividade M01 considerando Docker parado, redes e Kubernetes. Não executa `kubectl delete`.

**Com `--execute` (APENAS APÓS regressão e novo aceite interativo):** exige branch Git limpa, SHA exato da versão testada, confirmação do operador e arquivo de journal exclusivo em D ainda inexistente. Reexecuta as checagens, registra journal antes de **um DELETE de namespace com `DeleteOptions.preconditions.uid` congelado** (e `propagationPolicy=Foreground`) somente para C4-S01. Aguarda exclusão, compara inventário UID dos namespaces históricos e hashes de ambos os ZIPs. Em falha, registra `INTERRUPTED_DO_NOT_RETRY` e impede retry/forçar deleção. **O arquivo ZIP, backup, imagens, recursos históricos C2/Kubernetes e cluster kind permanecem intocados**.

`tests/test_benchmark_retirement_execute_c4_s01.py` adiciona **11 cenários sintéticos** (10 equivalentes aos casos C3 de inventário, consentimento, erro de UID, falha parcial, journaling, exclusão por UID e 1 caso com UID/hash/escopo congelados da C4 real). São **140 testes esperados** após os **129/129 PASS anteriores**; a suíte nova **não foi executada no Windows** por esta atividade.

## 3. Pendências para liberar E11-M01

1. Executar `compileall`, **140 testes** e a **prévia read-only C4-S01**. Se PASS, solicitar aceite de exclusão apenas C4-S01 e registrar `C4_S01_RETIREMENT_COMPLETE`, UIDs históricos preservados, hash do ZIP e backup em D.
2. Implementar/homologar fluxo geral **uma única bancada inédita por rodada**, com journal e ownership por IDs/UIDs dinâmicos congelados em arquivo de evidências, preflight, tempo, auditoria do ZIP, backup em D e desmobilização autorizada com fail-closed, para C2/C3/C4 em sequência B01–B10 (30 rodadas). **Não automatizar apagamento genérico nem reutilizar `m01-s01`**.
3. Aprovar roteiro de execução, procedimentos de falha parcial e monitoramento de limiares RAM/disco. Não converter tempos das qualificações sacrificial C2-S01/C3-S01/C4-S01 em amostras científicas.
4. Somente quando o controlador geral e testes locais forem PASS e a C4-S01 estiver encerrada, emitir aprovação específica para iniciar B01 em bancada `m01-b01`.

**Decisão:** `E11_M00H_C4_S01_QUALIFIED / RETIREMENT_C4_NOT_EXECUTED / E11_M01_BLOCKED`. Não houve execução de comandos de exclusão no desenvolvimento desta rotina.
