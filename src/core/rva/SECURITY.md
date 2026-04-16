# RVA Security & Privacy Policy (Phase 153)

## 1. Execution Tracing (存證與隱私)
為了工業化除錯，系統會捕捉 GUI 截圖並存儲於 `z:\del\rva\`。

### 1.1 預設行為
- **開發/測試環境** (ENV: `RVA_DEBUG_SAVE=True`): 預設開啟，確保自動化失敗時有圖可考。
- **生產/安裝包環境** (ENV: `RVA_DEBUG_SAVE=False`): **必須強制關閉**，防止敏感資訊（如個密、代碼內容）流出。

## 2. HITL (Human-In-The-Loop) 授權關鍵字
以下操作在 MCP 層級會被攔截，除非提供 `auth_code="OVERRIDE_153"`:
- `Erase`, `Program`, `Format`, `Flash`, `Delete`, `Clear`.

## 3. 數據安全
所有 `z:\del\rva\` 下的暫存圖檔會由 `aa-cleanup` 工作流定期（建議每 24 小時）清除。
