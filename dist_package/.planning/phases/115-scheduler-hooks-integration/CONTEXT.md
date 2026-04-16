# Phase 115 Context: Scheduler & Hooks Integration (v1.8.0 Foundations)

## 🎯 階段目標
1. 建立 **AA_Guardian** 全能監控引擎，實現全天候「自我審計」。
2. 整合 **git-hooks (pre-commit)**，將人性化 Manifest 自動化。
3. 為 **Worker 模式** 進行 LSP 語義化存取的先期實驗。

## 🧠 設計決策

### 1. Guardian Pro (守護者強化)
- **路徑**：`scripts/resilience/AA_Guardian.py`
- **邏輯**：整合現有的 `guardian_task.py`，增加 `audit_git_integrity()` 與 `audit_dashboard_freshness()`。

### 2. 人性化 Git-Hook 整合
- **機制**：開發一個獨立的 `git_manifest_hook.py`。
- **行為**：掛載至 `.git/hooks/pre-commit`，在提交前自動獲取 `diff --staged` 並產出分類報告。

### 3. LSP Pilot (語義先遣)
- **目標**：測試 `LSPTool` 對 C++/Python 專案的導航能力，驗證其是否能取代傳統 Grep。

## 📊 UAT 驗證指標
- [ ] 守護者能在背景自動修復 dashboard 過期數據。
- [ ] 手動執行 `git commit` 時，自動在 commit 訊息中看到分類 Manifest。
- [ ] LSP 探針能成功定位到一個遠端類別的定義。

---
*Created by ProblemSolver@AutoAgent-TW v1.7.2 - 2026-04-01*
