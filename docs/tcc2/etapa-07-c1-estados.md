# TCC2 — Etapa 07: C1 incremento 02 — máquinas de estado em memória

**Estado:** código e 11 testes adicionais publicados; execução da nova suíte no Windows **ainda não observada**. O cenário C1 com HTTP e processos distintos também não foi executado.

## Referências de continuidade

- Decisões mantidas: `docs/tcc2/etapa-04-arquitetura-distribuida.md` e `docs/tcc2/etapa-05-protocolo-experimental.md`.
- Referência original imutável: `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`.
- Validações já realizadas no Windows: C0 (18/18 testes, `PASS`, efeitos nos passos 3/7); contratos C1 (25/25 testes, print E07-D12).
- **Nesta entrega:** `prova-conceito/c1/state.py` e `prova-conceito/tests/test_c1_state.py`. A suíte deve crescer de 25 para **36 testes**; não afirmar resultado antes da execução real.

## Componentes e responsabilidades

| Papel | Classe | Entrada/estado | Saída |
|---|---|---|---|
| `attribute-source` | `AttributeSource` | Rodada, valores autoritativos, sequências de atributos, `request_id`, envio pendente | Snapshot inicial e `AttributeChanged` apenas para valores diferentes |
| `logic-engine` | `LogicEngine` | Snapshot, réplicas `Attribute`, `Premise`, `Condition`, watermarks e ledger | `ConditionChanged` somente em transições; `caused_by` aponta para atributo |
| `rule-executor` | `RuleExecutor` | Snapshot de condição, `Attribute` booleano local, `Premise`, `Condition`, `Rule`, `Action`, `Instigation`, ledger | Efeito estruturado exclusivamente em transição falso→verdadeiro |

Os envios são **callbacks síncronos injetáveis**, ainda no mesmo processo durante os testes deste incremento. A etapa seguinte substituirá esses callbacks pelo transporte HTTP/JSON e separará os três papéis em PIDs distintos.

### Snapshot, ordem e duplicação

- Produtor só aceita alterações depois de confirmar envio do snapshot ao avaliador; avaliador só aceita eventos depois de enviar o snapshot ao executor.
- O snapshot inicial recebe `snapshot_version = <run_id>:snapshot:0` e watermarks de atributos zerados. **Não há ressincronização/replay a partir de watermarks não nulos**; isso é rejeitado explicitamente. Não alegar recuperação automática nem tolerância a falhas.
- Eventos posteriores à inicialização são validados antes de mutar estado; sequências com lacuna/atraso ou `run_id` divergente são rejeitadas com `ContractError`, futuramente convertido em HTTP 4xx.
- Repetições idênticas de `event_id` retornam indicação de duplicata sem provocar efeitos adicionais. Reutilizar `event_id` com payload diferente é erro de conflito.
- O produtor preserva um envio pendente e **reenvia os mesmos dados e timestamp** após falha de ACK, permitindo deduplicação por `event_id`. Isso não equivale a fila persistente: tudo está em memória.
- Se a propagação de uma mudança do avaliador ao executor falhar depois de mutação parcial, o avaliador fica em estado `faulted`; **não** se considera rollback/replay automático.
- As estruturas atuais não são thread-safe e requerem processamento serializado por instância. O futuro servidor HTTP deverá preservar essa condição (por exemplo, lock por processo).

## Testes publicados para avaliação

`tests/test_c1_state.py` acrescenta **11 casos**: portão de snapshot, inicialização idempotente, equivalência da fixture C0, repetição de `request_id`, reentrega de eventos, conflito de mesmo `event_id`, lacunas, `run_id` errado, rejeição de valores inválidos sem mudança de estado, retry após perda simulada de confirmação e rejeição de snapshot não suportado.

A simulação de perda de ACK é um **teste unitário local**, não prova experimental de falha real de rede. Os resultados de C0/C1 devem continuar comparados por multiplicidade, ordem e causalidade, desconsiderando timestamps de transporte.

## Comandos completos — PowerShell na máquina do acadêmico

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

**Resultado esperado, ainda não medido na máquina do acadêmico:** `Ran 36 tests`, `OK`, códigos de saída 0. Registrar integralmente falhas, logs e capturas. Não executar serviços HTTP ou Docker/Kubernetes por causa desses testes.

## Próximos passos

1. Confirmar a suíte de estados com evidência real no Windows.
2. Implementar HTTP somente em localhost com `GET /health/live`, `GET /health/ready`, `GET /state`, `POST /attributes/change`, `POST /notifications/attribute`, `POST /notifications/condition` e endpoints controlados de inicialização por snapshot.
3. Executar três PIDs distintos com logs JSONL, enviar a fixture C0 e comparar efeitos com o oráculo independente (V02/V04).
4. Verificar resposta 4xx sem mutação (V03), reentrega sem duplicação (V05), lacunas e eventos atrasados (V06) e snapshot inicial (V07).
5. Consolidar evidências e limites antes de concluir a Etapa 07; Docker/Kubernetes da aplicação continuam reservados às Etapas 08–10.

**Nota científica:** os três papéis são uma adaptação experimental Python. O código não demonstra equivalência ao NOP Query C++, processamento de vídeo ou desempenho distribuído.
