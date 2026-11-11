# TCC2 — Etapa 05: protocolo de metodologia e experimentos

**Data:** 2026-11-11. **Estado:** protocolo planejado, sem testes executados.  
**Branch:** `tcc2/desenvolvimento`. **Origem:** `docs/tcc2/etapa-04-arquitetura-distribuida.md`, critérios V01–V12.  
**Código-base:** `JnetSilvestre/codigoPon`, `main`, `c2d525b5c675820806af34348e259bff32a6bc5f` (referência histórica da inspeção, não garantia de HEAD atual).

## 1. Pergunta, escopo, hipóteses e variáveis

**Questão central:** a prova Python pode preservar a semântica de notificações e executar seus componentes como serviços independentes orquestrados pelo Kubernetes, com registros verificáveis da comunicação, do isolamento e da organização?

**Objetivos aprovados (não reescritos):** analisar o PON e a prova; conteinerizar e projetar a infraestrutura; implantar e executar distribuído avaliando comunicação, isolamento e organização; registrar limitações e oportunidades. O desempenho é observação complementar, não requisito de ganho.

**H1 (funcional):** para a mesma sequência de entrada e estado inicial, execução local e distribuída produzem os mesmos eventos de efeito em ordem lógica. **H2 (operacional):** os serviços independentes são implantados e trocam notificações em Kubernetes. **H3 (exploratória):** custos/latência podem variar com o ambiente e a carga, sem direção presumida. Falhas de H1/H2 são resultados válidos e deverão ser registradas.

Variáveis controladas: código e imagem por SHA/digest, sequência de entrada, oráculo, definição das condições, semente, estado inicial, limites e solicitações de CPU/RAM, número de réplicas (1 por papel), versões e topologia. Independentes: ambiente C0–C4, nível de carga C5, eventualmente presença de falha provocada. Dependentes: correção/efeitos, eventos enviados/recebidos/descartados, erros, estado, latência, tempo decorrido, CPU, RAM, bytes de rede. Limitações: virtualização multinó não equivale a máquinas físicas; Python não equivale ao NOP Query C++.

## 2. Arquitetura experimental e cenários

- **C0 — oráculo local:** núcleo PON em um processo, entradas determinísticas, saídas estruturadas.
- **C1 — multiprocesso:** `attribute-source`, `logic-engine` e `rule-executor` em processos distintos, HTTP/JSON, sem Docker.
- **C2 — Docker:** mesmos três serviços e entradas em contêineres separados; comunicação em rede interna.
- **C3 — Kubernetes funcional:** Namespace `tcc2-pon`; um Deployment/Pod e um Service ClusterIP por papel; ConfigMap, probes e Job gerador se implementados.
- **C4 — multinó condicional:** posicionar e registrar ao menos produtor e avaliador em nós Kubernetes distintos. Se indisponível, declarar somente separação de processos/Pods e não afirmar distribuição física entre máquinas.
- **C5 — carga complementar:** executar, após aprovação dos testes funcionais, C0 e C3 em carga pequena, média e alta, mantendo as mesmas entradas e recursos documentados; não confundir diferença de overhead de ambiente com speedup por paralelismo. Não escalar réplicas de componentes com estado sem particionamento por cadeia e roteamento demonstrados.
- **F1 — reinício controlado:** experimento separado, após implementar replay integral ou snapshot/replay correto; sem persistência, não alegar continuidade nem alta disponibilidade.

## 3. Conjunto de dados determinístico e oráculo

Criar fixture versionada JSONL/CSV com `run_id`, `request_id`, `entity_id`, `value`, `step` e `seed`. Usar, inicialmente, dois atributos inteiros `atA` e `atB` com premissas `atA >= 5`, `atB == 1`, condição `P1 AND P2` e disparo de ação **apenas na transição falso→verdadeiro**. Inicialização `atA=0`, `atB=0`; snapshot de versão e números de sequência consistente. Este é um **caso de teste proposto**, não representação de uma consulta de vídeo.

