# TCC2 — Etapa 08: diagnóstico e parametrização da rede Docker

**Data de abertura:** 13/11/2026. **Branch de trabalho:** `tcc2/desenvolvimento`.  
**Referência C1 comprovada:** `be6b850d599504e9ea8166f02fd87b35313e5445`.  
**HEAD inicial da Etapa 08 após sincronização:** `3dadef829846fdf5f0bcf0c47c956b44eb89d821`.  
**Estado:** E08-I01 e E08-I02 aprovados no Windows; E08-I03 (imagens Docker) ainda em preparação. Nenhum build C2 executado.

## 1. Evidências reais recebidas

- **E08-D01:** PowerShell confirma branch `tcc2/desenvolvimento`, status limpo, Python 3.13.9, pip 25.2, Git 2.45.0.windows.1; HEAD local antes da sincronização `be6b850d599504e9ea8166f02fd87b35313e5445`, remoto `3dadef829846fdf5f0bcf0c47c956b44eb89d821`.
- **E08-D02:** Docker Desktop 4.99.0, Engine 29.9.3, contexto `desktop-linux`, 8 CPUs lógicas, 8.245.645.312 bytes configurados; WSL2 ativo; contêineres do kind preservados; `tcc2-python-validacao` parado com Exit 0; cluster `tcc2-pon` existente. Nenhuma limpeza executada.
- **E08-D03:** `git pull --ff-only` concluiu, apenas sete arquivos documentais diferiam desde C1; HEAD `3dadef829846fdf5f0bcf0c47c956b44eb89d821`; `compileall` exit 0; `unittest` **Ran 39 tests in 10.813s, OK, Testes: 0**; Git final limpo. A duração é da suíte, **não benchmark PON**.

## 2. Arquivos originais das capturas e hashes SHA-256

Os hashes abaixo foram calculados sobre os bytes dos PNGs recebidos nesta conversa. Os originais **não foram arquivados neste repositório**.

| ID | Arquivo | SHA-256 |
|---|---|---|
| E08-D03a | `image(20261113-195923).png` | `4227f659f596a4ec9b2622af141f6651afc22a72acbb83a6119f4b2702f96d72` |
| E08-D03b | `image(20261113-195935).png` | `33cdd6903b39bf3abeeaa136caa5f74511e9d9efb19567155fe5d82dea89c97b` |

## 3. Diagnóstico de C1 e decisão para E08-I02

- `c1/service.py` atende HTTP serial em `127.0.0.1` e propaga mensagens por porta numérica downstream.
- `c1/client.py` constrói URLs `http://127.0.0.1:<port>`; isso não atravessa contêineres separados.
- `c1/runner.py` e `c1/snapshot_race.py` devem conservar a operação local/localhost do C1 já validado.
- As classes de estado, contratos, fixture e oráculo permanecem sem alterações; a prova Python não equivale ao NOP Query C++ nem processa vídeos.
- Para C2, permitir `--listen-host 0.0.0.0` somente no contêiner, `--downstream-host` resolvido via DNS de rede Docker definida pelo projeto, e porta interna explícita (prevista: 8080). **Não publicar portas indiscriminadamente no host.**

## 4. Incremento E08-I02 — mudança sob validação

Arquivos: `prova-conceito/c1/client.py`, `c1/service.py`, `tests/test_c2_network_config.py`. Defaults C1 de `127.0.0.1` são mantidos. A única mudança é parametrização do endereço de escuta e do cliente; não modificar máquinas de estado nem payloads. Três novos testes isolados verificam URL, encaminhamento de snapshot via hostname e CLI (C1 padrão e C2 parametrizado).

