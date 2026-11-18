# TCC2 — E11-M00F — Procedimento de execução controlada de retirada C2-S01

**Data de elaboração:** 17/11/2026 (America/Sao_Paulo). **Estado:** `IMPLEMENTADO / REGRESSAO_WINDOWS_PENDENTE / EXECUCAO_NAO_AUTORIZADA`.  
**Escopo:** **exclusivamente** a rede e os quatro contêineres novos da qualificação sacrificial `e11-c2-m01-s01`. **Não** são objetos da matriz definitiva de 30 lotes. Não altera código funcional PON, imagens, Kubernetes, pilotos antigos ou dados experimentais.

## 1. Evidências e autorização

- A saída PowerShell do acadêmico do commit `53b2520cb60fd6f3265a71f4433c2533445947fd` confirmou `Ran 106 tests in 0.223s`, `OK`, `REGRESSAO: PASS` e prévia **real** `RETIREMENT_PREVIEW_READONLY_PASS_NOT_AUTHORIZATION`, `PREVIA SOMENTE LEITURA: PASS`.
- ZIP principal e backup em volume D têm SHA-256 **`6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6`**, 26 membros, e prévia sem recursos novos extras.
- A prévia real listou os IDs imutáveis abaixo. **O novo executor possui os IDs FIXADOS no código, não recebe nomes/IDs variáveis na CLI.** Uma mudança de ID ou label torna o procedimento inválido; **não adaptar hashes/IDs para forçar liberação**.

| Recurso novo exclusivamente permitido | ID imutável (SHA Docker) |
|---|---|
| Rede `tcc2-pon-e11-c2-m01-s01` | `0748fe465ec0d1cf31302808b403bdf85522fd70305f30e6067d4c58737f18ae` |
| `attribute-source` | `56439673aed7c8c19cf2b365cfa26c445cf7a59d47e7f73989957d6f7b7dd4b0` |
| `logic-engine` | `a0cf7976754f5628e26d5bc1f26ac47a1f866ccb357214b58c48aa04ffbefe32` |
| `rule-executor` | `2cb6bc4bf321141b2e07ce7b9cb4c7162e2ae72b26c40554c2385bbb55501ac9` |
| `benchmark-client` | `6dbbf1bce2f82a931530fc8fa19703a87debf244879af227750c0f672bbaaae0` |

**Nenhuma retirada foi autorizada pela saída `PREVIA: PASS`.** Para operação mutante posterior, é imprescindível (a) regressão sintética da versão atual, (b) prévia real PASS sem recursos concorrentes, (c) acordo/aceite explícito do operador **para estes cinco IDs**, (d) SHA completo do código testado, (e) ZIP original/cópia íntegros e (f) diário exclusivo em D: ainda inexistente.

## 2. Ferramenta `benchmark/retirement_execute_c2_s01.py`

- Sem `--execute`: executa **somente** o planejador `plan_s01_retirement`; nunca interrompe, remove, reinicia ou cria contêineres.
- Com `--execute`: exige `--approve AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C2_M01_S01` **e** `--approved-head <SHA40 do código efetivamente testado>`, além de Git limpo/branch `tcc2/desenvolvimento`.
- A ação começa com revalidação ZIP e backup em volumes lógicos separados, labels `tcc2.e11/campaign=m01` e `tcc2.e11/run-id=e11-c2-m01-s01`, topologia do Docker, 4 contêineres novos em execução, inventário de **todos** os contêineres (inclusive parados), ausência de outras redes `m...` e namespaces novos, identidades/IDs da rede e endpoints; exige os cinco IDs imutáveis acima.
- Registra **antes de cada mutação** em journal JSONL exclusivo em D: `D:\TCC2-Backup\E11-M00E\C2-m01-s01-retirement.jsonl` (`open('x')`, flush+fsync). Journal existente bloqueia repetição mesmo após falha parcial.
- Ordem fixa de paradas, por **ID completo**, com `docker container stop --time 10`: `client`, `attribute-source`, `logic-engine`, `rule-executor`; reconsulta identidade/labels/estado antes e depois de cada comando.
- Depois de todos parados, removem-se **somente esses quatro IDs**, com `docker container rm <id_completo>`, após inspeção de estado parado. Valida ausência do nome removido antes do seguinte.
- Rede é removida **somente após** confirmar `Containers` vazio e mesmo ID/labels, com `docker network rm <id_completo>`.
- Todos os comandos são disparados individualmente. Não há `docker system prune`, `docker rm -f`, `docker container prune`, `kind delete`, `kubectl delete`, operações por prefixo wildcard, reuso de IDs históricos, comandos de reinício ou limpeza de arquivos de evidências.
- Qualquer exceção interrompe imediatamente; grava `INTERRUPTED_DO_NOT_RETRY` quando possível, sem auto-rollback, retry ou intervenção sobre históricos. **Poderá existir estado parcial**, que exige análise específica dos IDs/journal antes de qualquer nova operação. A ferramenta intencionalmente não é genérica para as outras 29+ bancadas.

**Risco residual:** qualquer desmobilização destrói o estado volátil da qualificação já encerrada, ainda que os ZIPs/backup sejam preservados. Volumes C/D não têm independência física de hardware comprovada. O sistema operacional/Docker podem interromper containers por desligamentos; caso sejam encontrados parados, sem o estado esperado ou com IDs diferentes, o executor deve **falhar fechado sem remover nada**.

## 3. Gate de teste antes da autorização

O código novo adiciona `tests/test_benchmark_retirement_execute_c2_s01.py` com **10 cenários sintéticos** de permissão recusada, SHA/IDs divergentes, label/rede suspeita, journal existente, falha parcial e execução bem-sucedida mockada com exclusivamente os 9 comandos permitidos (4 stops, 4 removals, 1 network rm). Testar `compileall`, `unittest` e prévia `python -m benchmark.retirement_execute_c2_s01 --primary ... --backup ...`, **sem `--execute`**, no commit exato.

**Quantidade prevista:** **116 casos** (106/106 PASS anteriores + 10 novos); esse resultado é **estimativa, não execução**. Mesmo com 116 PASS, não há autorização automática para stop/rm. Após receber o PASS e a prévia read-only, exigir aprovação específica do operador para a desmobilização dos cinco IDs listados; só então fornecer o comando mutante final. O operador deverá executar uma única vez e fornecer o journal/saída para homologação.

## 4. Encaminhamento

- `E11_M00F_RETIREMENT_EXECUTOR_PREPARED_UNTESTED`: preparações documentais/código.
- `C2_S01_106_TESTS_AND_READONLY_PREVIEW_PASS`: evidência real anterior.
- `C2_S01_RETIREMENT_EXECUTION_NOT_AUTHORIZED`: **nenhum stop/rm/delete foi executado**.
- `E11_M01_MAIN_SERIES_BLOCKED`: novas qualificações C3/C4 e os blocos definitivos dependerão de conclusão segura desta fase e protocolo próprio de desmobilização com namespaces UIDs.

O pré-registro experimental E11-M00-v1 continua válido; nenhuma amostra C2-S01 entra nas 30 rodadas principais.
