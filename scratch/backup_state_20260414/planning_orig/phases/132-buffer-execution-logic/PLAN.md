# Plan: Phase 132 - Buffer-based Execution Engine

## 1. 執行目標 (Execution Objectives)
構建一個強健的任務緩衝系統，解決大規模處理時的 spinning 問題與狀態遺失風險。

## 2. 工作拆解 (Work Breakdown Structure)

### 2.1 基礎設施建設 (Infrastructure)
*   **Task 1**: 建立 `.agents/running_temp/` 目錄並確認權限。
*   **Task 2**: 實踐 `scripts/utils/buffer_manager.py` 核心類別。

### 2.2 核心模式實現 (Core Implementation)
*   **Task 3**: 實作 `initialize_task_buffer(tasks)` 函數，將大規模任務（如 100 個檔案路徑）寫入 JSONL。
*   **Task 4**: 實作迭代器 `fetch_pending_tasks(chunk_size)`，每次僅讀取指定數量的任務。
*   **Task 5**: 實作 `update_task_status(task_id, result)`，原地或追加更新任務完成狀態。

### 2.3 驗證與壓力測試 (QA & Testing)
*   **Task 6**: 建立 `scripts/tests/test_buffer_resilience.py`。
    *   **情境 1**：處理 20 個模擬任務，在執行到第 10 個時人為中斷。
    *   **情境 2**：重啟腳本，驗證其是否從第 11 個開始執行，而不會重新執名前 10 個。

## 3. 驗證標準 (UAT Criteria)
1.  **分片執行**：單次 API 輸出不超過設定的 Token 上限。
2.  **狀態持久化**：所有的 `running_temp/*.jsonl` 必須能反映真實進度。
3.  **恢復能力**：支援中斷後重啟執行（Resume）。

---
## 4. 時程預估 (Estimation)
*   開發：1 波浪 (Wave)。
*   QA：1 波浪。

---
> [!IMPORTANT]
> **預計產物**：`scripts/utils/buffer_manager.py` 將成為 AutoAgent-TW 全局通用的「任務隊列」標準庫。
