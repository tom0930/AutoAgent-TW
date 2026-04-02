# 修改問題加版本version: v2.3.0
# Phase 5: 智慧指令預測引擎 - 領域研究 (RESEARCH)

## 1. 現狀分析
目前 AutoAgent-TW 是命令驅動 (Command-driven) 的架構，開發者必須知道該何時打 `/aa-qa`, `/aa-ship` 或是 `/aa-fix`。缺少主動性 (Proactiveness)。要升級至 v2.3.0，必須引入上下文追蹤 (`ContextTracker`) 與指令預測 (`CommandPredictor`)，主動提供下一步行動建議。

## 2. 核心架構設計
- **ContextTracker**: 負責記錄歷史指令、當前 Git 狀態、變更的檔案、最近的測試結果。因為狀態需跨進程存取，建議儲存於 `.agent-state/context_snapshot.json`。
- **CommandPredictor**: 基於追蹤到的資訊，套用決策樹或 LLM 提示，產出信心指數最高的前三名指令建議。
- **HookManager 綁定**: 利用 `PostToolUse` 或 `git.post-commit` 等鉤子，在系統狀態發生改變的瞬間，自動驅動 `Predictor` 產生新建議。

## 3. 儀表板 (Dashboard) 整合
- 修改 `.agents/skills/status-notifier/templates/status.html`，新增「💡 建議下一步 (Suggested Actions)」的 UI 面板。
- 為了讓 Dashboard 獲得此數據，需在 `status_updater.py` 和 JSON Payload 內加入 `predicted_commands` 欄位。

## 4. 潛在坑點與防禦程式碼 (Defensive Programming)
- **效能問題**: 每次變更都預測可能會拖慢主要工具的速度。必須加上 `try/except` 與 Timeout = 1s 的限制，如果預測失敗就略過，不影響主工作流。
- **不穩定的資料結構**: 必須以嚴格的 Type Hint 規範 Predictor 輸出的格式 (如 Dict 包含 `command`, `confidence`, `reason`)。

## debug printf問題
- `predict()` 在運行時應列印 `[PREDICTOR] Analyzed context -> Suggestion: X (Confidence: 0.9)`，以便除錯。
