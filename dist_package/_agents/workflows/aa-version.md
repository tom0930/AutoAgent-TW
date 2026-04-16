---
description: Get Current AutoAgent-TW Version / 查詢當前系統版本與變更日誌。
---

# AutoAgent-TW Version Workflow

## Steps

### Step 1: 讀取核心配置
1. 讀取 `.planning/config.json` 獲取版本號碼。
2. 讀取 `version_list.md` 獲取最新變更日誌摘要。

### Step 2: 輸出報告
- **Version**: (從 config.json 提取)
- **Status**: (從 STATE.md 提取)
- **Latest Changes**: (從 version_list.md 提取最新一段)
