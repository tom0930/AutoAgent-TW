---
description: Auto-update AutoAgent-TW from Remote Git / 從遠端 Git 自動更新至最新版本。
---

# AutoAgent-TW Version Update Workflow

## Steps

### Step 1: 預檢狀態
1. 執行 `git status` 確認當前是否有未提交的工作。
2. 提示使用者如果有未提交的變更，建議先執行 `git stash` 或 `git commit`。

### Step 2: 執行更新
1. 執行 `git pull origin master`。
2. 如果出現衝突，提示使用者手動解決。

### Step 3: 更新後驗證
1. 執行 `/aa-version` 顯示更新後的版本號與最新日誌。
2. 顯示更新摘要：
   - 更新成功的內容清單。
   - 是否有任何涉及環境依賴的變更 (`package.json` / `requirements.txt`)。

### Step 4: 輸出更新摘要
包含：
- 更新前版本 vs 更新後版本。
- 新增功能亮點。
- // turbo
  - 執行 `python .agents/skills/status-notifier/scripts/status_updater.py --task "System Updated" --next "Ready for Task" --status done` 以同步儀表板。
