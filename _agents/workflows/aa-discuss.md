---
description: Discuss Phase N / 討論階段 N 的設計決策。
---

# AutoAgent-TW Discuss Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 匯入上下文
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 1: 匯入上下文" --status running
2. 讀取 `.planning/PROJECT.md`
3. 讀取 `.planning/REQUIREMENTS.md`
4. 讀取 `.planning/ROADMAP.md` 並定位到 Phase N 的需求與目標
5. 讀取 `.planning/STATE.md` 以了解之前 Phase 的決策
6. 讀取之前的 CONTEXT.md（如果存在）作為接續討論

### Step 2: 核心設計決策
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 2: 核心設計決策" --status running
2. 針對 Phase N 的需求，明確討論下列決策：
- 技術選型（資料庫、框架、工具等）
- 整體架構（MVC、微服務、Monolith 等）
- 數據模型與 API 設計
- 第三方庫選擇
- 測試策略

### Step 3: 討論流程
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 3: 討論中..." --status running
2. **如果是 auto-build 模式：**
- 自動使用預設推薦配置
- 直接產出 CONTEXT.md

**如果是交互模式：**
1. 列出關鍵決策點
2. 讓使用者選擇或提供建議
3. 針對每個選擇產出優缺點分析
4. 確認所有決策點均已完成

### Step 4: 產出 CONTEXT.md
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Step 4: 產出成果" --status running
2. 建立 Phase 目錄：
```bash
mkdir -p ".planning/phases/$(printf '%03d' $N)-phase-name"
```
3. 寫入 `CONTEXT.md`
4. Commit 變更：
```bash
git add .planning/phases/
git commit -m "docs: phase ${N} context decisions"
```

### Step 5: 下一步建議
// turbo
1. python .agents/skills/status-notifier/scripts/status_updater.py --task "Phase N 討論完成" --status done
2. 交互模式：`/aa-plan N`
3. 其他：自動執行
