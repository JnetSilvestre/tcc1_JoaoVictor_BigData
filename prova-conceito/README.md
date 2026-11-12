# TCC2 — Prova Python PON (adaptação experimental)

Esta pasta contém **cópia identificada e adaptada**, para testes e desenvolvimento incremental, do núcleo Python disponível em [JnetSilvestre/codigoPon](https://github.com/JnetSilvestre/codigoPon), commit exato `c2d525b5c675820806af34348e259bff32a6bc5f`. A pasta externa `codigoPon-referencia` do acadêmico não deve ser modificada.

**Não é** uma implementação do NOP Query C++ da tese, um sistema de consultas de vídeo, nem uma aplicação já distribuída.

## Etapa 07 — correção isolada de Condition

Arquivos `main.py` e `pon/*.py` copiados da referência fixada. A primeira alteração funcional encontra-se **somente em `pon/Condition.py`**:

- propagar transição para observadores da condição, usando `Notifier.notify()`;
- consultar ID público com `getId()`, evitando `AttributeError` por name mangling.

Os testes `tests/test_condition.py` verificam mudança falso→verdadeiro, transição inversa, ausência de notificações redundantes e propagação entre condições aninhadas. A contagem de dois estados verdadeiros é teste de transição, **não comprova ainda os dois efeitos executados por Rule/Action previstos no cenário C0**.

### Executar localmente (PowerShell, a partir da raiz do repositório da monografia)

```powershell
git branch --show-current
git pull --ff-only origin tcc2/desenvolvimento
Set-Location .\prova-conceito
python --version
python -m compileall -q .\pon .\tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
python .\main.py
Write-Host "Main: $LASTEXITCODE"
```

**Saída esperada**, e não resultado já obtido na máquina do acadêmico: `Ran 3 tests`, `OK`, saída final `Testes: 0`. Se houver falha, registrar stdout/stderr e investigar antes de prosseguir.

### Evidências a preservar

Prints originais do terminal com branch, commit (`git rev-parse HEAD`), versões, comando completo, saída e código de retorno; salvar logs e checksums quando possível. A Etapa 07 exige validação real em Windows antes de considerar esta correção aceita.

## Próximos incrementos

1. Confirmar testes de Condition no Windows e arquivar evidências.
2. Testar/corrigir Rule e IDs sem corromper a semântica notificada.
3. Implementar oráculo C0 completo e fixture JSONL com dois efeitos reais causados pelos passos 3 e 7.
4. Implementar três serviços Python em processos separados (C1) com contratos HTTP/JSON, ordem, deduplicação e snapshot.

Docker/Kubernetes da **aplicação** ficam para as Etapas 08–10. A monografia LaTeX e os dois diagramas da arquitetura permanecem preservados até validação.


## Segundo incremento da Etapa 07 — Rule/IDs (pendente de validação no Windows)

- `Rule.update` agora executa `Action/Instigation` de modo **síncrono e determinístico** quando recebe uma notificação de condição aprovada. O método explícito `async def execute` permanece disponível para chamadas com `await`. Não há agendamento automático sem controle por `asyncio.create_task`.
- `Notifier.setId` valida inteiros não negativos e verifica colisões antes de remover o registro anterior; `NOPManager` não substitui entidades de mesmo ID e só remove o proprietário correto do registro. ID 0 significa entidade local sem registro.
- Testes novos em `tests/test_rule.py` (4 testes) e `tests/test_ids.py` (4 testes). A fixture mínima dos sete passos valida **duas ações nos passos 3 e 7**, ainda sem representação JSONL nem metadados de rede.
- Essas escolhas são restritas à execução local C0. `NOPManager` continua singleton não thread-safe e não tem armazenamento persistente. C1 exigirá contratos e fronteiras de estado específicos.

### Próxima execução esperada no PowerShell

```powershell
Set-Location "$HOME\\tcc2\\etapa07\\tcc2-trabalho"
git branch --show-current
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\\prova-conceito
python -m compileall -q .\\pon .\\tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
python .\\main.py
Write-Host "Main: $LASTEXITCODE"
```

**Saída planejada, não observada ainda no Windows:** 11 testes `OK` e códigos de saída 0. Se ocorrer falha, preservar traceback e código de saída para diagnóstico.
