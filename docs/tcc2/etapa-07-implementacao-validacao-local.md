# TCC2 — Etapa 07: implementação e validação local (diagnóstico inicial)

**Data da inspeção estática:** 2026-11-12.  
**Estado em 12/11/2026:** diagnóstico estático e testes da referência comprovados por capturas do Windows; defeito de `Condition` reproduzido; cópia adaptada e testes de regressão publicados posteriormente, **ainda sem execução comprovada no Windows**. V01–V07 continuam **não aprovados**. Ver seções 8–9.  
**Branch exclusiva para alterações:** `tcc2/desenvolvimento` no repositório da monografia. Não modificar `master`.  
**Origem congelada para análise:** `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f`. Não modificar o repositório de referência.  
**Documentos obrigatórios preservados:** `docs/tcc2/etapa-04-arquitetura-distribuida.md`, `docs/tcc2/etapa-05-protocolo-experimental.md` e `docs/tcc2/etapa-06-preparacao-ambiente.md`.

## 1. Limites da atividade

A Etapa 07 começa pelo núcleo Python e pela validação C0 (oráculo em processo único). Somente após correções e testes funcionais locais será desenvolvido e validado C1 (três processos independentes com contratos HTTP/JSON). **Não** criar Dockerfile, imagens ou recursos Kubernetes da aplicação nesta etapa.

Preservar o objetivo aprovado: demonstrar viabilidade arquitetural e correção funcional, sem exigir ganho de desempenho. O código Python analisado **não é equivalente** ao NOP Query C++ da tese, nem uma consulta de vídeo. A aderência da escolha Python e de três serviços ao escopo acadêmico continua pendente de confirmação com o orientador.

## 2. Dependências observadas (análise de código, NÃO teste de execução)

Na revisão `c2d525b...`, foram lidos `main.py`, `pon/__init__.py`, `pon/Notifiable.py`, `pon/Notifier.py`, `pon/Attribute.py`, `pon/Premise.py`, `pon/Condition.py`, `pon/Rule.py`, `pon/Action.py`, `pon/Instigation.py` e `pon/NOPManager.py`.

- Importações explícitas externas ao pacote `pon`: apenas módulos da biblioteca padrão `json` e `asyncio`.
- `requirements.txt` ausente no caminho consultado do commit fixado; não instalar dependências por suposição.
- Ambiente da máquina documentado na Etapa 06: Python 3.13.9, pip 25.2 e ambiente `venv` funcional, mas **compatibilidade funcional do núcleo ainda não demonstrada**.
- `main.py` exercita apenas atributos, premissas e uma condição contraditória (igual e diferente simultaneamente); não instancia `Rule` nem `Action`, logo não valida uma cadeia completa.

## 3. Diagnóstico estático do núcleo (a confirmar por testes reais)

| Componente | Observação do código fixado | Risco e teste necessário |
| --- | --- | --- |
| `Attribute` | Setter notifica apenas se o valor muda; `getEncoded` usa JSON `{"v": ...}` | V01: igualdade/repetição, tipos e serialização |
| `Premise` | Reavalia ao receber mudança e propaga transições lógicas | V01: bordas, transições e ausência de eventos redundantes |
| `Condition` | `update` acessa `self.__id`, que não é declarado na própria classe (em `Notifier` há outro campo privado), e percorre os elementos de entrada em vez de chamar observadores | **Defeito provável bloqueante**: `AttributeError` na primeira transição da condição; corrigir usando a interface pública de ID e notificação, após reproduzir o defeito |
| `Rule` | `asyncio.create_task(self.execute())` é usado sem garantir laço de eventos ativo | **Defeito provável** em C0 síncrono; risco de coroutine não aguardada; fixar política de execução e testar efeito exatamente uma vez |
| `Notifier` / `NOPManager` | IDs não nulos registram entidades; `addEntity` substitui entradas com o mesmo ID sem rejeitar colisão | V01/V03: ID 0/local, colisões, troca de ID e consistência do registro |
| `Action` / `Instigation` | Chamadas de métodos locais síncronas | Necessário efeito estruturado observável e rastreabilidade para o oráculo |
| `NOPManager` | Instância singleton mantém estado em memória e lista de drivers, sem transporte HTTP concreto identificado | Isolar rodadas, evitar efeitos entre testes, não atribuir durabilidade ou semântica exatamente uma vez |

`Attribute.__eq__` produz `Premise`, não booleano; evitar pressupor semântica usual de igualdade/uso como chave de dicionário. A validação de mensagens HTTP/JSON não pode depender apenas de `handleEncoded`, que não implementa validação contratual.

