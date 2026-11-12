# Etapa 07 — Ensaio complementar C1 de mudança durante a confirmação do snapshot HTTP

**Situação em 12/11/2026:** código e teste publicados; **ensaio ainda NÃO executado no Windows do acadêmico**. O último resultado real documentado é a suíte de 38 testes aprovada (E07-D18).

## 1. Finalidade e vinculação ao protocolo

O critério V07 da Etapa 05 exige snapshot com watermark coerente antes do processamento incremental e inclui alterações durante a inicialização. O teste local de barreira em memória já passou; este incremento acrescenta um ensaio de **requisições HTTP reais** com três serviços Python em processos distintos e um proxy de teste que **atrasa exclusivamente o ACK** da instalação do snapshot.

Este não é um teste de corrida multi-threaded dentro dos serviços: `HTTPServer` atende requisições serialmente. É um teste controlado de chegada de uma alteração ao socket do produtor **enquanto ele ainda está bloqueado aguardando confirmação do snapshot**. Não autoriza alegar sincronização geral, alta disponibilidade, tolerância a perda de rede ou replay.

## 2. Implementação publicada

- `prova-conceito/c1/snapshot_race.py`: gera rodada independente e logs, inicia três processos em `127.0.0.1` e usa um pequeno proxy HTTP em thread do processo de teste; o proxy não integra a arquitetura de produção e **não substitui nenhum dos três serviços**.
- `prova-conceito/tests/test_c1_snapshot_http_race.py`: teste da CLI Python por `run()`, verifica `PASS`, causalidade, sequência de eventos, três PIDs, efeitos da fixture e checksums.
- Não altera `protocol.py`, `state.py`, `service.py`, `codigoPon` original ou manifests Docker/Kubernetes.

### Fluxo observável do ensaio

1. Iniciar `rule-executor` e `logic-engine` (PIDs distintos).
2. Iniciar o proxy de confirmação controlada e o `attribute-source` (terceiro PID).
3. Enviar `POST /init/snapshot` ao produtor. O proxy encaminha ao avaliador, que inicializa o executor; após os dois concluírem, o proxy **segura o ACK ao produtor**.
4. Enquanto o produtor aguarda o ACK, enviar **o corpo completo** de `POST /attributes/change` (passo 2: `atA=5`) por socket HTTP independente.
5. Confirmar que, antes de liberar o ACK, os estados do avaliador e executor permanecem inicializados sem efeitos adicionais.
6. Liberar o ACK do snapshot; conferir que a requisição concorrente retorna HTTP 200 e produz sequência `atA:1`.
7. Aplicar os passos 3–7 da fixture C0. O passo 1 (`atA=0`) é um no-op inicial e é omitido somente neste ensaio.
8. Conferir estado final, 5 notificações de atributo, 3 transições de condição e **2 efeitos nos passos 3 e 7**, com IDs e causalidade idênticos ao arquivo esperado.

## 3. Evidências e resultados

O ensaio gera sua própria pasta, com `manifest.json`, `validation.json`, `timeline.jsonl`, `effects.jsonl`, `expected.jsonl`, `states.json`, `checksums.sha256` e logs JSONL/stderr dos três serviços.

O `timeline.jsonl` registra `snapshot_installed_downstream`, `snapshot_ack_held`, `concurrent_change_sent`, `snapshot_ack_released` e `concurrent_change_responded`. Timestamps monotônicos são usados somente para ordenar eventos **dentro do processo de teste**; não são métricas experimentais de latência entre processos.

As verificações booleanas esperadas são: `three_distinct_pids`, `downstream_initialized_no_effects`, `change_completed_after_snapshot`, `expected_effects_and_causality`, `final_consistent_state`, `no_extra_events`, `ordered_gate_timeline`.

## 4. Execução no PowerShell (Windows do acadêmico)

Partindo de qualquer diretório, usar:

```powershell
Set-Location "$HOME\tcc2\etapa07\tcc2-trabalho"
git branch --show-current
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\prova-conceito
python --version
python -m compileall -q .\pon .\c0 .\c1 .\tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"

$rodada = "resultados-locais/c1-snapshot-http-$(Get-Date -Format yyyyMMdd-HHmmss)"
python -m c1.snapshot_race --output $rodada
Write-Host "V07-HTTP: $LASTEXITCODE"
Get-Content "$rodada/validation.json"
Get-Content "$rodada/manifest.json"
Get-Content "$rodada/timeline.jsonl"
Get-Content "$rodada/checksums.sha256"
git status --short
```

**Expectativas, não resultados observados:** suíte de 39 testes (38 anteriores + 1 de HTTP concorrente), códigos de saída 0, `status=PASS`, sete checks `true` e dois efeitos nos passos 3 e 7. Falhas, timeouts ou divergências devem ser preservados integralmente e investigados; não ajustar resultados manualmente.

## 5. Limitações e aceite

Se confirmado, o ensaio amplia V07 para a situação controlada de *chegada de uma requisição enquanto o ACK do snapshot permanece pendente* no produtor serial. Não cobre chegada durante mutação da réplica, vários clientes simultâneos, quebra de processo, persistência, retransmissões arbitrárias, mudança de nó ou recuperação. Tais limites devem aparecer na monografia e na transição para Docker/Kubernetes.

**Não converter testes de localhost ou durações do unittest em métricas de cluster.** A imagem de arquitetura definitiva deve refletir a implementação realmente validada, não uma hipótese.


## 6. Execução confirmada no Windows — 12/11/2026

**Este trecho substitui as expectativas anteriores por resultados observados, preservando o protocolo do ensaio.** Código `be6b850d599504e9ea8166f02fd87b35313e5445`; `compileall: 0`, `39/39 unittest OK em 11,152s`, `python -m c1.snapshot_race` `PASS`, `V07-HTTP: 0`, 7 checks `true` e dois efeitos nos passos 3 e 7. Os PIDs foram `1988`, `15164`, `18332` (proxy de teste executado em thread à parte).

As capturas E07-D19–D21 e seus SHA-256 constam no relatório `docs/tcc2/etapa-07-encerramento-funcional.md`. A sequência temporal registrada confirma que a alteração foi enviada antes da liberação do ACK, sendo recebida depois pelo produtor serial. Os limites de concorrência, tolerância a falhas e persistência da seção 5 continuam válidos. O arquivo ZIP local foi gerado com hash exibido, mas não enviado ao repositório.
