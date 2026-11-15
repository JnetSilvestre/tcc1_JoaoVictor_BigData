# TCC2 — Etapa 09 / C3 — checkpoint de implantação

**Data:** 15/11/2026. **Branch:** `tcc2/desenvolvimento`. **Status:** E09-D01 aceito com base na saida textual PowerShell fornecida pelo academico; E09-I01 aprovado no Windows por dry-run (8 recursos, retorno 0); E09-I02 aprovado no Windows pela implantacao real (3 Deployments/Pods/Services). E09-I03 ainda pendente. `master`, codigo de execucao e imagem Docker C2 nao foram modificados por este incremento.

## 1. E09-D01 — diagnostico somente leitura: resultado real informado

- Git: branch `tcc2/desenvolvimento`, SHA `2ea999a712032b2bf295362264e6a5a204b9986f`, sem linhas no `git status --short`.
- Docker: contexto `desktop-linux`, Linux, 8 CPUs logicas, `8245637120` bytes de memoria configurada, Engine `29.9.3`.
- Ferramentas: kind `v0.33.0`; kubectl client `v1.36.1`; cluster `tcc2-pon` e contexto `kind-tcc2-pon`.
- Imagem aprovada C2: tag `tcc2-pon:c2-e08-dbefcd2cf3d2`; ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`; `linux/amd64`; revisao OCI `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Dois nos Ready Kubernetes `v1.37.0`: `tcc2-pon-control-plane` e `tcc2-pon-worker`, ambos executados virtualmente sob Docker/WSL2 no mesmo computador fisico.
- Pods `kube-system` e `local-path-storage` observados em `Running` e `READY 1/1`. Alguns registraram reinicios anteriores, sem falha atual observada.
- Namespace `tcc2-pon` ausente; nenhum recurso C3 implantado.
- Requests informados pelo `describe nodes`: control-plane CPU 950m, memoria 290Mi; worker CPU 100m, memoria 50Mi. Memoria/CPU `allocatable` por no sao valores virtuais e **nao devem ser somados como hosts independentes**.
- `kubectl top nodes` retornou `Metrics API not available`; NAO ha amostras de uso de CPU/RAM obtidas por essa API.

**Limite:** texto enviado na conversa e registro GitHub, sem arquivo bruto de sessao ou comprovacao de medições de desempenho. Nenhuma execucao de Kubernetes da aplicacao ocorreu em E09-D01.

## 2. E09-I01 — configuracao planejada

Arquivo: `infraestrutura/kubernetes/c3/manifests.yaml` (oito documentos YAML):
1. Namespace `tcc2-pon`.
2. ConfigMap com os nomes DNS internos para o fluxo.
3. Deployments de `rule-executor`, `logic-engine` e `attribute-source`, uma replica por papel, imagem C2 identica, porta TCP 8080, sem alterar o nucleo Python.
4. Services ClusterIP para cada papel, com DNS pelo nome no namespace.

**Probes:** `GET /health/live` para liveness e readiness de transporte; o endpoint da aplicacao `GET /health/ready` retorna 503 antes do snapshot. Usar este ultimo como readiness do Pod bloquearia os endpoints de Service necessarios para propagar o snapshot. A verificacao funcional de `/health/ready` deve ser feita apos `POST /init/snapshot` autorizado na fase propria.

**Recursos provisórios por Deployment:** requests 100m CPU / 128Mi RAM; limits 500m CPU / 256Mi RAM. Sao valores iniciais de funcionamento, nao resultados medidos nem parametros definitivos do benchmark. Tres replicas totais = 300m/384Mi requests e 1500m/768Mi limits; todos compartilham hardware local.

**Imagem:** `imagePullPolicy: Never`; antes da implantacao, carregar a imagem aprovada no kind (nao fazer build nem publicar imagem em registro remoto). Se a importacao falhar, diagnosticar sem remover imagens ou contêineres anteriores.

**Agendamento:** nenhuma afinidade multinó imposta na prova minima C3. Posicionamento em nos distintos (C4/V09) sera provado separadamente, conforme topologia real, nunca confundido com distribuicao fisica entre maquinas. Nao aumentar replicas de papeis com estado.

## 3. Verificacao E09-I01 no Windows (somente leitura/dry-run)

Executar no PowerShell na raiz local do repositorio:

```powershell
git branch --show-current
git pull --ff-only
git rev-parse HEAD
$manifest = "infraestrutura/kubernetes/c3/manifests.yaml"
kubectl --context kind-tcc2-pon apply --dry-run=client -f $manifest
Write-Host "DRY_RUN_EXIT:" $LASTEXITCODE
git status --short
```

Apenas apos apresentar a saida e confirmar **dry-run 0**, considerar E09-I01 validado. `--dry-run=client` nao persiste recursos; nao executar `kubectl apply` real nesta fase. Nao usar `--dry-run=server` com Namespace + recursos dependentes no mesmo arquivo quando o Namespace ainda nao existe, porque a simulacao do Namespace nao o persiste.

## 4. Pendencias e proximo incremento

- **E09-I01 pendente** de verificacao real do YAML no PowerShell.
- **E09-I02:** confirmar imagem no Docker e carregar a imagem exata nos nos do cluster `kind`; em seguida implantar os oito recursos e verificar Deployments/Pods/Services com saida real.
- **E09-I03:** DNS HTTP/JSON, saude e snapshot inicial com `run_id` exclusivo de C3, sem reutilizar fixtures/POSTs das bancadas C2.
- **E09-I04:** fixture minima, oraculo, causalidade, identidades de Pods/containers/nos e logs/hashes; V02/V04/V08/V11 conforme evidencias. V07, V09, V10, V12 com status separado conforme testes executados.
- Preservar C2 V05/V06, ZIPs e hashes; nao reconstruir imagem, nao executar `docker prune` ou `kind delete`.

**Aprovacao nesta publicacao:** somente arquivo de configuracao criado; nenhuma afirmacao de que o cluster executou C3, nem de teste ou benchmark concluido.


## 5. Evidencia posterior — E09-I01 e E09-I02 aprovados (15/11/2026)

**E09-I01 (Windows):** `Test-Path` confirmou arquivo YAML; `kubectl --context kind-tcc2-pon apply --dry-run=client -f infraestrutura/kubernetes/c3/manifests.yaml` reconheceu os oito recursos (Namespace, ConfigMap, tres Deployments e tres Services), `DRY_RUN_EXIT: 0`. O primeiro erro de caminho relativo foi corrigido usando `git rev-parse --show-cdup`, evitando alteracao indevida da raiz com caracteres acentuados; foi falha de invocacao, nao sintaxe de YAML.

**E09-I02 (Windows):** preflight validou imagem Docker C2 `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`; `kind load docker-image` carregou a mesma imagem para `tcc2-pon-control-plane` e `tcc2-pon-worker`; `kubectl apply` criou os 8 recursos; `rollout status` terminou com sucesso para os tres Deployments; `kubectl get deploy,pods,svc -o wide` mostrou 3/3 Deployments `1/1`, tres Pods `Running 1/1` `RESTARTS=0`, tres Services `ClusterIP` porta 8080. A captura enviada foi texto do PowerShell, nao screenshot nem pacote bruto versionado.

**Posicionamento observado (E09-I02):**

| Papel | Nome observado do Pod | Pod IP | Node |
|---|---|---|---|
| attribute-source | `attribute-source-84ff976f49-z6v7b` | `10.244.1.2` | `tcc2-pon-worker` |
| logic-engine | `logic-engine-fcc5cc476-hr2ww` | `10.244.1.4` | `tcc2-pon-worker` |
| rule-executor | `rule-executor-fdd69799c-kz2k2` | `10.244.1.3` | `tcc2-pon-worker` |

V08 **parcial:** recursos implantados e Deployments disponiveis, mas transporte HTTP e fixture ainda nao comprovados. V09 **nao demonstrado:** todos os Pods da aplicacao no mesmo no virtual worker; nao ha distribuicao desta aplicacao entre nos e, em nenhuma hipotese, entre hosts fisicos. A readiness do Kubernetes consulta `/health/live`, nao significa `/health/ready` funcional (snapshot ainda nao enviado). Sem V12/benchmark.

**Proximo E09-I03:** preflight HTTP sem mutacao nos tres Services por DNS interno e inspeção do estado frio; somente se aprovados, um POST exclusivo de snapshot C3, seguido de leitura e registro dos tres estados. Nao repetir POST em caso de interrupcao; diagnosticar pelos estados/logs. Preservar C2, `master`, fonte e imagem.
