# Etapa 07 — Fechamento funcional de C0 e C1 (12/11/2026)

**Decisão:** a implementação e validação funcional mínima da Etapa 07 está **concluída no escopo local C0/C1**, com V01–V07 aceitos **somente nas condições ensaiadas**. Persistência, concorrência arbitrária, redes distribuídas entre nós, recuperação/replay e desempenho científico **não** foram demonstrados. As etapas de Docker/Kubernetes da aplicação começam depois deste marco, sem alterar esta evidência.

## 1. Documentos e origem

- Repositório da monografia: `JnetSilvestre/tcc1_JoaoVictor_BigData`, branch exclusiva `tcc2/desenvolvimento`; `master` preservada.
- Referência do núcleo: `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`, sem mudanças no original.
- Decisões aprovadas e restrições: `docs/tcc2/etapa-04-arquitetura-distribuida.md` e `docs/tcc2/etapa-05-protocolo-experimental.md`.
- Commit **executado na máquina do acadêmico** no último ensaio: `be6b850d599504e9ea8166f02fd87b35313e5445`.
- Ambiente observado: Windows 10 (manifesto `Windows-10-10.0.19045-SP0`), Python 3.13.9, três processos Python independentes em `127.0.0.1`.

## 2. Conclusões verificadas

- Primeiro núcleo corrigido e validado: `Condition`, `Rule`, `Notifier` e `NOPManager`, com regressões reais no Windows.
- C0: fixture determinística de 7 requisições, 5 mudanças efetivas, 3 transições, **2 efeitos nos passos 3 e 7**, correspondentes ao arquivo manual e ao oráculo independente.
- C1: `attribute-source`, `logic-engine`, `rule-executor`, comunicação HTTP/JSON real em localhost, snapshot inicial, deduplicação, ordenação e saída igual a C0. Rodada anterior: **37/37 testes, 12/12 checks verdadeiros e PASS**, evidências E07-D14–D17.
- Incremento de barreira local: **38/38** testes, E07-D18.
- **Ensaio final de alteração durante confirmação do snapshot HTTP (E07-D19–D21):** `compileall=0`; `unittest` **39/39 OK em 11,152 s** (duração da suíte, **não benchmark**); `python -m c1.snapshot_race` exibiu `status: PASS`, `V07-HTTP: 0`, **7/7 checks true**, efeitos `[3,7]`.
- PIDs observados no último manifesto: produtor `1988` na porta `54912`; avaliador `15164` na porta `54910`; executor `18332` na porta `54909`. Proxy temporário do teste na porta `54911`, **não é serviço permanente**.
- Os eventos `snapshot_installed_downstream → snapshot_ack_held → concurrent_change_sent → snapshot_ack_released → concurrent_change_responded` aparecem nessa ordem em `timeline.jsonl`. O teste **segurou o ACK**, enviou o pedido por socket durante a espera e confirmou processamento posterior pelo servidor serial.

## 3. Inventário de capturas da última rodada

| Identificador | Captura enviada | Dimensões | Bytes | SHA-256 da captura original |
|---|---|---|---:|---|
| E07-D19 | `image(20261112-220939).png` | 1920 × 1080 | 151911 | `a91ba7d0052c83d4ee9bacf4a6f5ce2c759e038691fa143f3096b50b31c8be75` |
| E07-D20 | `image(20261112-220951).png` | 1920 × 1080 | 110609 | `74aacbdfb193211bcb5991f7750ac2b98567b8745a7b9605c8e532421e73c46d` |
| E07-D21 | `image(20261112-221112).png` | 1920 × 1080 | 49166 | `72a91b12881a47b55b386540bab5849e952de54d27387d38a18a107f139f98e7` |

O PowerShell criou no computador do acadêmico `resultados-locais/c1-snapshot-http-20261112-190909.zip` e exibiu SHA-256 **`E454D6051048C37CD2276BFF6ACADCFAC04E2FE03449ABCAFCCA217C07B6FBA1`**. Este valor foi **transcrito da captura**, não recalculado sobre o ZIP: o arquivo binário continua no computador do acadêmico. O print mostra também `checksums.sha256` para os artefatos da rodada; os arquivos brutos não foram auditados diretamente por esta IA. Não afirmar que os PNGs ou ZIP foram enviados ao repositório.

## 4. Matriz V01–V07 — aceite no escopo local

