# Phase 3 Context: Adaptive Repair Loop

## Goals
優化自我修復機制，從「死板的三輪次上限」進化為「基於趨勢與多樣性的智能決策」。

## Design Decisions

### 1. Repair History Ledger (`repair_history.json`)
- **Decision**: 建立一個詳細的日誌，記錄每一輪：
  - 產出的錯誤內容 (Stderr/Test Failure)。
  - 修改的檔案與相關代碼。
  - 修改後的 QA 結果。

### 2. Termination Strategy
- **Decision**: 使用以下三個維度進行動態終止判斷：
  - **進步趨勢 (Trend)**: 若失敗的 Test Case 數量在減少，應允許繼續（即使超過三輪）。
  - **策略循環偵測 (Loop Detection)**: 若連續兩次嘗試了幾乎一樣的修復代碼且結果相同，應立即終止，防止進入無限迴圈。
  - **策略探索廣度 (Diversity)**: 若 Agent 持續嘗試完全不同的解決路徑，可以給予更多機會 (最多 5-6 輪)。

### 3. Integration
- **Decision**: Refactor `v1.5.0` 的 `/aa-fix` 調用邏輯。

## Next steps
- `/aa-plan 3`
