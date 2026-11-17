# TCC2 — E11-M00D — Ownership, backup e revisão não destrutiva de bancadas M01

**Data de elaboração:** 17/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Estado:** `IMPLEMENTED_IN_REPOSITORY / NOT_VALIDATED_ON_WINDOWS / NO_DELETE_AUTHORIZATION`.  
**Vinculação:** pré-registro metodológico E11-M00-v1, matriz M00A, auditoria E11-M00-v1 de **81/81 testes PASS** no commit `e6e83ffa64e5074b6bcb80635dd472a2f3cf2401`, `STATUS_ATUAL_TCC2.md` e laudos anteriores.

## 1. Problema e objetivo desta entrega

A campanha principal prevê **30 tentativas**, cada uma com bancada `m...` nova, sem reuso de estado. O ambiente Windows/WSL2/Docker/kind mostrou ~**2,01 GiB de RAM física livre** na última amostra, abaixo do limiar operacional previamente escolhido de **3 GiB**. Acumular contêineres/Pods novos comprometeria a capacidade e potencialmente o controle de condições; entretanto, **não é permitido limpar bancadas históricas** ou apagar tentativas novas sem evidências e autorização.

Esta etapa estabelece dois comprovantes, **sem implementar stop/rm/delete**:
1. **Proveniência positiva/IDs imutáveis dos recursos NOVOS da rodada** (Docker: ID de rede e IDs de quatro contêineres; Kubernetes: UID do namespace e UIDs/containerIDs dos quatro Pods).
2. **Verificação read-only da cópia do ZIP** fora do diretório original, com CRC e SHA-256 de todos os membros e igualdade byte a byte com o ZIP primário; informação se os dois arquivos estão em volumes de filesystem diferentes.

O módulo existente `lifecycle_audit.py` passa a exigir o `ownership-start.json` dentro do ZIP de rodadas `timing_only` aprovadas e a oferecer revisão conjunta de ZIP/ownership/backup. **O resultado nunca inclui comandos destrutivos e sempre retorna `delete_authorized=false`.**

## 2. Mudanças estritamente prospectivas no harness

- `benchmark/ownership.py`: funções `capture_docker_ownership` e `capture_kind_ownership` recebem leitor injetável, fazem apenas `docker network inspect`, `docker inspect`, `kubectl get namespace` e `kubectl get pods`; validam nome/label `tcc2.e11/campaign=m01`, `tcc2.e11/run-id=e11-cX-m01-bNN`, imagem imutável Docker, UID/ID, quatro papéis e namespace/rede corretos. Não leem, modificam ou consultam histórico.
- `benchmark/docker_c2.py`: **somente para etiquetas novas `m...`**, `docker network create` e `docker run` futuros declaram as duas labels positivas adicionais. Pilotos `p...` e imagens/código da aplicação aprovados não mudam. Após a criação da bancada nova, mas **antes do snapshot**, `ownership-start.json` é produzido após `topology-start.json`.
- `benchmark/prepare.py`: quando `label` é `m...`, o manifesto isolado gerado para C3/C4 recebe labels exclusivas no Namespace recém-proposto. **Manifestos históricos em `infraestrutura/` NÃO foram editados**, tampouco o template para labels `p...`.
- `benchmark/runner.py`: após preflight de C3/C4 e antes do snapshot, verifica a identidade do Namespace/4 Pods NOVOS e grava `ownership-start.json`. Não muda o posicionamento de Pods, requests/limits, tipo de serviço, número de réplicas ou código funcional.
- `benchmark/lifecycle_audit.py`: `ownership-start.json` integra os arquivos obrigatórios e sua identidade é confrontada com cenário/run_id; `review_retirement_packet` consolida `audit_archive`, ownership e comparação de backup em volume diferente, **sem autorizar ação**.

**Observação:** a validação de ownership de um Pod exige estado `Running`, containerID definido, restartCount=0, UID exclusivo e `app.kubernetes.io/part-of` do namespace. São verificações pré-snapshot; não constituem medida de desempenho nem prova de ausência de interferência externa.

## 3. Cópia e verificação das evidências

