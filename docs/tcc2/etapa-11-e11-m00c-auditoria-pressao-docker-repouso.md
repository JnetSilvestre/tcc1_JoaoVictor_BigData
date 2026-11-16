# TCC2 — E11-M00C — Auditoria de pressão em repouso: Docker, Windows e retenção

**Registro documental:** 16/11/2026 (America/Sao_Paulo); **branch:** `tcc2/desenvolvimento`.  
**Fonte primária:** transcrição de saída PowerShell enviada pelo acadêmico após consultas read-only `Get-CimInstance`, `docker stats --no-stream` e `docker system df`. Não há log original com SHA-256 nem carimbo UTC diretamente na transcrição. **Não se trata de execução experimental nova.**

## 1. Evidência literal relevante

- `RAM_WINDOWS_LIVRE_GiB=2,42`: memória livre instantânea reportada pelo Windows. Total físico previamente observado = 15,84 GiB; fração calculada aproximada = **15,3%**. A consulta anterior indicou 2,73 GiB em outro instante; não inferir tendência temporal nem causa dessa diferença a partir de dois pontos.
- `docker stats --no-stream`: **22 contêineres listados** como ativos, incluindo 2 contêineres de nós kind e 20 contêineres históricos da aplicação/cliente (2 pilotos C2 com 4 contêineres cada, e 4 trios históricos = 12).
- Nós kind: `tcc2-pon-control-plane` **870,2 MiB / 7,679 GiB**, CPU **14,30%**; `tcc2-pon-worker` **930,4 MiB / 7,679 GiB**, CPU **7,37%**. Soma aritmética dos dois valores `MEM USAGE` = 1.800,6 MiB (~1,76 GiB), **não significa 1,76 GiB exclusivos da infraestrutura kind** e não pode ser somada diretamente à memória física consumida no Windows ou confundida com pico/média de CPU.
- As duas bancadas piloto C2 continham `attribute-source`, `logic-engine`, `rule-executor` e `benchmark-client`. Os outros grupos históricos estavam identificados como `tcc2-v03`, `tcc2-v05`, `tcc2-v06`, `tcc2-c2`; os valores `MEM USAGE` não equivalem a consumo de um bloco futuro.
- `docker system df` reportou:
  - imagens: total 10, ativo 3, tamanho **3,859 GB**, `RECLAIMABLE=2,147 GB (55%)`;
  - contêineres: total **23**, ativos **22**, tamanho gravável **4,78 MB**, recuperável **524,3 kB (10%)**;
  - volumes locais: total **4**, ativos **2**, tamanho **2,564 GB**, recuperável **212 MB (8%)**;
  - build cache: 65 objetos, 0 ativos, **3,027 GB**, recuperável **1,374 GB**.
- O disco C: anteriormente tinha **65,03 GiB livres**; não houve nova consulta ao disco C no bloco `docker system df`. Tamanho da camada Docker não equivale à ocupação total de C: ou ao orçamento dos futuros ZIPs.

**Sem comandos mutantes:** a transcrição não contém `docker prune`, `docker rm`, `docker stop`, `kubectl apply/delete`, POST, snapshot ou benchmark.

## 2. Análise do risco experimental e não inferências

**Risco identificado:** 22 contêineres já ativos + 2,42 GiB de RAM física livre no instante da consulta. CPU dos nós kind não estava literalmente em 0% durante o instantâneo (14,30% e 7,37%), o que pode ser atividade transitória; não inferir pressão CPU sustentada sem série de controle. Os recursos históricos devem continuar intactos e podem ser fonte de atividade concorrente não controlada.

Os novos cenários usam limites nominais por bancada de **896 MiB** (3 serviços × 256 MiB e 1 cliente × 128 MiB). Este é **teto nominal agregado, não demanda observada**. Protocolo futuro não pode acumular indiscriminadamente 30 bancadas ativas, pois a série alteraria progressivamente a ocupação do host e sua comparabilidade temporal. Memória e CPU dos nós virtuais não equivalem a hardware independente.

**Nunca interpretar `RECLAIMABLE` como autorização para `docker system prune`, exclusão de volumes, imagens ou recursos antigos.** Quaisquer artefatos históricos permanecem protegidos, inclusive namespaces/Pods Kubernetes e imagens.

## 3. Proposta de ciclo de vida antes do congelamento E11-M00-v1

1. **Um cenário novo por vez**, sempre em identificadores `m...` inéditos, com consulta de existência imediatamente antes da criação e confirmação de inexistência do recurso; os nomes usados em PLAN_ONLY ainda não foram reservados.
2. Após cada nova execução futura, **preservar evidências primeiro**: manifest, hashes da fixture e rebased, snapshots/estados, logs/HTTP/oráculo/validação, metadados do host fora da janela do lote e arquivo ZIP com SHA-256/CRC; registrar `PASS`/falhas e conferir a integridade externa ao diretório/volume que seria descartado.
3. **Nenhuma remoção automática nesta revisão.** Preparar na fase seguinte mecanismo com allowlist positiva e verificações de identidade (nome completo, Docker ID ou namespace UID), ownership da rodada M01, ausência de pertencimento histórico, estado já arquivado, destino seguro do ZIP e aceite explícito. Se não houver solução auditável, **STOP por capacidade** em vez de acumular bancadas e alterar condições experimentais.
4. A eventual finalização/remoção de **somente uma bancada nova** após arquivamento pode tornar a campanha sustentável; essa política deverá ser aprovada **antes da primeira execução** e nunca alcançar `tcc2-pon`, `tcc2-pon-c4`, quaisquer `p...`, `tcc2-v03/v05/v06`, `tcc2-c2`, imagens ou volumes históricos.
5. Congelar prospectivamente pontos de controle de RAM Windows/WSL2, espaço livre em C e memória/CPU de nós kind fora do lote; critérios objetivos de `STOP` (OOM/restarts, host com pressão relevante, artefatos sem integridade, quota divergente) e calendário de blocos. Sem limite de recursos auditado, não declarar o experimento pronto.
6. A política v1 para CPU/RAM comparativas continua **`NOT_APPROVED`**; o instantâneo `docker stats` de repouso é inventário de capacidade, não mensuração da carga.
 
## 4. Situação de gates

| Gate | Estado após este laudo |
|---|---|
| 48 testes sintéticos e três PLAN_ONLY | `PASS` (laudos anteriores) |
| Identidade Docker/IDs planejados | `PASS_AT_OBSERVATION` (laudo anterior) |
| Memória física e disco Windows | `INVENTORY_PASS` (leituras pontuais) |
| Snapshot de pressão Docker/host | `READ_ONLY_BASELINE_RECORDED` |
| Recursos efetivamente disponíveis durante M01 | `NOT_VERIFIED` |
| Política de retenção/remoção restrita a recursos novos | `PROPOSED_NOT_APPROVED` |
| Preflight uniforme, environment.json e backup | `PENDING` |
| Protocolo E11-M00-v1 congelado | `NO` |
| E11-M01 | **`BLOCKED`** |

**Integridade:** registro documental; sem teste, snapshot, POST, apply, limpeza, exclusão ou alteração dos históricos. Não prometer medição futura ou trabalho em segundo plano.
