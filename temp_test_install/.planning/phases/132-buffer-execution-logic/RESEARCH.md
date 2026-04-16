# Research: Phase 132 - Buffer-based Execution Engine

## 1. 核心需求分析 (Core Requirements)
*   **抗超量能力**：避免單次 Token 處理量超過 6000-8000 tokens。
*   **持久化狀態**：即使工作進程中斷，下次啟動也能從正確位置恢復。
*   **低度依賴**：使用 Python 內建庫實現 JSONL 讀寫，確保 Windows 快遞安裝後的環境相容性。

## 2. 技術方案研究 (Tech Options)

### 2.1 JSON vs JSONL
*   **JSON**：讀寫整份文件，檔案大時內存較吃力，不適合頻繁更新狀態。
*   **JSONL (JSON Lines)**：
    *   **優點**：每一行是一個獨立的 JSON 物件。支援「追加 (Append)」模式模式模式。適合串流處理。
    *   **決策**：採用 **JSONL**。每處理完一個 Chunk，就追加一行狀態回報。

### 2.2 狀態追蹤邏輯 (State Tracking)
*   **Manifest 結構**：
    ```json
    {"task_id": "job_001", "file_path": "src/core.py", "status": "pending"}
    ```
*   **恢復機制 (Resume)**：讀取檔案最後一行，判定目前的進度指標 (Index)。

### 2.3 分片調度 (Chunking Manager)
*   建立一個 `BufferManager` 類別，負責：
    1.  `initialize(task_list)`: 將原始任務清單轉換為 JSONL。
    2.  `get_next_chunk(size)`: 返回下一批待處理任務。
    3.  `mark_done(task_id)`: 更新任務狀態。

## 3. 效能與限制 (Performance & Limits)
*   **單次限制**：預設每片處理 5 個檔案或 5000 個字元。
*   **清理機制**：任務成功完畢後，將 `running_temp/` 檔案移動至 `history/` 或自動刪除以防硬碟占用。

---
## 結論
技術上可行，且符合 Google Cloud 工程師對於「無狀態服務」的設計慣例。
