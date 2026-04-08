# RESEARCH: Git vs. Git-Skill Comparison

## 1. 現狀分析 (Current State: Standard Git Tools)
目前系統主要透過 `mcp_GitKraken` 提供 Git 功能：
- **基礎操作**：Add, Commit, Branch, Checkout, Push, Stash, Status.
- **進階工具**：GitLens Commit Composer, Launchpad, Start Work/Review.
- **缺點**：
    - 缺乏統一的 Commit 規範（雖有工具輔助，但非強制）。
    - 分支命名隨意，未與 Issue 系統深度鏈接。
    - 缺乏標準化的 PR 模板與 Code Review 流程。
    - 主要是「功能的執行者」而非「標準的維護者」。

## 2. 目標分析 (Target State: Git-Skill Enhanced)
加入 `git-skill` 後，系統轉變為「資深 Git 工程師」：
- **規範強制化**：嚴格執行 Conventional Commits (feat, fix, docs...).
- **分支結構化**：強制使用 prefix 分支 (feature/, fix/...)。
- **Issue 深度整合**：強制在 Commit Message 中關聯 Issue ID (Fixes #123)。
- **SOP 級文件**：提供完整的「團隊 Git 規範」文件，對標一線大廠標準。
- **Code Review 強化**：明確 PR 行數限制、Approve 機制與禁止直接推送到 main。

## 3. 差異點總結
| 維度 | 現有 Git (MCP) | 加入 Git-Skill 後 |
| :--- | :--- | :--- |
| **Commit 格式** | 隨意/描述性 | Conventional Commits (強制) |
| **分支命名** | 隨意命名 | `type/description` (強制) |
| **Issue 關聯** | 手動/偶爾關聯 | 每筆修復必須關聯 (強制關鍵字) |
| **歷史管理** | 直接提交 | 推薦 rebase 整理 (保持線路整潔) |
| **團隊協作** | 僅限 Tool 操作 | 具備完整 SOP、PR 模板、CR 要求 |
| **資安考量** | 較少 | 禁止 force push (推薦 lease), 安全分支策略 |

## 4. 實施關鍵
將 `git-skill.md` 作為 System Prompt 的一部分，在執行 Git 命令前先進行策略思考 (Think before Act)。
