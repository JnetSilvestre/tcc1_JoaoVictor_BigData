# Checkpoint compacto — Etapa 08 (13/11/2026)

## Estado funcional comprovado
- Branch de trabalho: `tcc2/desenvolvimento`; preservar `master` e `codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.
- Etapa 07: C0/C1 mínimos comprovados; efeitos nos passos 3 e 7 para fixture de sete entradas; 39 testes da etapa.
- E08-I01: Git/Docker/WSL2 diagnosticados e válidos no Windows.
- E08-I02: parâmetros de hostname/interface de escuta aprovados por 42 testes `unittest` no Windows, commit `cae5f40e43bba9b1a4f01d1f4286f5e2abe0ae91`.
- E08-I03: **aprovado em E08-D08**. Build de `tcc2-pon:c2-e08-dbefcd2cf3d2` a partir do código `dbefcd2cf3d2fbf220cff8eda34d52189e08192a` completou com `Build: 0`, resolução do digest específica `Registro: 0`, Python 3.13.18, UID 10001, imports e CLI retornando 0; Linux/amd64, 176 MB. Evidências E08-D08a/b recebidas; SHA-256 no documento de diagnóstico.

## Próximo incremento: E08-I04 / E08-D09
- Configurar rede Docker interna `tcc2-pon-c2`, sem portas publicadas e sem tocar no cluster kind.
- Iniciar três contêineres independentes a partir **da mesma imagem testada**: `tcc2-c2-rule-executor`, `tcc2-c2-logic-engine`, `tcc2-c2-attribute-source`; porta interna 8080, DNS por aliases iguais aos nomes dos papéis.
- Exigir evidência real de `docker ps`, `docker network inspect`, IDs distintos, três logs `listening` e GET HTTP interno `/health/live` de origem→avaliador e avaliador→executor.
- Deixar estados não inicializados (readiness 503), sem enviar fixture nesta rodada. Não concluir equivalência C2 nesta etapa parcial.
- **E08-D09 primeira tentativa falhou antes de criar recursos:** `docker image inspect --format '{{index .Config.Labels "org.opencontainers.image.revision"}}'` retornou `template parsing error: function "org" not defined` no PowerShell. Captura `image(20261113-210012).png`, SHA-256 `4eaf907129c646850fe36ca5335c71f9073c398b0c17ce1e92e705885f796b18`. Correção: ler JSON completo com `ConvertFrom-Json`, depois comparar label. E08-D09 permanece pendente.

## E08-D09 aprovado em 13/11/2026
- Captura `image(20261113-210408).png`, SHA-256 `53ecd7f79bc5fe5c35282f3ec4ce70a55fad6f94af90581a9f6703e5228d49c1` (PNG original ainda fora do repositório).
- Rede `tcc2-pon-c2` bridge interna, três contêineres Running com IDs diferentes e sem portas publicadas. `SOURCE -> LOGIC` e `LOGIC -> EXECUTOR` responderam HTTP 200 (`live=true`); três estados `ready=false` antes do snapshot; logs listening na porta 8080.
- E08-I04 aprovado exclusivamente para implantação Docker, saúde, DNS e transporte HTTP; notificações e equivalência não verificadas.

## Próximo E08-D10
- Confirmar contêineres ativos e estados ainda não inicializados; enviar uma única inicialização `POST /init/snapshot` ao produtor e conferir encadeamento até executor.
- Exigir `ready=true` nos três, mesma versão de snapshot, valores e watermarks iniciais, zero efeitos. Não aplicar fixture ainda. Se falhar parcialmente, preservar contêineres e logs antes de outra tentativa.

## E08-D10 aprovado (13/11/2026)
- Captura original `image(20261113-210955).png`, SHA-256 `fb949fba22f6b79796adaded539f8f92a890ba3bee36b8a553ed07cab15c29af` (não versionada).
- Rede interna preservada. Três serviços passaram de `ready=false` para `ready=true` com mesmo `run_id=c0-minimo-v1` e versão `c0-minimo-v1:snapshot:0`. Atributos/seq. iniciais 0, condição false, executor sem efeitos; logs de snapshot send/mutation/ack e contêineres Up.
- **Não reenviar snapshot.** C2 não passou pela fixture.

## Próximo E08-D11
- Verificar pré-condições de zero mutações de `/attributes/change` via logs, estados iniciais e contêineres. Executar sete passos sequenciais da fixture versionada e preservar HTTP, logs, estados, SHA-256 e manifesto.
- Comparar efeitos/ordem/causalidade com `fixtures/c0_esperado.jsonl`, C0 e oráculo independente. Se falhar parcialmente, bloquear reexecução automática.

## Limitações e preservação
- Uma rede Docker/contêineres no mesmo Windows/WSL2 não constitui multinó físico.
- C2 funcional, V02/V04/V05–V07 via Docker, métricas, figuras finais e Kubernetes estão pendentes.
- Não apagar kind, contêineres anteriores ou evidências; não executar `docker system prune`.
- Documentação detalhada: `docs/tcc2/etapa-08-diagnostico-rede.md`.

## E08-D11 — ferramenta de ensaio publicada, ainda sem teste no Windows
- `prova-conceito/c2/runner.py` usa a biblioteca padrão e `docker exec` por argumentos (sem problemas de aspas PowerShell) para aplicar 7 passos somente após preflight de snapshot e logs limpos; não reinicia contêineres.
- `prova-conceito/tests/test_c2_runner.py` adiciona 3 testes de pré-condição. Esperados **45 testes** totais (42 anteriores + 3), não realizados ainda no host.
- Em caso de erro, salva logs e `validation.json` FAIL; não reexecutar a fixture automaticamente. Efeitos, C0/oráculo, estados, entradas e hashes são coletados para auditoria após o ensaio.