**E08-I02 aprovado por evidência real:** HEAD `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, compilação 0, 42 testes OK e `Testes: 0` no Windows. Ainda não houve execução de rede Docker.

## 5. Comando de validação local após atualizar a branch

```powershell
Set-Location "$HOME\tcc2\etapa07\tcc2-trabalho"
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\prova-conceito
python -m compileall -q pon c0 c1 tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
git status --short
```

## 6. Limites e próximo marco

Não afirmar que há rede Docker ou contêineres PON rodando neste marco. A próxima etapa após regressão é o desenho dos Dockerfiles e do processo de construção/rastreio de imagens; antes disso, arquivar a prova de regressão e investigar qualquer falha. Kubernetes e distribuição entre nós permanecem Etapas 09–10. Dados reais futuros deverão alimentar diagramas e tabelas da monografia na Etapa 13.

## 7. E08-D04 — regressão real no Windows (13/11/2026)

- Fast-forward até `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`, branch `tcc2/desenvolvimento`.
- `Compilacao: 0`; `Ran 42 tests in 11.564s`; `OK`; `Testes: 0`; Git final sem alterações.
- Três novos testes verificam configuração de hostname/CLI com mocks: aprovação funcional de parametrização, não prova de comunicação Docker.
- A duração 11,564 s é da suíte, não medição de desempenho PON.

| Evidência | PNG original | Bytes | SHA-256 calculado dos bytes recebidos |
|---|---|---:|---|
| E08-D04a | `image(20261113-200758).png` | 144367 | `a38669c521c23456f85d43356bfacab58646260b6a8d74c85b3f491d0dbd0d33` |
| E08-D04b | `image(20261113-200811).png` | 71318 | `f8a00645992c6e21a0fa7957f958a5778b293eae798a15c941bef7bef90875f3` |

PNG originais recebidos nesta conversa, ainda não publicados no repositório.

## 8. Próximo passo E08-I03 — procedência da imagem base

Consultar no Windows a versão Python, arquitetura, imagem ID e RepoDigests da imagem oficial `python:3.13-slim` após download com plataforma `linux/amd64`. Registrar digest obtido para então criar Dockerfile(s) com base congelada, `.dockerignore` e builds de serviço. Não utilizar Docker/Kubernetes como evidência de execução da aplicação até os testes efetivos de C2.

## 9. E08-D05 — identificação real da imagem base (13/11/2026)

- Evidência: captura PowerShell `image(20261113-201558).png` recebida nesta conversa.
- SHA-256 da captura original calculado dos bytes recebidos: `39a2f3eb7a4b57cb4b9e9138b42b544984ffdc2a73a081856413d0a6da8173ef`.
- `docker pull --platform linux/amd64 python:3.13-slim`: `Digest: sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`, download informado como concluído.
- `docker image inspect`: `ImageID=sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`, `RepoDigests=["python@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90"]`, `OS=linux`, `Architecture=amd64`.
- Execução `docker run --rm --network none --platform linux/amd64 --entrypoint python python:3.13-slim --version`: `Python 3.13.18`.
- HEAD `94a2acd9f91124a988c9d46fc8558cf1822363a3`, branch sincronizada, status Git final limpo; nós kind preservados e `tcc2-python-validacao` permanece parado, com Exit 0.
- **Aceite E08-D05:** imagem de base identificada e teste isolado do interpretador concluído no Windows. Isso não comprova execução do PON na imagem.

## 10. E08-I03 — construção mínima sob validação

- Novo `prova-conceito/Dockerfile` fixa a imagem base pelo digest capturado em E08-D05; a construção deve usar `--platform linux/amd64`.
- `.dockerignore` mantém fora do contexto testes, fixtures, resultados locais e caches. `COPY` inclui somente núcleo `pon` e cinco módulos HTTP de runtime de `c1`.
- **Decisão arquitetural:** construir **uma imagem de runtime reutilizável** e executar **três contêineres diferentes**, cada um com `role` e parâmetros próprios. O isolamento depende dos contêineres, não de três cópias distintas da mesma imagem. Os três serviços continuam um por contêiner.
- Runtime usa UID/GID 10001, logs stdout não-bufferizados, sem bibliotecas Python externas instaladas; C0/oráculo, testes e fixture ficam no host para comparar resultados de C2 posteriormente.
- Execução como serviço usará `python -m c1.service <role> --port 8080 --listen-host 0.0.0.0` e, quando necessário, `--downstream-host <nome-dns> --downstream-port 8080`; endpoints de mutação não serão expostos publicamente. A rede Docker e as instâncias não serão criadas neste incremento.
- `LABEL org.opencontainers.image.revision` deve receber o HEAD completo como argumento de build. Imagens construídas localmente podem não apresentar `RepoDigests`; registrar ID local, tag, plataforma e revisão, sem inventar digest de publicação.
- **Situação:** Dockerfile e `.dockerignore` publicados no GitHub, **ainda sem build, smoke test nem validação de comunicação no Windows**.

### Procedimento planejado para validação de imagem

A partir da raiz do repositório, após sincronizar a branch e confirmar `git status --short` limpo:

```powershell
$sha = git rev-parse HEAD
$tag = "tcc2-pon:c2-e08-$($sha.Substring(0,12))"
docker build --platform linux/amd64 --progress=plain --build-arg "VCS_REF=$sha" -t $tag -f .\prova-conceito\Dockerfile .\prova-conceito
docker image inspect $tag --format 'ID={{.Id}} OS={{.Os}} ARCH={{.Architecture}} REV={{index .Config.Labels "org.opencontainers.image.revision"}}'
docker run --rm --network none --platform linux/amd64 --entrypoint python $tag -c "import os; import pon, c1.service; print('UID:', os.getuid()); print('IMPORTS: OK')"
docker run --rm --network none --platform linux/amd64 $tag rule-executor --help
```

Códigos de saída e logs devem ser preservados e analisados antes de classificar E08-I03 como aprovado.

## 11. E08-D06 — falha real de resolução do FROM (13/11/2026)

- **Evidência recebida:** `image(20261113-203658).png`, 1920x1080, PNG original; SHA-256 calculado `93822efcdbd3fc2aa816ed6aae7592e63b25606b42d7005430f2aa21a4fe03cd`.
- Git: fast-forward para `f2f54475ca45cfcd0845ee694fcf1680bed046f6`; branch exclusiva, status limpo antes da execução.
- Build: `docker build --platform linux/amd64 --progress=plain ...` interrompido em `[internal] load metadata for docker.io/library/python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`.
- Erro observado: `docker.io/library/python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90: not found`. `Build: 1`. PowerShell encerrou por `throw "Build Docker falhou."`, logo **não houve execução da inspeção de imagem construída nem dos smoke tests**.
- O Dockerfile foi publicado, mas nenhum build C2 aprovado. A falha ocorreu na resolução da imagem base antes de copiar/iniciar o PON; não constitui prova de defeito funcional do código Python.
- Diagnóstico em aberto: verificar no registro Docker Hub por `docker buildx imagetools inspect` a validade do digest remoto usado no `FROM`. A referência mostrada por `docker pull`/`docker image inspect` em E08-D05 não deve ser presumida resolvível pelo BuildKit sem confirmação.
- **Próximo ato:** executar comandos de inspeção somente leitura para comparar digest do registro, digest da referência com falha, imagem local. Não alterar código nem remover imagens até identificar causa e nova referência correta.

## 12. E08-D07 — diagnóstico real do manifesto remoto (13/11/2026)

- Evidência original: cinco PNGs enviados pelo acadêmico nesta conversa. SHA-256 abaixo calculados diretamente sobre os bytes recebidos, sem afirmar que foram versionados no GitHub.

| ID | PNG original | Bytes | SHA-256 |
|---|---|---:|---|
| E08-D07a | `image(20261113-204432).png` | 127232 | `4d2265087cc45e40e28ee3b535886bb7079505b720fd50a5fe7554f05077d961` |
| E08-D07b | `image(20261113-204441).png` | 145493 | `55e4b0f96444b94fd1fb74d473a515bbb37e6e29b3a32e3b978ac0bdd621dafe` |
| E08-D07c | `image(20261113-204450).png` | 145493 | `55e4b0f96444b94fd1fb74d473a515bbb37e6e29b3a32e3b978ac0bdd621dafe` |
| E08-D07d | `image(20261113-204522).png` | 148450 | `d6d25307f469bfd306d566f0ec0120f2107980f2d4048273e05dfc5f4161c1f9` |
| E08-D07e | `image(20261113-204531).png` | 63978 | `2e430c77269a860ae0121ee21115dc06f6e47e6039ac86fa642fb6cae1cc4243` |

- Git fast-forward ao HEAD `a9c74cd22044055798fd70542f526d7921879dde`; sem modificações locais ao final.
- `docker buildx imagetools inspect docker.io/library/python:3.13-slim` retornou código **0**, índice OCI multi-plataforma de digest `sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90`.
- Nesse índice consta um manifesto `linux/amd64` com digest `sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20`.
- `docker buildx imagetools inspect docker.io/library/python:3.13-slim@sha256:e48f59cdba69a3cbd9ed2cf0f348d90d45a8d35d098134cf1070bc106ee9ed90` retornou **1**, `not found`, reproduzindo a falha anterior de resolução explícita. A existência do índice via tag **não comprova que sua consulta por digest funcionará** neste ambiente.
- Imagem local consultada: Linux/amd64, RepoDigests exibido, sem alterações locais do Git. Ainda sem sucesso de build da aplicação nem teste de comunicação entre contêineres.

### Decisão E08-I03 (tentativa controlada)

- Alterar **apenas a referência FROM** para o digest `sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20` do manifesto `linux/amd64` listado na saída do registro, preservando a tag `python:3.13-slim` como identificador legível.
- Não atribuir causalidade definitiva à falha do índice: trata-se de uma referência que a consulta direta não resolveu. O manifesto específico é **candidato**, não referência já aprovada.
- Próximo passo **E08-D08**: testar `docker buildx imagetools inspect` diretamente para o novo digest; só se retorno 0, repetir o build, identificação da imagem e smoke tests. Se falhar, interromper e preservar a saída real antes de qualquer outra alteração.
- Sem execução de Kubernetes, sem medição de desempenho, sem conclusão do C2. Não modificar os módulos PON/HTTP.

## 13. E08-D08 — construção de imagem PON aprovada no Windows (13/11/2026)

- Evidências originais recebidas na conversa, com identificação SHA-256 sobre os bytes dos PNGs (arquivos ainda não incorporados ao GitHub):

| ID | PNG original | Bytes | SHA-256 |
|---|---|---:|---|
| E08-D08a | `image(20261113-205032).png` | 121646 | `f75edb60178c39b3d75293afc516141851795434cdb8da97e91501f49d538f4d` |
| E08-D08b | `image(20261113-205057).png` | 60669 | `d20793cbb68b2827579fca7e6c98c839b578fc99c3fe09f3e8bbfef1725cbc2e` |

- Git no Windows: fast-forward até `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`, branch `tcc2/desenvolvimento`, status final limpo.
- `docker buildx imagetools inspect` da referência específica `python:3.13-slim@sha256:48d884813cf44e927cf64c5529dd630dd3b18338c6dc727991eef9b71e934a20`: `Registro: 0`.
- `docker build --platform linux/amd64 ...` completado: `Build: 0`; tag local `tcc2-pon:c2-e08-dbefcd2cf3d2`. Docker reportou plataforma Linux/amd64, 176 MB na lista de imagens e label de revisão `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Smoke test sem rede: usuário `10001`, Python `3.13.18`, `IMPORTS: OK`, `Imports: 0`; CLI `python -m c1.service rule-executor --help` exibida com sucesso, `CLI: 0`.
- **Aceite E08-I03:** imagem Linux/amd64 construída, inspecionada e executada em testes mínimos no computador do acadêmico. Não houve três serviços executando simultaneamente, comunicação HTTP entre contêineres, inicialização da fixture nem equivalência funcional C2.

