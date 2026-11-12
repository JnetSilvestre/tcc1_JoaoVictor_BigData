# Etapa 07 — Cenário C0: oráculo local determinístico

**Estado:** implementação proposta e versionada; a validação final depende de testes reais na máquina do acadêmico. Nenhuma medição de desempenho foi feita por este roteiro.

## Propósito e fontes

Este incremento materializa o cenário C0 e a fixture mínima de 7 estímulos definidos na Etapa 05. Não constitui implementação NOP Query C++ nem processamento de vídeo. Os dois atributos inteiros iniciam com zero, as premissas são \`atA >= 5\` e \`atB == 1\` e a regra só dispara em transições **falso→verdadeiro**.

- \`fixtures/c0_minimo.jsonl\`: entrada versionada, com \`run_id\`, \`request_id\`, \`entity_id\`, \`value\`, \`step\` e \`seed\`.
- \`fixtures/c0_esperado.jsonl\`: **duas linhas estáticas**, verificadas conceitualmente a partir dos passos 3/7. Não é cópia da saída de \`execute_pon\`.
- \`c0/oracle.py\`: função independente que avalia os estados sem importar o pacote PON.
- \`c0/pon_execution.py\`: executa de fato \`Attribute → Premise → Condition → Rule → Action → Instigation\`; registra \`request\`, \`attribute_changed\`, \`condition_changed\`, \`rule_effect\`.
- \`c0/runner.py\`: compara, preservando ordem e multiplicidade, saídas do PON, oráculo independente e arquivo esperado; gera \`manifest.json\`, \`effects.jsonl\`, \`trace.jsonl\`, \`validation.json\`, \`oracle_independente.jsonl\` e checksums.
- \`tests/test_c0.py\`: sete testes novos (oráculo estático, causalidade, contagens, repetição, entradas inválidas, CLI positiva e CLI negativa).

## Comandos PowerShell

Na raiz do repositório clonado \`$HOME\tcc2\etapa07\tcc2-trabalho\`:

\`\`\`powershell
git branch --show-current
git status --short
git pull --ff-only origin tcc2/desenvolvimento
git rev-parse HEAD
Set-Location .\prova-conceito
python --version
python -m compileall -q .\pon .\tests .\c0
Write-Host "Compilacao: $LASTEXITCODE"
python -m unittest discover -s tests -p "test_*.py" -v
Write-Host "Testes: $LASTEXITCODE"
python -m c0.runner
Write-Host "C0: $LASTEXITCODE"
Get-Content .\resultados-locais\c0-minimo\validation.json
Get-Content .\resultados-locais\c0-minimo\effects.jsonl
Get-Content .\resultados-locais\c0-minimo\checksums.sha256
\`\`\`

**Expectativa a verificar, não resultado já obtido:** suíte ampliada para 18 testes, aprovação C0 com \`"status": "PASS"\`, dois efeitos nos passos 3 e 7, 5 mudanças de atributo, 3 transições de condição e 2 execuções de regra, códigos de saída zero.

## Evidências necessárias

Preservar capturas originais das execuções, \`git rev-parse HEAD\`, entradas, saídas, \`checksums.sha256\`, \`manifest.json\`, JSONL e códigos de retorno. Os arquivos de execução são locais e **não devem ser versionados indiscriminadamente**; para arquivamento científico, decidir diretório e tamanho antes de publicar. Não confundir a duração de \`unittest\` com benchmark.

A execução C0 não requer Docker, Kubernetes, portas ou redes. C1 utilizará os mesmos \`run_id\`, IDs de eventos e oráculo, mas exigirá contratos HTTP/JSON, snapshots, deduplicação e sequenciamento próprios. Uma transição local não demonstra entrega de rede.
