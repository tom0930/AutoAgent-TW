# 🚀 AutoAgent-TW v1.7.0 Resilience Release

這是 AutoAgent-TW 第一個具備 **「系統韌性 (Resilience)」** 與 **「智慧交付 (Delivery)」** 能力的正式發行版。

### 🛡️ 核心特點 (Core Features)
- **環境自癒 (Auto-Repair)**：內建 `budget_monitor.py`，當工具調用發生迴圈或 Token 消耗異常時，自動觸發重試機制與備援模型。
- **一鍵安裝 (EXE Installer)**：提供 `AutoAgent-TW_Setup.exe`，新手無需手動配置 Python，雙擊即可建立虛擬環境 (Venv)。
- **智慧模組化更新**：新增 `/aa-versionupdate` 引擎，支援僅更新 Skills 或 Docs，不再暴力覆蓋本地代碼。
- **視覺化交付 (Visual Doc Sync)**：`aa-gitpush` 引擎現在會自動在文檔末尾繪製 **Mermaid 邏輯流程圖**。

### 📦 包含資產 (Assets)
- **`AutoAgent-TW_Setup.exe`**: 適用於 Windows 的一鍵部署安裝程式。
  - **SHA256**: `770e7d7e139454d86f9fc8b7379bba787d398f73096c0111a6df9db3b92b12ed`
- **`Source code`**: 供開發者自行編譯與擴展。

### 🛠️ 快速安裝指引
1. 下載 `AutoAgent-TW_Setup.exe`。
2. 雙擊執行並選擇安裝路徑。
3. 提示輸入 API Key 後，系統將自動啟動 **Status Dashboard**。

---
*Powered by AutoAgent-TW Autonomous Delivery Engine.*
