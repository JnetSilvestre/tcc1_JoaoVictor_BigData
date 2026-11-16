# TCC2 — E11-I06 | Sondagem externa Docker durante lote (instrumento candidato)

**Estado:** implementação versionada para validação Windows E11-D08. Nenhuma carga, snapshot, criação de rede ou contêiner executada nesta alteração. A instrumentação de C2 sob carga **ainda não foi testada**. V12 continua pendente.

## 1. Mudança de instrumentos

- `benchmark/docker_c2.py` preserva rede/contêineres exclusivos, fixture canônica, cliente serial e oráculo; substitui APENAS a amostragem intrusiva com `docker exec` do piloto C2 por `EngineSampler`. O cliente e as sondagens `GET /state` continuam usando `docker exec` de forma localizada, FORA da janela ou no contêiner cliente, não para medir CPU/memória da aplicação.
- `benchmark/docker_engine_window.py`: coleta via `engine_stat` da Docker Engine API (`GET`, named pipe Windows), valida IDs/imagem/restarts e realiza uma primeira **consulta GET de recursos antes do snapshot**. Após o snapshot captura uma baseline específica, amostras durante e após o lote. Falha na primeira consulta impede mutação.
- Salva `engine-context.json`, `metrics-engine.jsonl`, `metrics-engine.csv`, `metrics-errors.json`, `metrics-collector-round-seconds.json`, client JSONL, resumo do lote, logs, estados, `validation.json`, checksum SHA-256 e ZIP.
- `quality_window` é CONSERVADORA: observa monotonicidade e identidade dos contadores, idade de atualização `docker_read_utc`/`retrieved_utc`, coerência UTC/perf_counter, duração mínima provisória 10 s, cinco pontos distintos, intervalo máximo 4 s e margens até 3 s. Timestamps duplicados com contadores distintos não habilitam janelas quando situados na borda. `cpu_delta_bracketing_s` só é calculado em janela que passa; não equivale a CPU exata do lote.
- `measurement_approved=false` continua incondicional, mesmo se a adequação temporal passar, pois não houve calibração do efeito observador. `memory_comparable_to_kubelet=false` também permanece, porque uso bruto de memória Docker não é a mesma métrica do working set Kubernetes.
- `tests/test_benchmark_docker_engine_window.py`: sete testes sintéticos sem Docker, snapshots, Kubernetes ou POST. Não há resultados de execução reais desta nova implementação.

## 2. Limitações e políticas de segurança

- Não reexecutar no C2 E11-P03 `tcc2-pon-e11-c2-p20261115-225314`. Esse ambiente foi usado em carga e depois por sonda somente leitura; novas mutações exigem rede/contêineres inéditos.
- Pré-voo da fonte externa e identidades Docker ocorre ANTES de qualquer snapshot; erro interrompe o piloto. Falha de monitor já durante carga é registrada separadamente e invalida a métrica, não transforma resposta funcional válida em medição científica aceita.
- Todas as métricas Docker dependem do Docker daemon e dos mesmos recursos físicos. Coletas seriadas não são simultâneas. C3/C4 ainda dependem de Summary API, e C4 compartilha o host físico com C2/C3.
- O cronômetro do cliente e a correção funcional são independentes da aprovação da coleta de CPU/memória.

## 3. Próximo gate E11-D08 (não mutante)

Sincronizar branch, verificar commit, executar `python -m compileall -q benchmark tests/test_benchmark*.py` e `python -m unittest discover -s tests -p 'test_benchmark*.py' -v`. Emitir PLAN_ONLY do futuro C2 de 1000 usando `python -m benchmark.docker_c2 --label pteste --run-id e11-c2-pteste --fixture <fixture-canonica-1000> --output <pasta-inexistente>` SEM `--execute`. Gerar fixture em diretório local inédito. Inspecionar saída antes de iniciar carga.

## 4. O que falta para fechar Etapa 11

Além deste gate de validação, restam: piloto de carga 1000 em novos C2/C3/C4, calibração ou limitação formal de CPU/memória/overhead e equivalência do gerador, política de aquecimento e reposição de estado, controle de variabilidade, fixação de cargas/limites/repetições e execução/auditoria das séries quantitativas previstas em E11-M01/A01. **Etapa 12 corresponde à análise científica dos resultados**, não à primeira execução dessas séries. O protocolo e quantidade de repetições ainda não foram congelados.

Referências metodológicas selecionadas: `docs/tcc2/etapa-11-auditoria-seletiva-perplexity.md`. Dados experimentais anteriores permanecem preservados; esta implementação não alterou `pon`, `c1` ou Dockerfile aprovado.
