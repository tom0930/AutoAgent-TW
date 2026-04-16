# Phase 1 Context: Scheduler Foundation

## Goals
建立核心排程守護行程 (Scheduler Daemon)，支援時間觸發 (Cron) 並能執行 AutoAgent-TW 內部的 `aa-` 系列指令。

## Design Decisions

### 1. Scheduler Engine
- **Decision**: 使用 **APScheduler** (BackgroundScheduler)。
- **Rationale**: 它提供了功能豐富的 Cron/Interval 觸發模式，支援持久化存儲 (Job Stores)，且在 Windows 環境中穩定度高。

### 2. Daemon Configuration
- **Decision**: 使用 `.agent-state/scheduled_tasks.json` 作為主要的任務儲存文件。
- **Rationale**: 易於讓其他腳本 (如命令列工具) 讀寫與管理。

### 3. Task Execution
- **Decision**: 當時間到達時，由 Daemon 啟動一個全新的 `subprocess` 執行指定的 `aa-` 指令。
- **Status Sync**: 執行過程將透過 Phase 4 (v1.5.0) 的狀態機制更新至視覺化 Dashboard。

## Next steps
- `/aa-plan 1` (Create initial scheduler backend logic).
