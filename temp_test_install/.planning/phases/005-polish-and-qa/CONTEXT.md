# Phase 5 Context: Polish & QA

## Goals
完成最後的 UI 打磨、多專案監控支援，並正式發布 v1.6.0 版本。

## Design Decisions

### 1. Dashboard Enhancements
- **Decision**: 在 `status.html` 中新增一個 "Scheduler" 標籤頁。
- **Source**: 讀取 `.agent-state/scheduled_tasks.json` 並列表顯示。

### 2. Multi-Project Support
- **Decision**: 在儀表板右上角顯示目前監控的專案路徑，並支援在多個專案狀態間切換。

### 3. Versioning
- **Decision**: 更新 `.planning/config.json` 與 `version_list.md`。

## Next steps
- `/aa-plan 5`
