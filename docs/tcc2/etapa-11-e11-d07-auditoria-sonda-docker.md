# TCC2 — Etapa 11 | E11-D07 — Auditoria independente da sonda Docker Engine API

**Execução local reportada:** 15/11/2026 ~23:09 America/Sao_Paulo; amostras na madrugada UTC 16/11/2026. **Natureza:** leitura SOMENTE de estatísticas de contêineres C2 já utilizados, sem nova carga, snapshot ou benchmark. **Estado:** `PASS_READ_ONLY` comprovado; calibração científica de CPU e memória DURANTE LOTES permanece **NÃO APROVADA**.

## 1. Origem e integridade dos arquivos

- Fonte primária: RAR5 bruto `e11-d07-20261115-230918.rar` anexado nesta conversa e inspecionado por leitura direta. Tamanho exato **7.223 bytes**; SHA-256 recalculado `4417bab258fa48dd09fc42e73e9d0522dd299083e948208436abed34e043d4eb`.
- Arquivo RAR contém oito entradas (6 arquivos, 2 diretórios), incluindo uma cópia ZIP sem compressão própria do RAR, `engine-probe.zip`, de **3.500 bytes**. ZIP extraído pelos offsets do item armazenado e verificado independentemente: SHA-256 `648bd8fb96384ec9495f10689522e0ca4f11a79b090ddb9e078d6ca1c11ed836`; coincide com terminal Windows. ZIP com **5 entradas** únicas, CRC 5/5 válido e **4/4 hashes SHA-256** dos arquivos de evidência correspondentes a `checksums.sha256`.
- Os oito registros de `engine-stats.jsonl` e suas colunas equivalentes em `engine-stats.csv` conferem exatamente.
- PowerShell: Git HEAD `266b5872cd0cf6c8226ec830fc884fad6c4b1750`; compilação sintática sem erros; 21/21 testes `test_benchmark*.py` aprovados (0,101 s de unittest — não é uma medição de desempenho); emissão PLAN_ONLY e execução de sonda somente de leitura. Esta verificação documental não executou código Python no Windows nem benchmarks.

## 2. Escopo instrumental verificado

- `engine-context.json`: acesso Docker via `npipe:////./pipe/dockerDesktopLinuxEngine`, Docker Engine API **1.56**; identificação de **quatro** contêineres do piloto `tcc2-pon-e11-c2-p20261115-225314` (source, logic, executor, client) por IDs distintos de 64 dígitos hexadecimais.
- `probe-report.json`: `status=PASS_READ_ONLY`, `read_only=true`, `fields_available_and_monotonic=true`, `measurement_approved=false`, `assessment.issues=[]`. Consistência entre relato, formato do coletor e oito amostras brutas confirmada.
- Amostras no intervalo aproximado de **2026-11-16 02:09:20.738–02:09:22.733 UTC**; **2 pontos por papel**, consultados sequencialmente. O tempo entre `docker_read_utc` da primeira e segunda leitura por papel é aproximadamente **1,57 s**, não uma janela de carga.
- CPU `cpu_stats.cpu_usage.total_usage` presente, não regressiva nos quatro papéis; contagens de `cpu_throttled_periods` iguais na primeira/última leitura; uso de memória bruto `memory_stats.usage` presente e limite nominal presente. Campos opcionais de rede e `inactive_file` também presentes.

## 3. Valores SOMENTE DE REPOUSO — não são resultados experimentais de lote

| Papel | CPU delta entre 2 leituras (milissegundos de CPU) | Último uso bruto de memória (MiB) |
|---|---:|---:|
| attribute-source | 0,211 | 56,383 |
| logic-engine | 0,224 | 47,547 |
| rule-executor | 0,296 | 21,211 |
| benchmark client | 0,000 | 4,254 |

Os números são descrições dos contadores durante leitura em repouso após o piloto, NÃO medidas de CPU/RAM da carga das 100 operações. O cliente constante de CPU 0 dentro da janela pode refletir o contêiner ocioso e/ou resolução da contabilidade; não significa consumo zero do cliente durante o lote anterior. A leitura dos três serviços não foi simultânea.

## 4. Aceitação e limites científicos

- **E11-D07 — APROVADO NO ESCOPO DE DISPONIBILIDADE / SOMENTE LEITURA**: a API remota local do Docker fornece estatísticas por ID de contêiner sem invocar `docker exec` dentro dos serviços; parser HTTP por named pipe funcionou no Windows real.
- `measurement_approved=false` permanece **correto**. Consultas ao daemon ainda possuem overhead de host. Delta de contador em repouso não demonstra atribuição ao lote, e o intervalo de 1,57 s não valida fronteiras nem cadência sob carga. Memória `memory_stats.usage` é uso bruto, diferente do `workingSetBytes` da Kubelet Summary API; `memory_cli_adjusted_bytes` também não constitui o mesmo conceito por definição.
- A diferença de carga entre C2, C3 e C4 não foi reavaliada nesta atividade. Não afirmar superioridade Docker ou Kubernetes, nem escalabilidade. O caso C4 ainda é multi-nó **virtual no mesmo computador físico**.
- Nenhum indício de nova mutação da aplicação consta no código da sonda/relatório; essa conclusão é de escopo do instrumento, não auditoria independente de todo o sistema operacional. Preserve a bancada `tcc2-pon-e11-c2-p20261115-225314`: não reenviar snapshot/fixture.

## 5. Decisões e próximos incrementos

1. Registrar E11-D07 `PASS_READ_ONLY` e aprovar a fonte de dados Docker Engine como candidata à instrumentação externa de C2; não aprovar ainda CPU/memória quantitativas.
2. **E11-I06 (próximo):** integrar amostras Docker Engine à janela temporal de carga em **bancada C2 nova**, guardando `docker_read_utc`, `retrieved_utc`, durações, IDs e limite; manter coleta somente externa ao serviço; validar mínimo de duração, intervalos e sobrecarga do monitor. Não adaptar nem executar dentro dos contêineres do piloto anterior.
3. Planejar diagnóstico de **1.000 requisições** em C2/C3/C4 em três bancadas novas, após pré-verificações de recursos e timeout. Ainda será um piloto, não as dez repetições definitivas.
4. Definir métrica de memória comparável entre os cenários antes de reivindicar diferenças: working set (Kubernetes) e memory usage bruto (Docker) NÃO podem ser equiparados silenciosamente.
5. Consolidar o desenho experimental e as fontes metodológicas selecionadas em `docs/tcc2/etapa-11-auditoria-seletiva-perplexity.md`, com revisão antes de V12.

**Referências dos artefatos:** ZIP bruto e arquivo RAR originais sob custódia externa; não versionados no GitHub. Nenhum arquivo experimental adicional foi fabricado.
