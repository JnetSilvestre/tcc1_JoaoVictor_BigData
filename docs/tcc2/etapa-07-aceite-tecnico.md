# TCC2 — Etapa 07: pré-encerramento técnico e matriz de aceite (12/11/2026)

**Status:** C0 e C1 mínimos comprovados no Windows por capturas de terminal; V01–V06 aprovados **no escopo dos testes especificados**, V07 **parcial** com lacuna de concorrência HTTP durante inicialização. Não declarar a Etapa 07 encerrada irrestritamente até registrar o teste complementar e o aceite final. **Nenhum desempenho distribuído foi medido.**

## 1. Fontes e revisões

- `JnetSilvestre/tcc1_JoaoVictor_BigData`, exclusivamente branch `tcc2/desenvolvimento`.
- Revisão **efetivamente testada no Windows para C1**: `f37dbc998eb5114a60335f5275c86b6e8bedee61` (manifesto).
- Referência congelada: `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` (sem modificação da origem).
- Decisões das Etapas 04/05 preservadas. Registros completos em `docs/tcc2/etapa-07-implementacao-validacao-local.md`, `etapa-07-c1-http.md`, `etapa-07-checkpoint.md`.
- A alteração mais recente em `tests/test_c1_state.py` acrescenta teste unitário de barreira de snapshot, **ainda sem execução no Windows**. A revisão testada `f37dbc...` permanece identificada para não misturar evidências.

## 2. Resultados observados do acadêmico

- Ambiente: Windows 10, Python 3.13.9, `compileall: 0`.
- Suíte: **37/37** `unittest` aprovados, tempo do framework **7,388 s** (não é benchmark).
- `python -m c1.runner`: **C1: 0**, `status: PASS` e **12/12** verificações verdadeiras.
- Três processos HTTP/JSON em `127.0.0.1`: PID 20472/porta 52911 (attribute-source), PID 19548/porta 52910 (logic-engine), PID 22276/porta 52909 (rule-executor).
- `run_id=c0-minimo-v1`, `seed=20260501`. Dois efeitos nos **passos 3 e 7**, iguais à fixture manual, C0 e oráculo independente.
- Sondas de prontidão, rejeição de mensagens inválidas, reentrega e sequências com lacuna constam como verificações verdadeiras.
- Sem Docker/Kubernetes da aplicação; sem execução distribuída entre nós; sem tolerância a falhas/replay/persistência comprovados.

## 3. Evidências de screenshots e arquivamento

| ID | Arquivo (captura na conversa) | SHA-256 do PNG verificado | Resultado |
|---|---|---|---|
| E07-D14 | `image(20261112-210144).png` | `9dadee3396b98d554eab392d70b47780643fb16089656d2f7b22be6e0964ad27` | Git fast-forward, 37 testes de integração iniciados, revisão do projeto |
| E07-D15 | `image(20261112-210212).png` | `38eab7a9468ce68b7a6fd9660c1ffe0c0bd0639e6a88f94586337b012deb9003` | 37/37 OK, `C1: 0`, `status=PASS`, 12/12 verificações verdadeiras, manifesto e PIDs |
| E07-D16 | `image(20261112-210250).png` | `81ef8d4f0987fb596c5d677aa193567cca2a3884f63a64be58ff0c32e731f037` | `checksums.sha256` dos artefatos da rodada |
| E07-D17 | `image(20261112-214847).png` | `e7b9bd7ad6545c9321aeee05655af9ee892be774c7e98b4704451c327f303bbe` | `Compress-Archive` e hash SHA-256 do arquivo ZIP local |

**Hash do ZIP mostrado pelo PowerShell, não verificado por acesso aos bytes do arquivo:** `D7A62AC62AFA23302F272D303E00DB6B622B92FA04E5B3B7F1DE7367BF735D17`. O comando selecionou a pasta C1 mais recente e criou um ZIP ao lado dela. O nome completo do ZIP não está legível no print, pois a coluna `Path` aparece truncada. As capturas estão anexadas à conversa, não armazenadas no GitHub; o ZIP continua no host Windows do acadêmico.

## 4. Matriz V01–V07 com delimitação científica

| Critério | Classificação nesta Etapa 07 | Fundamento e limite |
|---|---|---|
| V01 | **Aprovado na fixture mínima** | Notificação por mudança real, transições e dois efeitos nos passos 3/7; C0 e regressões locais |
| V02 | **Aprovado em C0↔C1** | C1 e C0 idênticos ao esperado/oráculo em multiplicidade, ordem e causalidade, `matches_c0`, `matches_manual`, `matches_oracle` verdadeiros |
| V03 | **Aprovado para payloads ensaiados** | Erros 422 para campos/tipos/versão, estado preservado; não é auditoria completa do protocolo |
| V04 | **Aprovado em localhost** | 3 PIDs reais distintos (`attribute-source=20472`, `logic-engine=19548`, `rule-executor=22276`), eventos correlacionados via HTTP/JSON e logs; sem distribuição em nós separados |
| V05 | **Aprovado para reentregas ensaiadas** | Mesmos eventos/request IDs deduplicados sem efeito adicional; não comprova exatamente-uma-vez após falhas/reinício |
| V06 | **Aprovado para lacunas/conflitos ensaiados** | HTTP 409 sem alteração de estado para gaps e reuso de IDs; replay não implementado |
| V07 | **Parcial — complementar** | Snapshot inicial, readiness 503 antes da instalação, watermarks zero e bloqueio pré-inicialização validados; **alterações concorrentes durante a instalação do snapshot no transporte HTTP não foram testadas diretamente**. Há novo teste unitário de barreira local publicado, ainda sem execução Windows |
| V11 (controle auxiliar) | **Parcial** | Manifesto, revisões, hashes e prints; ZIP local com SHA exibido, sem inspeção direta dos bytes nem cópia no repositório |