`benchmark/backup_integrity.py` implementa:
- `verify_zip_bytes(path)`: teste de CRC e comparação dos SHA-256 de membros declarados em `checksums.sha256`, **independentemente de PASS/FAIL funcional**, preservando também tentativas incompletas;
- `compare_backup_pair(primary, backup)`: rejeita mesmo arquivo, symlink, mesma pasta, byte/tamanho/checksum divergente; indica `different_filesystem_volume` via `st_dev`; sempre `commands=[]`, `delete_authorized=false`.
- `python -m benchmark.backup_integrity --primary <caminho> --backup <caminho>` apenas **verifica arquivos existentes**, não cria cópia, não move ou apaga. O operador deverá realizar a cópia por procedimento separado, com destino externo informado e pré-verificado, usando nome exclusivo e sem sobrescrever evidências anteriores. A cópia ainda **NÃO existe** nesta fase, pois a campanha M01 não começou.

**Cautela:** outro volume de filesystem NÃO comprova que os bytes residem em outro hardware físico; o campo `independent_physical_device_verified` permanece `false`. Um backup na mesma unidade poderá comprovar integridade dos bytes, mas não será aceito como backup em volume distinto para formar o pacote documental de revisão. Manter histórico completo de cópias e integridade.

## 4. Critério de revisão e bloqueio de limpeza

Após futura tentativa `FUNCTIONAL_PASS`, o fluxo documental proposto é:
1. Garantir que o ZIP da bancada nova está íntegro via `audit_archive`, incluindo todos os gates e `ownership-start.json`.
2. Confirmar `run_id`, labels de campanha, IDs/UIDs, identidade de imagem/topologia e ausência de recursos históricos como destinatários.
3. Confirmar uma **cópia de ZIP em volume distinto**, com SHA-256, CRC e membros íntegros e sem sobrescrita.
4. `review_retirement_packet` retorna `REVIEW_ONLY_EVIDENCE_CONSOLIDATED` e IDs imutáveis para revisão humana; **sempre `commands=[]` e `delete_authorized=false`**, ainda exige teste sacrificial separado e aceite explícito do operador antes de implementar eventual encerramento de **recursos novos**.

Falhas funcionais ou pré-voos interrompidos **também devem ter seus ZIPs/bytes/logs preservados**, embora `audit_archive` não conceda status elegível para revisão de aposentadoria. Não executar cleanup por causa de pressão de RAM; a ausência de procedimento seguro exige STOP da campanha, não remoção improvisada.

NUNCA usar `docker system prune`, `docker container prune`, `docker rm` genérico, `kubectl delete namespace` genérico, `kind delete` ou reiniciar/desativar bancadas `p...`, `tcc2-v03/v05/v06`, `tcc2-c2`, `tcc2-pon`, `tcc2-pon-c4`. As novas labels `m...` não representam autorização para uma dessas ações.

## 5. Testes e gates

Nesta revisão foram escritos **8 testes `OwnershipTests`**, **5 `BackupIntegrityTests`** e **2 novos `LifecycleAuditTests`**; total esperado **96 testes** (81 PASS antes destas mudanças + 15 novos), **ainda não executados no Windows**. Eles cobrem rejeição de IDs históricos/labels erradas/UIDs duplicados, YAML `m...`, preservação do render de pilotos `p...`, cópia ausente/divergente/CRC/SHA inválido, backup no mesmo volume, e revisão que sempre devolve `delete_authorized=false`.

**Gates para avançar:** `git pull --ff-only`, `compileall` e `unittest` do SHA atual; inspeção da renderização dos manifestos novos M01 **sem `kubectl apply`**, preservando o oráculo; revisão de mecanismos de provenance em ambiente sacrificial antes de qualquer snapshot/POST; margem do Windows `>=3 GiB` e disco `>=15 GiB`; quotas efetivas da bancada **nova** `500m/256Mi/128Mi/swap=0`; política de encerramento seguro de novos recursos submetida a teste e aceite antes de iniciar 30 lotes.

**Decisão atual:** `DESIGN_FROZEN / M00D_IMPLEMENTED_NOT_TESTED / M01_BLOCKED`. Esta entrega não executou testes no computador do acadêmico, Docker/Kubernetes, snapshot, POST, benchmark, cleanup ou qualquer mutação de bancadas históricas.
