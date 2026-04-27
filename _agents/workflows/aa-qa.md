---
description: QA Check Phase N / 執行階段 N 的 QA 檢查。
---

# AutoAgent-TW QA Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 匯入上下文
1. 讀取 `.planning/phases/{N}-*/PLAN.md`。
2. 提取所有 UAT 驗證準則。
3. 讀取 `.planning/REQUIREMENTS.md` 檢查需求對齊情況。

### Step 2: 自動化測試
執行所有相關測試：
1. 執行單元測試、集成測試。
2. 進行代碼靜態分析 (Linter, Type Checkers)。
   - **MUST DO**: 執行 `python scripts/shadow_check.py --action check` (Shadow Check 暫時啟動 Pyrefly，供底層審計使用，並保持等待讓 `/aa-ship` 可快速接著使用)
3. 使用 `run_command` 捕捉並記錄測試輸出。

### Step 3: 代碼審查 (Code Review)
針對 Phase N 的變更：
1. 分析代碼質量。
2. 檢查是否符合專案開發規範。
3. 評估效能與安全性風險。
4. **Surgical Change 驗證** (Karpathy 原則 3)：
   ```bash
   python scripts/diff_scope_check.py --plan .planning/phases/{N}-*/PLAN.md --staged
   ```
   - 如果有 UNPLANNED 變更，標記為 ⚠️ 並要求解釋。
5. **驗證合約執行** (Karpathy 原則 4)：
   - 讀取 `.planning/phases/{N}-*/verification_contract.yaml`
   - 逐一執行 `success_criteria` 中的每個 `test` 命令
   - 若命中 `negative_patterns`，立即 FAIL 並升級

### Step 4: 產出 QA-REPORT.md
包含：
- PASS/FAIL 列表。
- 每個 Issue 的具體描述。
- 失敗原因及修復建議 (High/Medium/Low 難度)。
- 覆蓋率概況。

### Step 5: 下一步建議
- 如果全部 PASS：執行 `/aa-guard N` 並準備 `/aa-ship N`。
- 如果有 FAIL：執行 `/aa-fix N` 自動修復 Issues。
- 交互模式下邀請使用者確認驗證結果。
