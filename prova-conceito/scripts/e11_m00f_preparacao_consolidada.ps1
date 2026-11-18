# E11-M00F: uma unica chamada, com gates e aceite explicito de C2-S01.
# IMPORTANTE: NAO executa as 30 rodadas definitivas; NAO aplica manifests Kube.
# Efeito mutante APENAS apos consentimento: remove 4 containers e 1 rede
# NOVOS e congelados da qualificacao C2-S01 usando executor ID/label-guarded.
# Nenhum container antigo, namespace antigo, imagem ou ZIP sera alterado.
$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

function Invoke-Gate {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$Command
    )
    Write-Host ("=== " + $Name + " ===") -ForegroundColor Cyan
    & $Command
    if ($LASTEXITCODE -ne 0) {
        throw ("GATE FALHOU: " + $Name + " (codigo " + $LASTEXITCODE + ")")
    }
}
function Assert-True {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) { throw "STOP: $Message" }
}
function Get-HistoricalContainers {
    $rows = @(docker ps -a --format '{{.Names}}|{{.ID}}')
    if ($LASTEXITCODE -ne 0) { throw "Docker ps -a falhou" }
    return @($rows | Where-Object {
        $_ -notmatch '^tcc2-pon-e11-c2-m01-s01-'
    } | Sort-Object)
}
function Get-NamespaceIdentities {
    $json = kubectl --context kind-tcc2-pon get namespaces -o json
    if ($LASTEXITCODE -ne 0) { throw "Namespaces indisponiveis" }
    $obj = $json | ConvertFrom-Json
    return @($obj.items | ForEach-Object {
        $_.metadata.name + "|" + $_.metadata.uid
    } | Sort-Object)
}