## 4. Primeiro roteiro de execução real no PowerShell (não executado aqui)

Executar no computador do acadêmico, após escolher pasta de trabalho sem arquivos conflitantes:

```powershell
New-Item -ItemType Directory -Force "$HOME\tcc2\etapa07" | Out-Null
Set-Location "$HOME\tcc2\etapa07"
git clone https://github.com/JnetSilvestre/codigoPon.git codigoPon-referencia
Set-Location .\codigoPon-referencia
git checkout --detach c2d525b5c675820806af34348e259bff32a6bc5f
git rev-parse HEAD
git status --short
python --version
python -m pip --version
python -m compileall -q .\pon
Write-Host "compileall exit code: $LASTEXITCODE"
python .\main.py
Write-Host "main.py exit code: $LASTEXITCODE"
```

Os comandos clonam e fazem checkout destacado da versão de referência, **sem alterações nem commits** em `codigoPon`. O `compileall` verifica sintaxe/importação por compilação de bytecode, mas **não substitui teste funcional**; `main.py` é apenas teste de fumaça limitado. Se a pasta já existir, inspecionar antes e não executar clone por cima dela.

### Caso mínimo para tentar reproduzir o defeito de Condition

Dentro de `codigoPon-referencia`, no PowerShell:

```powershell
@'
from pon import Attribute
atA = Attribute(0)
atB = Attribute(0)
cn = (atA >= 5) & (atB == 1)
print("inicial:", cn.approved())
atA.value = 5
print("apos atA:", cn.approved())
atB.value = 1
print("apos atB:", cn.approved())
'@ | python -
Write-Host "codigo de saida da reproducao: $LASTEXITCODE"
```

**Hipótese estática:** o último setter acionará `Condition.update` e falhará pelo acesso a `self.__id`. O retorno exato deverá ser documentado a partir da execução real; **não registrar como falha observada antes do teste**.

## 5. Critérios e evidências a coletar

- **E07-D01:** `git rev-parse HEAD`, `git status --short`, `python --version`, `python -m pip --version` com saída e captura original do terminal.
- **E07-D02:** `compileall` e `main.py` com códigos de saída, transcrição fiel e captura.
- **E07-D03:** reprodução mínima da transição `Condition`, saída completa, stack trace e código de saída; registrar sucesso ou falha.
- **E07-T01 (futuro):** testes automáticos da cadeia PON corrigida, fixture de sete passos e exatamente dois efeitos em C0.
- **E07-T02 (futuro):** C1, V02–V07, contratos HTTP, PIDs distintos, logs correlacionados e comparação automática ao oráculo.

Salvar logs de texto e prints originais com hora, comando, código-fonte/SHA e, quando possível, checksum SHA-256. Não criar ou rotular imagens ilustrativas como capturas reais. Não publicar credenciais nem valores sensíveis. O ambiente remoto/contêiner de uma ferramenta de IA não equivale à máquina Windows registrada na Etapa 06.

## 6. Ordem de implementação e aceite (sem antecipações)

1. Reproduzir a revisão fixada, registrar versões e testes de fumaça em ambiente local.
2. Criar testes de regressão para transições, notificação a observadores, `Rule`, IDs e não redundância; registrar primeiro os resultados reais da versão original.
3. Corrigir defeitos mínimos sem romper a semântica notificada; executar os testes novamente e preservar logs antes/depois.
4. Implementar fixture determinística da Etapa 05: `atA=0`, `atB=0`; `atA>=5`, `atB==1`; sete mudanças propostas; oráculo de dois efeitos nas etapas 3 e 7. Validar causalidade, multiplicidade e ordem.
5. Implementar C1: `attribute-source`, `logic-engine`, `rule-executor` em três processos HTTP/JSON, snapshot inicial, controle de `sequence` e `event_id`, rejeição de payload inválido e deduplicação.
6. Executar V01–V07 de verdade e comparar C0/C1, arquivando saídas e capturas. Após aceite, preparar transição para Etapa 08 (Docker), sem executá-la agora.

**Critério de conclusão da Etapa 07:** C0 e C1 funcionais, testes V01–V07 executados e resultados rastreáveis; nenhuma aprovação automática a partir deste diagnóstico.

## 7. Pendências desta publicação