Fixture mínima planejada, nesta ordem (mesmo `run_id`):
1. `atA=0` (sem mudança → sem AttributeChanged);
2. `atA=5` (mudança, condição permanece falsa);
3. `atB=1` (condição falso→verdadeiro → exatamente 1 efeito);
4. `atB=1` (sem mudança → nenhum efeito novo);
5. `atA=6` (mudança, condição continua verdadeira → nenhum efeito novo);
6. `atB=0` (verdadeiro→falso, sem efeito);
7. `atB=1` (falso→verdadeiro → exatamente mais 1 efeito).

**Oráculo esperado:** dois efeitos no total, causados pelos passos 3 e 7, nessa ordem, desconsiderando timestamps, IDs de Pod, latência e diferenças não semânticas. Os identificadores derivados do contrato devem ser determinísticos e correlacionáveis; a comparação deve preservar multiplicidade e ordem, não apenas comparar conjuntos.

**Níveis de carga (propostos, sujeitos ao inventário de hardware na Etapa 06):** S = 100, M = 1.000, L = 10.000 alterações de entrada, geradas de forma determinística com sementes fixas 20260501, 20260502, 20260503. Distribuição de valores, proporção de alterações efetivas, ordem e hash SHA-256 dos fixtures devem ser registrados antes da primeira medição. Reduzir L se ocorrer limite de recurso, justificando por registro versionado antes da análise. Cada fixture deve ter arquivo de resultados esperados gerado por oráculo validado e revisão manual dos casos mínimos, não por copiar a saída da implementação distribuída.

## 4. Matriz V01–V12 — procedimento e critério de aceitação

| ID | Teste/entrada | Resultado esperado e aceitação | Evidência |
|---|---|---|---|
| V01 | Fixture mínima; valores repetidos e transições | Nenhuma notificação para valor idêntico; somente mudanças pertinentes atravessam Attribute→Premise→Condition→Rule→Action; exatamente 2 efeitos | testes unitários, asserts, JSONL |
| V02 | Mesma fixture em C0 e C1–C3 | Sequência de efeitos, quantidade e causalidade **idênticas** ao oráculo; zero perdas/duplicações não esperadas em rodada sem falha | diff normalizado por `run_id`, saída e hashes |
| V03 | JSON válido, ausência de campos, tipo inválido, `schema_version` inadequado, ID desconhecido | Aceitar válidos; rejeitar inválidos por 4xx explícito; **nenhuma alteração de estado** em requisição rejeitada | respostas HTTP e estado antes/depois |
| V04 | Enviar mudança e rastrear o mesmo `event_id` | Logs vinculam origem, recebimento e causa em serviços e PIDs distintos; em C2/C3 contêineres distintos | logs JSONL, PID, container/pod UID |
| V05 | Reenviar `event_id` de atributo e de condição | No máximo uma aplicação e um efeito por transição; repetição produz confirmação/indicação de duplicata sem novo efeito | ledger de IDs, logs, contagem |
| V06 | Enviar sequências fora de ordem e com lacunas | Duplicata/atrasada detectada; lacuna bloqueada ou ressincronizada explicitamente; sem estado silenciosamente corrompido | resposta, último `sequence`, estado |
| V07 | Inicializar C1/C3 com snapshot; alterações durante inicialização | Snapshot e watermark coerentes antes do processamento incremental; resultado igual ao oráculo, sem janela de perda | `snapshot_version`, sequências, trace |
| V08 | Implantar C3 e submeter fixture | Deployments disponíveis, probes operacionais e comunicação via Services internos comprovada; resultado V02 | `kubectl get deploy,pods,svc -o wide`, logs |
| V09 | Rodar C4 se houver >=2 nós prontos | IDs de nós distintos para serviços participantes e troca de eventos correlacionada; se não, **não testável** (sem falsa aprovação) | `kubectl get pods -o wide`, nodes |
| V10 | Reinício de componente durante fixture separada | Com replay completo, resultado final igual ao oráculo; se sem mecanismo, falha/perda observada é registrada e critério de recuperação **não atendido** | eventos, restartCount, replay/logs |
| V11 | Repetição por terceiro a partir da documentação | SHA, imagens, manifests, fixtures, seeds, topologia, logs e comandos suficientes para refazer as rodadas e confrontar saídas | manifesto de execução, checksums |
| V12 | Medidas C0/C3 e C5, se instrumentadas | Séries com unidades, ponto de medição, ambiente, variabilidade e dados brutos; **não exigir melhoria** | CSV/JSONL e scripts de análise |