## 14. Incremento planejado E08-I04 — topologia de rede Docker

- **Próxima validação E08-D09 (não executada):** criar rede `bridge` **interna** nomeada `tcc2-pon-c2`, sem portas publicadas no host; iniciar `tcc2-c2-rule-executor`, `tcc2-c2-logic-engine` e `tcc2-c2-attribute-source`, todos a partir da imagem já construída `tcc2-pon:c2-e08-dbefcd2cf3d2`.
- Nomes DNS projetados via aliases: `rule-executor`, `logic-engine`, `attribute-source`; todos escutam na porta interna 8080, `--listen-host 0.0.0.0`; origem e avaliador usam `--downstream-host` com os aliases relevantes. Três instâncias, uma por papel, sem réplicas adicionais.
- Confirmar tag/label e ausência de mudanças no diretório `prova-conceito/` desde o commit da imagem antes do start; não reconstruir a imagem após commits somente documentais.
- Verificar contêineres `running`, IDs Docker distintos, rede correta, ausência de mapeamento de portas host, `GET /health/live` por DNS dentro da rede e logs de `listening`. Antes do snapshot, `/health/ready` é esperado 503; nenhum resultado de regra deve ter sido produzido.
- Evitar colisão com recursos existentes: interromper se rede ou nomes já existirem; não remover/reiniciar contêineres anteriores nem tocar no kind.
- Ainda faltam E08-I05, fixture e equivalência C2↔C0/C1; figuras futuras devem distinguir separação por contêiner no mesmo host de distribuição física multinó.