- **Executados posteriormente, em 12/11/2026:** compilação sintática, `main.py` e reprodução do defeito de `Condition`, com resultados e prints documentados na seção 8. **Ainda não executados:** testes de regressão da implementação corrigida.
- **Implementado posteriormente:** correção isolada de `Condition` e três testes unitários no diretório `prova-conceito/` (seção 9). **Ainda não implementados:** correções de `Rule`/IDs, fixture e oráculo C0 completos, três serviços HTTP, snapshot e deduplicação.
- **Produzidos posteriormente:** dois prints do terminal com diagnóstico e falha, recebidos na conversa (não incorporados ao repositório). **Ainda não produzidos:** logs estruturados do PON corrigido, resultados experimentais e métricas.
- **PENDENTE:** autorização/aderência acadêmica para adaptação da referência Python, confirmação com o orientador, definição de local definitivo dos arquivos adaptados.
- **Versionamento:** esta publicação documental foi feita exclusivamente em `tcc2/desenvolvimento`, sem alteração dos repositórios de código-base ou da monografia LaTeX.

## 8. Evidência recebida da máquina do acadêmico — 12/11/2026

**Origem:** duas capturas originais enviadas pelo acadêmico na conversa desta etapa, registrando comandos executados no Windows PowerShell em `$HOME\\tcc2\\etapa07\\codigoPon-referencia`. Os dados são observações **do computador do acadêmico**, não execução desta ferramenta de IA. Capturas preservadas na conversa, **ainda não incorporadas ao GitHub**.

### E07-D01 e E07-D02 — referência, sintaxe e teste de fumaça

Captura original: `image(20261112-195015).png` (857 × 859 pixels, 68.030 bytes, SHA-256 `35c196d446700e0d62a9f7e536111312fbb92f7a2c9a1917e78e7c41bfab225c`).

- O comando `git checkout --detach c2d525b5c675820806af34348e259bff32a6bc5f` concluiu no commit fixado; `git rev-parse HEAD` exibiu o mesmo SHA.
- `git status --short`: nenhuma alteração listada na captura.
- `python --version`: `Python 3.13.9`; `python -m pip --version`: `pip 25.2` (Python 3.13).
- `python -m compileall -q .\\pon`: código de saída `0`.
- `python .\\main.py`: execução completa do exemplo original, com saída `Execucao: 0`. O exemplo exibiu `cn1` falsa inicialmente e após alterações, pois usa conjunção entre premissas mutuamente exclusivas.
- **Limite:** esses dois comandos não provam funcionamento da cadeia com transição verdadeira nem execução de `Rule`/`Action`.

### E07-D03 — reprodução do defeito de Condition

Captura original: `image(20261112-195031).png` (857 × 859 pixels, 49.155 bytes, SHA-256 `268fff06dcb1a7f369521a6f1d0017f178b8cdc80192323e2eb28056bb266448`).

Entrada real: `atA=0`, `atB=0`, condição `(atA >= 5) & (atB == 1)`;

1. Estado inicial: `False`.
2. Depois de `atA.value = 5`: `False`.
3. Na atribuição `atB.value = 1`: **exceção real**; não houve confirmação do estado após `atB`.
4. Stack trace: `Attribute.value` → `Notifier.update` → `Premise.update` → `Condition.update`, linha que tenta acessar `self.__id`.
5. Erro observado: `AttributeError: 'Condition' object has no attribute '_Condition__id'`.
6. O PowerShell exibiu `Codigo de saida: 1` após a execução.

**Conclusão sustentada:** o defeito de encapsulamento em `Condition.update` foi **reproduzido** por execução real no Windows Python 3.13.9. V01 **não aprovado**; erro de execução funcional documentado. Os problemas de notificação a observadores, agendamento de `Rule` e colisão de IDs ainda são hipóteses derivadas da inspeção, **não reproduções comprovadas**.

### Próxima validação necessária

Preservar a cópia `codigoPon-referencia` intocada, construir/adaptar o núcleo em área de desenvolvimento da branch `tcc2/desenvolvimento`, criar teste de regressão que reproduza o erro antes da correção, corrigir `Condition` e testar a propagação correta; posteriormente abordar `Rule` e IDs. Capturar saídas dos testes anteriores e posteriores às correções e atualizar o status apenas com resultados efetivamente observados.

## 9. Cópia de desenvolvimento e regressão de Condition — 12/11/2026

### E07-D04 — branch de trabalho preparada

O acadêmico forneceu print adicional `image(20261112-195720).png` (30.751 bytes, SHA-256 `2f9494d6524e10821f665e1dd530b7e9feb1f80dcb7c4ab57be932da73ff224b`). A captura mostra o clone de `JnetSilvestre/tcc1_JoaoVictor_BigData` em `$HOME\\tcc2\\etapa07\\tcc2-trabalho`, `git branch --show-current` retornando `tcc2/desenvolvimento` e `git status --short` sem arquivos alterados. O print não inclui `git rev-parse HEAD` da monografia; não inferir SHA local a partir do clone.

