---
description: Self-Repair Cycle / 自我修復循環。
---

# AutoAgent-TW Fix Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 0: 預防性資源清理 (Environment Preparation)
1. 執行 `python scripts/kill_zombies.py`。
2. 確保前一次失敗或掛起的 MCP/Agent 進程已完全清除，避免 PID 堆疊與記憶體洩漏。

### Step 1: 讀取 QA 報告
1. 讀取 `.planning/phases/{N}-*/QA-REPORT.md`。
2. 提取所有 FAIL 標籤對應的 Issues。
3. 按照優先順序排列 Issues。

### Step 2: 啟動 PISRC LangGraph 循環
針對每一個 FAIL 的 Issue：
1. 將失敗的日誌與問題分類導入 PISRC (Persistent Issue Self-Review & Correction) 狀態機。
2. 透過執行 `python scripts/resilience/pisrc_graph.py` 或呼叫對應 PISRC API 初始化檢測。
3. 若連續失敗超過 3 輪，PISRC 將自動觸發 `level1_reviewer` 與 `level2_analyzer` 並產出 Root Cause Analysis (RCA)。

### Step 3: 套用 PISRC Corrector 修正與 Commit
1. 根據 PISRC 產出的 `proposed_fix`，自動調整代碼或工具 prompt。
2. 為每個修復產出獨立的 Commit：
```bash
git add [changed-files]
git commit -m "fix(phase-${N}): [RCA-based issue description]"
```

### Step 4: 系統驗證 (Validator) 與人工介入
1. PISRC 執行 `validator` 節點：模擬或真實重新執行測試。
2. 若 `success_rate` 大於定值，視為修復成功，結案寫入 `.agent-state/fix-log`。
3. 若 PISRC 落入 `human_interrupt` 節點，凍結當前圖狀態 (StateGraph) 並發出人類介入通知，等待使用者排除後再接續 (Resume) 執行。
