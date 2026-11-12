# Checkpoint compacto — Etapa 07 do TCC2 (12/11/2026)

## Base documental e versionamento
- Repositório: `JnetSilvestre/tcc1_JoaoVictor_BigData`; branch exclusiva: `tcc2/desenvolvimento`; `master` preservada.
- Referência original imutável: `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.
- Documentos normativos do projeto: `docs/tcc2/etapa-04-arquitetura-distribuida.md` e `docs/tcc2/etapa-05-protocolo-experimental.md`. Ambiente anterior: `docs/tcc2/etapa-06-preparacao-ambiente.md`.
- Histórico detalhado e evidências: `docs/tcc2/etapa-07-implementacao-validacao-local.md`.
- Nenhuma implementação em Docker/Kubernetes da aplicação na Etapa 07; figuras e capítulos LaTeX preservados.

## Evidências de execução REAL na máquina do acadêmico
- `Condition` original com erro `AttributeError` reproduzido; após correção, 3/3 regressões OK.
- Núcleo `Rule` / IDs: 11/11 regressões OK.
- Cenário C0: 18/18 `unittest` OK; `c0.runner` = PASS, duas ações nos passos 3 e 7; correspondência exata com fixture manual e oráculo independente, 7 requisições, 5 mudanças efetivas e 3 transições de condição.
- Contratos C1: em 12/11/2026, 25/25 `unittest` OK; Python 3.13.9, compilação 0, retorno de testes 0; screenshot E07-D12 `image(20261112-203727).png`, SHA-256 `a20f0d787f2ceeb7c53dbfe7c362ca14bee695a6214d2ddd1c81b2ad09680d0c`. Capturas originais ainda na conversa, não versionadas.
- Não declarar a duração do `unittest` como desempenho da aplicação.

## Código C1 atual — PENDENTE de execução na máquina
- `prova-conceito/c1/protocol.py`: contratos de mudança, snapshot, notificação de atributo e transição de condição; 7 testes de contrato já aprovados.
- `prova-conceito/c1/state.py`: novos estados `AttributeSource`, `LogicEngine`, `RuleExecutor`. Integração ainda por **callbacks em memória**, não HTTP.
- `prova-conceito/tests/test_c1_state.py`: 11 testes novos de estado, ordem, duplicata, snapshot, equivalência aos dois efeitos C0 e retry de evento com o mesmo timestamp após ACK perdido simulado.
- `seed` não é campo do contrato de mudança; o teste converte a fixture em payload removendo apenas esse metadado (commit `92f6066a4a1f2af4e89fe69f7b18e05aa22d024f`).
- **Próxima suíte prevista:** 36 testes (25 comprovados + 11 novos). Ainda **não executada** no Windows após os novos arquivos.
- Testes e modo de operação: `docs/tcc2/etapa-07-c1-estados.md`.

## Critérios ainda pendentes
- C1 real: três PIDs independentes `attribute-source` / `logic-engine` / `rule-executor`, comunicação HTTP/JSON em localhost, logs JSONL, snapshots inicializados, confronto de `effects.jsonl` com C0.
- V02–V07: equivalência, validação de 4xx sem mutação, PIDs/fluxo causal, deduplicação, sequências fora de ordem e inicialização por snapshot. Nenhum deles está aprovado na dimensão de transporte por este checkpoint.
- Sem persistência, concorrência thread-safe, replay de watermarks não nulos ou recuperação automática após falha parcial. Teste de ACK perdido é simulação **unitária**, não experimento real de rede.
- Após completar C1 e capturar evidências, concluir Etapa 07 com inventário de fontes, testes, limites e commits; Docker/Kubernetes da aplicação permanecem para Etapas 08–10.

## Próxima execução do acadêmico
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
git status --short
```

**Esperado, não observado ainda:** `Ran 36 tests` e `OK`; em caso de falha, preservar traceback e captura completa antes de alterar código.

## E07-D13 — validação das máquinas de estado (12/11/2026)

Captura original do PowerShell do acadêmico: `image(20261112-204915).png`.
SHA-256: `c1a9fdb5fedd4a144a01d4b392b271bfba4dd5f37c8bc240e5534780726a7f69`.
Branch `tcc2/desenvolvimento`, HEAD `52dd849727f179ec938172def7c37daeecec302b`,
Python 3.13.9, `compileall` retorno 0, 36/36 `unittest` OK em 0.471 s, retorno 0.
O tempo é da suíte. A evidência cobre as máquinas de estado em memória.
