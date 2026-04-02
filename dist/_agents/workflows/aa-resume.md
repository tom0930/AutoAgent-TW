---
description: Resume from Breakpoint / 斷點續傳與自動恢復。
---

# AutoAgent-TW Resume Workflow

## Trigger
- 使用者輸入 `/aa-resume` 或 `/aa-resume --auto`。

// turbo-all

## Steps

### Step 1: 匯入中斷狀態
1. 讀取 `.agent-state/auto-resume.json`。
2. 提取中斷時的 Phase 數、步驟名稱 (discuss/plan/execute/qa/fix) 和時間戳記。
3. 讀取 Git 代碼紀錄，檢查最後一個成功的原子 Commit。

### Step 2: 狀態清理與修補
1. 檢查是否存在殘留的暫存文件或未完成的執行 Wave。
2. 針對最後一個中斷的任務，嘗試恢復上次的部分進度。
3. 如果上次發生的是網絡或編譯錯誤，嘗試重新獲取數據。

### Step 3: 自動重啟與續點
1. 重新加載對應的 Phase 設定。
2. 基於中斷位置決定合適的重啟點（例如重新發送最後一個指令到 shell）。
3. 如果是執行階段，從最後一個失敗的 Wave 重新開始。

### Step 4: 恢復 Auto-Build 循環 (如果需要)
1. 重新加載 `auto-build` 模式的 Phase 隊列。
2. 在 `.agent-state/` 中更新續點標籤。

### Step 5: 狀態監控與進度更新
1. 確保 Resume 成功並繼續之前的工作進度。
2. 向使用者匯報：「已從 Phase N 的 [Step] 恢復成功。」
3. 持續監控後續執行的正確性與健康狀態。
