# E11-M00J — Controlador generalizado da campanha B01–B10: implementação bloqueada para homologação

**Data:** 18/11/2026 (America/Sao_Paulo). **Fonte de decisões:** pré-registro `docs/tcc2/etapa-11-e11-m00-v1-pre-registro-e-gates-m01.md`, evidências sacrificiais C2-S01/C3-S01/C4-S01 e resultado pré-campanha `M01_READONLY_BASELINE_PASS_NOT_EXECUTION_AUTHORIZATION`. **Nenhuma mudança de hipótese, carga, topologia, quotas, cenários ou ordem está sendo introduzida.**

## 1. Gate anterior observado de fato

A saída textual do acadêmico confirma HEAD `e407c1e2c27ae306bf54291b20f0386b0b84ee83`, **`Ran 151 tests in 0.338s`, `OK`**, `M01_READONLY_BASELINE_PASS_NOT_EXECUTION_AUTHORIZATION`, fixture canônica `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`, oráculo `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`, imagem `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`, sem bancadas M01 novas remanescentes. As três qualificações C2, C3 e C4 e suas retiradas foram revalidadas com ZIPs, backups D e journals completos. RAM Windows livre **8.127.991.808 bytes** e disco livre do projeto **69.667.672.064 bytes** passaram os gates. A matriz contém **30 slots** com o primeiro `e11-c2-m01-b01`, segundo `e11-c3-m01-b01` e terceiro `e11-c4-m01-b01`. **Nenhuma rodada definitiva foi executada.**

## 2. Implementação criada nesta etapa

`prova-conceito/benchmark/m01_lifecycle.py` é uma implementação prospectiva de **controlador de rodada única**, responsável pelos 30 slots congelados via `m01_readiness.full_schedule()`.

A API possui quatro fases:
- `plan`: leitura de Git, 3 ZIPs e journals sacrificiais, fixture, inventário global de recursos M01 **inclusive contêineres parados**, capacidade do host e encadeamento de slots. Emite `M01_SLOT_PLAN_ONLY` e `start_authorized=false` sem escrever artefatos ou alterar Docker/Kubernetes.
- `run` (**código preparado, bloqueado**): para um único slot autorizado, exige consentimento específico, Git HEAD aprovado/limpo, nenhum slot anterior incompleto, nenhum artefato prévio desta tentativa, capacidade e bancada inexistente. Cria journal exclusivo ANTES de qualquer comando de criação. Reusa somente executores existentes `benchmark.docker_c2` para C2 e `benchmark.runner` com `benchmark.prepare` para C3/C4; fixa `timing_only`, `timeout=10`, `batch-timeout=600` e a fixture única. Para Kube aplica apenas manifesto do namespace M01 novo, após dry-run de cliente, aguarda rollout e registra UID. Executa um snapshot/lote, sem retry. Audita `resultado.zip` com CRC/SHA/funcionalidade/cgroups/capacidade, cria cópia exclusiva em D, valida `compare_backup_pair`, escreve `M01_RUN_PASS_BACKED_UP` e **preserva** todos os recursos da bancada, que continuam ativos.
- `review`: somente leitura, após `RUN_PASS_BACKED_UP`, confere ZIP, cópia D, journal e compara IDs/UIDs e labels reais aos imutáveis `ownership-start.json` do ZIP; exige exclusividade de recursos M01, inventário fechado dos objetos da bancada, estado Running e ausência de reinícios. Emite `M01_RETIREMENT_REVIEW_ONLY_PASS` com `delete_authorized=false` e `commands=[]`.
- `retire` (**código preparado, bloqueado**): exige novo consentimento independente, HEAD completo aprovado, journal exclusivo e revalidação da prévia. Para C2, usa IDs completos de 64 hex para parar/remover **somente quatro contêineres novos e sua rede bridge interna nova**; para C3/C4, envia um único `kubectl delete --raw` do namespace novo com `DeleteOptions.preconditions.uid` obtido e congelado no ZIP, `propagationPolicy=Foreground`. Aguarda confirmação, confere UIDs históricos preservados e ZIPs intactos e registra `M01_RETIREMENT_COMPLETE`. **Nenhum comando de limpeza genérica, prune, --force, delete em namespace histórico ou reinício de pilotos**.

A frase de aceite é específica a `run_id` e fase: `AUTORIZO_RUN_E11_C2_M01_B01` e `AUTORIZO_RETIRE_E11_C2_M01_B01` para o primeiro slot, sem reutilização de aprovações das qualificações S01.

