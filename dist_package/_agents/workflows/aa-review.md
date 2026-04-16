---
description: AI Automated Code Reviewer / AI 自動代碼審查員。專為無人值守環境設計，模擬資深架構師進行深度代碼審計。
---

# AutoAgent-TW AA-Review Workflow

## Input
- Phase number: N (from $ARGUMENTS)
- Commit Range: Optional revision range (e.g., HEAD~3..HEAD)

// turbo-all

## Steps

### Step 1: 變更偵測 (Change Detection)
1. 獲取 Phase N 所涉及的所有變更檔案清單。
2. 執行 `git diff` 提取原始 Code Diff。
3. 讀取 `.planning/phases/{N}-*/PLAN.md` 以確定審查邊界（哪些是預期變更，哪些是副作用）。

### Step 2: 深度靜態掃描 (Deep Static Scan)
1. 調用 `pylint` / `ruff` (Python) 或 `clang-tidy` (C++)。
2. 檢查是否包含敏感資訊（Secrets, Keys）。
3. **SECURITY.md 同步檢查**: 確認程式碼變更是否已更新相關安全文檔。

### Step 3: AI 建築師評審 (AI Architect Review)
針對以下維度進行深度思考：
1. **Thread Safety**: 檢查是否有 Race Conditions。
2. **Resource Management**: 檢查是否有資源未釋放。
3. **GSD Compliance**: 是否符合 Discuss → Plan → Execute 流程中的決策。

### Step 4: 生成 REVIEW-REPORT.md
產出包含以下內容的 Markdown：
- **Summary**: 整體通過率與風險等級。
- **Critical Issues**: 必須立即修復的安全漏洞或崩潰點。
- **Refactoring Advice**: 工程美學建議。
- **Approval Status**: [APPROVED] / [REQUEST CHANGES] / [REJECTED]。

### Step 5: 自動化路由 (Routing)
- 如果 `REJECTED`：自動調用 `/aa-fix N` 傳遞 Review 意見進行導向修復。
- 如果 `APPROVED`：更新 `.agent-state/lock.json` 中的驗證狀態，標記為 `Review Passed`。
