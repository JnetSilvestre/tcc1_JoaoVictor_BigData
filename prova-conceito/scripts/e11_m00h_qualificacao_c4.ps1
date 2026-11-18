# E11-M00H: qualificacao sacrificial C4-S01 (fora dos 30 lotes).
# Somente namespace NOVO, com aceite interativo. Nao remove recursos nem
# reinicia historicos. Em falha, preservar o namespace, ZIP e journal.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Assert-Gate([bool]$condition, [string]$message) {
    if (-not $condition) { throw "STOP: $message" }
}
function Run-Checked([string]$step, [scriptblock]$command) {
    Write-Host ("=== " + $step + " ===") -ForegroundColor Cyan
    & $command
    Assert-Gate ($LASTEXITCODE -eq 0) ("Falha: " + $step)
}
function Write-Journal([string]$stage, [string]$note) {
    $line = [pscustomobject]@{
        utc = (Get-Date).ToUniversalTime().ToString("o")
        stage = $stage
        run_id = "e11-c4-m01-s01"
        note = $note
    } | ConvertTo-Json -Compress
    Add-Content -LiteralPath $journal -Value $line -Encoding UTF8
}
try {
    Set-Location (Split-Path -Parent $PSScriptRoot)
    $branch = (git branch --show-current).Trim()
    Assert-Gate ($LASTEXITCODE -eq 0 -and $branch -eq "tcc2/desenvolvimento") "Branch incorreta"
    $dirty = @(git status --porcelain)
    Assert-Gate ($LASTEXITCODE -eq 0 -and $dirty.Count -eq 0) "Git possui mudancas"
    $sha = (git rev-parse HEAD).Trim()
    Assert-Gate ($LASTEXITCODE -eq 0 -and $sha.Length -eq 40) "SHA Git invalido"
    Write-Host "GIT_SHA=$sha"

    Run-Checked "COMPILAR" { python -m compileall -q benchmark tests }
    $tests = @(cmd /c 'python -m unittest discover -s tests -p "test_benchmark*.py" 2>&1')
    $testExit = $LASTEXITCODE
    $tests | ForEach-Object { Write-Host $_ }
    $text = $tests -join [Environment]::NewLine
    Assert-Gate ($testExit -eq 0 -and $text -match "Ran 129 tests" -and $text -match "(?m)^OK\s*$") "Regressao 129/129 nao aprovada"
    Write-Host "REGRESSAO: 129/129 PASS" -ForegroundColor Green

    $dockerContext = (docker context show).Trim()
    Assert-Gate ($LASTEXITCODE -eq 0 -and $dockerContext -eq "desktop-linux") "Docker nao esta no contexto aprovado"
    $cgroup = (docker info --format '{{.CgroupVersion}}').Trim()
    Assert-Gate ($LASTEXITCODE -eq 0 -and $cgroup -eq "2") "Cgroup v2 indisponivel"
    $imageID = (docker image inspect tcc2-pon:c2-e08-dbefcd2cf3d2 --format '{{.Id}}').Trim()
    $approvedImageID = "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a"
    Write-Host "IMAGE_ID_OBSERVADO: $imageID"
    Write-Host "IMAGE_ID_APROVADO: $approvedImageID"
    Assert-Gate ($LASTEXITCODE -eq 0 -and $imageID -ceq $approvedImageID) "Imagem nao e a aprovada"

    $nodesRaw = kubectl --context kind-tcc2-pon get nodes -o json
    Assert-Gate ($LASTEXITCODE -eq 0) "Cluster Kubernetes indisponivel"
    $nodes = ($nodesRaw | ConvertFrom-Json).items
    $ready = @($nodes | Where-Object {
        $_.metadata.name -in @("tcc2-pon-control-plane","tcc2-pon-worker") -and
        @($_.status.conditions | Where-Object { $_.type -eq "Ready" -and $_.status -eq "True" }).Count -eq 1
    })
    Assert-Gate ($nodes.Count -eq 2 -and $ready.Count -eq 2) "Dois nos kind devem estar Ready"

    $os = Get-CimInstance Win32_OperatingSystem
    $c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $d = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
    $ram = ($os.FreePhysicalMemory * 1KB)/1GB
    $freeC = $c.FreeSpace/1GB
    $freeD = $d.FreeSpace/1GB
    Write-Host ("RAM_WINDOWS={0:N2}GiB C={1:N2}GiB D={2:N2}GiB" -f $ram,$freeC,$freeD)
    Assert-Gate ($ram -ge 3 -and $freeC -ge 15 -and $freeD -ge 15) "Capacidade inferior ao limite conservador"

    $fixture = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl"
    $c2original = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\C2-m01-s01.zip"
    $c2backup = "D:\TCC2-Backup\E11-M00E\C2-m01-s01.zip"
    $c2journal = "D:\TCC2-Backup\E11-M00E\C2-m01-s01-retirement.jsonl"
    foreach ($item in @($fixture,$c2original,$c2backup,$c2journal)) {
        Assert-Gate (Test-Path -LiteralPath $item) "Evidencia anterior nao localizada: $item"
    }
    $last = (Get-Content -LiteralPath $c2journal | Where-Object { $_.Trim() } | Select-Object -Last 1) | ConvertFrom-Json
    Assert-Gate ($last.stage -eq "COMPLETE" -and $last.status -eq "S01_RETIREMENT_COMPLETE") "C2-S01 ainda nao desmobilizada"
    $shaFixture = (Get-FileHash -LiteralPath $fixture -Algorithm SHA256).Hash.ToLowerInvariant()
    $approvedFixtureHash = "26121e3a8747c94fd8e690e4ca04762cf469e040ac31cdd7bd4c6aba14f90551"
    Write-Host "FIXTURE_SHA256_OBSERVADO: $shaFixture"
    Assert-Gate ($shaFixture -ceq $approvedFixtureHash) "Fixture canonica divergente"
    foreach ($file in @($c2original,$c2backup)) {
        $h = (Get-FileHash -LiteralPath $file -Algorithm SHA256).Hash.ToLowerInvariant()
        Assert-Gate ($h -eq "6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6") "ZIP C2-S01 alterado"
    }

    # C3 qualificada e desmobilizada por precondicao UID; auditoria C3 preservada.
    $c3Zip = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00G\C3-m01-s01\resultado.zip"
    $c3Backup = "D:\TCC2-Backup\E11-M00G\C3-m01-s01.zip"
    $c3Journal = "D:\TCC2-Backup\E11-M00G\C3-m01-s01-retirement.jsonl"
    foreach ($f in @($c3Zip, $c3Backup, $c3Journal)) {
        Assert-Gate (Test-Path -LiteralPath $f) "Evidencia/retirada C3 ausente: $f"
    }
    $c3End = (Get-Content -LiteralPath $c3Journal |
        Where-Object { $_.Trim() } | Select-Object -Last 1) | ConvertFrom-Json
    Assert-Gate ($c3End.stage -eq "COMPLETE" -and
        $c3End.status -eq "C3_S01_RETIREMENT_COMPLETE") "C3-S01 ainda nao foi desmobilizada"
    $expectedC3Sha = "463f56042536c95874a4f36dadfd5fd211fec18325132704c9f585d2ec6e80c8"
    foreach ($f in @($c3Zip, $c3Backup)) {
        $h3 = (Get-FileHash -LiteralPath $f -Algorithm SHA256).Hash.ToLowerInvariant()
        Assert-Gate ($h3 -eq $expectedC3Sha) "ZIP C3-S01 alterado"
    }

    $dockerBefore = @(docker ps -a --format '{{.Names}}|{{.ID}}' | Sort-Object)
    Assert-Gate ($LASTEXITCODE -eq 0) "Erro no inventario Docker"
    $dockerNames = @($dockerBefore | ForEach-Object { ($_ -split '\|')[0] })
    Assert-Gate (@($dockerNames | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' }).Count -eq 0) "Outra bancada Docker M01, inclusive parada"
    $networks = @(docker network ls --format '{{.Name}}')
    Assert-Gate ($LASTEXITCODE -eq 0 -and @($networks | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' }).Count -eq 0) "Rede M01 residual"
    $nsRaw = kubectl --context kind-tcc2-pon get namespaces -o json
    Assert-Gate ($LASTEXITCODE -eq 0) "Erro no inventario de namespaces"
    $nsItems = ($nsRaw | ConvertFrom-Json).items
    Assert-Gate (@($nsItems | Where-Object { $_.metadata.name -match '^tcc2-pon-e11-c[34]-m' }).Count -eq 0) "Namespace M01 anterior presente"
    $historicUIDs = @($nsItems | ForEach-Object { $_.metadata.name + "|" + $_.metadata.uid } | Sort-Object)

    $ns = "tcc2-pon-e11-c4-m01-s01"
    $dir = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00H\C4-m01-s01"
    $manifest = Join-Path $dir "manifest.yaml"
    $outputDir = Join-Path $dir "resultado"
    $zip = "$outputDir.zip"
    $backupDir = "D:\TCC2-Backup\E11-M00H"
    $backup = Join-Path $backupDir "C4-m01-s01.zip"
    $journal = Join-Path $backupDir "C4-m01-s01-journal.jsonl"
    foreach ($p in @($dir,$zip,$backup,$journal)) {
        Assert-Gate (-not (Test-Path -LiteralPath $p)) "Tentativa previa existe; nao repetir: $p"
    }
    Write-Host "QUALIFICACAO: C4-S01 SACRIFICIAL, FORA DAS 30 RODADAS" -ForegroundColor Cyan
    Write-Host "ACAO: cria apenas o namespace NOVO $ns e executa 1000 POSTs uma unica vez." -ForegroundColor Yellow
    Write-Host "C4 sera preservada ate auditoria do ZIP e autorizacao posterior de retirada." -ForegroundColor Yellow
    $approval = Read-Host "Digite AUTORIZO_EXECUTAR_QUALIFICACAO_C4_S01 para executar; outra resposta cancela"
    if ($approval -cne "AUTORIZO_EXECUTAR_QUALIFICACAO_C4_S01") {
        Write-Host "CANCELADO: nenhum recurso criado." -ForegroundColor Yellow
        exit 3
    }

    New-Item -ItemType Directory -Path $dir -ErrorAction Stop | Out-Null
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null
    Run-Checked "GERAR MANIFESTO INEDITO" { python -m benchmark.prepare --scenario C4 --label m01-s01 --output $manifest }
    Run-Checked "VALIDAR MANIFESTO SEM APPLY" { kubectl --context kind-tcc2-pon apply --dry-run=client --validate=strict -f $manifest }

    # Revalidar exclusividade no instante imediatamente anterior ao apply.
    $redoDocker = @(docker ps -a --format '{{.Names}}')
    Assert-Gate ($LASTEXITCODE -eq 0 -and @($redoDocker | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' }).Count -eq 0) "Bancada Docker M01 apareceu durante preflight"
    $redoNetworks = @(docker network ls --format '{{.Name}}')
    Assert-Gate ($LASTEXITCODE -eq 0 -and @($redoNetworks | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' }).Count -eq 0) "Rede Docker M01 apareceu durante preflight"
    $redoNsRaw = kubectl --context kind-tcc2-pon get namespaces -o json
    Assert-Gate ($LASTEXITCODE -eq 0) "Nao foi possivel reconfirmar namespaces"
    $redoNsItems = ($redoNsRaw | ConvertFrom-Json).items
    Assert-Gate (@($redoNsItems | Where-Object { $_.metadata.name -match '^tcc2-pon-e11-c[34]-m' }).Count -eq 0) "Namespace M01 apareceu durante preflight"
    New-Item -ItemType File -Path $journal -ErrorAction Stop | Out-Null
    Write-Journal "BEFORE_APPLY" ("git=" + $sha)
    Run-Checked "APLICAR SOMENTE MANIFESTO C4-S01" { kubectl --context kind-tcc2-pon apply -f $manifest }
    Write-Journal "AFTER_APPLY" $ns
    foreach ($role in @("rule-executor","logic-engine","attribute-source")) {
        Run-Checked ("AGUARDAR " + $role) { kubectl --context kind-tcc2-pon -n $ns rollout status deployment/$role --timeout=180s }
    }
    Run-Checked "AGUARDAR CLIENTE" { kubectl --context kind-tcc2-pon -n $ns wait --for=condition=Ready pod/e11-benchmark-client --timeout=180s }
    $nsDetails = kubectl --context kind-tcc2-pon get namespace $ns -o json
    Assert-Gate ($LASTEXITCODE -eq 0) "Namespace nao respondeu"
    $metadata = ($nsDetails | ConvertFrom-Json).metadata
    Assert-Gate ($metadata.labels.'tcc2.e11/campaign' -eq "m01" -and $metadata.labels.'tcc2.e11/run-id' -eq "e11-c4-m01-s01" -and -not [string]::IsNullOrWhiteSpace($metadata.uid)) "Proveniencia de namespace divergente"
    Write-Journal "NAMESPACE_UID" $metadata.uid

    Write-Journal "BEFORE_SNAPSHOT_BATCH" "Nao repetir caso interrompido"
    Run-Checked "EXECUTAR QUALIFICACAO C4 UMA VEZ" {
        python -m benchmark.runner --scenario C4 --label m01-s01 --run-id e11-c4-m01-s01 --fixture $fixture --output $outputDir --measurement-mode timing_only --timeout 10 --batch-timeout 600 --execute
    }
    Write-Journal "AFTER_BATCH" "executor PASS"
    Assert-Gate (Test-Path -LiteralPath $zip) "ZIP da rodada ausente"
    Run-Checked "AUDITAR ZIP" {
        python -c "from benchmark.lifecycle_audit import audit_archive; import json,sys; print(json.dumps(audit_archive(sys.argv[1],'C4','m01-s01','e11-c4-m01-s01')))" $zip
    }
    Assert-Gate (-not (Test-Path -LiteralPath $backup)) "Destino de backup ja existe"
    Copy-Item -LiteralPath $zip -Destination $backup -ErrorAction Stop
    $reportJson = @(python -m benchmark.backup_integrity --primary $zip --backup $backup)
    Assert-Gate ($LASTEXITCODE -eq 0) "Auditoria da copia falhou"
    $report = ($reportJson -join [Environment]::NewLine) | ConvertFrom-Json
    Assert-Gate ($report.status -eq "BACKUP_BYTES_VERIFIED_NO_CLEANUP_AUTHORIZATION" -and $report.different_filesystem_volume -eq $true) "Backup invalido"
    Write-Journal "BACKUP_PASS" $report.zip_sha256

    $dockerAfter = @(docker ps -a --format '{{.Names}}|{{.ID}}' | Sort-Object)
    Assert-Gate ($LASTEXITCODE -eq 0 -and ($dockerBefore -join '|') -ceq ($dockerAfter -join '|')) "Inventario de containers historicos mudou"
    $nowRaw = kubectl --context kind-tcc2-pon get namespaces -o json
    Assert-Gate ($LASTEXITCODE -eq 0) "Falha no inventario de namespaces final"
    $nowItems = ($nowRaw | ConvertFrom-Json).items
    $oldNow = @($nowItems | Where-Object { $_.metadata.name -ne $ns } | ForEach-Object { $_.metadata.name + "|" + $_.metadata.uid } | Sort-Object)
    Assert-Gate (($historicUIDs -join '|') -ceq ($oldNow -join '|')) "UID de algum namespace historico mudou"
    Write-Journal "COMPLETE" "C4_S01_PASS_ZIP_BACKUP_PRESERVADOS"
    Write-Host "QUALIFICACAO_C4_S01_PASS_ZIP_BACKUP_PRESERVADOS" -ForegroundColor Green
    Write-Host "ZIP: $zip"
    Write-Host "BACKUP: $backup"
    Write-Host "SHA256: $($report.zip_sha256)"
    Write-Host "JOURNAL: $journal"
    Write-Host "NAMESPACE: $ns UID: $($metadata.uid)"
    Write-Host "C3 e C4: QUALIFICACOES SACRIFICIAIS CONCLUIDAS; 30 LOTES: NAO INICIADOS"
}
catch {
    $journalVariable = Get-Variable -Name journal -ErrorAction SilentlyContinue
    if ($null -ne $journalVariable -and (Test-Path -LiteralPath $journalVariable.Value)) {
        try { Write-Journal "STOP_NO_RETRY" $_.Exception.Message } catch {}
    }
    Write-Host ("STOP: " + $_.Exception.Message) -ForegroundColor Red
    Write-Host "Preservar recursos, dados, journal e nao repetir automaticamente." -ForegroundColor Yellow
    exit 2
}