### Incremento técnico publicado na branch (não testado na máquina do acadêmico)

- **Commit:** `41792b5a459b348c39eacb4ad63e63b7f61cb15f` — código-base Python reproduzido do commit `JnetSilvestre/codigoPon@c2d525b5c675820806af34348e259bff32a6bc5f` em `prova-conceito/main.py` e `prova-conceito/pon/*.py`.
- **Alteração funcional única nesse incremento:** `prova-conceito/pon/Condition.py` passa a enviar notificações aos observadores com `self.notify()` e usa `self.getId()` para não acessar indevidamente o atributo privado de `Notifier`.
- **Testes adicionados, mas AINDA NÃO EXECUTADOS no Windows:** `prova-conceito/tests/test_condition.py` contém três testes com `unittest`: aprovação após duas premissas verdadeiras, sequência de transições com ausência de notificações redundantes e propagação entre condições aninhadas.
- **Documentação:** `prova-conceito/README.md` e `prova-conceito/.gitignore`; correção da formatação Markdown no commit `c2d253a91bbc13675a19e76fbb961ea2b45fc7ac`.
- **Sem alteração:** `codigoPon-referencia` permanece fixado no commit original; `Rule`, `Notifier`, `NOPManager` continuam como no código de referência, até regressões próprias.

### Próxima execução no PowerShell

Executar em `$HOME\\tcc2\\etapa07\\tcc2-trabalho`:

```powershell
git branch --show-current
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\\prova-conceito
python --version
python -m compileall -q .\\pon .\\tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
python .\\main.py
Write-Host "Main: $LASTEXITCODE"
```

Arquivar capturas originais do terminal com comandos, saída e código de retorno. A expectativa é `Ran 3 tests`, `OK` e retorno 0, **mas isso não foi confirmado na máquina do acadêmico**. Se falhar, registrar íntegro o erro antes de modificar o código. A aprovação desses testes será **parcial de V01**: eles não exercitam `Rule`/`Action` nem comprovam os efeitos completos do oráculo C0.

## 10. Validação real da correção de Condition — prints do PowerShell (12/11/2026)

**Origem:** duas capturas enviadas pelo acadêmico nesta conversa após executar o incremento publicado na branch `tcc2/desenvolvimento`, checkout local `4dcaf328ef31893246260623e741eb65aa71773f`. Os PNGs originais foram fornecidos na conversa, mas **ainda não estão arquivados no GitHub**. Esta seção registra evidência observada, não uma simulação de execução.

| Identificador | Arquivo da captura | Dimensões | SHA-256 do arquivo recebido |
| --- | --- | --- | --- |
| E07-D05 | `image(20261112-200509).png` | 1169 × 916 | `60391e4f7a6ca6889f413e0635e32ffe4d9cc6e2e1bc54e790c65da9841495ea` |
| E07-D06 | `image(20261112-200539).png` | 1169 × 658 | `393f224361e1aa9a25f05d81cd7691951a6b29e0903a300fc03c46d00b5f837e` |

### E07-D05 — sincronização e revisão

- `git branch --show-current` exibiu `tcc2/desenvolvimento`.
- `git status --short` não apresentou linhas antes da atualização.
- `git pull --ff-only origin tcc2/desenvolvimento` concluiu com `Fast-forward`, trouxe a pasta `prova-conceito` e arquivos de documentação; HEAD local mostrado após a atualização: `4dcaf328ef31893246260623e741eb65aa71773f`.

### E07-D06 — testes executados no Windows

- `python --version`: `Python 3.13.9`.
- `python -m compileall -q .\\pon .\\tests`: `Compilacao: 0`.
- `python -m unittest discover -s tests -p "test_*.py" -v`: `Ran 3 tests in 0.003s`, `OK` e `Testes: 0`.
- Casos `test_condition_approves_only_when_both_premises_are_true`, `test_nested_conditions_propagate_to_observers` e `test_notifications_only_on_condition_transitions`: os três exibiram `ok`.
- `python .\\main.py`: finalizou com `Main: 0`, sem erros aparentes; a condição contraditória desse exemplo permaneceu falsa em todos os passos.

**Interpretação:** o defeito de `Condition` previamente reproduzido foi corrigido e os três testes de regressão da correção passaram na máquina documentada. Esse subconjunto de V01 tem evidência positiva, mas **V01 completo/C0 ainda estão pendentes**, pois `Rule`, `Action`, `Instigation` e os dois efeitos previstos nos passos 3/7 não foram validados. Não houve C1 ou medições de desempenho.

