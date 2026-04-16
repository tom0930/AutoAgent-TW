# Install JetBrainsMono Nerd Font and Starship
# Version: 1.0.0

Write-Host "--- Phase 141: Environment Setup Starting ---" -ForegroundColor Cyan

# 1. Install JetBrainsMono Nerd Font
Write-Host "[1/2] Installing JetBrainsMono Nerd Font..." -ForegroundColor Yellow
winget install --id DEVCOM.JetBrainsMonoNerdFont --exact --silent --accept-source-agreements --accept-package-agreements

# 2. Install Starship
Write-Host "[2/2] Installing Starship..." -ForegroundColor Yellow
winget install --id Starship.Starship --exact --silent --accept-source-agreements --accept-package-agreements

Write-Host "--- Installation Complete ---" -ForegroundColor Green
Write-Host "Note: You might need to restart your terminal for 'starship' to be in PATH." -ForegroundColor Gray
