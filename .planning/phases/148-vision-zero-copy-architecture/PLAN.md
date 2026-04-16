# Phase 148: Vision Engine Zero-Copy & Standby - Implementation Plan

## 📈 複雜度評估
- **總步數**: 18 步
- **檔案跨度**: `src/core/rva/`, `src/core/orchestration/`, `config/`
- **風險等級**: 高 (涉及核心進程管理與系統資源)

## 🏗️ 任務拆解 (Atomic Splitting)

### Task 1: Foundation & Shared Memory Bridge
- **目標**: 實作 `pyrefly` 與 `Antigravity` 之間的零拷貝影像傳輸底層。
- **詳見**: `task_1_shared_memory.md`

### Task 2: Control Plane & State Machine
- **目標**: 實作 Named Pipe 命令通訊與 0% CPU 休眠狀態機。
- **詳見**: `task_2_control_logic.md`

### Task 3: Orchestrator Integration & Job Object
- **目標**: 將視覺引擎接入 `OrchestrationCoordinator` 並套用 Windows Job Object 保險絲。
- **詳見**: `task_3_integration.md`

## 🏁 最終完成標準 (UAT Criteria)
1. **進程穩定性**: 執行 `/aa-execute 148` 後，資源回收正常，不留殭屍進程。
2. **性能效能**: 影像傳輸 CPU 佔用下降 > 70% (相較於 Base64)。
3. **休眠功能**: `PAUSE` 訊號下，`pyrefly` CPU 佔用歸零。
4. **魯棒性**: 手動 Kill 主程序，`pyrefly` 必須在 10 秒內同步關閉。