### Próximo incremento planejado

Adicionar testes de `Rule` com execução síncrona determinística da ação na transição falso→verdadeiro, mantendo compatibilidade do método explícito `async def execute`; tornar colisões e troca de IDs seguras em `Notifier`/`NOPManager`; executar os testes no Windows e registrar os resultados **antes de declarar aprovação**. Não modificar o código-fonte fixado do repositório `codigoPon`.

## 11. Incremento 02 — Rule, identificação de entidades e testes (12/11/2026)

**Código publicado, ainda sem resultado de execução do novo incremento no Windows.**

- Commit `6165bfdbcfa152218452cf91776fc0be6b345ede` exclusivamente na branch `tcc2/desenvolvimento`.
- `prova-conceito/pon/Rule.py`: `update()` executa `Action/Instigation` diretamente quando a condição notifica transição para verdadeiro, sem `asyncio.create_task` implícito. `async def execute()` permanece awaitable quando chamado explicitamente. **Escolha justificada para C0:** efeito observável e determinístico sem depender de event loop ou `sleep`.
- `prova-conceito/pon/Notifier.py` e `NOPManager.py`: validar IDs inteiros não negativos, preservar 0 para entidade local, rejeitar colisões antes de remover o ID anterior, impedir sobrescrita silenciosa e remoção por entidade diferente da proprietária.
- `prova-conceito/tests/test_rule.py`: quatro testes, incluindo fixture da Etapa 05 com 7 passos e dois disparos esperados nos passos 3 e 7, execução sem loop ativo, execução dentro de loop e compatibilidade de `await rule.execute()`.
- `prova-conceito/tests/test_ids.py`: quatro testes para IDs duplicados, troca/desregistro, valores inválidos e prevenção de remoção indevida.
- `prova-conceito/tests/test_condition.py`: três testes anteriores preservados. **Total planejado:** 11 casos na suíte.
- `prova-conceito/README.md`: procedimento PowerShell atualizado.
- **Não executados até o momento desta publicação:** a suíte de 11 testes no Windows, C0 completo (oráculo independente e fixture JSONL), C1/HTTP, Docker/Kubernetes da aplicação. **Não marcar V01 como aprovado integralmente ainda.**
- **Limites de engenharia:** efeito síncrono é adequado ao pequeno cenário funcional em processo único, mas tarefas bloqueantes, reentrância e concorrência exigirão revisão quando forem definidos os serviços C1. O registro em `NOPManager` é em memória, sem sincronização entre threads/processos nem durabilidade.

### Verificação local necessária

Executar a partir da pasta raiz `$HOME\\tcc2\\etapa07\\tcc2-trabalho`:

```powershell
git branch --show-current
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\\prova-conceito
python --version
python -m compileall -q .\\pon .\\tests
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
python .\\main.py
Write-Host "Main: $LASTEXITCODE"
```

Arquivar saída real, códigos de retorno, print original e hash. Espera-se `Ran 11 tests`, `OK` e códigos 0; qualquer divergência será investigada como resultado real, sem correção silenciosa.


## 12. Terceira validação em PowerShell — suíte de 11 testes (12/11/2026)

**Fonte:** duas capturas do PowerShell da máquina Windows enviadas pelo acadêmico, preservadas nesta conversa. São evidências visuais reais (não simulação). Os PNGs originais não foram incorporados ao repositório; a identificação abaixo permite arquivamento posterior.

| Evidência | Captura (nome recebido) | Dimensão | Bytes | SHA-256 calculado dos bytes originais |
|---|---|---|---:|---|
| E07-D07 | `image(20261112-201405).png` | 1169 × 855 | 95012 | `92e0802a4d8bc4bd1c58aaff1aea5faaf094baea17a92a818783352d0075d0d4` |
| E07-D08 | `image(20261112-201417).png` | 1169 × 855 | 28671 | `7dcff8305edd779d81dc96a704addb3ad2476b7b59cc4d81144a981b650c8ec7` |

**Observações visíveis:**

- `git branch --show-current` exibiu `tcc2/desenvolvimento`; `git status --short` sem linhas listadas.
- `git pull --ff-only origin tcc2/desenvolvimento` concluiu em *Fast-forward*, com revisão local exibida `eb9d21780b4074a03accc9711d586f70ba38505b`.
- `python --version`: **3.13.9**; `python -m compileall -q .\\pon .\\tests`: **Compilacao: 0**.
- `python -m unittest discover -s tests -p "test_*.py" -v`: 11 casos **ok**, `Ran 11 tests in 0.011s`, `OK` e `Testes: 0`.
- O caso `test_seven_steps_trigger_exactly_two_effects_in_order` está entre os aprovados, verificando dois efeitos nos passos 3 e 7 (dentro de um teste unitário de cadeia local).
- `python .\\main.py` executou e terminou com `Main: 0`.

