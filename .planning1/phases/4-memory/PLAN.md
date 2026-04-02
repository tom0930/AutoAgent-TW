# Phase 4: 專案記憶與上下文管理 (Memory & Context Management) - PLAN

## Wave 1: 記憶資料層 (Data Layer)
- **Task 1.1**: 實作 `MemoryStore` (`scripts/memory/memory_store.py`)，支援檔案 JSON CRUD，並自動管理 `id`, `timestamp`, `content`, `tags`。
- **Task 1.2**: 實作 Focus System：如果記憶被標記為 `is_focused=True`，在 `export_context()` 時，只有该记忆的內容會被匯出，其餘會被遮蔽。

## Wave 2: CLI 介面與命令操作
- **Task 2.1**: 實作 `scripts/aa_memory.py`，支援的 subcommand 包括：
  - `add <text> --level L2 --tags tag1,tag2`: 新增
  - `list --level L2`: 列出所有記憶
  - `delete <id> --level L2`: 刪除指定 ID 記憶
  - `focus <id> --level L2`: 將特定記憶設為專注模式，或清空 focus
  - `export`: 匯出當前有效上下文

## Wave 3: 驗證與儀表板整合
- **Task 3.1**: QA Script，測試所有操作 (Add -> List -> Focus -> Export -> Delete)。
- **Task 3.2**: 更新 `status_updater.py` 和 Dashboard，反映專案記憶項目數量或 Focus 狀態。
