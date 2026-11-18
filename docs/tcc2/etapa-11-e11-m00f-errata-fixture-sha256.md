# E11-M00F — Errata de SHA-256 truncado na preparação consolidada

**Data:** 17/11/2026 (America/Sao_Paulo). **Origem:** saída PowerShell fornecida pelo acadêmico após execução do script consolidado em `92fc883b5179afc48053fd6ad8399486f9895b84`.

## 1. Evidência observada

Na versão `92fc883...` foram reportados:

- `Ran 116 tests in 0.226s`, `OK`, `REGRESSAO: 116/116 PASS`.
- `RAM=8,17GiB C=67,40GiB D=69,53GiB`.
- Em seguida: `STOP / PREPARACAO BLOQUEADA: STOP: Fixture canonica divergente`.
- **O STOP ocorreu antes** de `PREVIA EXCLUSIVA C2-S01`, renderização/dry-run C3/C4, `Read-Host` de autorização e de qualquer stop/rm. **Não foi efetuada desmobilização**, snapshot, POST, apply ou campanha definitiva nesta tentativa.

## 2. Diagnóstico preciso e correção

Inspeção textual do código exato publicado revelou uma **constante SHA-256 truncada com 50 caracteres**:

- INCORRETA no script v92fc883: `26121e3a8747c94fd8e690e040ac31cdd7bd4c6aba14f90551` (**50** hex).
- CORRETA no pré-registro e no `manifest.json` do ZIP C2-S01, conferida contra o valor da fixture determinística previamente observada: `26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551` (**64** hex).

**Causa confirmada do bloqueio da checagem:** string de comparação errada no código do script. Isso torna impossível passar quando `Get-FileHash` retorna um SHA-256 válido com 64 hex. **A saída fornecida não inclui o hash real atual do arquivo no Windows**, logo não se afirma nova validação da integridade do arquivo após essa tentativa. Evidência anterior do executor C2-S01 e `manifest.json` registrou o SHA correto; o arquivo original não foi editado nesta correção.

**Alterações versionadas:** corrigir constante; imprimir hash observado e esperado apenas em caso de divergência real; conferir comprimento da constante antes do gate; adicionar `tests/test_benchmark_powershell_preflight.py` com **1 teste estático de regressão do literal completo/gate**; atualizar contagem esperada de 116 para **117** testes. **Nenhum comportamento experimental da PoC, oráculo, fixture, Docker ou Kubernetes mudou.**

## 3. Retomada e critérios

- Após `git pull --ff-only`, conferir SHA novo, Git limpo e executar o script consolidado novamente, que repetirá as verificações desde o início. A tentativa anterior **parou antes de criar diretório de dry-run ou journal e antes de retirar a bancada**, portanto a retomada não representa um retry de execução mutante; nenhum cleanup automático deve ocorrer.
- O teste de regressão novo e a versão corrigida **ainda não foram executados no Windows**; não atribuir `117/117 PASS` antecipadamente.
- O procedimento continua exigindo **aceite interativo explícito** para a única ação mutante possível: desmobilizar **quatro contêineres e uma rede NOVOS C2-S01**, por IDs exatos, sem alterar históricos. O operador pode recusar e o código retorna status bloqueado.
- Se a nova execução reportar `FIXTURE_SHA256_OBSERVADO` diferente do esperado de 64 hex, **não sobrescrever fixture, não regenerar silenciosamente e não executar remoção**; analisar valor efetivamente retornado.
- Manter `E11_M01_BLOCKED`: o script **não** aplica C3/C4 nem realiza as 30 rodadas científicas.

**Veredito desta errata:** `E11_M00F_PRECHECK_HASH_LITERAL_BUG_FIXED_CODE_NOT_YET_RUNTIME_TESTED`.