**Classificação:** regressões de `Condition`, `Rule`, `Notifier` e `NOPManager` **aprovadas no escopo dos 11 casos**; boa evidência funcional parcial para V01. **Não interpretar tempo 0,011 s como medição de desempenho experimental**: é duração total relatada pelo framework de testes. C0 com fixture JSONL e oráculo independente **ainda não havia sido executado**; C1 e V02–V07 não aprovados.

**Próximo incremento:** fixture JSONL versionada, oráculo independente da cadeia PON, saída estruturada, comparação automática e manifestações de execução. Manter controle de commits por branch e registrar resultados após execução real.


## 13. Incremento 03 — C0 rastreável e oráculo independente (12/11/2026)

**Commit de implementação:** `f75b9c8be0d7d6eb54eb091d49dc3d3c1df1bf0a`, branch `tcc2/desenvolvimento`. A validação dinâmica no Windows **ainda não foi realizada** para este incremento. Consulte `docs/tcc2/etapa-07-c0-oraculo-local.md` para comandos e critérios.

- Fixture versionada com sete entradas do protocolo da Etapa 05, `run_id=c0-minimo-v1`, `seed=20260501`, atributos `atA`/`atB`, valores iniciais 0.
- `fixtures/c0_esperado.jsonl`: arquivo de duas saídas esperadas definidas previamente, passos 3 e 7. Sequências previstas: atributo `atA` duas mudanças, `atB` três; `cn1` três transições; `rl1` duas execuções.
- `c0/oracle.py`: oráculo lógico independente, sem importar o pacote PON; `c0/pon_execution.py`: cadeia PON real com notificações locais e rastreamento causal.
- `c0/runner.py`: compara saídas em ordem e multiplicidade, gera JSONL, manifesto e checksums, retorna código 1 em divergência funcional ou 2 em entrada inválida; código 0 planejado apenas em igualdade exata.
- `tests/test_c0.py`: sete casos novos, incluindo teste negativo de divergência, total de 18 casos na suíte.
- `resultados-locais/` ignorado pelo Git; não alterar objetivos nem capítulos LaTeX, nem criar Docker/Kubernetes da aplicação.

**Checkpoint para continuidade:** Etapas 04/05 preservadas; código original congelado; núcleo inicial validado por 11 testes reais (E07-D07/D08), C0 estruturado e **aguardando validação real**; depois C1 exige contratos HTTP/JSON, snapshot inicial, ordenação, deduplicação, testes V02–V07, tudo antes das Etapas 08–10. Registro de prints e arquivos reais permanece requisito para declarações de sucesso.


## 14. Validação real do cenário C0 — 12/11/2026

**Evidência:** três capturas originais de tela do Windows PowerShell, enviadas pelo acadêmico nesta conversa. Execução realizada no computador do acadêmico, não no ambiente da IA. Os PNGs permanecem nesta conversa; **não foram incorporados ao GitHub**. Seus hashes foram calculados sobre os arquivos recebidos.

| ID | Nome recebido | Dimensões | Bytes | SHA-256 |
|---|---|---|---:|---|
| E07-D09 | `image(20261112-202443).png` | 1920x1080 | 134166 | `cfc3b0358aa1e605970c7957663e0b3b0381519c8572889370caeb078b9a0ffd` |
| E07-D10 | `image(20261112-202532).png` | 1920x1080 | 71288 | `c5b7193aaa880505a88cd6e2215bbf077567f642bb4020eb7e9cb6b15afdba09` |
| E07-D11 | `image(20261112-202555).png` | 1920x1080 | 40405 | `df80f651181767ae76a155c9fa864d2775439b601eee38144348c1d89318aa47` |

**Observações reproduzidas nas capturas:**