**Classificação da avaliação:** aprovado, reprovado, não executado ou não aplicável (com justificativa). V01–V08 e V11 compõem o núcleo de validação funcional; V09 depende de multinó; V10 mede capacidade de recuperação de forma transparente e não impede caracterizar execução normal; V12 é complementar. Não converter `não executado` em `aprovado`.

## 5. Instrumentação e métricas

Logs de cada serviço em JSONL com UTC ISO-8601, `run_id`, `event_id`, `caused_by`, `entity_id`, `sequence`, `service`, `pod_uid` ou `container_id`, `pid`, `event_type`, `status`; registrar só payload necessário, sem credenciais. Gerador registra `perf_counter_ns()` para tempo decorrido no mesmo processo; em serviços distintos, **não subtrair relógios monotônicos de máquinas diferentes**. Latência ponta a ponta: medir no cliente gerador entre pedido inicial e confirmação observável de efeito (correlação e polling/evento), deixando explícito se inclui espera/polling. Latências entre nós exigem sincronização de relógios e relatório de erro; caso contrário, evitar alegações de precisão de latência por timestamps cruzados.

- **Correção funcional:** número de efeitos esperados, obtidos, ausentes, adicionais, fora de ordem; taxa de correspondência e estado final.
- **Tempo de execução:** segundos entre envio do primeiro estímulo e confirmação do último efeito com término/drain; para ausência de efeitos, usar sinal de conclusão e reconciliação de contagens.
- **Vazão:** alterações efetivas processadas/segundo e efeitos/segundo, com denominadores identificados.
- **Latência:** mediana, p95, p99 (somente com quantidade de amostras adequada) em ms; informar definição do início/fim e método.
- **CPU:** CPU-segundos por serviço e total, preferencialmente contador cumulativo por contêiner com janela delimitada; `kubectl top` é instantâneo e **não substitui série histórica**.
- **Memória:** pico de working set/RSS, por serviço, em MiB, com fonte exata; evitar soma ingênua de métricas incompatíveis.
- **Rede:** bytes enviados/recebidos e eventos retransmitidos, por serviço, quando disponibilizados por contadores/telemetria.
- **Recuperação:** número de reinícios, perda/duplicação após replay e tempo até estado pronto; não atribuir tolerância a falhas sem replay persistente validado.

**Instrumentos candidatos:** `pytest` para testes; cliente gerador em Python; logs estruturados; `kubectl get/describe/logs`; `docker inspect/stats` para C2; métricas de cgroups ou Prometheus/cAdvisor se realmente instalados na Etapa 06. Capturar versão/semântica do exportador, período de amostragem e overhead de medição. Nunca tratar métricas não coletadas como zero.

## 6. Repetições, comparabilidade e estatística

Primeiro executar testes de sanidade e fixtures mínimas; depois uma rodada piloto por cenário para ajustar timeout e instrumentos (excluída das estimativas). Para C5, **planejar 10 repetições independentes por cenário e nível de carga** após 1 aquecimento não contabilizado; essa escolha é planejamento, não alegação de suficiência estatística. Intercalar a ordem de cenários de modo balanceado (quando viável), reinicializar estado e confirmar ausência de trabalho residual antes de cada rodada. Definir timeout inicial de 60 s por fixture mínima e registrar timeout como falha, ajustável antes do início das séries de medição, com motivo. Usar mediana, p95 quando aplicável, mínimo/máximo e dispersão (IQR); intervalos de confiança por bootstrap se número de observações e pressupostos permitirem. Não descartar outliers sem política prévia, nem apresentar significância estatística como evidência de causalidade com ambientes diferentes. Registrar CPU total e recursos para interpretar tradeoffs. Não usar speedup como evidência de escalabilidade quando recursos ou trabalho por cenário não forem equivalentes.

## 7. Procedimento de execução e reprodutibilidade