## 15. E08-D09 — falha real na inspeção da label no PowerShell (13/11/2026)

- Captura PowerShell recebida na conversa: `image(20261113-210012).png`, 111.269 bytes; SHA-256 **calculado nos bytes recebidos**: `4eaf907129c646850fe36ca5335c71f9073c398b0c17ce1e92e705885f796b18`. PNG ainda não incorporado ao GitHub.
- HEAD atualizado por fast-forward até `c43cd1d6aa9e8ef2a015117f2fb15b8f5afda1bd`; sem indício de alteração no código do contêiner desde o build `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`.
- Falha no passo 2, consulta da label OCI no `docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'`: **`template parsing error: template: :1: function "org" not defined`**. O PowerShell e a CLI Docker não preservaram as aspas internas da expressão Go template.
- O `throw 'Imagem inexistente ou revisao divergente'` foi consequência genérica do erro de template; **não há evidência de imagem ausente ou de label divergente**.
- Como o fluxo parou no passo 2 antes de `docker network create`, **esta tentativa não criou rede ou contêineres C2**. Os comandos de inicialização exibidos no topo do print são entrada do bloco, não saída de execução.
- Correção proposta para validar no Windows: `docker image inspect` sem `--format`, processar JSON com `ConvertFrom-Json`, ler a propriedade `.Config.Labels.'org.opencontainers.image.revision'`. Comparar ao SHA do código do build. Repetir E08-D09 com essa leitura; não alterar a imagem nem o núcleo PON.
- **E08-D09 não aprovado. E08-I04 continua pendente.** Preservar saída original e não tratar erro de script como falha funcional da aplicação.

