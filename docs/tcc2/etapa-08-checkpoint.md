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

## Limitações e preservação
- Uma rede Docker/contêineres no mesmo Windows/WSL2 não constitui multinó físico.
- C2 funcional, V02/V04/V05–V07 via Docker, métricas, figuras finais e Kubernetes estão pendentes.
- Não apagar kind, contêineres anteriores ou evidências; não executar `docker system prune`.
- Documentação detalhada: `docs/tcc2/etapa-08-diagnostico-rede.md`.
