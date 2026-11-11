# STATUS ATUAL — TCC2

Atualizado em: 2026-11-11

## Etapas
- Etapa 02: concluída, conforme informação do acadêmico.
- Etapa 03: concluída, commit de referência `2eb080b93a38db47ea1149bb660a5379c6478bd4`.
- Etapa 04: concluída como **especificação arquitetural**, sem implementação nem validação experimental.
- Próxima: **Etapa 05 — Planejamento da metodologia e dos experimentos**.

## Repositórios e branches
- Monografia: `JnetSilvestre/tcc1_JoaoVictor_BigData`.
- Branch de trabalho permanente: `tcc2/desenvolvimento`.
- Marco histórico preservado: `tcc2/etapa-03-fundamentacao`.
- `master` permanece reservada para a integração ao fim do TCC.
- Código experimental: `JnetSilvestre/codigoPon`, `main`, commit `c2d525b5c675820806af34348e259bff32a6bc5f`.

## Entregáveis
- `docs/tcc2/etapa-04-arquitetura-distribuida.md`: arquitetura proposta, diagrama Mermaid, contratos JSON/HTTP, estado, riscos e critérios V01-V12.
- `capitulos/cap-proposta.tex`: seção adicionada sobre arquitetura Python; texto aprovado anteriormente preservado.
- Arquivos do repositório `codigoPon`: **não modificados**.

## Decisões provisórias
- Três serviços: `attribute-source`, `logic-engine`, `rule-executor`.
- Transporte inicial por HTTP/JSON, via Services internos de Kubernetes.
- Uma réplica por papel até existir particionamento e sincronização de estado.
- Carga determinística e oráculo local; validação do comportamento antes de alegar viabilidade.
- Sem incluir vídeos, reconhecimento de objetos, Kafka ou banco de dados na prova mínima.

## Pendências
- Orientador: confirmar aderência da prova Python e da divisão proposta ao escopo.
- Corrigir e testar `Condition`, `Rule` e registro/propagação de IDs no núcleo.
- Implementar serviços, adaptadores de comunicação, tratamento de duplicatas e snapshots.
- Definir protocolo da Etapa 05, hardware da Etapa 06 e executar testes nas etapas posteriores.
- Converter o diagrama de especificação em figura definitiva para LaTeX quando houver implementação validada.
- Compilação LaTeX/Overleaf: **não executada nem atestada nesta etapa**.
- Exclusão da branch histórica: não realizada; o novo ramo passa a ser o de trabalho, mantendo o antigo como referência.

## Próxima conversa
TCC2 — Fase II | Etapa 05: Planejamento da metodologia e dos experimentos. Usar as decisões e critérios V01-V12 do arquivo da Etapa 04, preservar os objetivos aprovados e especificar entradas, cenários, oráculo, critérios de aceitação, medições e evidências de distribuição efetiva.