Os códigos HTTP observados foram produzidos pelo roteiro de testes da fixture e avaliados no relatório C1. A aprovação é **de uma configuração serial em localhost**, não prova de correção geral para múltiplos clientes simultâneos ou falhas de rede arbitrárias.

## 5. Ponto pendente e sequência de fechamento

1. Sincronizar a branch após este relatório e executar a suíte ampliada, agora **38 casos previstos** (37 anteriores + teste determinístico de barreira durante snapshot).
2. Preservar screenshot, SHA da revisão, `Compilacao`/`Testes`, erro completo se houver falha. O teste novo é local em memória; não substitui experiência de concorrência HTTP real.
3. Deliberar/documentar teste controlado de alteração durante instalação de snapshot HTTP para completar o texto integral de V07 da Etapa 05. Não alegar proteção de perdas na presença de concorrência sem esse ensaio.
4. Guardar ZIP original em local estável e copiar o SHA acima para inventário do TCC2. Se disponível, validar depois seu conteúdo via checksums dos arquivos internos.
5. Após aceitar limites com evidências, registrar revisão final e marcar a Etapa 07 como concluída para C0/C1. Etapas 08–10 tratarão Docker/Kubernetes da aplicação; as métricas experimentais e figuras definitivas ficam para as etapas previstas.

## 6. Limites acadêmicos persistentes

A adaptação Python não demonstra equivalência integral ao NOP Query C++ nem processamento de vídeo. A divisão em três processos exige confirmação do orientador. **Não** apresentar o tempo de `unittest`, o teste local de ACK perdido ou os resultados de localhost como desempenho de cluster, alta disponibilidade ou distribuição multinó.


## 7. Evidência adicional E07-D18 e teste de transporte V07

**E07-D18 — captura original do PowerShell:** `image(20261112-215913).png`, dimensões 1920 × 1080, tamanho 150.253 bytes, SHA-256 **calculado sobre os bytes da imagem recebida**: `538070b0635b8a078750f745071a2b459fd3d9aae7610ff44b49b879d51808b9`.

Resultados observados no Windows: branch `tcc2/desenvolvimento`, HEAD `3742a852a7b448f15a998b18207a02765954019c`, Python 3.13.9, `Compilacao: 0`, `Ran 38 tests in 7.354s`, `OK`, `Testes: 0`. O teste `test_change_during_snapshot_handshake_is_rejected_before_ack` aparece com `ok`. **Esse teste é local em memória e não prova concorrência HTTP**. A duração é da suíte `unittest`, não benchmark do PON. A imagem foi enviada nesta conversa e ainda não é um arquivo bruto do repositório.

O teste de barreira local de snapshot foi aprovado em 38/38 regressões. Esse resultado **não remove por si só a pendência de V07 em HTTP** registrada na matriz acima.

Foi acrescentado um ensaio de integração de transporte controlado com três PIDs reais e um proxy de teste de ACK, descrito em `docs/tcc2/etapa-07-c1-snapshot-http.md`. Ele faz chegar uma requisição de atributo ao socket do produtor enquanto a confirmação do snapshot está pendente, verifica a ordem por linha do tempo, executa os passos restantes da fixture e compara os dois efeitos ao esperado. **Nova suíte: 39 casos previstos, ainda sem execução Windows.** Mesmo após eventual sucesso, tratar como uma chegada serializada durante handshake, não como garantia geral de concorrência.


## 8. Atualização conclusiva após evidências E07-D19–D21 (12/11/2026)

**A matriz da seção 4 era uma avaliação intermediária** (V07 parcial). Após a execução real do ensaio HTTP de barreira, a classificação **mais recente** de V07 é: **aprovado apenas para chegada controlada de requisição durante espera do ACK do snapshot, processada em servidor HTTP serial**. As demais classificações de V01–V06 seguem válidas apenas no escopo ensaiado; não há garantia de concorrência geral.

- Código de referência e revisão executada: `be6b850d599504e9ea8166f02fd87b35313e5445`.
- Suite do Windows: **39/39 OK em 11,152s**, compilação 0, `V07-HTTP: 0`, sete checks do relatório `true`, efeitos nos passos 3/7 e três PIDs distintos. As capturas E07-D19–D21 comprovam a execução.
- `timeline.jsonl`: `snapshot_installed_downstream` → `snapshot_ack_held` → `concurrent_change_sent` → `snapshot_ack_released` → `concurrent_change_responded`.
- ZIP local com hash exibido `E454D6051048C37CD2276BFF6ACADCFAC04E2FE03449ABCAFCCA217C07B6FBA1`; sem acesso direto ao binário ou auditoria independente.
- **Relatório final e limites:** `docs/tcc2/etapa-07-encerramento-funcional.md` contém classificação V01–V07, evidências E07-D19–D21 e pendências V11/academia. Não confundir este marco local com teste de Kubernetes ou desempenho distribuído.
