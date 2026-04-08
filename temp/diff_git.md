# 資深架構師報告：Git 基礎能力 vs. Git-Skill 強化系統差異分析

**報告人**：Tom (資深全端系統架構師)
**日期**：2026-04-08
**版本**：v1.0.0
**文件路徑**：`.\temp\diff_git.md`

---

## 0. 摘要 (Executive Summary)
本報告旨在深度對比「一般 AI Git 自動化操作」與「導入 `git-skill` 專業規範後」的本質差異。傳統 AI 操作僅停留在「執行命令」層級，而 `git-skill` 將 Git 提升至「工程管理與協作標準」層級，確保代碼資產的長期可維護性、可追溯性與團隊協作效率。

---

## 1. 核心能力對比表 (Comparison Table)

| 維度 | 現有基礎 Git (MCP-based) | 導入 `git-skill` 後 (Professional Mode) | 效益提升 |
| :--- | :--- | :--- | :--- |
| **Commit 哲學** | 任務導向，一整塊變更提交 | **原子提交 (Atomic Commit)**，一次只做一件事 | 極大提升 Bug 定位速度 |
| **Commit 格式** | 描述性文字 (e.g. "update files") | **Conventional Commits** (feat, fix, refactor...) | 自動化生成 Changelog 的基礎 |
| **分支管理** | 隨意命名 (e.g. "new-api") | **類型前綴制** (feature/, fix/, hotfix/...) | 分支意圖一眼識別 |
| **Issue 鏈接** | 偶爾提到 Issue | **強制關聯 (Fixes #ID)**，修補必有關聯 | 實現 100% 的需求追溯性 |
| **歷史整潔度** | 產生大量 merge commits | 嚴格執行 **Rebase**，保持線性歷史 | 簡化 Code Review 負擔 |
| **安全性** | 基礎指令操作 | **禁止 Force Push**，推行 `force-with-lease` | 避免團隊代碼被覆蓋的災難 |

---

## 2. 深度技術差異分析

### 2.1 從「寫完就好」到「規範先導」
- **現狀**：AI 在執行任務後，通常會直接執行 `git commit -m "implement feature X"`。這種方式雖然完成了動作，但在大型團隊中會導致 Commit Log 雜亂無章。
- **Git-Skill 模式**：在執行任何 Git 動作前，系統會先思考「這屬於哪種變更類型？」、 「應該切換到哪個標準分支？」以及「如何寫出對 Reviewer 友好的 PR 描述？」。這是一種 **Strategy-First** 的行為模式。

### 2.2 真正的資安衛士 (Security Guard)
- **Git-Skill** 強制要求對保護分支 (main/master) 的尊重。
- 禁止在 Production 環境執行破壞性操作。
- 引入了資安工程師的思維：確保每筆提交都有證據鏈 (Issue ID)，這在符合金融業或資安合規 (Compliance) 要求的專案中是不可或缺的。

### 2.3 高階協作：PR 級產出
- 傳統模式下，AI 很少主動生成高品質的 Pull Request。
- **Git-Skill** 內建了專業的 PR 模板，包含 `What`, `Why`, `How` 以及 `Checklist`。這讓 AI 產出的代碼能直接進入專業團隊的審核流程，無需人工二次加工。

---

## 3. 使用建議與 SOP (Best Practices)

### 3.1 啟用方式
當您需要進行任何代碼變更時，建議以以下方式觸發：
> 「Tom，請使用 `git-skill` 標準幫我開發功能 A 並提交。」

### 3.2 預期行為
1. **Discuss**: Tom 會先確認 Issue ID 與分支名稱。
2. **Plan**: 設計原子化的提交計畫。
3. **Execute**: 執行代碼，並按類別進行多個次 atomic commits。
4. **Ship**: 自動產生符合 `ARCHITECTURE.md` 與 `ROADMAP.md` 的 PR 文件。

---

## 4. 總結
`git-skill` 不僅是一個 Prompt 或一個工具，它代表了 **Principal Engineer 等級的品質保證**。它將「代碼變更」轉化為「工程資產」，是實現高品質 GSD (Get Shit Done) 流程的核心關鍵。

---
**附錄：Commit 類型速查**
- `feat`: 新功能
- `fix`: Bug 修復
- `docs`: 文件修改
- `refactor`: 重構（非功能性變更）
- `perf`: 效能優化
- `chore`: 建置/依賴等瑣事
