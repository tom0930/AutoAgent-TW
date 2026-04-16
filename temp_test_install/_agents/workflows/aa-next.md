---
description: Auto-Detect Next Step / 自動偵測並執行下一步。
---

# AutoAgent-TW Next Workflow

## Input
- Repository: tom0930/AutoAgent-TW (預設)

// turbo-all

## Steps

### Step 1: 匯入上下文
1. 讀取 `.planning/STATE.md`。
2. 讀取 `.agent-state/` 下的所有日誌、QA 報告與當前狀態。
3. 識別當前正處於哪個 Phase、哪個步驟 (CONTEXT/PLAN/EXECUTE/QA)。

### Step 2: 狀態分析
1. 分析最後一次 Commit 或產出的文件。
2. 確定當前步驟是否已完整執行。
3. 如果在上一步驟發生錯誤，則標記為需要 `/aa-fix`。

### Step 3: 決定下一個邏輯步驟
基於當前狀態決策：
- 若 Phase N 剛完成計畫：推薦 `/aa-execute N`。
- 若 Phase N 剛執行完畢：推薦 `/aa-qa N`。
- 若 QA 失敗：推薦 `/aa-fix N`。
- 若 Phase N 完整通過：推薦 `/aa-ship N` 與下一步的 `/aa-discuss N+1`。

### Step 4: 執行命令
1. 輸出將要執行的具體命令。
2. 如果是 `--auto` 模式，直接執行該命令。
3. 如果是交互模式，請求使用者對下一個建議操作進行確認。

### Step 5: 更新當前狀態
1. 在 `.agent-state/history` 記錄此步驟決策。
2. 更新 ROADMAP 進展概況。
