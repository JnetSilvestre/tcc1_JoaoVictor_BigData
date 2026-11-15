# Etapa 08 — Execução consolidada de V06: E08-D18G/H

## Situação e pré-requisitos

Cenário **C2 (três contêineres Docker em um único host)**, sem Kubernetes ou métricas de benchmark.

**Já validado e auditado independentemente:**
- E08-D18D/E: snapshot `v06-order-v1`, 3/3 serviços prontos, zero efeitos. ZIP `c2-v06-snapshot-20261115-180612.zip`, SHA-256 `544e9fe8eb12878268393db5eeddaa698a9c02cee5c19080f56cb490a2c21987`.
- E08-D18F: `AttributeChanged` válido com sequência 2 antes de 1, rejeitado HTTP 409, estados inalterados, somente um novo log no avaliador. ZIP original `c2-v06-attribute-gap-r1-20261115-182647.zip`, **14 entradas/13 hashes** auditadas diretamente em 15/11/2026 na conversa; 6.807 bytes; SHA-256 `4a92b7e6307e46161c6a5cf818a7ffdf7a241ba69be24fe0ef126a82655e77da`. Não repetir o POST.

**Pendente, não executado neste commit:**
1. **E08-D18G:** `AttributeChanged` de outra rodada (`run_id=v06-other-run`) ao avaliador. Exige HTTP 409 `run_id divergente`, nenhum efeito ou alteração de estado.
2. **E08-D18H:** `ConditionChanged` com sequência 2 antes de 1 no executor. Exige HTTP 409 `evento atrasado ou lacuna de sequence`, nenhum efeito ou alteração de estado.

O executor `prova-conceito/c2/v06_batch.py` tem preflight de branch limpa, imagem, rede, IDs/horários/restarts, V05 rodando, estados e logs V06 idênticos aos últimos arquivos de E08-D18F e SHA-256 dos 13 arquivos do manifesto. O executor **não** repete E08-D18F, o snapshot, ou qualquer outro POST anterior. Antes de cada novo POST escreve `request-intent.json`; executa no máximo uma tentativa por caso, verifica resposta e estado/logs, interrompe imediatamente após qualquer divergência, e arquiva ZIP com bytes conferidos. Em caso de falha, **não repetir a execução**: analisar as evidências primeiro.

## Comando único na máquina Windows

Executar no PowerShell, a partir do clone local da branch `tcc2/desenvolvimento`:

```powershell
Set-Location "$HOME\tcc2\etapa07\tcc2-trabalho\prova-conceito"
git pull --ff-only origin tcc2/desenvolvimento
if ($LASTEXITCODE -ne 0) { throw "Falha no git pull" }

python -m compileall -q c0 c1 c2 pon tests
if ($LASTEXITCODE -ne 0) { throw "Compilacao falhou" }

python -m unittest discover -s tests -p 'test_*.py' -q
if ($LASTEXITCODE -ne 0) { throw "Regressao falhou; nenhum POST enviado" }

$anterior = "resultados-locais/c2-v06-attribute-gap-r1-20261115-182647"
if (-not (Test-Path -LiteralPath $anterior)) {
  throw "Pasta de evidencias E08-D18F nao encontrada: nao executar POST"
}
$saida = "resultados-locais/c2-v06-batch-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
python -m c2.v06_batch --snapshot $anterior --output $saida
$codigo = $LASTEXITCODE
git status --short
if ($codigo -ne 0) {
  throw "E08-D18G/H nao aprovados. NAO executar novamente nem reenviar notificacoes."
}
Write-Host "Rodada V06 G/H aprovada; arquivamento e hashes impressos acima."
```

A suíte deve ter **93 testes previstos** (88 existentes antes desta mudança + 5 novos), mas **nenhum resultado de execução no Windows deve ser inferido antecipadamente**. Se algum teste falhar, interromper antes de produzir eventos.

## Evidências e aceite

Saída em `prova-conceito/resultados-locais/c2-v06-batch-<timestamp>/` e ZIP adjacente. Os arquivos incluem `manifest.json`, `states-before/after.json`, `validation.json`, `checksums.sha256`, logs antes/depois por serviço, além de `E08-D18G/` e `E08-D18H/` com requisição, intenção, resposta, estado pós-POST e logs. ZIP é verificado quanto a CRC, bytes e contagem; a auditoria científica **independente** exige receber o ZIP bruto e revalidar os hashes e o conteúdo.

- `status=PASS`, `cases_completed=2`, duas respostas 409 esperadas.
- Estados idênticos antes/depois dos dois casos, sem novos efeitos.
- Somente um log `mutation` de rejeição no receptor designado para cada caso; os demais logs preservados.
- Sem alteração de `run_id`, watermark e snapshot; V05 em execução.

**Após V06:** avaliar formalmente cobertura V07 em C2 (snapshot e teste anterior em C1), registrar limites: ausência de restart/recovery, persistência e concorrência geral, e preparar encerramento Etapa 08. O teste de C3/Kubernetes pertence às Etapas 09/10.
