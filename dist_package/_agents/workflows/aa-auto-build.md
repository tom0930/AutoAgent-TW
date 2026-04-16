---
description: Auto Build (One-click) / 一鍵自動建構。
---

# AutoAgent-TW Auto-Build Workflow

## Trigger
- 使用者輸入 `/aa-auto-build` 進行全自動執行。

// turbo-all

## 執行細項
本 workflow 引導 L3/L4 級別的全自動開發循環。

## 執行步驟

### Step 1: 初始化 (Initialize)
1. 讀取 `.planning/PROJECT.md`。
2. 若專案未初始化，執行 `/aa-new-project --auto`。
3. 等待初始化成功後繼續。

### Step 2: 階段自動循環 (Phase Auto-Loop)
遍歷 ROADMAP.md 中的所有 Phases 並自動執行：

```
FOR phase_num IN (1..total_phases):
    
    # 2a. 討論 (Batch 模式)
    /aa-discuss ${phase_num} --auto
    
    # 2b. 規劃
    /aa-plan ${phase_num} --auto
    
    # 2c. 執行 (Wave 併行模式)
    /aa-execute ${phase_num} --auto
    
    # 2d. QA 驗證
    /aa-qa ${phase_num} --auto
    
    # 2e. 自我修復 (循環)
    WHILE QA_RESULT == "FAIL" and tries < 3:
        /aa-fix ${phase_num} --auto
        /aa-qa ${phase_num} --auto
    
    # 2f. Guardian 檢查點
    /aa-guard ${phase_num} --auto
    
    # 2g. 出貨與 Commit
    /aa-ship ${phase_num} --auto
    
    # 更新目前第 N 階段完成狀態
    echo $((phase_num + 1)) > .agent-state/current-phase
    
ENDFOR
```

### Step 3: 完成 (Complete)
1. 更新 `.planning/STATE.md` 為完成。
2. 將所有 Phase 進行 Git 合併 (如果需要)。
3. 產生全專案執行總結報告。

### Step 4: 異常用處處理 (Error Handling)
1. 自動記錄錯誤日誌至 `.agent-state/auto-resume.json`。
2. 支持續點續傳 (`/aa-resume`)。
3. 在嚴重錯誤時通知使用者並介入。
