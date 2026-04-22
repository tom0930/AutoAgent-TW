# AutoAgent-TW Industrial Memory Guard v1.0
# Monitors and reclaims memory if bloat is detected.

$THRESHOLD_MB = 2000
$REAPER_SCRIPT = "scripts/kill_zombies.py"
$SHADOW_KIL_SCRIPT = "scripts/shadow_check.py"

function Get-AntigravityMemory {
    $processes = Get-Process -ErrorAction SilentlyContinue | Where-Object { 
        $_.Name -match "Antigravity" -or 
        $_.CommandLine -match "autoagent-tw" -or 
        $_.CommandLine -match "pyrefly" -or
        $_.CommandLine -match "mcp-router"
    }
    $totalMemory = ($processes | Measure-Object -Property PrivateMemorySize64 -Sum).Sum / 1MB
    return $totalMemory
}

$currentMem = Get-AntigravityMemory
Write-Host "[Memory-Guard] Current Antigravity footprint: $([math]::Round($currentMem, 2)) MB" -ForegroundColor Cyan

if ($currentMem -gt $THRESHOLD_MB) {
    Write-Host "[Memory-Guard] ⚠️ Memory threshold exceeded ($THRESHOLD_MB MB)! Launching reclamation..." -ForegroundColor Yellow
    
    # Run reaper
    Write-Host "[Memory-Guard] Step 1: Deduplicating singletons via AgentReaper..."
    python $REAPER_SCRIPT
    
    # Run shadow kill
    Write-Host "[Memory-Guard] Step 2: Termination of persistent pyrefly daemons..."
    python $SHADOW_KIL_SCRIPT --action kill
    
    $newMem = Get-AntigravityMemory
    Write-Host "[Memory-Guard] ✅ Reclamation complete. New footprint: $([math]::Round($newMem, 2)) MB" -ForegroundColor Green
} else {
    Write-Host "[Memory-Guard] ✅ Footprint within industrial limits." -ForegroundColor Green
}
