# TCC2 — E11-M00E — Verificação da cópia do ZIP C2-S01 em D:

**Data documental:** 17/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.

**Fonte primária:** saída PowerShell enviada pelo acadêmico para a cópia e execução do comando `python -m benchmark.backup_integrity --primary ... --backup ...`. O assistente **não acessou diretamente o volume D:** e não recalculou o hash da cópia no computador do acadêmico; a evidência de cópia provém do verificador local do usuário. O SHA-256 do ZIP original havia sido conferido independentemente no laudo `etapa-11-e11-m00e-auditoria-zip-real-c2-s01.md`.

## 1. Resultado reportado

**Origem:** `C:\Users\João Victor\TCC2-Evidencias\E11-M00E\C2-m01-s01.zip`.  
**Cópia:** `D:\TCC2-Backup\E11-M00E\C2-m01-s01.zip`.

Saída observada:
- `SHA256: PASS` e `BACKUP: PASS`;
- `status=BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION`;
- `zip_sha256=6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6`;
- `zip_bytes=175736`;
- `members=26`;
- `different_filesystem_volume=true`;
- `independent_physical_device_verified=false`;
- `delete_authorized=false` e `commands=[]`.

O programa realizou verificação de CRC, hashes internos e igualdade de bytes/SHA-256 entre os arquivos. Esta evidência sustenta **duas cópias íntegras em volumes lógicos distintos** no instante da consulta. **Não sustenta independência de discos físicos**: C: e D: podem pertencer ao mesmo dispositivo, e a localização não oferece proteção garantida contra falha desse disco.

## 2. Decisão e implicações para a qualificação

**Gate `C2_S01_BACKUP_IN_DISTINCT_VOLUME_VERIFIED` = PASS reportado.** O ZIP original, a cópia e seus SHA devem permanecer preservados. A qualificação sacrificial C2-S01 reportou `STATUS: PASS` e foi auditada funcionalmente no documento anterior, mas **não faz parte dos 30 lotes definitivos**.

**Nenhuma remoção/parada está autorizada**, mesmo após o backup:
1. Verificar **em modo somente leitura** o ownership real da rede e quatro contêineres `e11-c2-m01-s01` no estado atual, e confrontar os IDs com `ownership-start.json` preservado no ZIP.
2. Executar somente leitura `audit_archive`, `capture_docker_ownership`, `compare_backup_pair` e `review_retirement_packet`, garantindo `REVIEW_ONLY_EVIDENCE_CONSOLIDATED`, `commands=[]` e `delete_authorized=false`.
3. Para encerramento de recursos **exclusivamente novos**, ainda serão necessários procedimento específico de allowlist positiva (nome completo, IDs imutáveis, labels), teste sacrificial sem tocar em históricos e decisão/autorização expressa do operador. Sem isso, a bancada fica preservada e C3/C4/M01 continuam bloqueados pelo gate de exclusividade.
4. Todas as 20 unidades históricas Docker e os namespaces/Pods Kubernetes anteriores devem continuar intocados; **não executar `docker stop/rm/prune` ou `kubectl delete` genéricos**.

**Estado:** `E11_M00E_C2_S01_QUALIFICATION_PASS / BACKUP_DISTINCT_VOLUME_PASS / RETIREMENT_UNAUTHORIZED / E11_M01_BLOCKED`.

**Integridade:** a redação deste registro não executou comandos em Docker/Kubernetes nem escreveu, apagou ou modificou o ZIP original, sua cópia ou recursos históricos.
