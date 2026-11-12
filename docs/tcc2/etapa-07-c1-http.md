# Etapa 07 — C1 por HTTP em três processos

A prova usa a biblioteca padrão do Python, com um processo para cada papel da
Etapa 04. Cada servidor escuta em `127.0.0.1` e processa uma requisição por vez.
O executor inicia primeiro, seguido pelo avaliador e pelo produtor. O sistema
operacional atribui as portas, registradas no manifesto de cada rodada.

| Papel | POST | Ação |
|---|---|---|
| attribute-source | `/init/snapshot` | Recebe `{"run_id":"..."}` e envia snapshot inicial ao avaliador |
| attribute-source | `/attributes/change` | Valida a alteração e encaminha o evento se houver mudança |
| logic-engine | `/init/snapshot`, `/notifications/attribute` | Instala a réplica e encaminha snapshot ou transições ao executor |
| rule-executor | `/init/snapshot`, `/notifications/condition` | Instala a condição e executa a regra na transição falso→verdadeiro |

Todos expõem `GET /health/live`, `GET /health/ready` (503 antes do snapshot)
e `GET /state`. Cada inicialização confirma o snapshot downstream antes de
marcar o papel como pronto. Chamadas simultâneas ao mesmo processo são
serializadas pelo servidor.

## Reprodução no PowerShell

No clone da branch `tcc2/desenvolvimento`, execute:

```powershell
git branch --show-current
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\prova-conceito
python --version
python -m compileall -q pon c0 c1 tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
$rodada = "resultados-locais/c1-$(Get-Date -Format yyyyMMdd-HHmmss)"
python -m c1.runner --output $rodada
Write-Host "C1: $LASTEXITCODE"
Get-Content "$rodada/manifest.json"
Get-Content "$rodada/validation.json"
Get-Content "$rodada/checksums.sha256"
```

A CLI inicia e encerra os três serviços. Cada rodada requer um diretório novo.
Os logs por serviço registram envio, recebimento, confirmação e efeito com PID,
payload e timestamp. `http.jsonl` registra as sondagens, requisições e respostas.
`states.json` contém o estado após o snapshot e após a fixture. O manifesto
registra Python, revisão, fixture, portas e PIDs. `checksums.sha256` cobre as
saídas da rodada. `validation.json` retorna PASS apenas se todas as verificações
forem verdadeiras. A CLI retorna 1 em caso de divergência.

## Rodada automatizada desta sessão

No commit `a0d1a5e17f6c2942865d3e7e4ffc4f92a8f0e129`, o C1 retornou 0,
com 12 verificações verdadeiras. PIDs observados: produtor 24004, avaliador
21908 e executor 23852. A compilação retornou 0 e a suíte integrada executou
37 testes com sucesso nesta sessão. A reprodução do C1 pelo acadêmico
aguarda a saída correspondente. A E07-D13 cobre o incremento anterior.

| Critério | Verificação observada nesta sessão |
|---|---|
| V02 | Igualdade exata com execução C0, fixture manual e oráculo independente, incluindo ordem, multiplicidade e causalidade. Efeitos nos passos 3 e 7. |
| V03 | Campos ausentes, valor booleano, entidade desconhecida e versão inválida rejeitados com 422, com inspeção de estado antes e depois. |
| V04 | Três PIDs distintos e payloads correlacionados entre origem, recebimento e efeito. |
| V05 | Reentrega HTTP de eventos de atributo e condição, além de repetição de request_id, sem novo efeito. |
| V06 | Lacunas e payload alterado para ID anterior rejeitados com 409 em ambos os receptores, preservando o estado. |
| V07 | Prontidão 503 e mudança rejeitada antes do snapshot. Três versões iguais e sequências zeradas antes da fixture. |

Os arquivos de efeitos C1, C0 e oráculo têm SHA-256
`498c390f23f1a11f4ffe6c2560958582f29eb9df2ac70887f3e4742a99829e0c`.
O SHA-256 de `validation.json` é
`53ebe49bd1457f3a952baf4c4e41b426e208745a62fa80ef318b1efc58d590d5`.
A rodada está em `prova-conceito/resultados-locais/c1-etapa07`.

## Limites

