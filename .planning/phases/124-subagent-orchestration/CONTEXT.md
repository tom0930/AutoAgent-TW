# Phase 124: Sub-Agent Orchestration Engine (v1.9.0 Core)

## 🎯 目標 (Objectives)
實施基於 LangGraph 的 Supervisor-Worker 子代理編排架構，支援多任務平行處理、實時狀態同步至 Dashboard，並確保系統在子代理異常時仍具備極高韌性。

## 🛠️ 技術選型 (Technical Selection)
- **編排框架**: `LangGraph` (基於狀態機與 DAG 的調度器)。
- **平行處理**: `multiprocessing` (進程隔離，保護主控 Daemon)。
- **實時更新**: 增強型 `status_updater.py` 與 `status_state.json` 輪詢機制，支援 Dashboard 即時推送子代理進度。
- **權限控制**: 整合 `permission_engine.py` 嚴格限制子代理文件活動。
- **資源管理**: 由 `budget_monitor.py` 持續追蹤子代理之 Token 與 Memory 消耗。

## 🏗️ 核心架構 (Architecture)
1. **Orchestrator Handler**: 代理用戶請求，生成任務圖並啟動編排邏輯。
2. **Spawn Manager**: 負責建立、監控、清理多個獨立副進程之 Sub-Agents。
3. **Supervisor Agent**: 負責決策、工作分配、故障切換 (Failover)。
4. **Worker Agents**: 專門執行具體 Task（如實作、測試、安全性掃描）。

## 🛡️ 資安與韌性 (Security & Resilience)
- **隔離執行**: 每個 Sub-Agent 在獨立進程中運行，防止 Memory Leak 或 Crash 蔓延。
- **即時熔斷**: 當偵測到迴圈 (Loop) 或預算超支時，主控 Daemon 可立即終止指定 PID。
- **數據完整性**: 子代理完成任務後，僅彙整報告，不直接合併至 Main Branch（直到 UAT 通過）。

## 📊 Dashboard 整合 (Verification Focus)
- 使用 `status-notifier` 現有的 JSON 狀態機，擴充 `subagents` 陣列。
- **關鍵驗證**: 每次狀態更新必須完整解析 JSON，避免破壞 Dashboard 讀取邏輯、確保 UI 不會掛掉。

## 📝 備註 (Notes)
- 參考 `temp/newplanning.md` 階段 1 的相關規劃。
- 進度顯示需包含子代理的 Task Name, Status (Running/Done/Fail), Progress (0-100%)。
