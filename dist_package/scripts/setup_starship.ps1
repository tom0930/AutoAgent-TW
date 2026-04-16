# Setup Starship in PowerShell Profile
# Version: 1.1.0

Write-Host "--- Phase 141: Shell Configuration Starting ---" -ForegroundColor Cyan

# Ensure the config exists
$ConfigPath = "z:\autoagent-TW\.config\starship.toml"
if (!(Test-Path $ConfigPath)) {
    Write-Error "Starship config not found at $ConfigPath"
    exit 1
}

# Build Profile path from .NET Special Folders to avoid encoding issues with $PROFILE string
$DocPath = [System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::MyDocuments)
$ProfileDir = Join-Path $DocPath "WindowsPowerShell"
$ProfilePath = Join-Path $ProfileDir "Microsoft.PowerShell_profile.ps1"

Write-Host "Resolved Profile Path: $ProfilePath"

if (!(Test-Path $ProfileDir)) {
    Write-Host "Creating profile directory: $ProfileDir"
    [System.IO.Directory]::CreateDirectory($ProfileDir) | Out-Null
}

if (!(Test-Path $ProfilePath)) {
    Write-Host "Creating new profile file: $ProfilePath"
    # Use .NET to create file to be extra safe
    [System.IO.File]::WriteAllText($ProfilePath, "")
}

# Backup profile
$BackupPath = "$ProfilePath.bak_$(Get-Date -Format 'yyyyMMddHHmmss')"
Copy-Item $ProfilePath $BackupPath
Write-Host "Profile backed up to: $BackupPath"

# Inject Setup
$config_block = @"

# --- Starship Integration (AutoAgent-TW Optimized) ---
if (Test-Path "$ConfigPath") {
    `$env:STARSHIP_CONFIG = "$ConfigPath"
}
if (Get-Command starship -ErrorAction SilentlyContinue) {
    Invoke-Expression (&starship init powershell)
}
# --- End Starship ---
"@

$content = Get-Content $ProfilePath -Raw
if ($content -notmatch "starship init") {
    Add-Content -Path $ProfilePath -Value $config_block
    Write-Host "Success: Starship initialization added to `$PROFILE." -ForegroundColor Green
} else {
    Write-Host "Skip: Starship is already configured in `$PROFILE." -ForegroundColor Yellow
}

Write-Host "--- Configuration Complete ---" -ForegroundColor Green
Write-Host "Please restart your terminal or run: . `$ProfilePath" -ForegroundColor Cyan