- Branch `tcc2/desenvolvimento` e `git pull --ff-only` via fast-forward; HEAD exibido `51b3539f8735eb56da754a6239886a3a725860ad`.
- Python 3.13.9 e `python -m compileall -q .\\pon .\\tests .\\c0` com `Compilacao: 0`.
- `python -m unittest discover -s tests -p "test_*.py" -v`: **Ran 18 tests in 0.478s; OK; Testes: 0**. Todos os 18 casos listados apresentam `ok`, inclusive teste positivo/negativo da CLI, oráculo independente e regressões anteriores.
- `python -m c0.runner` retornou relatório com `status: PASS` e `C0: 0`. Campos `expected_fixture_matches_independent_oracle`, `pon_matches_manual_expected` e `pon_matches_independent_oracle` estão `true`.
- Saída esperada/observada `[3,7]`, dois efeitos `rl1:1` e `rl1:2` em sequência, rastreáveis às transições `cn1:1` e `cn1:3` e notificações `atB:1` e `atB:3`.
- Contagens: `request=7`, `attribute_changed=5`, `condition_changed=3`, `rule_effect=2`. Estado final `atA=6`, `atB=1`, condição verdadeira, sequências dos atributos `atA=2`, `atB=3`.
- A tela mostra `effects.jsonl` com duas linhas e `checksums.sha256` com 5 entradas para os arquivos produzidos; os hashes dos arquivos gerados **não foram verificados independentemente a partir de seus bytes**, apenas observados na captura. `git status --short` ao final não exibiu alterações.

**Resultado e limite:** cenário C0 mínimo **aprovado funcionalmente na máquina do acadêmico**, limitado a esta fixture determinística e aos 18 testes. Não se demonstrou execução interprocessos, robustez a falhas, ou desempenho distribuído. O tempo `0.478s` é o tempo da suíte de testes informado por unittest, não uma medição experimental de latência/vazão. Próximo avanço: C1 HTTP/JSON, com validação da comunicação real, snapshots e deduplicação/ordem (V02–V07).


## 15. Preparação do cenário C1 — primeiro incremento de contratos (12/11/2026)

Após comprovação do cenário C0 (seção 14), foi publicado o **esquema de mensagens para C1**, sem servidores HTTP ainda: `prova-conceito/c1/protocol.py`, `c1/__init__.py` e `tests/test_c1_contracts.py`. O protocolo rejeita tipos incompatíveis, IDs incorretos, versões desconhecidas, timestamps não UTC e campos ausentes ou extras. Registra contratos de snapshot para a futura sincronização inicial. O campo `step` é opcional para rastrear a fixture C0.

**Documento específico:** `docs/tcc2/etapa-07-c1-contratos.md`. **Estado:** sete novos testes versionados, total previsto de 25, pendentes de execução real no computador do acadêmico. Isto NÃO comprova V02–V07, comunicação, PIDs distintos, deduplicação nem estado inicial aplicado. O próximo incremento só começará a execução de serviços após confirmação ou diagnóstico dos testes de contrato.


## 16. Evidência C1 — testes dos contratos aprovados no Windows (12/11/2026)

**E07-D12:** arquivo de captura original enviado na conversa `image(20261112-203727).png`, dimensões 1920 × 1080, 135.992 bytes, SHA-256 `a20f0d787f2ceeb7c53dbfe7c362ca14bee695a6214d2ddd1c81b2ad09680d0c`. Imagem está preservada na conversa e **não foi incorporada ao GitHub**.

Comandos e saídas legíveis: branch `tcc2/desenvolvimento`, `git pull --ff-only` por fast-forward, HEAD `fe7e4d9b066d3c3f69b3d781ed9184c9ee2d8943`; Python 3.13.9; `python -m compileall -q .\\pon .\\c0 .\\c1 .\\tests` com `Compilacao: 0`; `python -m unittest discover -s tests -p "test_*.py" -v` com 25 testes `ok`, `Ran 25 tests in 0.542s`, `OK`, `Testes: 0`.

**Classificação:** sete testes novos de validação estrutural dos contratos C1 e as 18 regressões anteriores passaram. O sistema de mensagens ainda **não foi executado por HTTP, nem em três processos**. Portanto V02–V07 não estão aprovados por este teste; a duração da suíte não é medição experimental.


## 17. C1 — máquinas de estado propostas (12/11/2026)

Após a aprovação real dos 25 testes de contratos (E07-D12), publicadas as classes `AttributeSource`, `LogicEngine` e `RuleExecutor` em `prova-conceito/c1/state.py`, junto de 11 testes locais em `tests/test_c1_state.py`. Código disponível nos commits `efbc597fc733b14fb31bbb07bcca3232f30a2f5a` e `21c1de121fbe862bceed8883b64674096212a576`; procedimento detalhado em `docs/tcc2/etapa-07-c1-estados.md`.

**Estado rigoroso:** ainda não executados no Windows os novos testes (36 previstos), tampouco C1 entre três PIDs. A troca entre papéis usa **callbacks no mesmo processo para testes unitários**, não HTTP. O avaliador usa `Attribute/Premise/Condition` e o executor `Rule/Action/Instigation`; as notificações têm snapshots, IDs, ordem e detecção de duplicação. Não há persistência nem recuperação automática, e o snapshot inicial da prova exige watermarks zero. V02–V07 permanecem pendentes de evidências interprocessos.