## 16. E08-D09 — três contêineres em rede Docker interna comprovados (13/11/2026)

- Evidência real: captura de PowerShell `image(20261113-210408).png`, **126.879 bytes**, SHA-256 calculado sobre os bytes recebidos **`53ecd7f79bc5fe5c35282f3ec4ce70a55fad6f94af90581a9f6703e5228d49c1`**. PNG original recebido na conversa; não versionado no GitHub.
- Git local do acadêmico: fast-forward para `dd546f284aff576fe02c5aecfb318a1535b075f7`; imagem usada `tcc2-pon:c2-e08-dbefcd2cf3d2`, produzida a partir do código `dbefcd2cf3d2fbf220cff8eda34d52189e08192a`; plataforma Linux/amd64. Nenhum rebuild necessário para commits documentais.
- `docker network create --driver bridge --internal tcc2-pon-c2` retornou ID de rede. `docker network inspect`: `Driver=bridge`, `Internal=true`, **três membros**.
- Três contêineres `Running=true` com identificadores Docker distintos: `tcc2-c2-rule-executor`, `tcc2-c2-logic-engine`, `tcc2-c2-attribute-source`; mesma imagem, porta interna 8080 e sem binding publicado ao host (verificações do script concluídas).
- `docker exec` no produtor: HTTP GET `http://logic-engine:8080/health/live` com resposta `{'service':'logic-engine','pid':1,'live':True}`. No avaliador: HTTP GET `http://rule-executor:8080/health/live` com resposta `{'service':'rule-executor','pid':1,'live':True}`. Consultas confirmam resolução DNS e comunicação real pelo transporte HTTP entre contêineres.
- Cada contêiner informou PID interno 1, fato compatível com namespaces PID isolados; PID interno não deve substituir ID Docker para identificar instâncias.
- `GET /state` nos três serviços: `ready=False`, esperado antes do snapshot. Logs JSONL de cada serviço mostram evento `listening`, porta 8080. Saída final `E08-D09: VALIDACOES CONCLUIDAS`.
- **Aceite E08-I04 no escopo de infraestrutura:** isolamento por contêiner, rede privada, resolução DNS, HTTP de saúde e estados frios verificados no Windows. **Não demonstra ainda entrega de AttributeChanged/ConditionChanged, snapshot instalado, dois efeitos, equivalência com C0/C1, recuperação, métricas ou multinó físico.**

### Próximo incremento E08-D10 (planejado, não executado)

- Fazer preflight dos três contêineres ativos na rede `tcc2-pon-c2` e de `ready=false` em cada estado; abortar sem mutação se já houver inicialização prévia.
- Enviar somente `POST /init/snapshot` ao `attribute-source`, com `run_id=c0-minimo-v1` (fixture versionada), executando dentro do contêiner de origem; o código encaminha ao `logic-engine` e ao `rule-executor` por HTTP/JSON com ACKs.
- Verificar `ready=true`, `snapshot_version=c0-minimo-v1:snapshot:0`, sequência 0 e atributos iniciais `atA=0`, `atB=0` (produtor/avaliador), condição e aprovação falsas, nenhum efeito registrado no executor.
- Coletar logs `docker logs` dos três serviços para evidenciar `send`, `ack`, `mutation` de snapshot, com cuidado para não chamar `POST` duas vezes se script interromper depois da inicialização.
- **Não enviar ainda a sequência de alterações determinísticas**. Ela será ensaiada em incremento seguinte, com confrontação ao oráculo C0/fixture manual.

## 17. E08-D10 — snapshot inicial realmente validado em C2 (13/11/2026)

