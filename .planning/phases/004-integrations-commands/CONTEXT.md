# Phase 4 Context: Integrations & Commands

## Goals
將 `status-notifier` 深度集成到 `AutoAgent-TW` 的核心工作流中，確保每一個 phase 的開始、執行中與結束都能自動更新儀表板。同時引入 LINE Notify 以提供外部異常警報。

## Design Decisions

### 1. Workflow Injection
- **Decision**: 修改 `_agents/workflows/*.md`。
- **Rationale**: 雖然可以在 Python 腳本內注入，但在 Markdown Workflow 階層注入最為靈活。
- **Mechanism**: 在每個 wave 區塊添加 `// turbo` 腳本執行 `status_updater.py`。

### 2. LINE Notify Integration
- **Decision**: 建立 `scripts/line_notifier.py`。
- **Rationale**: 發生 `FAIL` 或 `Stagnation` 時，主動發送通知到使用者手機，實現跨端監測。

### 3. Progressive Reveal
- **Decision**: 修改 `/aa-progress` 工作流。
- **Action**: 當使用者輸入 `/aa-progress` 時，除了顯示文字進度，最後應輸出儀表板的本地連結（或 IP 連結）。

## Next steps
- /aa-plan 4
