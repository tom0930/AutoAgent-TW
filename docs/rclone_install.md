# Rclone 知識庫同步系統安裝指南

本指南將引導您完成 Rclone 的安裝與配置，使專案能將 LineBot 接收到的資料同步至 Google Drive (掛載為 R: 磁碟機)，並解決 RAMDisk 環境下的快取問題。

## 📋 前置需求

在開始之前，請務必先安裝 **WinFsp** (Windows File System Proxy)，這是 Rclone 磁碟掛載所需的底層驅動：

1.  下載 **WinFsp**: [官方下載連結](https://winfsp.dev/rel/)
2.  執行 `.msi` 並依照預設選項完成安裝。

---

## 🚀 安裝與配置步驟

### 1. 安裝 Rclone 工具
本專案提供自動化腳本將 Rclone 安裝至系統建議路徑 `C:\soft\rclone`：

```powershell
# 請在專案根目錄執行
powershell -ExecutionPolicy Bypass -File scripts/install_rclone.ps1
```

### 2. 配置 Google Drive (安全配置模式)
執行以下指令開始互動式配置。本流程**不包含**預設金鑰，需由安裝者自行授權：

```powershell
C:\soft\rclone\rclone.exe config create gdrive drive scope drive
```
*   **操作指引**:
    1. 執行後會自動開啟瀏覽器。
    2. 登入您的 Google 帳號。
    3. 點擊「允許」授權 Rclone 存取您的雲端硬碟。
    4. 瀏覽器顯示 "Success!" 後即可關閉。

### 3. 設定開機自動掛載 (支援 RAMDisk)
針對 `Z:\` 為 RAMDisk 的環境，腳本已內建目錄自動建立機制：

```powershell
powershell -ExecutionPolicy Bypass -File scripts/setup_boot_mount.ps1
```
*   這會在 Windows 啟動資料夾中建立捷徑。
*   預設掛載磁碟機編號為 **R:**。
*   預設快取路徑為 **Z:\cache**。

---

## 🛠️ 維護與疑難排解

*   **手動重新掛載**:
    執行 `scripts/mount_gdrive.ps1` 即可手動啟動 R: 槽。
*   **檢查連線**:
    執行 `rclone lsd gdrive:` 檢查是否能正常列出雲端目錄。
*   **清空快取**:
    重開機後 RAMDisk (Z:) 會自動清空，無需手動維護快取資料。

---

> [!IMPORTANT]
> **資安提示**: 
> 本安裝過程完全符合 Zero-Knowledge 規範。所有 Token 與配置皆儲存在本地端 `%APPDATA%\rclone\rclone.conf` 中，請勿將該設定檔上傳至 Git 倉庫。
