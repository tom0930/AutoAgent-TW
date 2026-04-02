---
description: Get Current AutoAgent-TW Version / 查詢當前系統版本與變更日誌。
---

# AutoAgent-TW Schedule Workflow

## Purpose
基於 v1.6.0 透明度升級計畫，提供自動排程觸發機制。

## Commands

### 1. 列表 (List)
`/aa-schedule list`
- 顯示當前已排程的所有任務。

### 2. 新增 (Add)
`/aa-schedule add`
- **參數**:
  - `--name`: 任務名稱 (e.g. "Nightly Test")
  - `--trigger`: `cron` 或 `interval` (預設 `interval`)
  - `--params`: 觸發參數 JSON (e.g. `{"minutes": 10}`)
  - `--command`: 指令內容 (e.g. `python .agents/skills/status-notifier/scripts/status_updater.py --task "Scheduled Run" --status running`)

### 3. 移除 (Remove)
`/aa-schedule remove <ID/Name>`

### 4. 守護行程管理 (Daemon Control)
`/aa-schedule start` - 啟動背景排程守護行程。
`/aa-schedule stop` - 停止背景排程守護行程。

## Usage Notes
- 執行 `start` 將會啟動一個獨立的背景進程。
- 修改 `scheduled_tasks.json` 後，Daemon 將在 10 秒內自動同步變更。
- 任務執行日誌可在 `.agents/logs/scheduler.log` 查閱。
