---
description: Check Project Progress / 查看目前的專案進度。
---

# AutoAgent-TW Progress Workflow

## Input
- Repository: tom0930/AutoAgent-TW (預設)

// turbo-all

## Steps

### Step 1: 匯入上下文
1. 讀取 `.planning/PROJECT.md`。
2. 讀取 `.planning/ROADMAP.md`。
3. 讀取 `.planning/STATE.md` 與 `.agent-state/current-phase`。
4. // turbo
   - 執行 `python .agents/skills/status-notifier/scripts/cc_manager.py --check-audit` 以預檢架構審核狀態。

### Step 2: 狀態概況生成
1. 提取所有已完成、正在進行中、待辦的 Phases。
2. 顯示當前系統版本 (從 `config.json` 讀取)。
3. 列出當前 Phase 的執行進度 (CONTEXT/PLAN/EXECUTE/QA)。
3. 計算任務完成率 (UAT Pass Rate)。

### Step 3: Git 統計與分析
1. 獲取最近的 Commits 與變更趨勢。
2. 發覺潛在的進度阻塞點。
3. 展示當前開發效率指標。

### Step 4: 輸出報告
包含：
- 當前狀態匯總。
- 路線圖視覺化進度條。
- 待辦清單摘要。
- 專案健康度評估。

### Step 5: 自動推薦下一步
1. 基於當前進度狀態，自動顯示推薦執行的下一個命令（如 `/aa-discuss N`）。
2. // turbo
   - 執行 `python .agents/skills/status-notifier/scripts/cc_manager.py --check-audit` 以檢查架構師審計狀態。
3. 更新並提醒任何逾期或高優先級的任務。

### Step 6: 顯示視覺化儀表板
1. 顯示儀表板連結：`http://localhost:5175` (Antigravity Global React Dashboard)。
2. // turbo
   - 執行 `python .agents/skills/status-notifier/scripts/status_updater.py --task "Progress Check" --next "Next Recommended Phase" --status idle` 以確保狀態同步。
