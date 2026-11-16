# TCC2 — Etapa 11 / E11-I03 — Refinamento da instrumentação temporal

**Estado:** código preparado na branch `tcc2/desenvolvimento` e testes sintéticos acrescentados, ainda não executados no Windows. Não houve nova rodada, novo namespace, POST ou benchmark no contexto desta modificação.

## Motivação (E11-P01)

O piloto C3 de 100 requisições foi funcionalmente correto, mas durou ~2,244 s enquanto o período abrangido pelas poucas amostras do Kubelet era de ~3 s. O indicador anterior `usable_cpu=true` atestava apenas contador monotônico, sem relação suficientemente controlada com a janela de trabalho. Portanto os números exploratórios não são o consumo exato da aplicação.

## Alterações

- `benchmark/client.py`: `batch_started_utc` e `batch_finished_utc` junto às fronteiras do relógio monotônico `perf_counter_ns`, sem subtrair timestamps de nós distintos. Marca UTC serve a aproximação de cobertura, não ao cálculo de latência.
- `benchmark/collector.py`: separa `cpu_counter_present_monotonic`, `cpu_window_adequate`, `memory_window_adequate` e reporta por papel número de pontos, bordas, max de memória AMOSTRADO e diferença entre amostras que enquadram o lote. `usable_cpu` passa a significar adequação conservadora de janela, não mera monotonicidade. `cpu_delta_bracketing_s` inclui CPU fora do lote quando as bordas não coincidem; NÃO publicar como CPU exata.
- Gate preliminar de adequação: duração >=10s, >=5 timestamps distintos, amostras envolventes a <=3s de cada borda, máximo de 4s sem ponto e sem regressão do contador. São critérios instrumentais **provisórios para piloto**; não alegar calibração de relógios distintos, potência estatística ou precisão das bordas. Ajustar antes de congelar V12 após observar medições reais.
- `benchmark/runner.py`: faz uma captura inicial da Summary API antes do cliente e registra `batch-summary.json`; também produz `requests.csv` e `metrics-samples.csv` derivados, preservando `client.stdout.jsonl` e `metrics-samples.jsonl` como brutos. Em falhas, continua arquivando o que conseguir.
- `benchmark/evidence.py`: escrita de CSV. `tests/test_benchmark.py`: testes sintéticos de fronteiras, rejeição de lote curto, adequação sintética de lote longo e detecção de regressão do contador.

## Itens expressamente não implementados

- Nenhuma alteração nos serviços funcionais `pon/` e `c1/`, nem na imagem C2 aprovada.
- Nenhuma implantação ou benchmark C4/C2, escalonamento horizontal, replay ou processamento em computadores físicos distintos.
- Ainda falta tornar o cenário Docker C2 comparável, padronizar o custo/posicionamento do gerador, validar o comportamento sob carga de 1.000 requisições e congelar warmup/repetições.

## Gate E11-D05 (somente preparação)

Na pasta `prova-conceito`, após sincronizar a branch correta e com Git limpo, usar:

```powershell
git pull --ff-only --quiet origin tcc2/desenvolvimento
python -m compileall -q benchmark tests/test_benchmark.py
python -m unittest discover -s tests -p test_benchmark.py -v
git status --short
```

**Proibido inserir `--execute`, `kubectl apply`, novos POSTs ou repetir snapshot da bancada E11-P01** neste gate. Os resultados dos testes ainda não foram observados.

## Encaminhamento

Após E11-D05 aprovar a versão nova, preparar um piloto C4/100 em namespace inédito para equivalência funcional; os dados de CPU de uma carga curta podem continuar marcados `cpu_window_adequate=false` sem reprovar a equivalência funcional. Em paralelo, planejar carga média e C2 comparável. Pesquisas no Perplexity devem fundamentar decisões metodológicas com referências verificadas.
