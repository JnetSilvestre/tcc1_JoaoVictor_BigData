# Etapa 07 — Cenário C1, incremento 01: contratos HTTP/JSON

**Estado:** contratos e testes publicados; o C1 em três processos ainda NÃO foi implementado ou validado.

## 1. Origem e escopo

Preserva as decisões das Etapas 04 e 05 e utiliza como referência funcional o C0 aprovado (18 testes, dois efeitos em passos 3 e 7). Os contratos serão utilizados pelos serviços attribute-source, logic-engine e rule-executor. Nenhuma dependência de terceiros foi adicionada.

## 2. Arquivos deste incremento

- prova-conceito/c1/protocol.py: valida mudança de atributo, snapshot inicial, snapshot de condição, notificação de atributo e notificação de condição; ContractError será convertido em respostas HTTP 4xx no próximo incremento.
- prova-conceito/tests/test_c1_contracts.py: sete testes com campos válidos, obrigatórios/inesperados, versões, tipos, IDs, timestamps e snapshots.
- prova-conceito/c1/__init__.py: pacote Python local.

## 3. Semântica dos contratos

- run_id isola rodadas; event_id segue run_id:entity_id:sequence; sequence ordena notificações por entidade.
- caused_by liga a transição de condição à notificação de atributo; o identificador da regra e o efeito observável serão adicionados no executor.
- step é opcional na mensagem de borda e usado pela fixture C0 para rastreabilidade; não altera os campos mínimos aprovados na Etapa 04.
- emitted_at exige timestamp ISO 8601 com fuso UTC; isso não autoriza comparar relógios monotônicos de processos ou calcular latência experimental por diferença de relógios não sincronizados.
- Valores dos atributos são inteiros e não aceitam booleanos. A prova mínima conhece atA, atB e cn1.
- Snapshots trazem snapshot_version, valores atA/atB e watermarks de sequência; a inicialização coerente e sua rejeição de concorrência ainda precisam ser implementadas/testadas.

## 4. Executar no PowerShell — somente validação dos contratos

Na raiz do repositório local tcc2-trabalho:

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
```

**Expectativa, não resultado no Windows:** 25 testes (18 anteriores + 7 novos), todos aprovados e retorno 0. Guardar capturas originais, código de saída e SHA local.

## 5. Próximos incrementos

1. Implementar estado por papel, deduplicação, rejeição de lacunas, snapshot e disparo observável; testar o fluxo com chamadas locais.
2. Conectar as máquinas de estado por HTTP/JSON e executar três processos Python separados em localhost (C1).
3. Validar V02–V07 e a equivalência da saída C1 com o oráculo C0; preservar PIDs, logs JSONL, scripts e hashes.

Não usar Docker/Kubernetes da aplicação nesta etapa. Não classificar V02–V07 como aprovados antes de provas reais.
