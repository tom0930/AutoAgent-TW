# pyrefly_guardian.ps1
# AutoAgent-TW Pyrefly Memory Guardian
# 
# 策略：Pyrefly 啟動後做完第一次索引就 Kill，減少常駐記憶體
# 由 IDE 在需要時自動重新啟動（Pyrefly 支援快速冷啟動）
# 
# 使用方式：
#   啟動守護: Start-Job -FilePath z:\autoagent-TW\scripts\pyrefly_guardian.ps1
#   手動執行: .\scripts\pyrefly_guardian.ps1 -Threshold 800 -WatchDuration 120

param(
    [int]$ThresholdMB = 600,        # 超過此 MB 開始計時
    [int]$KillAfterSeconds = 120,   # 超過閾值後幾秒強制 Kill
    [int]$CheckIntervalSeconds = 10, # 檢查間隔
    [switch]$DryRun                  # 只報告不殺
)

$VERSION = "1.0.0"
$LOG_PREFIX = "[PyreflyGuardian v$VERSION]"

Write-Host "$LOG_PREFIX Started. Threshold: ${ThresholdMB}MB, Kill after: ${KillAfterSeconds}s"

$overThresholdSince = $null

while ($true) {
    $proc = Get-Process pyrefly -ErrorAction SilentlyContinue
    
    if (-not $proc) {
        Write-Host "$LOG_PREFIX Pyrefly not running. Waiting..."
        $overThresholdSince = $null
        Start-Sleep -Seconds $CheckIntervalSeconds
        continue
    }
    
    $memMB = [math]::Round($proc.WorkingSet64 / 1MB, 1)
    $pid = $proc.Id
    
    if ($memMB -gt $ThresholdMB) {
        if (-not $overThresholdSince) {
            $overThresholdSince = Get-Date
            Write-Host "$LOG_PREFIX Pyrefly (PID: $pid) exceeds ${ThresholdMB}MB: ${memMB}MB. Starting ${KillAfterSeconds}s countdown..."
        }
        
        $elapsed = ((Get-Date) - $overThresholdSince).TotalSeconds
        $remaining = [math]::Round($KillAfterSeconds - $elapsed)
        
        if ($elapsed -ge $KillAfterSeconds) {
            Write-Host "$LOG_PREFIX KILLING Pyrefly (PID: $pid) - Memory: ${memMB}MB (was over threshold for $([math]::Round($elapsed))s)"
            if (-not $DryRun) {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
                Write-Host "$LOG_PREFIX Killed. IDE will restart Pyrefly on next file open."
            } else {
                Write-Host "$LOG_PREFIX [DRY-RUN] Would kill PID $pid"
            }
            $overThresholdSince = $null
        } else {
            Write-Host "$LOG_PREFIX Pyrefly (PID: $pid): ${memMB}MB - Kill in ${remaining}s..."
        }
    } else {
        if ($overThresholdSince) {
            Write-Host "$LOG_PREFIX Pyrefly memory dropped to ${memMB}MB - countdown reset."
            $overThresholdSince = $null
        } else {
            Write-Host "$LOG_PREFIX Pyrefly (PID: $pid): ${memMB}MB - OK"
        }
    }
    
    Start-Sleep -Seconds $CheckIntervalSeconds
}
