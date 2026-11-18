# E11-M00H — Errata das constantes C4 e conclusão da retirada C3-S01

**Data:** 18/11/2026 (America/Sao_Paulo). **Evidência primária:** saída do PowerShell enviada pelo acadêmico; **não** houve execução Docker/Kubernetes pelo assistente nesta revisão.

## 1. Retirada C3-S01 concluída e preservada

Sob Git HEAD `819fbc9be34249781c9e774891e7d1bd2db6f5db`, o acadêmico executou regressão **128/128 PASS**, digitou **`AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C3_M01_S01`** e recebeu `status=C3_S01_RETIREMENT_COMPLETE`. Namespace novo **`tcc2-pon-e11-c3-m01-s01`**, UID **`41fa5e1b-1de5-40da-b72a-e051742788c1`**, foi removido por requisição DELETE com precondição de UID. Relatório do executor: `historic_resources_targeted=0`, `original_and_backup_preserved=true`. Journal `D:\TCC2-Backup\E11-M00G\C3-m01-s01-retirement.jsonl` terminou `COMPLETE`, conferido pelo bloco PowerShell.

ZIP C3-S01 original e backup anteriormente verificados: `463f56042536c95874a4f36dadfd5fd211fec18325132704c9f585d2ec6e80c8`. Retirada C3 **não é rodada da amostra científica**.

## 2. C4-S01 interrompida corretamente no preflight

Ainda sob HEAD `819fbc9...`, script C4 registrou `128/128 PASS` e **`STOP: Imagem nao e a aprovada`**. A falha ocorreu na linha de validação `docker image inspect`, **antes** de verificação de RAM/disco, antes de `Read-Host`, criação de diretório de tentativa, `kubectl apply`, snapshot, POST, journal ou arquivo ZIP C4. Portanto **C4-S01 NÃO foi executada nem criada por essa tentativa**; não houve alteração de recursos K8s por parte do fluxo C4.

A revisão do arquivo `scripts/e11_m00h_qualificacao_c4.ps1` identificou **substituição textual indevida na clonagem de C3 para C4**: o procedimento substituiu ocorrências de `c3` embutidas nos hashes de 64 caracteres por `c4`, gerando estes valores **INCORRETOS**:
- Docker imagem no script: `sha256:b9c714f32e359e7a21df264a926a840191c4ffb6d53bb0483f5e161143d8667a`.
- Fixture 1000 no script: `26121e3a8747c94fd8e690e4ca04762cf469e040ac41cdd7bd4c6aba14f90551`.

**Valores CORRETOS pré-fixados e anteriormente verificados:**
- Docker imagem: `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Fixture canônica: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`.

A falha da comparação é **explicada inteiramente pelo literal incorreto** no script. **Não comprova** que a imagem foi substituída no host: a saída não contém o valor efetivamente retornado pelo `docker image inspect`. Não reconstruir imagem, não alterar fixture, não reiniciar containers/nodes.

## 3. Correção e retomada

Ajustado `scripts/e11_m00h_qualificacao_c4.ps1` para os SHA exatos e incluídas mensagens `IMAGE_ID_OBSERVADO` e `FIXTURE_SHA256_OBSERVADO`, que deixam eventual divergência futura auditável. Adicionado **1 teste estático** `tests/test_benchmark_powershell_c4_preflight.py` que compara imagem do script com `benchmark.ownership.IMAGE_ID` e hash da fixture com a constante canônica, além de verificar o gate de cenário. **129 testes são esperados; ainda NÃO executados no Windows para a nova revisão.**

É seguro reiniciar **apenas o preflight C4** pela versão atualizada, porque a tentativa falhou **antes de criar namespace e qualquer estado de C4**. Contudo, os gates continuam obrigatórios: Git limpo, regressão, imagem/fixture, namespace C3 realmente ausente, journal C3 completo, RAM livre >=3 GiB, C/D >=15 GiB e exclusividade M01. Após aprovação interativa específica `AUTORIZO_EXECUTAR_QUALIFICACAO_C4_S01`, a C4-S01 sacrificial poderá ser criada uma única vez e deverá ser preservada com ZIP e backup para auditoria e futura retirada por UID.

**Estado:** `C3_S01_RETIREMENT_COMPLETE / C4_S01_IMAGE_HASH_SCRIPT_BUG_CORRECTED_PENDING_129_TESTS / E11_M01_BLOCKED`. **Nenhum resultado C4 ou 30 lotes principais é alegado.**
