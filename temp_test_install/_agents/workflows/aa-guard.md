---
description: Guardian Safety Scan / Guardian 安全掃描與備份。
---

# AutoAgent-TW Guardian Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 匯入上下文
1. 讀取 `.planning/PROJECT.md`。
2. 讀取 `.planning/ROADMAP.md`。
3. 檢查當前分支狀態。

### Step 2: 安全掃描 (Safety Check)
1. 檢查代碼中是否存在硬編碼的敏感數據 (Credentials, API Keys)。
2. 進行常見安全漏洞檢查。
3. 驗證所有依賴項的安全性（如有必要）。

### Step 3: 備份與 Checkpoint (災難恢復)
1. 自動建立本地 Git Checkpoint：
```bash
git add .
git commit -m "guard(phase-${N}): security checkpoint"
```
2. 確保工作區狀態穩定，避免破壞性變更。

### Step 4: 合規性檢查
1. 檢查是否符合 License 規範。
2. 確認文檔完整度 (README, Doxygen, Docstrings)。
3. 給予代碼結構改進建議。

### Step 5: 下一步建議
- 提示執行 `/aa-ship N` 開始發布此階段。
- 交互模式下確認掃描結果。
