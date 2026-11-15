# Etapa 08 — Encerramento técnico do cenário Docker C2

**Data:** 15/11/2026. **Decisão:** **Etapa 08 concluída quanto à construção, execução e validação funcional delimitada do cenário C2 (Docker, host único)**. A aprovação não significa que todos os critérios V01–V12 globais estejam satisfeitos. A implantação em Kubernetes e a avaliação operacional/distribuída continuam pendentes nas Etapas 09–10.

## 1. Escopo validado

- Uma imagem Linux/amd64 reutilizada em três contêineres de serviço independentes, em rede Docker interna com encaminhamento HTTP/JSON entre `attribute-source`, `logic-engine` e `rule-executor`.
- Estado frio e inicialização via snapshot HTTP verificados, incluindo `ready`, `run_id` e watermarks.
- Fixture C0/C2 comparada ao oráculo: efeitos esperados nos passos 3 e 7 (ensaio principal anterior, E08-D11, evidências e auditoria preservadas).
- Rejeições deliberadas de requisições inválidas em estado frio: 10/10 casos HTTP 4xx em C2/V03, com estados invariantes.
- V05: deduplicação de `AttributeChanged` e `ConditionChanged`; reenvio idêntico com ACK e sem novos efeitos; conflito de mesmo ID com payload diferente rejeitado HTTP 409, sem corromper estado. Ensaios sequenciais e evidências ZIP anteriores documentados.
- V06: snapshot dedicado e três testes adversariais de ordem/identidade, com resultado `PASS`, HTTP 409 esperado, estado funcional preservado e logs verificáveis:
  - E08-D18F-R1: lacuna `AttributeChanged` seq. 2 antes de 1;
  - E08-D18G: `run_id` divergente em `AttributeChanged`;
  - E08-D18H: lacuna `ConditionChanged` seq. 2 antes de 1.
- Última regressão real Windows: **93/93 `unittest` aprovados**; duração da suíte 10,966 s, **não** benchmark. Git limpo ao final, conforme print e ZIP.

## 2. Rastreabilidade e procedência

- Commit realmente executado na última rodada: `2ea999a712032b2bf295362264e6a5a204b9986f`. Comandos de construção/execução, versões e dependências preservados no repositório.
- Último ZIP auditado: `c2-v06-batch-20261115-184915.zip`, 13.566 bytes, SHA-256 `24ff2fbc4aa28acfec0bad90c3677301cfadbce7efea51c9368b6e50953c1be1`, CRC aprovado, **27 entradas, 26 hashes internos válidos**.
- Laudo: `docs/tcc2/etapa-08-auditoria-v06-batch.md`. Laudos anteriores: `docs/tcc2/etapa-08-auditoria-v06-snapshot.md` e auditorias V05. Evidências brutas ZIP continuam armazenadas na máquina do acadêmico/conversa, **não no GitHub em binário**. Esta documentação não substitui os arquivos originais.

## 3. Limites e critérios deliberadamente em aberto

1. O cenário C2 roda em **um host Docker**, não constitui prova de distribuição física, Kubernetes nem tolerância a falhas.
2. **V07 global PARCIAL:** ensaio C1 verificou uma janela controlada de corrida no snapshot; em C2 o snapshot/coerência iniciais foram demonstrados, mas **não** a corrida HTTP de alteração durante inicialização na bancada V06. Em C3 o teste ainda não foi realizado.
3. **V08 NÃO EXECUTADO:** sem Deployments, Services e Pods da aplicação Kubernetes comprovados.
4. **V09 NÃO EXECUTADO:** implantação da aplicação em múltiplos nós não demonstrada; depende de >=2 nós prontos e distribuição real.
5. **V10 NÃO EXECUTADO em C2/C3:** não houve validação de recuperação completa/replay depois do restart de um componente na fixture.
6. **V11 PARCIAL globalmente:** reprodutibilidade e hashes das rodadas C2 fortemente documentados, porém reprodução por terceiro e C3 pendentes.
7. **V12 NÃO EXECUTADO:** sem séries de medições válidas de latência, vazão, CPU, memória ou rede para comparação científica.
8. HTTP serial por processo, estado residente em memória, sem recuperação automática geral, persistência ou garantia de ordenação sob concorrência arbitrária. Não generalizar resultados além da fixture e casos adversariais executados.

## 4. Decisão de encerramento e próximos passos

**Encerrar os ensaios C2 desta Etapa 08 no escopo previsto**, preservando contêineres V05/V06, logs, ZIPs, sha256, imagem, TAG e relatórios. **Não repetir POST nem reconstruir/reinicializar bancadas já auditadas.** É desnecessário continuar criando microensaios Docker para os mesmos casos.

Prosseguir para **Etapa 09**, com preparação e implantação C3 em Kubernetes (`kind` existente deverá ser diagnosticado antes de uso), manifests, Deployments, Services, probes e verificações de distribuição em pods. Replicar a fixture C0/C1/C2 em C3 em cenário isolado e testar V07 conforme protocolo original. A **Etapa 10** fará a experimentação e avaliação dos custos computacionais com plano de medidas explícito e dados brutos. O status `PASS` dos casos Docker não implica ganho de desempenho ou equivalência com um cluster multinó.
