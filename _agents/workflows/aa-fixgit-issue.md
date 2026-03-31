---
description: Fix GitHub Issue with aa-new-project / 自動抓取 GitHub Issue 並自動用 aa-new-project 修正。
---

# AutoAgent-TW Fix GitHub Issue Workflow

## Input
- Repository: tom0930/AutoAgent-TW (預設)
- Issue ID: (選填)

// turbo-all

## Steps

### Step 1: 獲取 Issues 列表
1. 使用 `mcp_GitKraken_issues_assigned_to_me` 獲取分配給我的 Issues。
2. 讓用戶選擇需要處理的 Issue。

### Step 2: 提取 Issue 內容
1. 讀取 Issue 的完整描述、標籤和相關評論。
2. 識別具體的功能需求或 Bug 報告。

### Step 3: 初始化修正專案
1. 執行 `/aa-new-project --auto`。
2. 將 Issue 內容注入到專案規劃中，確保所有 Phase 都對齊 Issue。

### Step 4: 規劃與執行
1. 自動執行 `/aa-plan 1` 以應對 Issue。
2. 根據需求完成代碼編寫。

### Step 5: 結案與提交 (Commit & Push)
1. 使用 `mcp_GitKraken_issues_add_comment` 告知已由 AutoAgent 自動修復。
2. 自動提交變更：
```bash
git add .
git commit -m "fix(issue): resolved issue via AutoAgent-TW"
git push
```
3. 更新 `version_log.md` (包含詳細回應細節與 `@file:` 文件清單) 並提示完成。
