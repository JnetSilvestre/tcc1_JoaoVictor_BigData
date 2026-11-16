# TCC2 — Etapa 11 / E11-D10 — Auditoria de frescor da Kubelet Summary API

**Execução local:** 15/11/2026 às 23:50 (America/Sao_Paulo). **Natureza:** duas leituras SOMENTE LEITURA de métricas e consultas de segurança do cluster em namespaces históricos; não houve criação de Namespace, aplicação de YAML, snapshot, POST nem benchmark. **Base documental:** ZIP real `probe(1).zip` enviado na conversa, inspecionado e validado pelo auditor.

## 1. Proveniência e integridade

- Git HEAD reportado e gravado: `3f8e80d6c44cdc8a3a4ffbde4e48a75ae27cf828`.
- ZIP `probe(1).zip`: **15.672 bytes**, SHA-256 recalculado `dd5f29c050a985219d4d2a2bebb88d4004afa639fdf409fe0825bbbed4866d5a`, exatamente o hash da transcrição do PowerShell.
- **6 arquivos distintos**, 6/6 CRC corretos, 5/5 SHA-256 de `checksums.sha256` corretos: `c3-manifest-NOT-APPLIED.yaml`, `c4-manifest-NOT-APPLIED.yaml`, `canonical-expected.jsonl`, `canonical-inputs.jsonl`, `e11-d09-report.json` e `checksums.sha256`.
- Fixture 1000 `inputs.jsonl` SHA-256 `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551`; expected SHA-256 `430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c`. Composição 1000 mudanças solicitadas, 874 efetivas, 126 no-op, 500 transições e 250 efeitos.

## 2. Identidades, disponibilidade e isolamento

- Contexto `kind-tcc2-pon`. Nodes `tcc2-pon-worker` e `tcc2-pon-control-plane` ambos Ready. Docker local usa imagem aprov. `sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a`.
- Namespaces históricos `tcc2-pon` e `tcc2-pon-c4` presentes. Os namespaces deste planejamento `tcc2-pon-e11-c3-p20261115-235031` e `tcc2-pon-e11-c4-p20261115-235031` ainda NÃO EXISTEM; `safe_to_apply_later=false` deliberadamente no relatório.
- Os dois YAMLs foram apenas gerados localmente, sem `kubectl apply`. Cada um utiliza namespace exclusivo, três serviços e um benchmark-client com a imagem aprovada. C4 preserva o nodeSelector do logic-engine para control-plane.

## 3. Série de duas coletas históricas / repouso

- Worker primeira `captured_utc=2026-11-16T02:50:32.901415+00:00`, segunda `02:50:43.186587+00:00`, intervalo ~10,285 s.
- Control-plane primeira `02:50:33.021317+00:00`, segunda `02:50:43.289395+00:00`, intervalo ~10,268 s.
- Worker **5 contêineres com campos CPU e memória válidos**, 3/5 com timestamp de CPU distinto e aumento do contador; 2/5 permaneceram com timestamp e contador iguais. Control-plane **1 com campos válidos, 1/1 timestamp CPU distinto e aumento do contador**. Nenhuma regressão.

| Nó | Namespace | Contêiner | Avanço timestamp CPU de origem | Delta contador CPU (ns) | Idade da fonte na última captura |
|---|---|---|---:|---:|---:|
| worker | `tcc2-pon-c4` | attribute-source | 15 s | 6.894.000 | 5,187 s |
| worker | `tcc2-pon` | rule-executor | 14 s | 8.240.000 | 4,187 s |
| worker | `tcc2-pon` | logic-engine | 16 s | 9.704.000 | 1,187 s |
| worker | `tcc2-pon-c4` | rule-executor | **0 s** | 0 | **17,187 s** |
| worker | `tcc2-pon` | attribute-source | **0 s** | 0 | **12,187 s** |
| control-plane | `tcc2-pon-c4` | logic-engine | 17 s | 10.069.000 | 7,289 s |

**Observação:** CPU `0` de delta entre duas leituras em repouso NÃO representa custo zero da aplicação ou futura carga. As fontes têm cadência dispar e podem ser reutilizadas pela Summary API em consultas consecutivas; com apenas duas amostras não inferir período exato de atualização nem efeitos observadores.

## 4. Comparação documental com E11-D09

| Nó | E11-D09 (consultas separadas ~2,2 s) | E11-D10 (consultas separadas ~10,3 s) |
|---|---|---|
| worker | 0/5 timestamps CPU distintos | 3/5 timestamps distintos |
| control-plane | 0/1 | 1/1 |

Conclusão: a fonte atualiza alguns contadores ao longo de uma janela maior, sem garantia de atualização uniforme dos 4 papéis sob carga. `status=PASS_READ_ONLY` e `sampling_approved=false` estão corretos e não são contraditórios.

## 5. Decisões e próximos passos

1. **E11-D10 APROVADO** como diagnóstico read-only de acesso, integridade e avanço parcial de timestamps. Não aprovar CPU/memória como métricas científicas definitivas nem inventar custo de CPU a partir de repouso.
2. Próximo gate: **E11-D11**, preparar **somente** a nova bancada C3/1000 em namespace próprio, e confirmar Pods Ready/estado frio/identidades de imagem, sem snapshot ou carga. A preparação altera exclusivamente um namespace novo e não pode tocar namespaces históricos. Monitorar capacidade do host.
3. E11-P05: somente após auditoria do E11-D11, emitir um snapshot e uma carga C3/1000 única no novo namespace; aprovar equivalência funcional de 250 efeitos. Contadores CPU/memória permanecerão condicionais ao gate de qualidade das amostras (pode reprovar, sem invalidar automaticamente a funcionalidade).
4. C4/1000 em namespace novo diferente, após auditoria C3. **NUNCA** reexecutar a carga/snapshot em namespace já gasto.
5. Depois: calibrar observador, definir como relatar memória não equivalente, congelar repetição/ordem experimental e executar séries E11-M01 + auditoria E11-A01. Etapa 12 é análise posterior. Nodes kind são virtuais no MESMO host físico.

**A auditoria não enviou nenhuma requisição ou comando para o cluster; ZIP original preservado fora do GitHub.**
