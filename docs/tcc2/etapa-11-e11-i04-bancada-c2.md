# TCC2 — Etapa 11 / E11-I04 — Bancada C2 e revisão da qualidade temporal

**Situação:** instrumentos publicados para validação. NÃO foram executados no Windows, nenhuma rede Docker criada, nenhuma rodada/benchmark executada. Os pilotos E11-P01/P02 continuam apenas exploratórios. V12 permanece pendente.

## Entregas

- `benchmark/collector.py`: tratar timestamp repetido do kubelet com contadores CPU crescentes como **resolução temporal insuficiente**, e não regressão real. Monotonicidade avaliada na ordem da coleta; `cpu_duplicate_timestamp_count`, `cpu_timestamp_ambiguous_count`, `cpu_counter_regressed` e `cpu_timestamp_regressed` explícitos. O gate de cobertura de CPU rejeita bordas ambíguas. Contador regressivo segue inválido.
- `benchmark/docker_c2.py`: prepara cenário **novo C2** em rede Docker bridge interna, quatro contêineres (três serviços + cliente) com nomes exclusivos. Compartilha a imagem Docker aprovada e o cliente Python de C3/C4; `--execute` deve ser chamado uma única vez em bancada nova. Sem a flag, apenas PLAN_ONLY. O núcleo funcional não foi alterado.
- `tests/test_benchmark_docker_c2.py`: garante nomes isolados, fixture canônica, argumentos Docker, não exposição de portas, mesma imagem e quotas candidatas. Testes sintéticos ainda não rodados no Windows.

## Configurações C2 propostas e limites de interpretação

- Serviços: teto de **0,5 CPU** e **256 MiB** cada; cliente: 0,5 CPU e 128 MiB, correspondendo aos limites nominais dos manifests Kubernetes C3/C4. Docker `--memory-swap` é igual a `--memory` para tentar desabilitar swap, **sujeito à efetiva disponibilidade e verificação no host**. CPU `requests` de Kubernetes **não se transfere** diretamente a uma reserva Docker; só os tetos são semelhantes.
- Cada papel roda em um contêiner, HTTP/JSON serial, Docker DNS de aliases de serviços, rede `--internal` e nenhuma porta publicada. O cliente roda em contêiner distinto, com uma invocação `docker exec -i python -` para **todo o lote**, não uma por POST.
- Para C2, a captura candidata de CPU/memória lê `cpu.stat`, `memory.current` e `memory.peak` por meio de `docker exec` dentro dos contêineres. **AVISO:** essa coleta é INTRUSIVA e cria processos de medição dentro dos mesmos cgroups que são avaliados. Consequentemente, os números ainda NÃO podem ser usados como CPU/RAM comparável frente à Summary API de Kubernetes. Instrumentação C2 requer posterior calibração ou acesso externo ao cgroup por contêiner. Os dados brutos são diagnósticos; `measurement_approved=false`.
- Registros de tempo e vazão são do MESMO cliente Python utilizado em C3/C4; essa comparabilidade inicial não isola o custo de Kubernetes, devido à rede, namespace, scheduler e diferença no mecanismo de implantação.
- O cluster kind e as bancadas históricas permanecem presentes durante o piloto C2 para não alterar C3/C4. A carga de fundo dos serviços já implantados pode afetar os valores; registrar e controlar no protocolo definitivo.

## Segurança e preservação

- Nunca reutilizar `tcc2-pon-c2`, `tcc2-c2-*` (C2 funcional) nem os namespaces `tcc2-pon`, `tcc2-pon-c4`, `tcc2-pon-e11-c3-p20261115-213740` e `tcc2-pon-e11-c4-p20261115-220023`.
- `benchmark/docker_c2.py` exige novo label e run_id, imagem idêntica ao C2 aprovado, Git limpo e runtime sem diff desde BUILD_SHA. A bancada nova não pode existir.
- `--execute` criará Docker network e contêineres novos e fará UM snapshot e UM lote. Em erro/timeout, salvar artefatos, **não** repetir na mesma bancada; rede/contêineres ficam preservados.
- Testes sintéticos e `PLAN_ONLY` não iniciam contêineres; não se interpreta a duração de unittest como benchmark.

## Gate E11-D06 (somente verificações)

Depois de sincronizar `tcc2/desenvolvimento`, na pasta `prova-conceito`:

```powershell
python -m compileall -q benchmark tests/test_benchmark.py tests/test_benchmark_docker_c2.py
python -m unittest discover -s tests -p 'test_benchmark*.py' -v
python -m benchmark.fixtures --sizes 100 --output resultados-locais/e11-d06-fixtures-INEDITO
python -m benchmark.docker_c2 --label p01 --run-id e11-c2-p01 --fixture resultados-locais/e11-d06-fixtures-INEDITO/s100/inputs.jsonl --output resultados-locais/e11-d06-plan
```

Não usar `--execute` até a revisão das saídas. Depois de E11-D06, podemos autorizar **um único piloto C2 de 100 requisições em bancada exclusiva**, ainda fora da série estatística.

## Antes de V12

Validar C2 com imagem, entradas, oráculo e limites; comparar efeitos nos três cenários; ensaiar cargas 1.000 em novas bancadas para janelas de CPU maiores; calibrar overhead da coleta; controlar cenários por blocos e ordem; definir warmup real, como proceder com Pod client, congelar 10 repetições iniciais após piloto de variabilidade. Documentação científico-metodológica seletiva já está em `docs/tcc2/etapa-11-auditoria-seletiva-perplexity.md`.