**Chave de segurança incondicional da revisão atual: `MAIN_CAMPAIGN_ENABLED = False`.** Mesmo se o usuário tentar `--stage run` ou `--stage retire`, a CLI e as funções de execução negam autorização ANTES de executar qualquer comando mutante. Essa chave **NÃO deve ser ativada** até os novos testes Windows, revisão de código e a liberação operacional documentada da primeira rodada.

## 3. Journals, arquivos e idempotência

Para o slot `e11-cX-m01-bNN`:
- original: `%USERPROFILE%\TCC2-Evidencias\E11-M01\<run_id>\resultado.zip`;
- backup: `D:\TCC2-Backup\E11-M01\<run_id>.zip`;
- journal de execução: `D:\TCC2-Backup\E11-M01\<run_id>-run.jsonl`;
- journal de retirada: `D:\TCC2-Backup\E11-M01\<run_id>-retirement.jsonl`;
- arquivo de precondição Kubernetes, caso aplicável: `D:\TCC2-Backup\E11-M01\<run_id>-delete-options.json`.

A criação usa `open('x')`/ `open('xb')`, não sobrescreve artefatos e grava registros `flush` + `fsync`. Quando uma fase lança erro, insere `INTERRUPTED_DO_NOT_RETRY` e não faz rollback, retry de POST/snapshot, limpeza ou tentativa substitutiva. Um arquivo ou journal de tentativa anterior provoca STOP. Cada rodada seguinte exige **comprovação do journal `M01_RUN_PASS_BACKED_UP` e do journal `M01_RETIREMENT_COMPLETE`** de todos os slots precedentes, hashes e backups equivalentes; artefatos de slots posteriores provocam STOP de ordem. A sequência B01–B10 permanece como pre-registrada.

É deliberado que uma falha possa deixar namespace/contêineres novos e evidência parcial preservados. Nesse caso, o operador deve interromper a campanha e tratar a situação como pendência forense separada; **não executar automaticamente outra rodada** e não usar um tempo funcionalmente reprovado como se fosse PASS.

## 4. Testes preparados e próximos gates

`tests/test_benchmark_m01_lifecycle.py` acrescenta **22 testes sintéticos** de ordem fixa/identidades, nomeação, autorização negada, inventário/objeto Kube estranho, Docker M01 parado/extra, Git sujo, prevenção de repetição, journal de falha, cópia em D, DELETE pré-condicionado ao UID e proteção contra IDs arquivados divergentes. A versão anterior tinha **151 testes PASS observados no Windows**; após 22 casos novos, **173 são esperados, ainda NÃO executados no Windows**. Os testes usam mocks e filesystem temporário, sem tocar Docker/Kubernetes reais.

### Comando de verificação somente leitura após atualizar o checkout

No diretório `prova-conceito`, rodar `python -m compileall -q benchmark tests`, `python -m unittest discover -s tests -p "test_benchmark*.py"` e:

```powershell
$fixture = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl"
python -m benchmark.m01_lifecycle --position 1 --stage plan --fixture $fixture --backup-root "D:\TCC2-Backup"
```

O relatório deverá apresentar **`M01_SLOT_PLAN_ONLY`**, `e11-c2-m01-b01`, `start_authorized=false` e `commands=[]`; a ausência de `--execute` e a trava `MAIN_CAMPAIGN_ENABLED=false` impedem qualquer criação, POST ou exclusão.

## 5. Decisão e limitações

Esta etapa implementa, mas **NÃO homologou em execução real** o ciclo geral M01. Validação sintética mais resultados das qualificações específicas S01 **não equivalem automaticamente** a uma homologação operacional do código recém-criado, que precisa de revisão estática, regressão no ambiente Windows, teste fail-closed e aprovação operacional documentada antes de B01.

**Estado:** `E11_M00J_GENERALIZED_LIFECYCLE_IMPLEMENTED_DISABLED / SYNTHETIC_TESTS_PENDING / E11_M01_MAIN_SERIES_BLOCKED`.

CPU/RAM continuam **não coletados durante o lote** e não aprovados como comparativo de desempenho; apenas T_batch, throughput e RTTs são os desfechos quantitativos permitidos. O ambiente C4 consiste em dois nós kind virtuais no **mesmo computador físico**, não em dois servidores independentes.
