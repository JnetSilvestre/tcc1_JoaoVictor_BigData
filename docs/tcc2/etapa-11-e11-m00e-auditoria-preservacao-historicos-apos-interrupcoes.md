# TCC2 — E11-M00E — Integridade dos recursos históricos após interrupções

**Data documental:** 17/11/2026 (America/Sao_Paulo). **Branch:** `tcc2/desenvolvimento`.  
**Fonte:** saída textual fornecida pelo acadêmico para os comandos somente leitura `docker ps -a`, `docker network ls`, `kubectl --context kind-tcc2-pon get namespaces`, `kubectl --context kind-tcc2-pon get pods -A -o wide`. Não foram entregues logs do Docker daemon, eventos Kubernetes ou arquivo de saída assinado.  
**Estado:** `HISTORICAL_RESOURCES_PRESENT_BUT_RUNTIME_CHANGED / ROOT_CAUSE_UNCONFIRMED / M01_BLOCKED`.

## 1. Docker: contêineres e redes

A listagem `docker ps -a` contém **20 contêineres históricos de aplicação/cliente**, todos com **`Exited (137) 27 hours ago`** no instante da consulta:

- oito contêineres dos dois pilotos C2: `tcc2-pon-e11-c2-p20261115-232946-*` (4) e `tcc2-pon-e11-c2-p20261115-225314-*` (4);
- três contêineres para cada família `tcc2-v06`, `tcc2-v05`, `tcc2-v03` e `tcc2-c2` (12).

Os nomes e IDs abreviados permanecem listados. Isso **não prova estado anterior intacto**, mas contraria a hipótese de que os 20 contêineres tenham sido removidos. Existe ainda `tcc2-python-validacao` **`Exited (0)`**, não confundido com os 20. Os dois contêineres kind aparecem **`Up 3 hours`** (dados relativos ao instante da consulta), sem prova causal de reinicialização específica.

As redes particulares `tcc2-pon-c2`, `tcc2-pon-c2-v03`, `tcc2-pon-c2-v05`, `tcc2-pon-c2-v06`, `tcc2-pon-e11-c2-p20261115-225314` e `tcc2-pon-e11-c2-p20261115-232946` estão listadas, além de `bridge`, `host`, `kind` e `none`.

**Código 137:** indica término de processo normalmente associado a `SIGKILL` (128+9), mas **não identifica por si só OOM**; também pode resultar de parada forçada de serviço/daemon ou interrupção do ambiente. Sem `State.OOMKilled`, `State.FinishedAt`, eventos e logs, **não atribuir a causa à memória**.

## 2. Kubernetes: histórico preservado em objetos, não em continuidade de processos

Constam namespaces `tcc2-pon`, `tcc2-pon-c4`, dois pilotos C3 (`tcc2-pon-e11-c3-p20261115-213740`, `tcc2-pon-e11-c3-p20261115-235728`) e dois pilotos C4 (`tcc2-pon-e11-c4-p20261115-220023`, `tcc2-pon-e11-c4-p20261116-001328`), todos `Active`.

- Nos quatro namespaces de pilotos C3/C4, os serviços de aplicação listados estão `Running` e `1/1`, com **`RESTARTS=1`**, última reinicialização indicada como aproximadamente 3h3m antes da saída.
- Nos namespaces históricos `tcc2-pon` e `tcc2-pon-c4`, os três serviços também apresentam **`RESTARTS=1`**.
- Todos os quatro Pods `e11-benchmark-client` dos pilotos aparecem como **`0/1 Unknown`**, e não como cliente em execução saudável; não assumir prontidão da bancada original.
- Em `kube-system`, vários Pods do plano de controle/rede mostram reinicializações (p.ex. CoreDNS 4, kindnet 4, kube-controller-manager 4). `etcd` e `kube-apiserver` apresentam `AGE` aproximado 3h3m; a saída não comprova causa única ou sequência exata dos eventos.
- Os dois nós kind `Ready` de consulta anterior ainda são capazes de responder ao API server. **Isso não restaura o estado original das aplicações nem valida automaticamente a conservação de estados em memória dos pilotos.**

## 3. Impacto experimental e decisão

- **Evidências documentais já coletadas:** os resultados pilotos previamente arquivados não são automaticamente invalidados pelo estado atual; seus artefatos e checksums devem ser preservados e avaliados pelos próprios critérios que regiam a coleta. Não repetir medições nos contêineres/Pods históricos nem declarar continuidade sem evidências.
- **Runtime histórico:** estado atual **diverge do estado dos pilotos**. É incorreto descrever 20 contêineres históricos como ainda ativos; estão parados. É igualmente incorreto descrever os históricos Kubernetes como sem reinicialização.
- **Nova campanha:** o desenho E11-M00-v1 mantém 30 rodadas apenas em bancadas novas `m...`, após validação sacrificial autorizada. A observação de interrupções históricas demanda (i) diagnóstico não mutante de causa, (ii) novo inventário de baseline e concorrência, (iii) atenção a reinício de Docker/kind, e (iv) manutenção de registros explícitos de estabilidade/restarts por rodada. Não misturar implicitamente pilos antigos com novos como se fossem a mesma época de host.
- **Sem remoção/restart/limpeza** dos históricos, mesmo se `Exited` ou `Unknown`. Não usar `docker start`, `docker rm`, `docker prune`, `kubectl delete` ou `kubectl rollout restart` para esta auditoria.

## 4. Próximo diagnóstico de baixo risco, somente leitura

Confirmar `State.OOMKilled`, `State.ExitCode`, `State.FinishedAt`, `State.Error` de cada um dos 20 contêineres históricos com `docker inspect` (não usar `docker start`). Consultar `lastState.terminated.reason`, `restartCount` e `phase` dos Pods históricos via `kubectl get pods -A -o json` (não usar `kubectl exec` nos históricos). Eventuais logs de daemon e WSL2, se disponíveis, poderão reforçar ou refutar hipóteses, mas não reescrever evidências antigas.

**Gate:** `E11_M00E_HISTORICAL_RUNTIME_AUDIT_REQUIRED`, `E11_M01_BLOCKED`. O precheck de capacidade do Windows foi `PASS` (8,81 GiB RAM livre, 67,43 GiB disco) com os nodes kind ativos, porém **não prova segurança das novas bancadas nem causa dos códigos 137**.

**Integridade:** documento de análise de saída fornecida pelo acadêmico. Não foi executada mutação Docker/Kubernetes, novo experimento, snapshot, POST, cleanup ou intervenção sobre históricos pelo assistente.
