# TCC2 — Etapa 07: auditoria direta do ZIP da rodada V07

**Data da auditoria:** 12/11/2026. **Fonte:** arquivo ZIP anexado pelo acadêmico nesta conversa, proveniente da execução no Windows. Esta análise verifica os bytes recebidos e seus registros, **não é uma nova execução do sistema PON**.

## 1. Identificação e integridade

- Arquivo: `c1-snapshot-http-20261112-190909.zip`, **5.867 bytes**, SHA-256 calculado diretamente `e454d6051048c37cd2276bff6acadcfac04e2fe03449abcafcca217c07b6fba1`.
- Hash **idêntico ao que foi mostrado no PowerShell** na evidência E07-D21. A coincidência atesta consistência entre o artefato recebido e o hash exibido anteriormente, não substitui uma assinatura digital de origem.
- Teste do ZIP/CRC (`ZipFile.testzip()`): sem erros.
- ZIP contém **13 entradas**: `checksums.sha256` e outros **12 arquivos**. O manifesto de checksums abrange exatamente os 12; os 12 hashes SHA-256 foram recalculados sobre os bytes internos e **todos coincidiram**.
- Os três `*.stderr.log` estão vazios, dentro do que esta rodada registrou.

## 2. Manifesto auditado

| Item | Valor efetivamente presente no ZIP |
|---|---|
| Cenário | `C1-snapshot-http-race` |
| `run_id` | `c0-minimo-v1` |
| `seed` | `20260501` |
| Git SHA | `be6b850d599504e9ea8166f02fd87b35313e5445` |
| Python | `3.13.9` |
| Plataforma declarada | `Windows-10-10.0.19045-SP0` |
| Produtor | PID `1988`, porta `54912` |
| Avaliador | PID `15164`, porta `54910` |
| Executor | PID `18332`, porta `54909` |
| Proxy temporário de teste | Porta `54911`, não é quarto serviço permanente |
| `validation.json` | `status=PASS`; **7/7 checks `true`** |
| Resultado | Efeitos `rl1:1` e `rl1:2`, nos passos **3 e 7** |

## 3. Auditoria programática dos arquivos reais

Foram efetuadas **20 checagens adicionais de consistência — 20/20 aprovadas**, independentemente de confiar apenas no campo `status` do relatório. São elas:

1. Commit do manifesto coincide com a revisão registrada como testada.
2. Os três PIDs são distintos.
3. PIDs e papéis informados em todos os logs condizem com o manifesto.
4. `run_id` é igual em todos os estados finais.
5. `snapshot_version` é idêntico nos três estados.
6. Valores finais de atributos iguais entre produtor e avaliador (`atA=6`, `atB=1`).
7. Sequências dos atributos iguais (`atA=2`, `atB=3`).
8. Sequência de condição igual no avaliador e executor (`3`).
9. IDs de notificações de atributos transmitidas iguais aos IDs recebidos pelo avaliador.
10. IDs de notificações de condição transmitidas iguais aos IDs recebidos pelo executor.
11. Efeitos nos logs do executor iguais a `effects.jsonl` e ao estado registrado pelo executor.
12. `effects.jsonl` idêntico a `expected.jsonl`.
13. Dois passos de efeito são exatamente `[3,7]`.
14. `caused_by` e `attribute_event_id` de cada efeito referem-se a eventos existentes.
15. Etapas principais do handshake e envio da alteração aparecem na ordem esperada.
16. Marcas `monotonic_ns` da linha do tempo não são decrescentes.
17. Três logs `stderr` sem conteúdo.
18. Relatório declara `PASS` e sete verificações verdadeiras.
19. `checksums.sha256` cobre exatamente os outros 12 arquivos.
20. Todos os 12 SHA-256 internos recomputados correspondem ao manifesto.

**Contagens diretamente verificadas nos logs:** **5** notificações de atributo, **3** notificações de condição e **2** execuções de regra. Efeito no passo 3: `rl1:1` causado por `cn1:1` e `atB:1`; passo 7: `rl1:2` causado por `cn1:3` e `atB:3`.

## 4. Ordem causal documentada

A sequência no `timeline.jsonl` foi:

```text
snapshot_installed_downstream
snapshot_ack_held
concurrent_change_sent
snapshot_ack_released
attribute_forwarded (atA:1)
concurrent_change_responded (HTTP 200)
```

Isso comprova, neste ensaio controlado, o envio de uma alteração HTTP durante a retenção da confirmação de snapshot e sua resposta após a liberação do ACK, **com servidor serial no produtor**. Não autoriza afirmações de sincronização geral para múltiplos clientes, persistência, recuperação de falhas ou distribuição multinó.

## 5. Rastreabilidade científica e limites

- O arquivo bruto **foi recebido e inspecionado diretamente nesta conversa**, superando o registro anterior de que apenas prints e hashes estavam disponíveis.
- A auditoria reforça V11 **para esta rodada específica**, mas V11 permanece **parcial globalmente**, pois os arquivos de todas as demais rodadas e cenários não foram integralmente auditados, e este ZIP não foi incorporado ao repositório.
- A Etapa 07 continua funcionalmente concluída somente para **C0/C1 mínimos**, com V01–V07 aprovados **nos casos testados**. Nenhuma análise de desempenho científico, Docker/Kubernetes ou execução entre nós foi realizada nesta auditoria.
- Os capítulos LaTeX e figuras definitivas ficam para as etapas designadas. Referência original imutável: `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`. Branch `master` preservada.

**Próxima atividade:** Etapa 08 (Docker/C2), com execução e evidências na máquina do acadêmico, sem inventar resultados novos.
