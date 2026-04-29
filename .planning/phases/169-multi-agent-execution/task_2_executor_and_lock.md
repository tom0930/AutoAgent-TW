# Task 2: Executor Sandbox & FileLock Manager

**目標**: 
實作隔離的執行環境，包含生命週期管理 (TTL)、檔案邏輯鎖以及 Git 物理暫存。

## 具體步驟
1. 建立 `scripts/execution/lock_manager.py`。
   - 實作 `FileLockManager` (使用 `asyncio.Lock` 字典)。
   - 實作 `acquire` 與 `release`，追蹤當前 `active_writers`。
2. 建立 `scripts/execution/executor.py`。
   - 實作 `isolated_executor` (@asynccontextmanager)。
   - 結合 `asyncio.wait_for` 處理 Strict TTL。
   - **成功路徑**: 任務執行結束後，呼叫 `subprocess.run(["git", "add", ...])`。
   - **失敗路徑**: 若發生 `TimeoutError` 或異常，呼叫 `subprocess.run(["git", "reset", "--", ...])` 恢復。
   - 在 `finally` 區塊強制釋放 FileLock。
3. 撰寫整合測試 `tests/test_executor_and_lock.py`，模擬多代理並行寫入與超時情境。

## 驗證標準 (UAT Criteria)
- `python -m pytest tests/test_executor_and_lock.py -v` 必須通過 (`exit_code == 0`)。
- 超時測試必須確認 Git Index 被正確清空 (`git reset`)。
