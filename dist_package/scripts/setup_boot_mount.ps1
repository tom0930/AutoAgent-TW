# 設定開機自啟動 (setup_boot_mount.ps1)
$ScriptName = "mount_gdrive.ps1"
$ScriptPath = Join-Path (Get-Location) "scripts\$ScriptName"
$StartupFolder = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = Join-Path $StartupFolder "AutoAgent_GDrive_Mount.lnk"

Write-Host ">>> 正在將掛載腳本加入開機啟動..." -ForegroundColor Cyan

# 建立捷徑
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
# 執行命令：powershell.exe -ExecutionPolicy Bypass -File "路徑"
$Shortcut.TargetPath = "powershell.exe"
$Shortcut.Arguments = "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""$ScriptPath"""
$Shortcut.WorkingDirectory = (Get-Location).Path
$Shortcut.Description = "AutoAgent-TW GDrive Mount"
$Shortcut.Save()

Write-Host "------------------------------------------"
Write-Host "✅ 設定完成！" -ForegroundColor Green
Write-Host "捷徑已建立在: $ShortcutPath" -ForegroundColor Gray
Write-Host "下次開機後，R: 磁碟機將自動掛載。" -ForegroundColor Gray
Write-Host "------------------------------------------"