A prova instala apenas snapshot inicial, com watermarks zero. Os testes cobrem
a barreira de inicialização e uma rodada serial. A rodada não mede chegada
concorrente durante a instalação, recuperação de rede, persistência, replay
após reinício ou latência experimental. Docker e Kubernetes da aplicação
pertencem aos incrementos seguintes. A origem do núcleo permanece fixada em
`JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.


## Reprodução confirmada no Windows do acadêmico — 12/11/2026

A implementação do Work foi reproduzida no host acadêmico, **não apenas no ambiente Work**: Git `f37dbc998eb5114a60335f5275c86b6e8bedee61`, Python 3.13.9, compilação 0, 37/37 testes `unittest` OK, `C1: 0`, `status: PASS` e 12 checks true; PIDs `20472`, `19548`, `22276`, portas `52911`, `52910`, `52909`, efeitos passos 3/7. O ZIP local foi criado e seu SHA exibido por PowerShell, mas o ZIP ainda não foi inspecionado/transferido para o GitHub.

| ID | Arquivo (captura na conversa) | SHA-256 do PNG verificado | Resultado |
|---|---|---|---|
| E07-D14 | `image(20261112-210144).png` | `9dadee3396b98d554eab392d70b47780643fb16089656d2f7b22be6e0964ad27` | Git fast-forward, 37 testes de integração iniciados, revisão do projeto |
| E07-D15 | `image(20261112-210212).png` | `38eab7a9468ce68b7a6fd9660c1ffe0c0bd0639e6a88f94586337b012deb9003` | 37/37 OK, `C1: 0`, `status=PASS`, 12/12 verificações verdadeiras, manifesto e PIDs |
| E07-D16 | `image(20261112-210250).png` | `81ef8d4f0987fb596c5d677aa193567cca2a3884f63a64be58ff0c32e731f037` | `checksums.sha256` dos artefatos da rodada |
| E07-D17 | `image(20261112-214847).png` | `e7b9bd7ad6545c9321aeee05655af9ee892be774c7e98b4704451c327f303bbe` | `Compress-Archive` e hash SHA-256 do arquivo ZIP local |

**Hash do ZIP mostrado pelo PowerShell, não verificado por acesso aos bytes do arquivo:** `D7A62AC62AFA23302F272D303E00DB6B622B92FA04E5B3B7F1DE7367BF735D17`. O comando selecionou a pasta C1 mais recente e criou um ZIP ao lado dela. O nome completo do ZIP não está legível no print, pois a coluna `Path` aparece truncada. As capturas estão anexadas à conversa, não armazenadas no GitHub; o ZIP continua no host Windows do acadêmico.

**Avaliação de V07:** o roteiro de transporte valida readiness 503, rejeição de mudanças antes do snapshot e versões iniciais coerentes, porém não injeta alteração concorrente com a transação de instalação de snapshot. Essa lacuna permanece declarada; novo teste de barreira de estado em memória pendente de execução não é prova direta de concorrência HTTP. Para a matriz de aceite e demais limites, consultar `etapa-07-aceite-tecnico.md`.


## Atualização V07 — teste complementar de handshake do snapshot HTTP

**E07-D18 — captura original do PowerShell:** `image(20261112-215913).png`, dimensões 1920 × 1080, tamanho 150.253 bytes, SHA-256 **calculado sobre os bytes da imagem recebida**: `538070b0635b8a078750f745071a2b459fd3d9aae7610ff44b49b879d51808b9`.

Resultados observados no Windows: branch `tcc2/desenvolvimento`, HEAD `3742a852a7b448f15a998b18207a02765954019c`, Python 3.13.9, `Compilacao: 0`, `Ran 38 tests in 7.354s`, `OK`, `Testes: 0`. O teste `test_change_during_snapshot_handshake_is_rejected_before_ack` aparece com `ok`. **Esse teste é local em memória e não prova concorrência HTTP**. A duração é da suíte `unittest`, não benchmark do PON. A imagem foi enviada nesta conversa e ainda não é um arquivo bruto do repositório.

Foi publicada uma verificação controlada de HTTP, com proxy de ACK de teste (não é um quarto serviço permanente) e três processos da aplicação. Para executar e arquivar `validation.json`, `timeline.jsonl`, `manifest.json`, logs e hashes, consultar `docs/tcc2/etapa-07-c1-snapshot-http.md`. **A execução no Windows deste incremento ainda está pendente.**
