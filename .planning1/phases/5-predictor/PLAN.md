# 執行計畫 (PLAN) - Phase 5: 智慧指令預測引擎 (v2.3.0)

## 架構變動概覽
- **新增**: `scripts/predictor/context_tracker.py`
- **新增**: `scripts/predictor/command_predictor.py`
- **新增**: `scripts/hooks/hook_manager.py` (基礎版本，用來接收事件並觸發 Predictor)
- **修改**: `scripts/scheduler_daemon.py`
- **修改**: `.agents/skills/status-notifier/templates/status.html`

## 執行 Wave 拆解

### Wave 1: 上下文追蹤器基礎元件
**目標**: 實作 `ContextTracker` 記錄最近的操作與 Git 狀態。
1. 建立 `scripts/predictor/` 目錄。
2. 撰寫 `context_tracker.py`。
   - 包含 `track_file_change`, `track_command`, `track_git_event`。
   - 狀態持久化到 `.agent-state/context_snapshot.json`。
3. 提供 `get_current_context()` 讀取方法。

### Wave 2: 預測引擎規則模組
**目標**: 實作 `CommandPredictor` 根據 Context 輸出指令。
1. 撰寫 `command_predictor.py`。
2. 實作以規則為基礎的推論 (`PREDICTION_RULES`)，例如 "file_saved_after_edit" 建議 "/aa-qa"。
3. 實作 `predict(context)` 輸出含有 `{"command", "suggestion", "confidence"}` 的候選陣列。
4. 防呆：包含完整的 Logging (debug printf)。若 `context_snapshot` 無效，不應當下當機。

### Wave 3: Hook 觸發機制與排程整合
**目標**: 在特定事件或排程迴圈內主動觸發 Predictor。
1. 建立 `scripts/hooks/hook_manager.py` 模擬基礎事件註冊器。
2. 將 `hook_manager` 中註冊推論邏輯。
3. 修改 `scheduler_daemon.py`：
   - 迴圈中加入讀取 `context_tracker` -> 呼叫 `predict()` -> 更新 `status_updater.py` 或獨立寫出 `.agent-state/predictions.json`。

### Wave 4: 儀表板 UI 呈現
**目標**: 將這些主動推播的預測指令更新至前端。
1. 修改 `status.html` 內的 `<script>`，處理 `AA_STATUS.predictions`。
2. 新增一個「💡 自動助手建議 (Auto-Assistant Suggestions)」區塊。
3. 顯示前三名的候選清單與自信分數。

## 驗證標準 (UAT Criteria)
- [ ] 能在 `.agent-state/context_snapshot.json` 觀察到事件被追蹤。
- [ ] Dashboard 能動態顯示來自 `Predictor` 的推薦選項。
- [ ] 模擬發生檔案修改後，Predictor 會主動推薦 `/aa-qa` 或是 `/commit` 等行動。
- [ ] (防禦測試) 即使 Tracker 拋錯，主 Daemon 仍能運作不當機。
