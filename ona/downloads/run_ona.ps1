# run_ona.ps1 — one-shot ONA driver. Auto-detects Rscript, ensures kaleido,
# runs the parameterized R template, then renders PNG via the kaleido bridge.
#
# Usage:
#   pwsh run_ona.ps1 -RScript .\my_ona_run.R -OutDir .\figures `
#                    -OutBaseName ona_figure [-Width 1200] [-Height 750]
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string]$RScript,
    [Parameter(Mandatory = $true)] [string]$OutDir,
    [Parameter(Mandatory = $true)] [string]$OutBaseName,
    [int]$Width = 1200,
    [int]$Height = 750,
    [string]$Rscript_Exe = "C:\Program Files\R\R-4.5.2\bin\Rscript.exe",
    [string]$Python_Exe = "python"
)

$ErrorActionPreference = "Stop"
$skillDir = Split-Path -Parent $PSCommandPath
$renderer = Join-Path $skillDir "render_ona_kaleido.py"

if (-not (Test-Path $Rscript_Exe)) {
    $cands = @(
        "C:\Program Files\R\R-4.5.2\bin\Rscript.exe",
        "C:\Program Files\R\R-4.5.1\bin\Rscript.exe",
        "C:\Program Files\R\R-4.4.2\bin\Rscript.exe",
        "C:\Program Files\R\R-4.4.1\bin\Rscript.exe"
    )
    $found = $cands | Where-Object { Test-Path $_ } | Select-Object -First 1
    if ($null -eq $found) {
        throw "Rscript not found. Install R 4.4+ or pass -Rscript_Exe."
    }
    $Rscript_Exe = $found
}

Write-Host "[ona] Rscript: $Rscript_Exe"

# Ensure Python deps
$probe = & $Python_Exe -c "import kaleido, plotly; print(kaleido.__version__)" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[ona] installing kaleido + plotly ..."
    & $Python_Exe -m pip install -U kaleido plotly | Out-Null
}

# Run R
Write-Host "[ona] running R: $RScript"
& $Rscript_Exe $RScript
if ($LASTEXITCODE -ne 0) { throw "Rscript failed (exit $LASTEXITCODE)." }

$jsonPath = Join-Path $OutDir ($OutBaseName + ".json")
$pngPath  = Join-Path $OutDir ($OutBaseName + ".png")
if (-not (Test-Path $jsonPath)) {
    throw "R did not produce $jsonPath — check OUT_BASENAME / FIG_DIR in the R script."
}

Write-Host "[ona] rendering PNG via kaleido ..."
& $Python_Exe $renderer $jsonPath $pngPath $Width $Height
if ($LASTEXITCODE -ne 0) { throw "kaleido render failed (exit $LASTEXITCODE)." }

Write-Host "[ona] DONE: $pngPath"
