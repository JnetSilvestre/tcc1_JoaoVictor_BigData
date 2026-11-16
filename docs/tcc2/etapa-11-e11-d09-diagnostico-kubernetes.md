# TCC2 — Etapa 11 | E11-D09 — Diagnóstico SOMENTE LEITURA Kubernetes C3/C4, carga 1.000

**Situação:** código publicado para execução e auditoria no Windows. **Nenhum** Pod, Namespace, ConfigMap, Deployment, Service, snapshot, POST, benchmark ou alteração de configuração foi executado durante a preparação deste procedimento.

## Objetivo

Preparar dois manifests NOVOS para C3 e C4, ambos com a fixture canônica E11 de 1.000 requisições, validar o oráculo e a identificação de cada namespace, confirmar presença dos namespaces funcionais históricos `tcc2-pon` e `tcc2-pon-c4`, Ready dos nós `tcc2-pon-worker` e `tcc2-pon-control-plane`, imagem Docker aprovada e Kubelet Summary API em ambos os nós.

## Segurança

- Módulo: `python -m benchmark.kube_preflight --label <novo> --fixture <fixture1000> --output <nova pasta> [--probe]`.
- Sem `--probe`: valida fixture e YAML e prepara dados somente no diretório local; `PLAN_ONLY`. Com `--probe`: adicionalmente executa **exclusivamente consultas GET** Kubernetes e Docker, usando o contexto `kind-tcc2-pon`, e duas leituras `/api/v1/nodes/{node}/proxy/stats/summary` por nó. Não executa `kubectl apply`, `create`, `exec`, `delete`, `rollout`, reinício, nem POST à aplicação.
- O namespace planejado deve estar ausente da listagem real do cluster; o script exige existência dos namespaces antigos e nós Ready. YAML gerado termina em `-NOT-APPLIED.yaml`. Os IDs C3 e C4 são diferentes, embora compartilhem a semente/fixture canônica.
- Não reutilizar `tcc2-pon`, `tcc2-pon-c4`, `tcc2-pon-e11-c3-p20261115-213740`, `tcc2-pon-e11-c4-p20261115-220023` ou `tcc2-pon-e11-c2-p20261115-225314` / `p20261115-232946`.

## Critérios

- Fixture `inputs.jsonl` seed 20260502, 1000 linhas, SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; `expected.jsonl` SHA-256 `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`.
- Composição de carga: **874 mudanças efetivas**, **126 no-ops**, **500 transições de condição**, **250 efeitos**; estado final esperado `atA=10,atB=0`.
- A verificação de manifestos é **estática**: confere namespace isolado, imagem e componente cliente; não é admissão Kubernetes nem garantia de agendamento. Manifests C3/C4 preservam código/limites/tolerations originais, sem adaptação a resultados exploratórios.
- Kubelet Summary API: dados de Pods históricos apenas permitem confirmar disponibilidade e observar se timestamp CPU avança entre 2 coletas. `PASS_READ_ONLY` = acesso + amostras distintas em ambos nós; `PASS_READ_ONLY_WITH_TIMESTAMP_WARNING` = API acessível mas pelo menos um nó sem avanço de timestamp. **Ambos NÃO aprovam métricas do lote** e NÃO liberam automaticamente execução de carga.
- O teste da API não inspeciona os novos Pods, porque os namespaces planejados **não foram criados**. Na execução posterior, a identidade do Pod e do contêiner precisará ser auditada novamente; a cobertura de CPU sob carga poderá ainda falhar.

## Saídas

Um diretório exclusivo `resultados-locais/e11-d09-<timestamp>` com `canonical-inputs.jsonl`, `canonical-expected.jsonl`, `c3-manifest-NOT-APPLIED.yaml`, `c4-manifest-NOT-APPLIED.yaml`, `e11-d09-report.json`, `checksums.sha256` e ZIP. No modo `--probe`, também registra dois snapshots condensados por nó, metadados de readiness, namespace e status da API no relatório.

## Plano posterior

1. Validar testes sintéticos E11-D09 (5 testes novos) e o ZIP somente de leitura. Auditoria humana de namespace, saúde dos nós e serialização/timestamps da Summary API.
2. Somente após aprovação: preparar os dois namespaces isolados para pilotos C3/1000 e C4/1000, UM por vez, com `--execute` limitado aos respectivos namespaces novos, preservando o estado anterior. Uma falha após snapshot/POST impede repetição no mesmo namespace.
3. Após pilotos: calibrar carga/CPU/throttling e aquecimento, congelar o desenho E11-M01 e realizar séries repetidas independentes antes da auditoria E11-A01. **Etapa 12 analisa os dados**, não substitui a série experimental.

**Observação metodológica:** todos os nós kind são contêineres no MESMO host físico; não inferir distribuição multinó em máquinas independentes. A CPU/memória da Kubelet Summary API têm significado diferente do uso bruto de memória da Docker Engine API. Não descrever amostras pré-benchmark como resultados de desempenho.
