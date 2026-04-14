<#
.SYNOPSIS
    AutoAgent-TW Professional Installer Bootstrapper
    Architecture by Tom (Senior Architect)
#>

$ErrorActionPreference = "Stop"

Write-Host "==================================================" -ForegroundColor Cyan
Write-Host "   AutoAgent-TW Industrial Setup Bootstrapper" -ForegroundColor Cyan
Write-Host "   v2.4.1 | Production Grade" -ForegroundColor Cyan
Write-Host "==================================================" -ForegroundColor Cyan

# 1. Environment Check
Write-Host "[1/3] Checking System Prerequisites..." -ForegroundColor Blue
try {
    $pythonVersion = python --version 2>$null
    if ($null -eq $pythonVersion) {
        Write-Error "Python not found! Please install Python 3.10 or higher from python.org."
    }
    Write-Host "Found $pythonVersion" -ForegroundColor Gray
} catch {
    Write-Error "Python is required but not found in PATH."
}

# 2. Execution Policy Check
$policy = Get-ExecutionPolicy
if ($policy -eq "Restricted") {
    Write-Host "⚠️  Execution Policy is 'Restricted'. Attempting to bypass for this session..." -ForegroundColor Yellow
}

# 3. Execute Core Logic
Write-Host "[2/3] Launching Core Installation Logic..." -ForegroundColor Blue
$currentDir = Get-Location
$scriptPath = Join-Path $currentDir "scripts\aa_installer_logic.py"

if (-not (Test-Path $scriptPath)) {
    Write-Error "Installer logic not found at $scriptPath. Please run from project root."
}

# Run Python logic with --auto if requested by any external env or just run default
python "$scriptPath" --target "$currentDir" --lang "zh-TW"

# 4. Final Notification
Write-Host "[3/3] Finalizing Environment..." -ForegroundColor Blue
Write-Host "Done! Please run 'aa-tw --help' in a NEW terminal window to verify." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Cyan
