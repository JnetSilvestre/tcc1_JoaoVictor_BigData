# TCC2 — Etapa 11 / E11-D03 — Auditoria da preparação no Windows

**Data da execução:** 15/11/2026 21:27 (horário local registrado no diretório).  
**Fonte:** transcrição PowerShell fornecida pelo acadêmico nesta conversa; arquivo TXT original não recebido para recálculo independente do SHA-256.  
**Classificação:** PREPARAÇÃO APROVADA COM RESSALVA DE CAMINHO; nenhum benchmark, snapshot, kubectl apply real ou Pod experimental iniciado.

## 1. Git e incidente de diretório
- HEAD antes da rodada: `00f69cd18ed02f4d65a6335e7078d15cad35dc50`.
- A execução do PowerShell começou dentro de `prova-conceito`, e `Push-Location ".\prova-conceito"` buscou incorretamente `prova-conceito\prova-conceito`; erro não terminante devido a `$ErrorActionPreference = "Continue"`.
- Os comandos Python seguintes funcionaram porque o diretório corrente já era `prova-conceito`, mas a etapa de localização falhou e não deve ser declarada sem ressalva.
- `git status --short` terminou sem entradas.
- Para futuros procedimentos usar detecção robusta do diretório, com erro terminante para caminhos ausentes e `try/finally` condicionado a `Push-Location` bem-sucedido.

## 2. Execuções realmente comprovadas pela transcrição
- `python -m compileall -q benchmark tests/test_benchmark.py` não reportou falhas; a saída não contém valor explícito de exit code, mas o fluxo progrediu.
- `unittest discover ... test_benchmark.py`: **6 testes aprovados, 0,052 s de duração da suíte**. Não é benchmark.
- Três fixtures geradas com seed fixa, JSONL e SHA-256 **reportados** pelo gerador:

| N | Seed | Mudanças efetivas | Transições condição | Efeitos esperados | SHA-256 inputs.jsonl | SHA-256 expected.jsonl |
|---:|---:|---:|---:|---:|---|---|
| 100 | 20260501 | 86 | 49 | 25 | e2ee29163bed0755dee2e44c3c17929b7bcb6039cbdf8c16d5907988d2489d14 | 441849d87d3d2d6d56365fa1614dd89445530bd63cc9ec87eda1244e7a46cc3b |
| 1000 | 20260502 | 874 | 500 | 250 | 26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551 | 430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c |
| 10000 | 20260503 | 8749 | 5000 | 2500 | 984d844b5be3e3a4d394dbf2c5e815d067fd2dc9e56dc3e1715e2aa44ff0b323 | 15aad1bb25e7d835ac790f2b4bdae75e23521faaec6fe1f5c28464e854b782b2 |

- Foram gerados manifestos C3/C4 para namespaces `tcc2-pon-e11-c3-p01` e `tcc2-pon-e11-c4-p01`; `kubectl apply --dry-run=client -o name` listou 9 recursos por cenário (Namespace, ConfigMap, três Deployments, três Services e um Pod cliente). Nada foi aplicado.
- `benchmark.runner` sem `--execute` retornou `PLAN_ONLY` para C3/100, com os 25 efeitos previstos e `execute:false`. Nenhum evento enviado.
- Log PowerShell informado: `tcc2-e11-d03-20261115-212711.txt`, SHA-256 exibido `AF5C76D3E6C377A8A70E754CE9CA7FFC8F0C75E2C46AE0FE5D7BD6455325EB48`. Hash do arquivo não auditado independentemente nesta conversa.

## 3. Ajustes preventivos realizados APÓS a saída E11-D03

Os testes reportados pelo acadêmico referem-se à versão anterior ao endurecimento posterior do controlador. Não declarar os patches abaixo como testados no Windows até nova execução:
- `benchmark/runner.py`: salvamento de stdout parcial, stderr parcial e amostras de telemetria em falha/timeout; tentativa de preservar logs/identidades e estados em falha; continua sem retry.
- `benchmark/runner.py`: preflight compara semântica das linhas à fixture canônica regenerada (não apenas seed/tamanho), impedindo carga adulterada com identidade aparentemente correta.
- `tests/test_benchmark.py`: novo assert de rejeição de fixture adulterada dentro da suíte existente.
- Estes ajustes não alteram `pon/`, `c1/`, a imagem C2, nem manifestos/Pods C3/C4.

## 4. Próximo gate

Executar apenas atualização fast-forward e sintaxe/suíte de testes depois dos patches, com localização automática da raiz de `prova-conceito`. Em seguida, revisar a saída e liberar separadamente criação da bancada isolada, antes de um piloto C3 de 100 operações. **Proibido reexecutar snapshot ou fixture sobre C3/C4 validados.**

Status: V12 NÃO EXECUTADO; instrumentação parcial comprovada por testes sintéticos antes dos patches, piloto NÃO EXECUTADO.
