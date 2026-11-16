# TCC2 — Etapa 11 / E11-I05: sonda Docker Engine sem docker exec

**Situação:** código preparado e versionado, **não executado no Windows ainda**. Nenhum benchmark, snapshot, POST, criação/remoção/reinício de contêiner, Kubernetes apply ou alteração do núcleo PON foi executado nesta atividade.

## Diagnóstico e escolha

No E11-P03 C2, cgroup v2 foi lido por comandos `docker exec` dentro dos contêineres da aplicação. Esse mecanismo gera processos auxiliares nos mesmos cgroups observados e torna a coleta INTRUSIVA. O E11-I05 acrescenta `benchmark/docker_engine_api.py`, sonda **separada** que consulta somente `GET /vX.Y/containers/{id}/stats?stream=false&one-shot=true` pelo named pipe local do Docker Engine no Windows. Não instala bibliotecas, não habilita daemon TCP, não monta socket nos contêineres e não chama Docker exec/run. Tem modo `PLAN_ONLY` sem a flag `--probe`.

**Fonte técnica primária:** Docker Engine API (https://docs.docker.com/reference/api/engine/version/v1.56/ , `Get container stats based on resource usage`), e Docker Desktop FAQ (https://docs.docker.com/desktop/troubleshoot-and-support/faqs/general/ , named pipe Windows). A versão efetiva do Engine é lida via `docker version --format` no próprio ambiente e não é presumida. A sonda só aceita `npipe:////./pipe/docker_engine` ou `npipe:////./pipe/dockerDesktopLinuxEngine`; TCP, SSH ou outro endpoint são recusados.

## Medidas e limites

- CPU: `cpu_stats.cpu_usage.total_usage` é contador CUMULATIVO em nanossegundos por contêiner. Um delta entre amostras de fronteira é uma aproximação que inclui tempo fora do lote. `precpu_stats` não substitui leitura de fronteira própria.
- Memória: `memory_stats.usage` é uso bruto informado pelo Engine; **não** equivale automaticamente a `workingSetBytes` na Summary API do kubelet. `memory_stats.stats.inactive_file` permite calcular separadamente o valor aproximado ajustado da CLI (`usage - inactive_file`) em cgroup v2 quando disponível, sem rotulá-lo como RSS. `memory.peak` não está garantido no retorno da API.
- A leitura via host evita processos `docker exec` DENTRO dos serviços, mas continua consumindo CPU/IO do host/Docker daemon. Sem ensaios de overhead e sem mesmas fronteiras/definições que C3/C4, não há medida CPU/memória cientificamente aprovada.
- `--probe` opera sobre os QUATRO contêineres do C2 piloto E11-P03 já gasto `p20261115-225314`, validando nome prefixado, imagem aprovada, label `tcc2.e11=pilot`, estado Running, restartCount=0 e IDs 64hex. O worker só usa requisição GET. Amostras em repouso não são resultado de carga.
- 2 amostras sequenciais por papel por padrão. Timestamps `docker_read_utc` vêm da API, `retrieved_utc` é do Windows; não presumir sincronização perfeita ou frescor universal.
- C4 tem logic-engine no control-plane virtual; E11-I05 não altera a arquitetura nem soluciona esse fator de confusão.

## E11-D07 (executar SOMENTE diagnósticos no Windows)

Sincronizar Git em `tcc2/desenvolvimento`, verificar commit e Git limpo. Executar syntax e a suíte `test_benchmark*.py`, e `python -m benchmark.docker_engine_api --label p20261115-225314 --output resultados-locais/e11-d07-NOVO/engine-probe` sem `--probe` para PLAN_ONLY. Se a suíte for aprovada, repetir o comando **com** `--probe` em diretório *novo*, que apenas consulta estatísticas do Docker Engine sem alterar contêineres ou workloads.

Não executar `benchmark.docker_c2 --execute`, não gerar um novo snapshot, não repetir o piloto C2, nem enviar requisições à aplicação. Uma eventual falha de pipe/API deve ser investigada sem mutar o sistema.

## Evidência e aprovação

Artefatos de `--probe`: `engine-context.json`, `engine-stats.jsonl`, `engine-stats.csv`, `probe-report.json`, `checksums.sha256`, `ZIP`. PASS_READ_ONLY significa somente que contadores estavam acessíveis/monotônicos em dois instantes, **não** medição aprovada. Faltam séries de 1000, calibração de overhead, comparação de definição da memória, alinhamento CPU, repetição por blocos, aleatorização e controle da carga do host para congelar V12.

**Não inferir resultados antes da execução real.**