| Critério | Classificação | Limite |
|---|---|---|
| V01 | **Aprovado (C0)** | Mudanças efetivas e disparos conforme fixture mínima; não cobertura geral da semântica PON |
| V02 | **Aprovado (C0↔C1)** | Igualdade exata da sequência, multiplicidade e causalidade na fixture sem falha |
| V03 | **Aprovado (mensagens ensaiadas)** | Rejeição 4xx explícita sem mutação observável para entradas inválidas testadas |
| V04 | **Aprovado (localhost)** | Entrega HTTP entre três PIDs distintos, logs e IDs; não multinó |
| V05 | **Aprovado (reentrega ensaiada)** | Duplicatas não criam efeitos adicionais em processo ativo; sem exatamente-uma-vez após reinício |
| V06 | **Aprovado (lacunas/conflitos ensaiados)** | Rejeição 409 sem corrupção silenciosa; não há replay automático |
| V07 | **Aprovado (snapshot e chegada durante ACK controlado)** | Snapshot consistente, readiness, evento recebido durante ACK e processado após liberação; teste HTTP serializado, sem concorrência arbitrária |

**V11 — evidência reprodutível parcial:** comandos, códigos, manifestos mostrados, capturas e checksums inventariados. Necessita guarda permanente/transferência e auditoria independente dos arquivos brutos do ZIP para uma trilha científica mais robusta.

## 5. Decisões e limites de pesquisa

1. A implementação local em Python é **adaptação de prova de conceito**, não implementação do NOP Query C++ e não realiza consultas de vídeo.
2. Os processos HTTP executaram em **um único Windows**, não em nós Kubernetes.
3. `HTTPServer` serializa as requisições por serviço; o proxy de teste retarda a confirmação para criar uma ordenação controlada, sem provar segurança para múltiplos clientes simultâneos.
4. Sem persistência, replay pós-reinício, failover, tolerância a interrupções arbitrárias, HA nem medição de CPU/RAM/latência experimental.
5. `11,152 s` foi o tempo da suíte `unittest`, **não** latência PON, vazão ou desempenho distribuído.
6. Manter pendente a confirmação acadêmica com o orientador sobre a adequação da implementação Python e dos três serviços ao objetivo da monografia.

## 6. Entregáveis e transição

- Código Python da prova: `prova-conceito/pon`, `c0`, `c1`, `fixtures` e `tests`.
- Scripts reprodutíveis: `python -m c0.runner`, `python -m c1.runner --output <pasta_nova>`, `python -m c1.snapshot_race --output <pasta_nova>`.
- Histórico detalhado: `docs/tcc2/etapa-07-implementacao-validacao-local.md`, `etapa-07-c1-http.md`, `etapa-07-c1-snapshot-http.md`, `etapa-07-aceite-tecnico.md`.
- Arquivo ZIP da rodada C1-snapshot HTTP: **guardar original, manter hash e metadados**; se fornecido posteriormente, verificar checksums internamente, sem alterar o histórico de resultados.
- Próximo marco técnico: **Etapa 08 — Docker e C2**, com dependências/imagens fixadas e evidências locais; depois Etapas 09–10 Kubernetes/C3. Diagramas finais e capítulos experimentais somente com evidências do que for implementado nas etapas correspondentes.

**Declaração de encerramento:** a **Etapa 07 está concluída funcionalmente para a prova mínima C0/C1**. A inspeção independente dos artefatos brutos, V11 completo, decisões acadêmicas com orientador e os próximos cenários (C2/C3) são pendências explícitas, não resultados ocultos ou presumidos.


## 7. Auditoria do ZIP original — atualização posterior

Em 12/11/2026, o acadêmico anexou o ZIP original `c1-snapshot-http-20261112-190909.zip`, que foi **inspecionado diretamente**: SHA-256 `e454d6051048c37cd2276bff6acadcfac04e2fe03449abcafcca217c07b6fba1`, 5.867 bytes, CRC sem erros, **12/12 checksums internos verificados** e **20/20 checagens adicionais de consistência** aprovadas. Estados, PIDs, registros causais e efeitos dos passos 3 e 7 coincidem com os resultados anteriores.

Ver relatório `docs/tcc2/etapa-07-auditoria-zip.md`. Essa evidência **supera apenas a pendência histórica de acesso aos bytes desse ZIP**; o aceite V01–V07 permanece restrito aos cenários ensaiados e V11 continua **parcial no conjunto do TCC2**. Não foi feito novo benchmark nem execução Docker/Kubernetes.
