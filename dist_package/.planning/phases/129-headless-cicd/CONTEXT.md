# CONTEXT: Phase 129 — Headless Mode + CI/CD Integration

## 🎯 核心目標
將 AutoAgent-TW 轉變為能完全無人值守執行的自動化代理系統。透過結合 CI/CD 平台（如 GitHub Actions）與專屬的 Headless 標記，實現全自動的 GSD 工作流循環（Discuss -> Plan -> Execute -> Review -> Ship）。

---

## ✅ 最終技術決策

### 1. 如何自動化 (Headless Automation Strategy)
*   **觸發機制**: 由 GitHub Actions 的 Cron Job（排程定時執行）或特定的 Git Push 觸發。
*   **執行模式 (`--auto` / `--headless`)**: 執行 `AutoAgent-TW` 工作流時注入 `--auto` 參數。在指令層級，腳本會全面抑制互動式的 `input()` 詢問，採用最高信心度 (Default/Recommended) 的決策，且不開啟任何 GUI 視窗。
*   **狀態鎖定 (State Locking)**: 運作期間於 `.agent-state/lock` 建立鎖定檔，確保不會有多個 CI Runner 或實例同時寫入，避免發生衝突與上下文覆蓋。
*   **自動回退 (Auto-Rollback)**: 若 QA 或編譯遭遇無法修復之嚴重錯誤（FAIL 且嘗試修復三次未果），自動觸發 Git Reset 回退至上一個穩定之 Checkpoint。

### 2. `/aa-review` 無人值守代碼審查機制
*   **必要性**: **強烈需要**。由於沒有人類在過程中確認代碼，系統必須具備自我審核機制。
*   **職責**: `/aa-review` 扮演 CI 流程的「自動化審核員」(AI Reviewer)。
*   **運作邏輯**: 在出貨 (`/aa-ship`) 前置入 `/aa-review`。該指令會讀取 Phase N 的程式碼變更 (Diff) 與 `QA-REPORT.md`，並以不同於開發代理的 Persona 進行防禦性、安全性與效能評估。若 `/aa-review` 退件，流程會退回 `/aa-fix`。

### 3. 通知與監控機制 (Notification)
*   **決策**: **完全移除 LineBot**。
*   **替代方案**: 所有的狀態回報與異常警告將直接輸出。
    *   **成功時**: 建立 PR，並在 PR Comment 自動拋出 Phase 執行總結。
    *   **失敗時**: 透過 GitHub Issues 自動開單，保留詳細錯誤日誌 (`.agent-state/auto-resume.json`) 供日後人工或另一波 Agent `aa-fixgit-issue` 進行修復。

---

## ⏱️ 估計與驗證 (UAT Criteria)
*   **UAT 1 (無人介入執行)**: 在終端機以 `python ./path/to/main --auto` 執行整個 Phase，期間不出現任何阻塞式的輸入要求。
*   **UAT 2 (狀態鎖定)**: 當系統正在執行任務時，嘗試啟動第二個實例，第二個實例必須被 `.agent-state/lock` 攔截並優雅退出。
*   **UAT 3 (審查觸發)**: 引發一段已知問題的代碼，驗證 `/aa-review` 能夠準確攔截攔截出貨並回報至日誌。
