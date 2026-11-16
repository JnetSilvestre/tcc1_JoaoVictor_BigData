# TCC2 — E11-M00C — Evidência Windows de RAM física, RAM disponível e disco C:

**Data documental:** 16/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fonte:** transcrição textual enviada pelo acadêmico nesta conversa, proveniente de `Get-CimInstance Win32_ComputerSystem`, `Get-CimInstance Win32_OperatingSystem` e `Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"`, seguida de formatação em GiB. Não foram fornecidos log bruto/checksum nem timestamp embutido na medição. **Registro exclusivamente documental.**

## 1. Medições reportadas

| Campo PowerShell | Resultado reportado | Interpretação |
|---|---:|---|
| `RAM_HOST_TOTAL_GiB` | `15,84` | RAM física total do Windows |
| `RAM_HOST_LIVRE_GiB` | `2,73` | Memória física livre/disponível reportada pelo SO no instante da consulta |
| `DISCO_C_TOTAL_GiB` | `930,59` | Capacidade do volume lógico C: |
| `DISCO_C_LIVRE_GiB` | `65,03` | Espaço livre do volume lógico C: no instante da consulta |

Razão aritmética aproximada de RAM disponível/total = **17,2%**; disco livre/total = **7,0%**. Os valores têm duas casas decimais, portanto as porcentagens são aproximações. Não interpretar como média, pico, série temporal ou estado garantido na futura execução.

## 2. Confronto com inventário previamente comprovado

O `docker info` anterior anunciou **`MemTotal=8245637120` bytes (~7,68 GiB)** para o daemon em `desktop-linux`, com cgroup v2, 8 CPUs. Cada node kind anunciou `8052380Ki` e CPU allocatable `8`, mas ambos pertencem ao **mesmo host WSL2/Docker**: não somar como dois recursos físicos independentes.

Nos futuros cenários C2/C3/C4, limites nominais referenciados são **3 serviços × 256 MiB + 1 cliente × 128 MiB = 896 MiB por bancada**, caso os quatro papéis sejam criados com essas cotas. **Isso é soma de limites configurados, não previsão de uso real ou garantia de alocação**, e não inclui Docker/WSL2/kind, serviços históricos, caches, kernel e demais processos do host.

**Risco operacional interpretativo:** com apenas 2,73 GiB de RAM física reportada livre na amostra, a pressão de memória pode interferir em variabilidade, OOM, swap/WSL2 e desempenho. A memória informada pelo daemon não corresponde à RAM física livre do Windows. É necessário observar condições por bloco; não há base para declarar `INSUFFICIENT` nem `CAPACITY_APPROVED` apenas com essa amostra.

**Disco:** 65,03 GiB livres são um valor observável, mas ainda não existe orçamento real de armazenamento para 30 ZIPs, volumes Docker, logs e eventuais blocos substitutivos; não presumir capacidade aprovada por esse número isolado.

## 3. Gate e procedimento antes de M01

- **PASS:** inventário de RAM física total, RAM física livre pontual e disco total/livre reportado.
- **PENDING:** uso e pressão atuais do Docker/WSL2/host, uso/limites reais dos contêineres relevantes, espaço ocupado por evidências, quota e swap efetivos; política de limiar de parada por memória/disco; GETs uniformes, metadados/backup e aprovação do protocolo E11-M00-v1.
- **Recomendação operacional para congelamento:** somente **um cenário ativo por vez** na série definitiva, preservando todos os recursos históricos; registrar RAM Windows livre e uso do Docker/WSL2 imediatamente antes e depois de cada bloco. Se houver pressão instável, falha de disponibilidade, OOM/restarts ou swap excessivo observado, `STOP` com evidência; não alterar quotas ou excluir recursos históricos como medida corretiva ad hoc.
- Não há evidência de 30 execuções, testes de desempenho adicionais, nova medição de CPU/RAM por lote ou consumo real de bancada nesta conversa.

**Estado:** `E11-M00-v1-CANDIDATE / BLOCKED_FOR_M01`. Nenhum comando mutante executado para este registro.