try {
    $project = Split-Path -Parent $PSScriptRoot
    Set-Location $project

    $branch = (git branch --show-current).Trim()
    Assert-True ($LASTEXITCODE -eq 0 -and $branch -eq "tcc2/desenvolvimento") "Branch incorreta"
    $porcelain = @(git status --porcelain)
    Assert-True ($LASTEXITCODE -eq 0 -and $porcelain.Count -eq 0) "Git nao esta limpo"
    $sha = (git rev-parse HEAD).Trim()
    Assert-True ($LASTEXITCODE -eq 0 -and $sha.Length -eq 40) "HEAD Git invalido"
    Write-Host "SHA DO CODIGO: $sha"

    Invoke-Gate "COMPILACAO PYTHON" { python -m compileall -q benchmark tests }

    Write-Host "=== REGRESSAO COMPLETA ===" -ForegroundColor Cyan
    # unittest escreve em stderr; cmd redireciona internamente para stdout
    # e evita NativeCommandError espurio no Windows PowerShell 5.1.
    $testLog = @(cmd /c 'python -m unittest discover -s tests -p "test_benchmark*.py" 2>&1')
    $testCode = $LASTEXITCODE
    $testLog | ForEach-Object { Write-Host $_ }
    Assert-True ($testCode -eq 0) "Falha nos testes Python"
    $testText = $testLog -join "`n"
    Assert-True ($testText -match 'Ran 116 tests' -and $testText -match '(?m)^OK\s*$') "Esperados 116 testes PASS"
    Write-Host "REGRESSAO: 116/116 PASS" -ForegroundColor Green

    Assert-True ((docker context show).Trim() -eq "desktop-linux") "Docker context incorreto"
    Assert-True ($LASTEXITCODE -eq 0) "Docker indisponivel"
    $cg = (docker info --format '{{.CgroupVersion}}').Trim()
    Assert-True ($LASTEXITCODE -eq 0 -and $cg -eq "2") "Docker cgroup v2 ausente"
    $image = (docker image inspect tcc2-pon:c2-e08-dbefcd2cf3d2 --format '{{.Id}}').Trim()
    Assert-True ($LASTEXITCODE -eq 0 -and $image -eq "sha256:b9c714f32e359e7a21df264a926a840191c3ffb6d53bb0483f5e161143d8667a") "Imagem aprovada ausente/divergente"

    $nodesJson = kubectl --context kind-tcc2-pon get nodes -o json
    Assert-True ($LASTEXITCODE -eq 0) "Consulta Kube nodes falhou"
    $nodes = ($nodesJson | ConvertFrom-Json).items
    $ready = @($nodes | Where-Object {
        $_.metadata.name -in @("tcc2-pon-worker", "tcc2-pon-control-plane") -and
        @($_.status.conditions | Where-Object {
            $_.type -eq "Ready" -and $_.status -eq "True"
        }).Count -eq 1
    })
    Assert-True ($nodes.Count -eq 2 -and $ready.Count -eq 2) "Dois nos kind nao estao Ready"

    $so = Get-CimInstance Win32_OperatingSystem
    $c = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='C:'"
    $d = Get-CimInstance Win32_LogicalDisk -Filter "DeviceID='D:'"
    $ramGiB = ($so.FreePhysicalMemory * 1KB) / 1GB
    $diskCGiB = $c.FreeSpace / 1GB
    $diskDGiB = $d.FreeSpace / 1GB
    Write-Host ("RAM={0:N2}GiB C={1:N2}GiB D={2:N2}GiB" -f $ramGiB, $diskCGiB, $diskDGiB)
    Assert-True ($ramGiB -ge 3 -and $diskCGiB -ge 15 -and $diskDGiB -ge 15) "Capacidade insuficiente"

    $original = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\C2-m01-s01.zip"
    $backup = "D:\TCC2-Backup\E11-M00E\C2-m01-s01.zip"
    $fixture = Join-Path $env:USERPROFILE "TCC2-Evidencias\E11-M00E\fixture-1000-s01\s1000\inputs.jsonl"
    foreach ($f in @($original, $backup, $fixture)) {
        Assert-True (Test-Path -LiteralPath $f) "Falta arquivo: $f"
    }
    $fixtureHash = (Get-FileHash -LiteralPath $fixture -Algorithm SHA256).Hash.ToLowerInvariant()
    Assert-True ($fixtureHash -eq "26121e3a8747c94fd8e690e040ac31cdd7bd4c6aba14f90551") "Fixture canonica divergente"
    $zipHash = (Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant()
    $backupHash = (Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant()
    $wantedZip = "6e448f37f80456590af80309586e245b038b6e143400cd4b4d325766dd8d5bd6"
    Assert-True ($zipHash -eq $wantedZip -and $backupHash -eq $wantedZip) "ZIP/backup divergente"

    # Capturas de inventario: apenas para comparar identidades, nunca restaurar historicos.
    $historyBefore = @(Get-HistoricalContainers)
    $namespacesBefore = @(Get-NamespaceIdentities)

    Write-Host "=== PREVIA EXCLUSIVA C2-S01 (SOMENTE LEITURA) ===" -ForegroundColor Cyan
    Invoke-Gate "PREVIA SAFETY" {
        python -m benchmark.retirement_execute_c2_s01 --primary $original --backup $backup
    }
    $journal = "D:\TCC2-Backup\E11-M00E\C2-m01-s01-retirement.jsonl"
    Assert-True (-not (Test-Path -LiteralPath $journal)) "Journal de tentativa anterior ja existe"

    # Antes de retirar C2-S01, preparar manifestos NOVOS C3/C4 em DRY RUN
    # somente no cliente. Server-side dry-run nao serve para um Namespace
    # ainda inexistente e resources no mesmo arquivo.
    $stage = Join-Path $env:USERPROFILE ("TCC2-Evidencias\E11-M00F\dry-run-" + $sha.Substring(0,12))
    Assert-True (-not (Test-Path -LiteralPath $stage)) "Preflight desta revisao ja existe; preservar e analisar"
    New-Item -ItemType Directory -Path $stage -Force | Out-Null
    foreach ($scenario in @("C3","C4")) {
        $manifest = Join-Path $stage ($scenario.ToLower() + "-m01-s01.yaml")
        Invoke-Gate "RENDER $scenario" {
            python -m benchmark.prepare --scenario $scenario --label m01-s01 --output $manifest
        }
        Invoke-Gate "DRY RUN CLIENT $scenario" {
            kubectl --context kind-tcc2-pon apply --dry-run=client --validate=strict -f $manifest
        }
        $ns = "tcc2-pon-e11-" + $scenario.ToLower() + "-m01-s01"
        $lookup = @(kubectl --context kind-tcc2-pon get namespace $ns -o name --ignore-not-found)
        Assert-True ($LASTEXITCODE -eq 0 -and $lookup.Count -eq 0) "Namespace de qualificacao $ns JA EXISTE ou consulta falhou"
        Write-Host "$scenario MANIFESTO: PREPARADO/NAO APLICADO" -ForegroundColor Green
    }

    Write-Host ""
    Write-Host "A UNICA operacao destrutiva proposta agora:" -ForegroundColor Yellow
    Write-Host "PARAR E REMOVER 4 CONTEINERES E 1 REDE, SOMENTE da nova C2-S01." -ForegroundColor Yellow
    Write-Host "NENHUM historico, ZIP, Kubernetes ou imagem sera removido." -ForegroundColor Yellow
    Write-Host "O journal sera mantido no volume D:; nao repetir em falha."
    $phrase = "AUTORIZO_DESMOBILIZAR_EXCLUSIVAMENTE_C2_M01_S01"
    $approval = Read-Host "Digite exatamente $phrase para AUTORIZAR; qualquer outra entrada cancela"
    if ($approval -cne $phrase) {
        Write-Host "SEM AUTORIZACAO: C2-S01 permanece intacta." -ForegroundColor Yellow
        Write-Host "RESULTADO: GATES_E_PREVIEW_PASS_C2_NAO_RETIRADA_M01_BLOQUEADA"
        exit 3
    }

    # UM UNICO ponto mutante, depois de testes, dry-run, preview e aceite.
    Invoke-Gate "RETIRADA C2-S01 POR IDs IMUTAVEIS" {
        python -m benchmark.retirement_execute_c2_s01 --primary $original --backup $backup --execute --approve $phrase --approved-head $sha
    }

    Assert-True (Test-Path -LiteralPath $journal) "Journal obrigatorio ausente"
    $lines = @(Get-Content -LiteralPath $journal | Where-Object { $_.Trim() })
    Assert-True ($lines.Count -gt 5) "Journal incompleto"
    $last = $lines[-1] | ConvertFrom-Json
    Assert-True ($last.stage -eq "COMPLETE" -and $last.status -eq "S01_RETIREMENT_COMPLETE") "Retirada nao concluida"

    # Historicos nao podem ser alterados por essa operacao.
    $historyAfter = @(Get-HistoricalContainers)
    $nsAfter = @(Get-NamespaceIdentities)
    Assert-True (($historyBefore -join "`n") -ceq ($historyAfter -join "`n")) "Inventario historico Docker mudou"
    Assert-True (($namespacesBefore -join "`n") -ceq ($nsAfter -join "`n")) "Inventario historico Kube mudou"
    $newContainers = @(docker ps -a --format '{{.Names}}' | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' })
    Assert-True ($LASTEXITCODE -eq 0 -and $newContainers.Count -eq 0) "Container M01 residual"
    $newNetworks = @(docker network ls --format '{{.Name}}' | Where-Object { $_ -match '^tcc2-pon-e11-c2-m' })
    Assert-True ($LASTEXITCODE -eq 0 -and $newNetworks.Count -eq 0) "Rede M01 residual"
    $newNamespaces = @(Get-NamespaceIdentities | Where-Object { $_ -match '^tcc2-pon-e11-c[34]-m' })
    Assert-True ($newNamespaces.Count -eq 0) "Namespace M01 inesperado"

    Assert-True ((Get-FileHash -LiteralPath $original -Algorithm SHA256).Hash.ToLowerInvariant() -eq $wantedZip) "ZIP original alterado"
    Assert-True ((Get-FileHash -LiteralPath $backup -Algorithm SHA256).Hash.ToLowerInvariant() -eq $wantedZip) "ZIP de backup alterado"

    Write-Host "C2-S01: RETIRADA CONTROLADA PASS" -ForegroundColor Green
    Write-Host "HISTORICOS: IDENTIDADES PRESERVADAS" -ForegroundColor Green
    Write-Host "C3/C4: YAML NOVOS PREPARADOS E DRY-RUN PASS; NAO APLICADOS" -ForegroundColor Green
    Write-Host "JOURNAL: $journal"
    Write-Host "MANIFESTOS: $stage"
    Write-Host "RESULTADO: E11_M00F_C2_CLOSED_READY_FOR_KUBE_QUALIFICATION"
    Write-Host "SERIE B01-B10: AINDA NAO INICIADA"
}
catch {
    Write-Host ("STOP / PREPARACAO BLOQUEADA: " + $_.Exception.Message) -ForegroundColor Red
    Write-Host "NAO repetir, reiniciar ou remover recursos em caso de falha parcial." -ForegroundColor Yellow
    exit 2
}
