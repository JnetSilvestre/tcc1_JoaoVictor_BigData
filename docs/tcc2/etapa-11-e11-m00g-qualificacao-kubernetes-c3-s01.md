# E11-M00G — Pré-registro de qualificação sacrificial Kubernetes C3-S01

**Data documental:** 18/11/2026 (America/Sao_Paulo). **Status:** `C3_QUALIFICATION_PREPARED_NOT_EXECUTED`; `E11_M01_MAIN_SERIES_BLOCKED`.

## 1. Marco anterior confirmado

Conforme transcript PowerShell fornecido pelo acadêmico, em SHA `b83e0b8902593259c005e20760fff61d9f205a50`, o script `scripts/e11_m00f_preparacao_consolidada.ps1` concluiu `Ran 117 tests in 0.242s`, `OK`, `FIXTURE CANONICA SHA256: PASS`, nós kind acessíveis, RAM Windows livre **5,59 GiB**, discos C **64,73 GiB** e D **69,53 GiB**. Dois manifestos C3/C4 novos `m01-s01` passaram `kubectl apply --dry-run=client --validate=strict`; **NÃO foram aplicados**.

O operador forneceu frase de autorização específica para a **bancada nova sacrificial C2-S01**, e a retirada retornou `S01_RETIREMENT_COMPLETE`, `containers_stopped_removed=4`, `network_removed=1`, `historic_resources_targeted=0`, `zip_original_or_backup_modified=false`. Journal `D:\TCC2-Backup\E11-M00E\C2-m01-s01-retirement.jsonl` terminou com `COMPLETE` conforme validado pelo script; os inventários de nomes/IDs Docker históricos e UIDs de namespaces Kubernetes históricos não mudaram pela comparação antes/depois. **Nenhum dado de C2-S01 compõe as 30 rodadas principais**.

## 2. Pequeno endurecimento de segurança antes de novas bancadas

`benchmark/campaign_exclusivity.py` foi alterado para consultar `docker ps -a` em vez de `docker ps`, de modo a bloquear também contêineres **novos M01 parados**. Incluiu-se um teste sintético em `tests/test_benchmark_campaign_exclusivity.py` que exige a opção `-a` e falha na presença de um contêiner `m...` extra. Por essa mudança, **118 testes são esperados**, mas ainda não há comprovação de PASS no Windows para este SHA mais recente. O código funcional PON, imagem imutável, fixture e matrizes não foram alterados.

## 3. Próxima qualificação C3-S01 (NÃO é a série definitiva)

Script novo `prova-conceito/scripts/e11_m00g_qualificacao_c3.ps1`, com execução prospectiva **única e não repetível** após consentimento interativo específico `AUTORIZO_EXECUTAR_QUALIFICACAO_C3_S01`. Antes da criação:
- Git branch limpa, 118 testes/compileall PASS, imagem aprovada SHA, Docker cgroup v2 e os dois nós kind Ready;
- RAM Windows `>=3 GiB`, discos C e D `>=15 GiB`;
- fixture canônica de 1000 entradas SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`;
- ZIP C2-S01 principal e cópia com SHA `6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6`, journal de retirada C2-S01 concluído;
- `docker ps -a`, redes Docker e namespaces do cluster para ausência de qualquer outro recurso `m...`; IDs históricos fotografados antes, com reconfirmação de exclusividade imediatamente antes de `kubectl apply`.

**Somente após aceite:** gerar manifesto exclusivo em `C:\Users\<perfil>\TCC2-Evidencias\E11-M00G\C3-m01-s01\manifest.yaml`; executar `kubectl apply --dry-run=client`, depois `kubectl apply` somente desse manifesto. O namespace novo autorizado é **`tcc2-pon-e11-c3-m01-s01`**, com labels `tcc2.e11/campaign=m01` e `tcc2.e11/run-id=e11-c3-m01-s01`. Aguardar três Deployments/Pod cliente Ready, registrar UID do Namespace e executar **uma única chamada** `python -m benchmark.runner --scenario C3 --label m01-s01 --run-id e11-c3-m01-s01 --measurement-mode timing_only --execute` com 1000 POSTs (seed 20260502), após seus gates de cgroup/ownership/exclusividade/estado frio.

Após eventual `PASS` do executor, **auditar** ZIP com `audit_archive`, criar cópia inédita em D e validar CRC/SHA byte a byte com `backup_integrity`; fotografar inventários históricos. Guardar journal da tentativa em `D:\TCC2-Backup\E11-M00G\C3-m01-s01-journal.jsonl`. **Nunca deletar o namespace C3-S01 automaticamente.** Em qualquer erro ou timeout, registrar e preservar namespace, ZIP, logs e journal; NÃO repetir snapshot/POST, nem fazer `rollout restart`, `delete` ou `prune`.

Essa qualificação também **não será usada como amostra estatística**. O ambiente é kind virtual de dois nós no mesmo host físico; não equivale a dois hosts independentes. CPU/RAM continuam `NOT_COLLECTED` durante o lote, sem comparação de consumo.

## 4. A próxima trava

Mesmo que a C3-S01 passe, será preciso **homologar um procedimento separado de desmobilização por namespace UID, labels, backup e aceite** antes de criar C4-S01, respeitando exclusividade. A C4-S01 também será qualificada fora da matriz e terá os mesmos requisitos de arquivamento. Somente após ambas e um ciclo de vida generalizado que suporte 30 rodadas isoladas deve-se liberar `E11-M01`.

**Integridade:** documento e script foram criados no GitHub, mas não foram executados no Windows nem no cluster. Nenhum resultado real novo de C3, C4 ou das 30 rodadas é alegado.
