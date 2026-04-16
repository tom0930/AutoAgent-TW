---
description: Fix GitHub PR with aa-new-project / 自動抓取 GitHub PR 並自動用 aa-new-project 修正。
---

# AutoAgent-TW Fix GitHub PR Workflow

## Input
- Repository: tom0930/AutoAgent-TW (預設)
- Pull Request ID: (選填，若未提供則列出並選擇)

// turbo-all

## Steps

### Step 1: 獲取 Pull Requests 列表
1. 使用 `mcp_GitKraken_pull_request_assigned_to_me` 獲取 PRs。
2. 如果沒有指定 PR ID，列出所有開啟的 PRs 並讓用戶選擇。

### Step 2: 讀取 PR 詳情
1. 使用 `mcp_GitKraken_pull_request_get_detail` 獲取 PR 的標題、描述和變更的文件內容。
2. 提取 PR 中提到的問題或改進需求。

### Step 3: 初始化修正專案
1. 執行 `/aa-new-project --auto`，並將 PR 的內容作為上下文輸入。
2. 自動填充 `.planning/PROJECT.md` 和 `REQUIREMENTS.md`，將 PR 中的任務轉化為專案目標。

### Step 4: 開始執行
1. 自動推進到 `/aa-discuss 1` 和 `/aa-plan 1`，根據 PR 的需求制定執行計畫。
2. 執行修復並提交代碼。

### Step 5: 結案與提交 (Commit & Push)
1. 完成後，使用 `mcp_GitKraken_pull_request_create_review` 告知已自動處理。
2. 提交修復代碼並推送：
```bash
git add .
git commit -m "fix(pr): resolved PR feedback via AutoAgent-TW"
git push
```
3. 更新 `version_list.md`。
