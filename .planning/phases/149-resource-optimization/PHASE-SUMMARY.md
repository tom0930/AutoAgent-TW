# PHASE-SUMMARY: Phase 149 (Resource Optimization & MCP Singleton Refinement)

## 1. 變更範疇 (Scope of Changes)
本次變更旨在徹底解決 AutoAgent-TW 在快速重啟或自動修復 (`/aa-fix`) 過程中產生的 MCP 進程重複堆疊（Memory Bloat）問題。

### 核心實施 (Technical Implementation)
- **Singleton Pattern**: 在 `MCPClientManager` 實作真正的 Singleton 模式，確保全域唯一實例。
- **Fingerprinting (進程指紋)**: 基於 `command` 與 `args` 生成唯一的 Hash 字串，用於精準識別正在運行的 MCP 服務進程。
- **Precision Harvesting**: 修改 `_deduplicate_server_process`，支援透過指紋判定並終止衝突進程，而非僅依賴名稱比對，避免誤殺 shell 或其他無關進程。
- **Lifecycle Integration**: 將去重機制整合至 `startup()` 與 `_connect_server_with_retry()`，實現「啟動前清場、失敗後自愈」的閉環管理。

## 2. 測試與驗證 (Testing & Verification)
- **熱修復驗證**: 通過 `scratch/verify_singleton_mcp.py` 測試，證實連續兩輪 `startup()` 呼叫後，系統依然維持 4 個 MCP 進程（對應 4 個啟用中的 Server），無任何重複。
- **指紋正確性**: 已驗證不同參數配置會生成不同指紋，確保系統具備處理多樣化 Server 配置的能力。
- **Reaper 整合**: `AgentReaper` 在啟動時能成功清理 `node.exe` 與 `powershell.exe` 的孤兒實例。

## 3. 專案影響 (Impact)
- **穩定性**: 顯著降低 `/aa-fix` 導致的資源耗盡風險。
- **內存佔用**: 在靜態模式下，MCP 服務佔用歸零（隨啟隨關）或維持在 Singleton 最小佔用。

---
**核准人**: Tom (Senior System Architect)
**版本**: v3.2.7
