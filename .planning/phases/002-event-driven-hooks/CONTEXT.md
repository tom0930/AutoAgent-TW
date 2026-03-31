# Phase 2 Context: Event-Driven Hooks

## Goals
讓 AutoAgent-TW 能對 Git 事件或 CI 失敗做出反應，達成真正的「被動啟動」。

## Design Decisions

### 1. Unified Event Mapping (`hooks.json`)
- **Decision**: 建立 `.agent-state/hooks.json` 作為主要的事件映射表。
- **Format**: 映射 `event_name` -> `command_list`。

### 2. Git Synchronization
- **Decision**: 使用 `.git/hooks/post-commit` 作為進入點。
- **Mechanism**: 一個輕量級的 `scripts/event_handler.py` 檢查對應的 Hook 設定。

### 3. CI Failure Simulation
- **Decision**: 透過偵測特定路徑的文件 (如 `.agent-state/ci-failed`) 或環境參數來觸發自動修復。

## Next steps
- `/aa-plan 2`
