# Phase 153: Human-in-the-loop (HITL) Verification Contracts

## 📌 意圖
建立一套工業級的「驗證合約」機制。當 AI 代理在執行高風險操作（如 RVA 引擎觸發 `Erase`, `Program` 或執行具有破壞性的 `run_command`）時，系統必須暫停並開啟一個標準化的授權介面，由人類使用者核可後產生 `auth_code` 供後續執行。

## 🎯 目標
1. **合約標準化**：定義 `VerificationContract` 格式，包含 `risk_level`, `action_description`, `security_context`。
2. **多通道授權**：
   - CLI 交互模式 (Input/Output)。
   - (未來) Browser/Notification 授權介面。
3. **授權碼分發**：產生具有時效性的一次性令牌 (TOTP style or unique hash)，供 MCP Tools 驗證使用。
4. **追溯性**：在 `rva_audit.log` 與 `security.log` 中記錄是哪位人類在什麼時間核准了哪個動作。

## 🏗️ 架構設計
- **Contract Manager** (`src/core/security/contract_manager.py`): 負責儲存待核准的合約與產發 code。
- **HITL Interceptor**: 集成到 `mcp_router_gateway.py`，當工具參數包含危險模式時自動阻斷。
- **Contract UI**: 簡單的實例化對話框腳本，提示使用者確認。

## 🛡️ 資安考量 (Threat Model)
- **授權碼盜用**：確保 code 與當前 session 綁定，防止 replay attack。
- **授權疲勞**：避免對瑣事也進行授權，導致使用者習慣性按下 `y`（分級制度）。
- **權限提升**：確保 `auth_code` 只能用於特定的合約目標，不能通用。

## 🔗 依賴
- **Phase 138 (RVA Engine)**: 提供 RVA 的攔截器實例。
- **Phase 146 (Memory L2)**: 儲存活躍的合約狀態。
