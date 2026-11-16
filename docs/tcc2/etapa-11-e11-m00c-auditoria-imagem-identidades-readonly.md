# TCC2 — E11-M00C — Auditoria somente leitura: imagem, identidades inéditas e allocatable

**Registro:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fonte primária:** captura de tela de PowerShell fornecida pelo acadêmico (não log original com SHA-256 próprio).  
**Escopo:** confrontar controles remanescentes do protocolo `E11-M00-v1-CANDIDATE` sem qualquer execução experimental.

## 1. Evidência observável na captura

- `git pull --ff-only origin tcc2/desenvolvimento`: fast-forward de `707d456` para `5365ee4`, reportado sem conflitos.
- `git rev-parse HEAD`: **`5365ee4f13ffe76608f27b6e8edbaa6a501f6adf`**.
- `docker image inspect tcc2-pon:c2-e08-dbefcd2cf3d2 --format '{{.Id}}'`: **`sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`**, idêntico ao ID de imagem aprovado/documentado no C2 e pilotos E11.
- Consultas `docker network ls`, `docker ps -a`, `kubectl --context kind-tcc2-pon get namespaces` alimentaram tabela de quatro verificações. Todas as saídas booleanas exibidas foram **False**:
  - `RedeC2JaExiste = False`, nome `tcc2-pon-e11-c2-m01-b01`;
  - `ContainerC2JaExiste = False`, prefixo `tcc2-pon-e11-c2-m01-b01-*`;
  - `NamespaceC3JaExiste = False`, `tcc2-pon-e11-c3-m01-b01`;
  - `NamespaceC4JaExiste = False`, `tcc2-pon-e11-c4-m01-b01`.
- `kubectl ... get nodes -o custom-columns=...`:
  - `tcc2-pon-control-plane`: `CPU_ALLOC=8`, `MEM_ALLOC=8052380Ki`;
  - `tcc2-pon-worker`: `CPU_ALLOC=8`, `MEM_ALLOC=8052380Ki`.
- A captura termina em prompt, sem linhas retornadas pelo `git status --porcelain`, o que **é consistente com árvore de trabalho limpa**. A ausência de mensagens de erro das consultas é evidência favorável, mas o bloco não checou individualmente todos os exit codes de `docker network ls` e `docker ps -a`.
- Os comandos `Get-CimInstance Win32_ComputerSystem` e `Get-PSDrive C` aparecem digitados, porém **NÃO é visível qualquer objeto ou valor `RAMHostGiB` ou `LivreGiB` no resultado capturado**. Logo, não declarar RAM física ou disco livre verificados.

## 2. Interpretação técnica rigorosa

1. `IMAGE_SHA_MATCH_PASS`: identidade da imagem candidata ao benchmark foi verificada read-only no Docker daemon local. Isso **não** confirma que a imagem está carregada em ambos os nodes kind, nem prova quota efetiva de contêiner ainda inexistente.
2. `PROPOSED_IDENTITIES_ABSENT_PASS`: os quatro nomes verificados não existiam **no momento da consulta**. Ausência não é reserva, e outras rodadas/bancadas históricas continuam protegidas; repetir preflight imediatamente antes de qualquer mutação futura.
3. `KIND_ALLOCATABLE_REPORTED`: o Kubernetes reporta 8 CPUs e 8052380Ki em **cada node virtual**. Os nodes kind compartilham o **mesmo host físico/daemon**, e os valores **NÃO devem ser somados** para inferir CPUs físicas ou RAM independente; `allocatable` não significa recursos efetivamente livres para os experimentos.
4. `HOST_RAM_DISK_UNKNOWN`: total de RAM física Windows e espaço livre da unidade C **não demonstrados** pela captura. CPU pressure, memória disponível, quotas/period e swap reais por cgroup continuam pendentes.
5. `NOT_AN_EXPERIMENT`: nenhum POST, snapshot, benchmark, `docker run`, `kubectl apply`, restart ou exclusão foi relatado nesses comandos. Este registro **não comprova** viabilidade quantitativa das 30 rodadas.

## 3. Gates atualizados para E11-M00C

| Gate | Situação |
|---|---|
| Fixture SHA/oráculo e três PLAN_ONLY | `PASS` (auditoria M00C precedente) |
| Compileall + 48/48 testes novos/legados | `PASS` (auditoria M00B precedente) |
| Docker image ID local aprovado | `PASS` |
| Rede, contêineres e namespaces planejados ausentes | `PASS_AT_OBSERVATION` |
| Nodes kind Ready / CPU_MEM allocatable informados | `PASS_INVENTORY`, não capacidade livre |
| RAM física Windows e espaço livre em C | `NOT_OBSERVED` |
| Quotas reais, memória efetivamente livre, concorrência host | `PENDING` |
| GETs finais homogêneos, preservação `environment.json` | `PENDING` |
| Política de reposição, critérios de interrupção e versão congelada | `CANDIDATE_UNFROZEN` |
| CPU/RAM comparativas | `NOT_APPROVED` |
| Iniciar E11-M01 | `NOT_AUTHORIZED` |

**Próximo controle seguro:** usar comandos Windows `Get-CimInstance`, `Get-PSDrive`, `Get-Counter` ou equivalentes com saída textual explícita e tratamento de erros, registrar memória livre e disco. Comparar limites efetivos apenas em bancadas novas futuras, por leitura de cgroup e validação pré-POST. A preparação de `environment.json` e a política de GETs devem preceder o congelamento. Não executar comandos mutantes nesta fase.

**Integridade:** análise de screenshot + documentação GitHub; sem execução Docker/Kubernetes pelo assistente nem alteração de bancadas históricas. Estado final deste laudo: `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`.
