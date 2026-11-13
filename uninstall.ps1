# ==============================================================================
# Agent-Notifier: One-liner Uninstaller for Windows (PowerShell)
# Repository: https://github.com/Meo2k/Agent-Notifier
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "     Agent-Notifier Windows Uninstaller   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# Detect Python
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "[Error] Python 3 was not found in PATH." -ForegroundColor Red
    exit 1
}

$localManager = Join-Path $env:USERPROFILE ".gemini\config\hooks\notifier\manage_hook.py"

if (Test-Path $localManager) {
    Write-Host "[+] Running local uninstaller..." -ForegroundColor Blue
    & $pythonCmd $localManager uninstall -y
} else {
    $guid = [System.Guid]::NewGuid().ToString("N")
    $tempZip = Join-Path $env:TEMP "Agent-Notifier-$guid.zip"
    $tempDir = Join-Path $env:TEMP "Agent-Notifier-$guid"
    try {
        Write-Host "[+] Downloading uninstaller from GitHub..." -ForegroundColor Blue
        $repoZipUrl = "https://github.com/Meo2k/Agent-Notifier/archive/refs/heads/main.zip"
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        Invoke-WebRequest -Uri $repoZipUrl -OutFile $tempZip -UseBasicParsing
        Expand-Archive -Path $tempZip -DestinationPath $tempDir -Force
        
        $extractedRoot = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
        $installerScript = Join-Path $extractedRoot.FullName "manage_hook.py"
        & $pythonCmd $installerScript uninstall -y
    }
    finally {
        if (Test-Path $tempZip) { Remove-Item -Path $tempZip -Force -ErrorAction SilentlyContinue }
        if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue }
    }
}

Write-Host "`n[✓] Agent-Notifier uninstalled successfully!" -ForegroundColor Green
