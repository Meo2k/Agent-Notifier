# ==============================================================================
# Agent-Notifier: One-liner Installer for Windows (PowerShell)
# Repository: https://github.com/Meo2k/Agent-Notifier
# ==============================================================================

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "       Agent-Notifier Windows Installer   " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan

# 1. Detect Python 3
$pythonCmd = $null
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pythonCmd = "python"
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    $pythonCmd = "python3"
} else {
    Write-Host "[Error] Python 3 is required but was not found in PATH." -ForegroundColor Red
    Write-Host "Please install Python from https://www.python.org/ or Microsoft Store and retry." -ForegroundColor Red
    exit 1
}

$pyVer = & $pythonCmd --version 2>&1
Write-Host "[+] Using Python: $pyVer" -ForegroundColor Blue

# 2. Setup temp directory
$guid = [System.Guid]::NewGuid().ToString("N")
$tempZip = Join-Path $env:TEMP "Agent-Notifier-$guid.zip"
$tempDir = Join-Path $env:TEMP "Agent-Notifier-$guid"

try {
    Write-Host "[+] Downloading Agent-Notifier from GitHub..." -ForegroundColor Blue
    $repoZipUrl = "https://github.com/Meo2k/Agent-Notifier/archive/refs/heads/main.zip"
    
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
    Invoke-WebRequest -Uri $repoZipUrl -OutFile $tempZip -UseBasicParsing

    Write-Host "[+] Extracting files..." -ForegroundColor Blue
    Expand-Archive -Path $tempZip -DestinationPath $tempDir -Force

    $extractedRoot = Get-ChildItem -Path $tempDir -Directory | Select-Object -First 1
    if (-not $extractedRoot) {
        Write-Host "[Error] Failed to find extracted repository folder." -ForegroundColor Red
        exit 1
    }

    $installerScript = Join-Path $extractedRoot.FullName "manage_hook.py"
    if (-not (Test-Path $installerScript)) {
        Write-Host "[Error] manage_hook.py was not found in the downloaded archive." -ForegroundColor Red
        exit 1
    }

    Write-Host "[+] Running hook installer..." -ForegroundColor Blue
    & $pythonCmd $installerScript install -y

    Write-Host "`n[✓] Agent-Notifier installation complete!" -ForegroundColor Green
    Write-Host "------------------------------------------" -ForegroundColor Cyan
    Write-Host "Quick test command:"
    Write-Host "  $pythonCmd ~/.gemini/config/hooks/notifier/notifier.py --test task_completed" -ForegroundColor Yellow
    Write-Host "------------------------------------------" -ForegroundColor Cyan
}
finally {
    if (Test-Path $tempZip) { Remove-Item -Path $tempZip -Force -ErrorAction SilentlyContinue }
    if (Test-Path $tempDir) { Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue }
}
