# Phase 116 Context: Dashboard Automation (aa-Dashboard)

## 📋 需求背景 (Problem Statement)
目前檢視 AutoAgent-TW 儀表板需要手動尋找 `status.html` 路徑並在瀏覽器開啟。為了提升效率 (One-click UX)，需要一個標準化的 `aa-dashboard` 命令，自動偵測後端伺服器狀態並引導使用者開啟介面。

---

## 🎯 核心設計決策 (Design Decisions)

### 1. 實作語言與工具
- **語言**: Python 3.10+
- **模組**: `webbrowser` (開啟瀏覽器), `socket` (連接埠偵測), `subprocess` (背景啟動伺服器)。

### 2. 伺服器層級策略
- **埠位**: 預設為 `9999`。
- **自啟動機制 (Auto-Start)**: 
  - 如果 `9999` 未被佔用且無回應，`aa-dashboard` 應嘗試啟動一個輕量級的 `http.server` (掛載於專案根目錄)。
  - 若已啟動則直接進入開啟步驟。

### 3. 使用者體驗 (UX)
- **命令名稱**: `aa-dashboard` (支援全小寫以便於鍵入)。
- **反饋**: 在 Terminal 顯示連線狀態與開啟的 URL。
- **跨平台**: 須能在 Windows 下無縫啟動預設瀏覽器。

### 4. 目標 URL
- `http://localhost:9999/.agents/skills/status-notifier/templates/status.html`

---

## 🛠 實作關鍵點 (Implementation Points)
- [ ] **偵測邏輯**: 嘗試建立 Socket 連線至 `localhost:9999`，等候超時則判斷為未啟動。
- [ ] **背景伺服器**: 使用 `subprocess.Popen` 啟動 `python -m http.server 9999` 並進行進程分離。
- [ ] **延遲開啟**: 伺服器啟動後需等待約 0.5-1 秒再開啟瀏覽器，確保 HTTP 服務已就緒。

---

## ✅ 驗證標準 (UAT)
1. 在未使用伺服器的情況下執行 `aa-dashboard`，應能自動啟動伺服器並彈出網頁。
2. 在伺服器已運作的情況下執行，不應產生衝突或重複進程，僅彈出網頁新分頁。

---
*Decision finalized by Antigravity v1.8.0 - Phase 116 Discuss*
