---
description: Execute Phase N (Parallel) / 執行階段 N 的所有 Plans。
---

# AutoAgent-TW Execute Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 匯入執行計畫
1. 讀取 `.planning/phases/{N}-*/PLAN.md`
2. 提取所有待執行的任務與其對應的 Wave。

### Step 2: 併行執行計畫 (Wave 執行)
1. 按照 Wave 順序分批執行任務。
2. 同一 Wave 內的不同任務將盡可能併行。
3. 每個任務執行完畢後立即提交 (Commit) 到 Git：
```bash
git add [changed-files]
git commit -m "feat(phase-${N}): [task-title]"
```

### Step 3: 即時監控與錯誤修正
1. 監控 stdout 和 stderr。
2. 如果任務執行失敗，記錄詳細錯誤訊息。
3. 對於可以直接修復的小錯誤，自動調整代碼。

### Step 4: 狀態更新
1. 在 `.planning/STATE.md` 中將 Phase N 標記為完成。
2. 更新 `.agent-state/` 下的相關狀態。

### Step 5: 下一步建議
1. 執行 `/aa-qa N` 進行自動化測試與驗證。
2. 交互模式下提醒用戶進行手動驗證。
