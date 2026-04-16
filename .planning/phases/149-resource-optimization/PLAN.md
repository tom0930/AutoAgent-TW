# Phase 149: High-Density Resource Optimization & Process Reaper

## 🎯 目標 (Objective)
解決使用者報告的 **4,088 MB (4GB)** 記憶體膨脹問題。
我們將從兩個維度優化：「垂直優化 (單程精簡)」與「水平優化 (屍體清理)」。

## ⚠️ 使用者審閱必要項 (Review Required)
> [!IMPORTANT]
> 本次修改將導入 **Agent Singleton** 機制。如果您在多個 IDE 視窗中同時運行 AutoAgent-TW，可能會有其中一個被系統判定為「舊視窗」而強制啟動生命週期檢查。

## 🛠️ 提議變更 (Proposed Changes)

### 1. 垂直優化：視覺引擎零拷貝精煉
針對 `pyrefly.exe` 佔用 667MB 的問題，消除所有中間副本。

#### [MODIFY] [shared_memory_manager.py](file:///z:/autoagent-TW/src/core/rva/shared_memory_manager.py)
- **移除 `frame.tobytes()`**: 改用 `np.copyto` 或直接對 `shm.buf` 進行切片賦值。
- **避免新陣列分配**: 允許傳入現有緩存。

#### [MODIFY] [pyrefly_service.py](file:///z:/autoagent-TW/src/core/rva/pyrefly_service.py)
- **MSS 渲染優化**: 直接從 `mss` 獲取數據寫入 SHM，減少 `np.array()` 的重複包裹。
- **主動 GC**: 在 `PAUSE` 狀態下增加 `gc.collect()` 並清除 `sct` 實例。

---

### 2. 水平優化：進程生命週期自動收割 (Agent Reaper)
解決「48 個進程」累積問題，確保舊 Agent 不會變成殭屍。

#### [MODIFY] [win32_job.py](file:///z:/autoagent-TW/src/utils/win32_job.py)
- **實作 `limit_memory_usage`**: 為 Job Object 加上硬性的 `JOB_OBJECT_LIMIT_JOB_MEMORY` 限制，例如 2GB，超限自動終止，防止死當。

#### [NEW] [agent_reaper.py](file:///z:/autoagent-TW/src/utils/agent_reaper.py)
- **啟動檢查**: 在 Agent 啟動時掃描系統中的 `Antigravity` 進程。
- **過期清理**: 如果發現啟動時間超過 1 小時且已無活動的進程，主動終止。
- **單一執行緒鎖**: 確保同一個 Workspace 只會有一個 RVA 控制平面實例。

---

### 3. MCP 服務優化
#### [MODIFY] [rva_server.py](file:///z:/autoagent-TW/src/core/mcp/rva_server.py)
- 優化 FastMCP 啟動參數，確保在 Python 進程中啟用 `--lazy` 載入以節省 initial RAM。

## ❓ 未決問題 (Open Questions)
> [!CAUTION]
> 是否需要為 RVA 引擎設定一個 **Auto-Sleep Timer**？(例如 5 分鐘無抓取請求自動退回 PAUSE)。目前是手動 PAUSE。

## ✅ 驗證計畫 (Verification Plan)

### 自動化測試
1. **Memory Profiling**: 使用 `memory_profiler` 對 `pyrefly_service` 進行 10 分鐘壓力測試，確保記憶體曲線為水平線。
2. **Reaper Test**: 手動啟動三個擬態 Agent，驗證新啟動的 Agent 是否能正確收割孤兒進程。

### 手動驗證
1. 打開 Windows 任務管理員，觀察 `pyrefly.exe` 在 `RESUME` -> `PAUSE` 多次循環後是否能維持在 < 100MB。
