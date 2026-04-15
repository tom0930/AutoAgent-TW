# Check if rg is already in path
if (Get-Command "rg" -ErrorAction SilentlyContinue) {
    Write-Host "Ripgrep (rg) is already in PATH." -ForegroundColor Green
    return
}

# Potential winget paths
$wingetPackageDir = "$HOME\AppData\Local\Microsoft\WinGet\Packages"
$rgExe = Get-ChildItem -Path $wingetPackageDir -Filter "rg.exe" -Recurse | Select-Object -First 1

if ($rgExe) {
    $rgDir = Split-Path $rgExe.FullName
    Write-Host "Found ripgrep at: $rgDir" -ForegroundColor Cyan
    
    # Add to current session
    $env:Path += ";$rgDir"
    Write-Host "Added to current session PATH." -ForegroundColor Yellow
    
    # Verify
    rg --version
} else {
    Write-Host "Ripgrep not found in WinGet packages. Please ensure it's installed." -ForegroundColor Red
}