1. **Congelar protocolo:** aprovar com orientador a cadeia Python, o escopo e os critérios; fixar SHA e fixture.
2. **Etapa 06:** inventariar SO, CPU, RAM, disco, virtualização, ferramentas, privilégios, versões e número de nós realizável; escolher cluster local e registrar limitações.
3. **Etapa 07:** corrigir `Condition`, `Rule`/asyncio e IDs; implementar testes unitários, C0/C1, oráculo e serialização; aprovar V01–V07 antes do cluster.
4. **Etapa 08:** construir imagens com dependências fixas e registrar `image digest`; rodar C2 e verificar isolamento e V02.
5. **Etapas 09–10:** implantar C3 (e C4 apenas se factível); registrar `kubectl config current-context`, `kubectl get nodes -o wide`, `kubectl get pods,deploy,svc -n tcc2-pon -o wide`, `kubectl describe` e logs; comprovar V08/V09.
6. **Etapa 11:** executar fixtures pré-definidas com novas `run_id` e reset; salvar todas as rodadas, inclusive erros e timeouts; F1 e C5 apenas conforme recursos e mecanismos.
7. **Etapa 12:** validar integridade, gerar gráficos por script versionado e discutir limitações e resultados observados.
8. **Etapa 13:** consolidar redação acadêmica e figuras da arquitetura **realmente implementada**; conferir compilação Overleaf.

**Pacote por rodada (sugestão de estrutura):** `experimentos/<run_id>/manifest.json`, `inputs.jsonl`, `expected.jsonl`, `effects.jsonl`, `service-*.jsonl`, `metrics.csv` (se instrumentado), `k8s-pods.txt`, `environment.json`, `checksums.sha256`, `validation.json`. O `manifest.json` deve registrar UTC, operador, protocolo, cenário, código Git SHA, digests, versões, recursos, nó/pod, fixture/hash, seed, parâmetros, status, motivo de exclusão/timeout e observações. Evitar credenciais e dados sensíveis. Guardar dados brutos imutáveis e produzir tabelas derivadas separadamente. Scripts de comparação devem falhar (exit != 0) em discrepâncias funcionais.

## 8. Correspondência com os objetivos específicos

| Objetivo aprovado | Evidência |
|---|---|
| Analisar fundamentos e aplicação | diagnóstico Etapas 02/04; testes V01 |
| Conteinerizar e projetar | Dockerfile, digests, manifests, C2, V03/V04 |
| Implantar e executar distribuído | C3, V02/V04/V07/V08, topologia V09 quando disponível |
| Identificar limitações e oportunidades | erros V05/V06/V10, registros V11, métricas V12 e análise crítica |

## 9. Duas representações arquiteturais e momento de inserção

**Modelo 1 — hipótese conceitual herdada do TCC1:** manter a figura e a referência atuais em `capitulos/cap-proposta.tex`, claramente identificadas como hipótese preliminar (não refletindo necessariamente serviços da implementação). Não renomear nem substituir silenciosamente.

**Modelo 2 — arquitetura operacional de três serviços:** manter o Mermaid e contratos na documentação da Etapa 04. **Figura definitiva da implementação:** gerar apenas quando o código e a comunicação estiverem validados nas Etapas 07–10; inserir na versão definitiva do capítulo de metodologia/arquitetura na Etapa 13, com legenda, fonte, rótulo LaTeX e referência cruzada, distinguindo arquitetura planejada e executada. Não inserir agora um diagrama hipotético como arquitetura comprovada.

## 10. Registro de decisões, pendências e transição

**Decisões:** núcleo C0–C3; configuração inicial 1 réplica/serviço; oráculo determinístico; aceitação funcional exata sem tolerar perdas ou efeitos extras; evitar salto lógico de múltiplos Pods para multinó; C4/C5/F1 condicionais; nenhum resultado ou teste declarado executado.

**Pendências:** validação do orientador; verificar fidelidade da prova Python; corrigir núcleo e implementar serviços/replay; inspeção de hardware na Etapa 06; definição real de instrumentação, recursos e limites; validar compilação LaTeX; criar figuras operacionais somente após implementação.

**Gancho Etapa 06:** produzir inventário real de máquina/virtualização, versões e capacidade de multinó; escolher Docker/Kubernetes compatíveis; definir recursos e instrumentos viáveis, sem alterar os critérios funcionais do protocolo. Este arquivo constitui **plano**, não relatório de experimentos.
