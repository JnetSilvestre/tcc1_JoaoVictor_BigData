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
