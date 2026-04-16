---
description: Context-Aware Delivery / 智慧型交付與文檔同步。
---

# AutoAgent-TW GitPush Workflow

## Input
- Commit Message: $ARGUMENTS

// turbo-all

## Steps

### Step 1: 預覽變更與狀態
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 1: 準備交付..." --status running
2. git status
3. git diff --staged

### Step 2: 執行智慧型交付引擎
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 2: 產出摘要與更新文檔..." --status running
2. python scripts/aa_git_pusher.py "$ARGUMENTS"

### Step 3: 確認交付狀態
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "交付成功！" --status done
2. git log -n 1 --stat
3. 列出已更新的文件清單

### Step 4: 下一部分 (Next Phase)
1. 提示 Phase N 已完成並已推送到雲端。
2. 自動建議進入下個 Phase 討論。
