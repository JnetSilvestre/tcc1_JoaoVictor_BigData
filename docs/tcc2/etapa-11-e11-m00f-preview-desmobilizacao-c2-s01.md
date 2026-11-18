# TCC2 — E11-M00F — Prévia segura de desmobilização da bancada sacrificial C2-S01

**Data:** 17/11/2026 (America/Sao_Paulo). **Situação:** `PREVIEW_IMPLEMENTED / WINDOWS_TEST_PENDING / NO_CLEANUP_AUTHORIZED`.  
**Vinculação:** auditoria de ZIP real C2-S01, backup íntegro em outro volume e revisão consolidada `REVIEW_ONLY_EVIDENCE_CONSOLIDATED`. **A qualificação C2-S01 não integra as 30 rodadas B01–B10.**

## 1. Evidência de entrada

O acadêmico enviou retorno `REVISAO SOMENTE LEITURA: PASS`:
- `run_id=e11-c2-m01-s01`;
- `zip_sha256=6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6`;
- `backup_volume_distinto=true`;
- `ids_conferidos=true`;
- `delete_authorized=false`, `commands=[]`.

Esse retorno comprova que o script de revisão encontrou os mesmos IDs de rede e contêineres gravados no ZIP no instante da consulta, após `audit_archive` e `compare_backup_pair`. **Não autoriza remoção**.

## 2. Ferramenta prospectiva exclusivamente de prévia

`prova-conceito/benchmark/retirement_preview_c2.py` aceita somente a bancada **C2-S01**, sem parametrização de outro cenário/rodada. Não possui `--execute` nem lógica de `stop`, `rm`, `delete` ou `prune`. Seu output sempre contém `commands=[]` e `delete_authorized=false`, mesmo com `PASS`.

O pré-voo:
1. Reaudita ZIP original C2-S01 e ZIP copiado em outro volume de filesystem.
2. Captura labels, nomes, imagem aprovada, IDs e estado **Running** da rede e dos quatro contêineres novos por consultas somente leitura.
3. Compara estritamente os IDs e nomes com `ownership-start.json` preservado dentro do ZIP.
4. Lista `docker ps -a` (não apenas `docker ps`) para bloquear **outros contêineres novos, inclusive parados**; lista redes `m...` para bloquear outra rede nova; lista namespaces Kubernetes `m...` para bloquear outra bancada nova.
5. Confere que a rede S01 tem **somente** os quatro endpoints esperados e que cada contêiner só está conectado à rede S01, sem endpoints estrangeiros.
6. Exibe as identidades imutáveis propostas como allowlist **documental**, exigindo procedimento de execução comprovadamente seguro e aprovação operacional separada.

**Históricos preservados:** `tcc2-pon-e11-c2-p...`, `tcc2-v03/v05/v06`, `tcc2-c2`, namespaces `tcc2-pon`, `tcc2-pon-c4` e pilotos antigos C3/C4. O código consulta inventários globais para detectar outros recursos novos, mas não para mutar históricos.

## 3. Testes de regressão

`prova-conceito/tests/test_benchmark_retirement_preview_c2.py` adiciona **10 testes sintéticos** ao conjunto anterior de **96/96 PASS**, total **106 testes esperados**, **não executados ainda no Windows na versão nova**. Verificam fail-closed para contêiner novo parado extra, rede adicional nova, namespace novo Kubernetes, endpoint estrangeiro, rede modificada, ID de rede alterado, arquivo ZIP com ID divergente, backup no mesmo volume e política de execução `delete_authorized=false`.

Validar `python -m compileall -q benchmark tests` e `python -m unittest discover -s tests -p "test_benchmark*.py" -v` no SHA completo da versão presente. Não atribuir o PASS de 96 à implementação nova de M00F.

## 4. Uso proposto, sem modificar o runtime

Com o código validado, no diretório `prova-conceito`, executar:

```powershell
python -m benchmark.retirement_preview_c2 --primary "C:\Users\João Victor\TCC2-Evidencias\E11-M00E\C2-m01-s01.zip" --backup "D:\TCC2-Backup\E11-M00E\C2-m01-s01.zip"
```

A ferramenta deverá terminar com `PREVIA SOMENTE LEITURA: PASS`; isso não interrompe nem remove contêineres. **Não repetir a qualificação C2-S01**.

## 5. Decisão para possível encerramento posterior

Uma vez aprovada a prévia, será necessária uma ferramenta distinta, auditável e testada, que valide IDs completos e labels antes e durante qualquer `stop`/`rm`, registre journaling independente e **jamais** execute operações sobre nomes/UIDs históricos. Qualquer etapa mutante exigirá **aceite explícito do operador** e procedimento de interrupção em caso de erro parcial. Cópia de backup em dois volumes **não equivale** a discos físicos independentes.

**Estado:** `E11_M00F_PREVIEW_UNVALIDATED / E11_M01_BLOCKED`. O objetivo do próximo teste é validar a segurança do planejamento, **não iniciar a série definitiva nem liberar limpeza**.