## E07-D13 — validação das máquinas de estado (12/11/2026)

Captura original do PowerShell do acadêmico: `image(20261112-204915).png`.
SHA-256: `c1a9fdb5fedd4a144a01d4b392b271bfba4dd5f37c8bc240e5534780726a7f69`.
Branch `tcc2/desenvolvimento`, HEAD `52dd849727f179ec938172def7c37daeecec302b`,
Python 3.13.9, `compileall` retorno 0, 36/36 `unittest` OK em 0.471 s, retorno 0.
O tempo é da suíte. A evidência cobre as máquinas de estado em memória.

## C1 HTTP/JSON — rodada automatizada

Três processos em localhost, snapshot inicial e fixture C0 executados com
`PASS`, 12 verificações verdadeiras e efeitos nos passos 3 e 7. A suíte
integrada passou com 37 testes nesta sessão. A reprodução do C1 pelo acadêmico
aguarda nova saída. Evidência anterior E07-D13 registra 36/36 testes das
máquinas de estado no PowerShell do acadêmico. Procedimento, alcance de V02–V07
e hashes em [C1 HTTP](etapa-07-c1-http.md).


## 18. Evidências do C1 e ZIP arquivado localmente (12/11/2026)

Reprodução C1 no Windows comprovada por prints E07-D14 a E07-D16 e arquivo ZIP local com checksum exibido no print E07-D17. Executou 37/37 testes, `C1: 0`, 12/12 verificações e dois efeitos nos passos 3 e 7 em três PIDs diferentes. O conteúdo do ZIP não foi acessado pela IA; a pasta e arquivo permanecem na máquina. SHA, critérios, limitações e classificação por V01–V07 foram registrados no novo `docs/tcc2/etapa-07-aceite-tecnico.md`. **Nova regressão de barreira de snapshot publicada, 38 testes previstos, sem execução Windows ainda.**


## 19. E07-D18 e novo ensaio de inicialização HTTP (12/11/2026)

**E07-D18 — captura original do PowerShell:** `image(20261112-215913).png`, dimensões 1920 × 1080, tamanho 150.253 bytes, SHA-256 **calculado sobre os bytes da imagem recebida**: `538070b0635b8a078750f745071a2b459fd3d9aae7610ff44b49b879d51808b9`.

Resultados observados no Windows: branch `tcc2/desenvolvimento`, HEAD `3742a852a7b448f15a998b18207a02765954019c`, Python 3.13.9, `Compilacao: 0`, `Ran 38 tests in 7.354s`, `OK`, `Testes: 0`. O teste `test_change_during_snapshot_handshake_is_rejected_before_ack` aparece com `ok`. **Esse teste é local em memória e não prova concorrência HTTP**. A duração é da suíte `unittest`, não benchmark do PON. A imagem foi enviada nesta conversa e ainda não é um arquivo bruto do repositório.

- Publicado ensaio `c1/snapshot_race.py` e seu teste de integração `tests/test_c1_snapshot_http_race.py`; roteiro em `docs/tcc2/etapa-07-c1-snapshot-http.md`.
- Não realizado ainda o novo ensaio na máquina do acadêmico. **Não classificar V07 como plenamente aprovado antes da revisão do relatório e dos logs de transporte**.


## 20. Encerramento funcional — E07-D19 a E07-D21 (12/11/2026)

**Apenas para C0/C1 mínimos**, a Etapa 07 foi concluída funcionalmente no Windows. Em `be6b850d599504e9ea8166f02fd87b35313e5445`, o acadêmico executou 39 testes `unittest` aprovados em 11,152s, compilação com código 0 e o ensaio `c1.snapshot_race` com `PASS`, `V07-HTTP: 0`, sete checks verdadeiros e efeitos nos passos 3 e 7. Três PIDs distintos com transporte HTTP local. O ensaio V07 usou um proxy de ACK de teste para reter confirmação do snapshot enquanto uma alteração chegou ao socket, processada depois pelo servidor serial.

**Inventário auditável, SHA-256 dos PNGs, hash exibido do ZIP local, matriz V01–V07 e limites:** `docs/tcc2/etapa-07-encerramento-funcional.md`. V11 com auditoria de bytes do ZIP e confirmação acadêmica pelo orientador permanecem pendentes. Etapas Docker/Kubernetes e experimentos de desempenho ainda não foram executados.
