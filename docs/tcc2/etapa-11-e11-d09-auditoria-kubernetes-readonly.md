# TCC2 — Etapa 11 / E11-D09: auditoria real do diagnóstico Kubernetes C3/C4/1000

**Data local do PowerShell:** 15/11/2026, 23:44 America/Sao_Paulo. **Evidência primária:** ZIP real `probe.zip` recebido na conversa; inspecionado por leitura direta de arquivo ZIP, com CRCs, SHA-256 e conteúdo JSON/YAML. Nenhum benchmark, snapshot, apply, criação ou remoção de Pod foi executado nessa auditoria.

## 1. Integridade documental

- ZIP original: **15.632 bytes**. SHA-256 recalculado `3d348be564c20282473d120147a1d86f0347f8d7a47d2a5bb312b9c56e471636`, corresponde exatamente ao SHA-256 exibido no PowerShell.
- **6 arquivos** únicos internos, **6/6 CRC válidos**, **5/5 SHA-256** listados em `checksums.sha256` válidos. Entradas: `c3-manifest-NOT-APPLIED.yaml`, `c4-manifest-NOT-APPLIED.yaml`, `canonical-expected.jsonl`, `canonical-inputs.jsonl`, `checksums.sha256`, `e11-d09-report.json`.
- Git HEAD reportado e gravado em JSON: `70714f545a1dc4dc2b192a2833a446f2ef8b5462`. Python compileall passou, **33/33 testes sintéticos** PASS (0,177 s = tempo de testes, NÃO benchmark). Primeira execução PLAN_ONLY e segunda `--probe`: nenhuma chamada mutante conforme código e relatório.
- SHA-256 canônico inputs 1000 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; oracle `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`. Futuros runs rebaseados terão hashes próprios.

## 2. Plano YAML C3/C4

| Cenário | Namespace EXCLUSIVO proposto, NÃO criado | Run ID |
|---|---|---|
| C3 | `tcc2-pon-e11-c3-p20261115-234409` | `e11-c3-p20261115-234409` |
| C4 | `tcc2-pon-e11-c4-p20261115-234409` | `e11-c4-p20261115-234409` |

- Manifestos YAML no ZIP têm **7.550 bytes (C3) e 7.945 bytes (C4)**, respectivamente; oito campos `namespace:` por arquivo, todos referindo o namespace exclusivo. Quatro imagens aprovadas por YAML (3 serviços e um cliente), sem referência exata a `namespace: tcc2-pon` ou `namespace: tcc2-pon-c4`; `e11-benchmark-client` presente; sem comandos `kubectl apply/create`. Verificações locais de `validate_manifest` constam no relatório. Não foram submetidos à admissão Kubernetes nem aplicados.
- Ambos os planos esperam **1000 POST, 874 mudanças, 126 no-ops, 500 transições e 250 efeitos**, estado final `atA=10`, `atB=0`.

## 3. Estado do cluster (leitura real)

- Contexto: `kind-tcc2-pon`; **dois nós Ready**: `tcc2-pon-worker` e `tcc2-pon-control-plane`. Kubelet **v1.37.0** e containerd **2.3.4** registrados; kernel WSL2 **6.18.58.1-microsoft-standard-WSL2**, nodes virtuais no MESMO host. `allocatable.cpu=8` em ambos os nós NÃO prova 16 CPUs físicas independentes: compartilham o host.
- Namespaces históricos `tcc2-pon` e `tcc2-pon-c4` presentes. Namespaces candidatos de C3/C4 ainda AUSENTES (portanto não houve aplicação). `safe_to_apply_later=false` reportado explicitamente, pois a aprovação do diagnóstico não libera aplicação.
- Docker local manteve imagem aprovada, ID `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.

## 4. Kubelet Summary API: alerta em AMBOS OS NÓS

Resumo de duas consultas em repouso com intervalo de aproximadamente **2,2 segundos** entre capturas no mesmo nó:

| Nó | Pods/contêineres históricos observados | CPU com campo válido | Memória com campo válido | Timestamps CPU distintos entre consultas |
|---|---:|---:|---:|---:|
| worker | 5 | 5 | 5 | **0/5** |
| control-plane | 1 | 1 | 1 | **0/1** |

- Não houve regressões dos contadores de CPU nem timestamp de origem. Mas os **seis contadores cumulativos permaneceram exatamente iguais** entre as consultas, assim como os timestamps de memória. A validade sintática dos campos não implica frescor temporal.
- Capturas worker: **2026-11-16T02:44:12.806780+00:00** e **02:44:15.067012+00:00**; idade do timestamp CPU observada de aproximadamente **0,807 s a 12,067 s**, dependendo do Pod e leitura.
- Capturas control-plane: **02:44:12.938692+00:00** e **02:44:15.163115+00:00**; `logic-engine` histórico com `cpu_time_utc=02:43:58Z` nas duas; idade aproximada **14,939 a 17,163 s**.
- `PASS_READ_ONLY_WITH_TIMESTAMP_WARNING` é, portanto, consistente com os dados brutos. `sampling_approved=false` continua correto. Não há erro de rede nem evidência de falha operacional dos serviços apenas por esse alerta.
- Não é possível concluir se os timestamps vão progredir durante carga de 1000, nem inferir intervalo de atualização estável com duas consultas ociosas. É metodologicamente inválido usar diferenças iguais a zero em estados ociosos como custo CPU de futuras cargas.

## 5. Decisão e próximos passos

1. **E11-D09 aprovado para integridade, segurança e acessibilidade da Summary API, com ressalva de frescor temporal nos DOIS nós.** Os manifests são candidatos tecnicamente coerentes, mas NÃO liberados para apply automático.
2. Fazer **E11-D10 adicional e somente leitura**: repetir `benchmark.kube_preflight` com novo label/output e `--interval 10` (limite já suportado) para estudar se os timestamps históricos avançam numa janela mais longa; nenhuma criação/POST. Não reutilizar output E11-D09, e não mexer nos namespaces históricos.
3. Se permanecerem congelados em repouso, isso não invalida a comparação primária de **RTT e vazão**, que usa o relógio do cliente dentro do Pod, mas impede afirmar qualidade de CPU/memória apenas com base em Summary API. Decidir então entre pilotos funcionais 1000 com CPU secundária explicitamente não aprovada, ou novo instrumento calibrado.
4. Só após avaliação da sequência instrumentada e controles de cluster, autorizar E11-P05 C3/1000 e E11-P06 C4/1000, em **namespaces novos**, um de cada vez. A medição `measurement_approved`/`usable_cpu` não pode ser inferida de `PASS_READ_ONLY`.
5. Séries E11-M01 e auditoria E11-A01 ainda pendentes; V12 não iniciado. Não concluir efeito causal puro do Kubernetes ou distribuição entre hosts físicos.

**Fonte:** somente ZIP real e transcrição PowerShell. O ZIP bruto original permanece fora do repositório; este laudo é versionado para rastreabilidade.
