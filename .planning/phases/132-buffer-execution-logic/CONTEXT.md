# Phase 132: 緩衝執行引擎 (Buffer-based Execution Engine)

## 🎯 需求分析 (Requirement Analysis)
解決 AI 在處理大型任務（如大量檔案修改、海量資訊檢索）時發生的「一次性處理過載」導致的 Spinning 問題。核心思想是建立一個 **Running Buffer (暫存中繼站)**。

## 💡 核心設計決策 (Design Decisions)

### 1. 中繼架構 (Buffer Strategy)
*   **目錄規範**：建立 `.agents/running_temp/` 作為工作目錄。
*   **任務清單 (Manifest)**：
    *   AI 會先將待處理的「檔案清單」或「資料片段」寫入 `running_temp/task_manifest.json`。
    *   這確保了當前任務的「範圍 (Scope)」是持久化的。

### 2. 迭代執行 (Chunking Execution)
*   **分片 (Slicing)**：不再一次讀寫 50 個檔案，而是根據 Token 預算，每次處理 N 個（例如每次 5 個）。
*   **狀態追蹤**：每完成一個分片，更新 `task_manifest.json` 中的 `status` (pending -> done)。
*   **彙整 (Aggregation)**：所有分片完成後，AI 再從 `running_temp/` 讀取所有結果進行最終彙編。

### 3. 三大優勢 (Core Benefits)
*   **防中斷 (Resilience)**：如果 Session 斷掉，AI 重啟後只需讀取 `running_temp/` 即可接續，無需重新開始。
*   **防 Spinning (Performance)**：降低單次請求的輸入/輸出長度，保持 UI 響應靈活。
*   **透明化 (Observability)**：使用者可以隨時查看 `running_temp/` 了解目前是在「處理哪一部分」。

---

## 🛠 實作計畫 (Implementation Plan)
1.  **建立結構**：配置 `.agents/running_temp/` 並更新 `.gitignore`。
2.  **更新核心指令**：在 `/aa-helper` 與 `/aa-execute` 邏輯中導入「Chunking 檢查點」機制。
3.  **測試案例**：以「掃描並修改全專案所有文檔的版權宣告」作為壓力測試，驗證緩衝機制的有效性。

---
## Tom 的架構師總結：
「這是一個非常成熟的**批處理調度 (Batch Scheduling)** 思想。透過將『記憶』外掛到檔案系統，AI 的工作窗口將不再受限於單次對話的 Token 上限，實現真正的工業級大批量處理。」
