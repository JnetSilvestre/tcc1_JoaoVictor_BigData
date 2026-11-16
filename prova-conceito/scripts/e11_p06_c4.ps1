# TCC2 / Etapa 11 / E11-P06
# PLANO POR PADRAO; -ExecuteOnce realiza UM snapshot e UMA carga C4/1000.
# Nao faz kubectl apply/create/delete/restart e nao reutiliza bancadas anteriores.
[CmdletBinding()]
param([switch]$ExecuteOnce)

$ErrorActionPreference = "Stop"
$project = Split-Path -Parent $PSScriptRoot
$label = "p20261116-001328"
$namespace = "tcc2-pon-e11-c4-$label"
$runId = "e11-c4-$label"
$context = "kind-tcc2-pon"
$approvedAncestor = "4874822c2474d5757963f9f83587df98ed445a1f"
$expectedRecoveryHash = "49348f296b3b85039805e06f0d319bfdb024bdb34ad8b01605935cf57b657f1d"
$expectedInputHash = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"
$expectedOracleHash = "430e61ca65d582f0441eb49649d9577905d0f8fa9e1d5ff04bc01eb53eda7b1c"

$stamp = Get-Date -Format "yyyyMMdd-HHmmss"
$log = Join-Path $env:TEMP "tcc2-e11-p06-$stamp.txt"
$pushed = $false
$executionStarted = $false
$script:failed = $false
Start-Transcript -Path $log | Out-Null
try {
    Write-Host "=== E11-P06: GIT E SINTAXE ==="
    if (-not (Test-Path (Join-Path $project "benchmark\runner.py"))) {
        throw "Projeto invalido."
    }
    Push-Location -LiteralPath $project
    $pushed = $true
    $branch = (git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $branch -ne "tcc2/desenvolvimento") {
        throw "Branch incorreta."
    }
    if ((git status --porcelain | Out-String).Trim()) {
        throw "Git nao esta limpo."
    }
    git merge-base --is-ancestor $approvedAncestor HEAD
    if ($LASTEXITCODE -ne 0) {
        throw "HEAD nao descende da auditoria aprovada."
    }
    $head = (git rev-parse HEAD).Trim()
    $originHead = (git rev-parse origin/tcc2/desenvolvimento).Trim()
    if ($LASTEXITCODE -ne 0 -or $head -ne $originHead) {
        throw "HEAD difere de origin/tcc2/desenvolvimento. Faça git pull --ff-only antes."
    }
    Write-Host "HEAD: $head"
    python -m compileall -q benchmark tests
    if ($LASTEXITCODE -ne 0) { throw "Falha na compilacao sintatica." }
    python -m unittest discover -s tests -p "test_benchmark*.py" -v
    if ($LASTEXITCODE -ne 0) { throw "Unittests falharam." }
    Write-Host "TESTES: PASS"

    Write-Host "=== FIXTURE E ORACULO ==="
    $base = Join-Path $project "resultados-locais\e11-d08-20261115-232603\fixtures\s1000"
    $fixture = Join-Path $base "inputs.jsonl"
    $oracle = Join-Path $base "expected.jsonl"
    foreach ($file in @($fixture,$oracle)) {
        if (-not (Test-Path -LiteralPath $file)) { throw "Arquivo canônico ausente: $file" }
    }
    if ((Get-FileHash -LiteralPath $fixture -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedInputHash) {
        throw "Fixture divergente."
    }
    if ((Get-FileHash -LiteralPath $oracle -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedOracleHash) {
        throw "Oraculo divergente."
    }

    Write-Host "=== RECOVERY E11-R01 AUDITADA ==="
    $recoveryPath = Join-Path $project "resultados-locais\e11-r01-20261116-002238\recovery\recovery-report.json"
    if (-not (Test-Path -LiteralPath $recoveryPath)) {
        throw "Relatorio do E11-R01 nao encontrado."
    }
    if ((Get-FileHash -LiteralPath $recoveryPath -Algorithm SHA256).Hash.ToLowerInvariant() -ne $expectedRecoveryHash) {
        throw "Hash da recovery anterior divergente."
    }
    $recovery = Get-Content -LiteralPath $recoveryPath -Raw | ConvertFrom-Json
    if ($recovery.status -ne "PASS_COLD_READ_ONLY" -or
        $recovery.namespace -ne $namespace -or $recovery.run_id -ne $runId -or
        $recovery.cold_state_confirmed -ne $true -or
        $recovery.snapshot_executed -ne $false -or
        $recovery.benchmark_executed -ne $false) {
        throw "Recovery anterior nao confirma estado frio."
    }

    Write-Host "=== CONTEXTO E IDENTIDADES DOS QUATRO PODS ==="
    $currentContext = (kubectl config current-context).Trim()
    if ($LASTEXITCODE -ne 0 -or $currentContext -ne $context) {
        throw "Contexto Kubernetes incorreto."
    }
    $podsText = kubectl --context $context -n $namespace get pods -o json
    if ($LASTEXITCODE -ne 0) { throw "Nao foi possivel consultar os Pods C4." }
    $pods = @( (($podsText | Out-String) | ConvertFrom-Json).items )
    if ($pods.Count -ne 4) { throw "A bancada C4 nao possui exatamente 4 Pods." }
    $nodesByRole = @{
        "attribute-source" = "tcc2-pon-worker"
        "logic-engine" = "tcc2-pon-control-plane"
        "rule-executor" = "tcc2-pon-worker"
        "e11-benchmark-client" = "tcc2-pon-worker"
    }
    foreach ($role in $nodesByRole.Keys) {
        $foundPods = @( $pods | Where-Object { $_.metadata.labels.app -eq $role } )
        if ($foundPods.Count -ne 1) { throw "Pod ausente/duplicado: $role" }
        $podInfo = $foundPods[0]
        $previous = $recovery.pods.PSObject.Properties[$role].Value
        $statuses = @($podInfo.status.containerStatuses)
        if ($null -eq $previous -or
            $podInfo.metadata.uid -ne $previous.uid -or
            $podInfo.metadata.name -ne $previous.name -or
            $podInfo.spec.nodeName -ne $nodesByRole[$role] -or
            $podInfo.status.phase -ne "Running" -or
            $statuses.Count -ne 1 -or
            $statuses[0].ready -ne $true -or
            $statuses[0].restartCount -ne 0 -or
            $statuses[0].containerID -ne $previous.container_id -or
            $statuses[0].imageID -ne $previous.runtime_image_id -or
            $podInfo.spec.containers[0].image -ne $previous.image_tag) {
            throw "Pod foi alterado desde E11-R01: $role"
        }
        Write-Host "POD PASS: $role / $($podInfo.metadata.uid)"
    }

    Write-Host "=== PLAN_ONLY EM BANCADA JA PREPARADA ==="
    $out = Join-Path $project "resultados-locais\e11-p06-$stamp"
    New-Item -ItemType Directory -Path $out -ErrorAction Stop | Out-Null
    $runOut = Join-Path $out "run"
    $podsText | Set-Content -LiteralPath (Join-Path $out "pods-before.json") -Encoding UTF8
    Write-Host "RUN_ID: $runId"
    Write-Host "NAMESPACE: $namespace"
    Write-Host "EVIDENCIAS: $out"
    python -m benchmark.runner --scenario C4 --label $label --run-id $runId --fixture $fixture --output $runOut
    if ($LASTEXITCODE -ne 0) { throw "PLAN_ONLY falhou." }

    if (-not $ExecuteOnce) {
        Write-Host "E11-P06: PLAN_ONLY PASS"
        Write-Host "SNAPSHOT: NAO; BENCHMARK: NAO; APPLY: NAO"
    } else {
        Write-Host "=== E11-P06: EXECUCAO UNICA DE 1000 ==="
        Write-Host "O runner revalida cold state/logs ANTES do primeiro snapshot."
        $executionStarted = $true
        python -m benchmark.runner --scenario C4 --label $label --run-id $runId --fixture $fixture --output $runOut --timeout 10 --batch-timeout 600 --period 1 --execute
        if ($LASTEXITCODE -ne 0) { throw "Piloto falhou. NAO repetir snapshot/carga." }
        $validation = Join-Path $runOut "validation.json"
        if (-not (Test-Path -LiteralPath $validation)) {
            throw "validation.json ausente. NAO repetir."
        }
        $v = Get-Content -LiteralPath $validation -Raw | ConvertFrom-Json
        if ($v.status -ne "PASS") { throw "Validacao funcional falhou. NAO repetir." }
        $q = $v.validation.metric_quality
        Write-Host "STATUS_FUNCIONAL: $($v.status)"
        Write-Host "CPU_WINDOW_ADEQUATE: $($q.cpu_window_adequate)"
        Write-Host "MEMORY_WINDOW_ADEQUATE: $($q.memory_window_adequate)"
        Write-Host "CLOCK_COHERENT: $($q.clock_coherent)"
        Write-Host "METRIC_SAMPLES: $($q.sample_count)"
        Write-Host "AUDITORIA CIENTIFICA: PENDENTE"
        if ($q.issues) { $q.issues | ForEach-Object { Write-Host "ISSUE: $_" } }
        $zip = "$runOut.zip"
        if (-not (Test-Path -LiteralPath $zip)) { throw "ZIP do piloto ausente." }
        Write-Host "ZIP: $zip"
        Write-Host "ZIP_SHA256: $((Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash)"
        Write-Host "E11-P06: PASS FUNCIONAL; METRICAS EM AUDITORIA"
    }
}
catch {
    $script:failed = $true
    Write-Host "E11-P06: BLOQUEADO OU FAIL" -ForegroundColor Red
    Write-Host "ERRO: $($_.Exception.Message)"
    if ($executionStarted) {
        Write-Host "NAO REPETIR NESTA BANCADA. Preservar ZIP e estado dos Pods." -ForegroundColor Yellow
    } else {
        Write-Host "Nenhum snapshot/carga iniciado pelo script E11-P06."
    }
}
finally {
    if ($pushed) { Pop-Location }
    Stop-Transcript | Out-Null
    Write-Host "LOG: $log"
    if (Test-Path -LiteralPath $log) {
        Write-Host "LOG_SHA256: $((Get-FileHash -LiteralPath $log -Algorithm SHA256).Hash)"
    }
}
if ($script:failed) { throw "E11-P06 interrompido. Consulte o log; nao repetir carga." }
