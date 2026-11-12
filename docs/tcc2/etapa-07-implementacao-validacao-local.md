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
