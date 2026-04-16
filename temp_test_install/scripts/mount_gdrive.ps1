# rclone 掛載腳本 (mount_gdrive.ps1)
$RCLONE_EXE = "C:\soft\rclone\rclone.exe"
$REMOTE = "gdrive:"
$MOUNT_POINT = "R:"
$CACHE_DIR = "z:\cache"

# 1. 建立 RAMDisk 快取目錄
if (!(Test-Path $CACHE_DIR)) {
    New-Item -ItemType Directory -Path $CACHE_DIR -Force | Out-Null
}

# 2. 啟動掛載 (背景執行)
Write-Host ">>> 正在掛載 Google Drive 到 R: ..." -ForegroundColor Green
& $RCLONE_EXE mount $REMOTE $MOUNT_POINT `
    --vfs-cache-mode full `
    --cache-dir $CACHE_DIR `
    --vfs-cache-max-age 24h `
    --buffer-size 64M `
    --no-console
