# Phase 3 Context: Live Logs & Advanced Monitors

## Goals
增強透明度，引入「即時日誌流」與「執行異常偵測」，讓使用者能即時看到 AI 的詳細操作日誌，並在 AI 執行停滯時獲得主動提醒。

## Design Decisions

### 1. Live Log Streaming
- **Decision**: 在 `status_state.json` 中新增 `live_logs` 陣列（儲存最近 5~10 條）。
- **Rationale**: 效能平衡。不需要傳送完整 log 檔案，只需傳送最新片段供前端循環顯示。
- **Source**: 由 `status_updater.py` 主動獲取 or 由執行腳本傳入。

### 2. Stagnation Detection (偵測停滯)
- **Decision**: 基於 `last_log_timestamp` 與當前時間差。
- **Logic**: 如果超過 90 秒沒有更新 `status_state.json`，前端 Banner 變更為黃色並顯示警告訊息。

### 3. Self-Repair Round Tracking
- **Decision**: 在狀態中新增 `repair_round` 欄位 (0/3)。
- **Rationale**: 讓使用者知道 AI 是否正在進入重新嘗試流程。

## Next steps
- /aa-plan 3
