---
description: Ship Phase N / 出貨階段 N 與 PR 生成。
---

# AutoAgent-TW Ship Workflow

## Input
- Phase number: N (from $ARGUMENTS)

// turbo-all

## Steps

### Step 1: 匯入上下文
1. 讀取 `.planning/PROJECT.md`。
2. 讀取 `.planning/ROADMAP.md` 與當前 Phase N 已完成的所有計畫、研究與代碼 Commit。
3. // turbo
   - 執行 `python .agents/skills/status-notifier/scripts/cc_manager.py --phase $N --check-audit` 以驗證最終品質。
4. 讀取 `.planning/phases/{N}-*/QA-REPORT.md` 確認質量。

### Step 2: 產出摘要 (Phase Summary)
針對 Phase N 的變更：
1. 自動讀取 git diff。
2. 產出一個包含變更範疇、技術實施與測試結果的 JSON 報告。
3. 為該階段生成 README 或 CHANGELOG 更新內容。

### Step 3: 自動化發布與 Commit (若為 auto 模式)
1. 確保所有 Phase 相關的 `.planning` 文件已提交。
2. 自動建立 Git 分支 (如果指定了 Git 工作流)。
3. 在 `.planning/ROADMAP.md` 中將 Phase N 狀態標記為 `Completed`。
4. 在 `.agent-state/current-phase` 更新為 `N+1`。
5. 更新 `version_log.md`：將此階段的回應細節、主要技術實施與 `@file:` 文件清單寫入版本紀錄。

### Step 4: 建立 Pull Request (可選)
1. 根據使用者的 Git 分支模式，建立 Pull Request 並添加 Phase 摘要。
2. 標註相關的 GitHub Issue ID (如果存在)。

### Step 6: 記憶持久化 (Memory Mining)
// turbo
1. 如果已安裝 `mempalace`，執行 `mempalace mine . --mode projects`。
   > [!NOTE]
   > 指令會自動讀取本地 `mempalace.yaml` 中的 `wing` 設定（如 `autoagent_tw`），確保記憶與 `InvoiceAI` 等其他專案完美隔離。

### Step 7: 準備下一個階段
1. 提示 Phase N 已完成。
2. 推薦執行 `/aa-discuss N+1` 進入下一階段討論。
3. 交互模式下為使用者產出總結信息。

### Step 8: 系統資源回收 (Active Reaper)
// turbo
1. 執行 `python scripts/shadow_check.py --action kill` 強制回收記憶體與殘留進程。