- Captura original da sessão Windows `image(20261113-210955).png`, 139616 bytes, SHA-256 `fb949fba22f6b79796adaded539f8f92a890ba3bee36b8a553ed07cab15c29af`. Original na conversa, **não versionado no GitHub**.
- `git pull --ff-only` atualizou o clone para `df42f0447ac1c5ad579d600ea6fc6646a7ac432e`, somente documentação desde o build da imagem `tcc2-pon:c2-e08-dbefcd2cf3d2`.
- Rede `tcc2-pon-c2` consultada com `Internal=true`; três contêineres ativos com estados `ready=false`, `run_id=null` antes do POST.
- `POST /init/snapshot` no `attribute-source` com `run_id=c0-minimo-v1`: resposta observada `{"duplicate": false, "ready": true, "snapshot_version": "c0-minimo-v1:snapshot:0"}` (HTTP 200).
- `GET /state` nos três: `run_id=c0-minimo-v1`, `snapshot_version=c0-minimo-v1:snapshot:0`, `ready=true`. Produtor e avaliador com atributos `atA=0, atB=0`, sequências `atA=0, atB=0`; avaliador com `condition=false`, `condition_sequence=0`, `condition_events=[]`, `received_ids=[]`, `faulted=false`; executor com `approved=false`, `condition_sequence=0`, `effects=[]`, `received_ids=[]`, `faulted=false`.
- Logs JSON dos serviços mostram encaminhamento de snapshot `send`, recebimento `mutation`, confirmação `ack` entre produtor→avaliador→executor; todos permanecem `Up`. Script concluiu `E08-D10: SNAPSHOT VALIDADO` sem exceção.
- **Aceite E08-D10:** propagação real do snapshot/ACKs por HTTP na rede Docker e estados iniciais consistentes comprovados. Isso **não demonstra** ainda propagação de alterações, transições, efeitos C2 ou equivalência funcional com o oráculo.

## 18. Próxima atividade E08-D11 — executar fixture sem repetir snapshot

- Estado herdado: três contêineres **já inicializados**, executar somente sete chamadas `POST /attributes/change` da fixture versionada `prova-conceito/fixtures/c0_minimo.jsonl`, em ordem, pelo produtor.
- Antes de mutar o estado, validar estados iniciais e consultar logs da origem para garantir ausência de mutações prévias em `/attributes/change` (inclusive passo 1 que não modifica valor). Se existirem, bloquear repetição e diagnosticar.
- Coletar transcript de cada POST, estados finais, logs por contêiner, hashes SHA-256 de entradas/saídas e manifesto de imagem/commit. Comparar efeitos e causalidade com fixture manual, C0 e `c0.oracle.calculate_expected_effects` independente.
- Resultado desejado mas **ainda não observado em Docker**: cinco notificações de atributos, três transições de condição e dois efeitos nos passos 3 e 7. Não apresentar como aprovado antes de receber logs reais.
- Se houver erro durante mutação parcial, **não reenviar a fixture automaticamente**; preservar estado e logs. Ainda não há recuperação persistente/replay comprovados. Kubernetes fora do escopo da etapa.

## 19. E08-D11 — executor reprodutível de fixture (preparado, não executado)

- Scripts adicionados: `prova-conceito/c2/__init__.py`, `prova-conceito/c2/runner.py`, `prova-conceito/tests/test_c2_runner.py`.
- A imagem C2 aprovada permanece imutável: o executor roda **no Python do Windows** e usa `docker exec` para chamar HTTP `127.0.0.1:8080` dentro do contêiner de origem, que repassa notificações aos outros pela rede interna Docker.
- Preflight: Git limpo, runtime inalterado desde build, três contêineres Running com IDs distintos, rede bridge interna, mesmo snapshot `c0-minimo-v1:snapshot:0`, estado inicial zerado, ausência de mutações de atributo prévias inclusive eventos redundantes (detectados nos logs).
- Comparações: fixture manual, C0 local da aplicação, oráculo independente, ordem/causalidade e contagem de notificações em logs. Diretório novo `resultados-locais/` (ignorado pelo Git), captura em `finally` dos três logs e `checksums.sha256`, sem parar contêineres.
- **Estado:** código da ferramenta publicado, ainda não testado no Windows, fixture C2 ainda não aplicada. Próxima ação: compilar + 45 testes, depois executar uma única rodada `python -m c2.runner --output ...`; nunca reenviar em caso de falha parcial sem diagnóstico dos arquivos.
