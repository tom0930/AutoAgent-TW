---
description: Self-Repair Cycle / 自我修復循環。
---

# AutoAgent-TW Fix Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 讀取 QA 報告
1. 讀取 `.planning/phases/{N}-*/QA-REPORT.md`。
2. 提取所有 FAIL 標籤對應的 Issues。
3. 按照優先順序排列 Issues。

### Step 2: 自動診斷
對於每個失敗的 Issue：
1. 讀取發生錯誤的代碼片段。
2. 使用 `run_command` 重新執行測試並捕捉錯誤日誌。
3. 如果需要，使用 `search_web` 或查閱相關庫文檔。
4. 針對 Issue 產出具體修復方案。

### Step 3: 自動修復與 Commit
1. 依次修復所有 Issues。
2. 套用修正代碼、增加必要的測試或更新配置。
3. 為每個修復產出獨立的 Commit：
```bash
git add [changed-files]
git commit -m "fix(phase-${N}): [issue-description]"
```

### Step 4: 重新驗證
1. 重新執行 `/aa-qa N` 以確信問題已修復。
2. 如果仍存在 FAIL，重複 Step 2-3 (最多 3 輪)。

### Step 5: 結案報告
1. 記錄所有修復詳情於 `.agent-state/fix-log`。
2. 告知使用者哪些部分已被自動修復。
3. 若修復失敗（超過 3 輪），請求使用者介入人工排除。
