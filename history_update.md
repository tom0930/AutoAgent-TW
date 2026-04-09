# /.context/README.md

## 專案 Context 管理規則（必讀）

這個資料夾是用來讓 antigravity（Grok）以及其他 AI 輔助工具（Cursor、Claude Code 等）**精準且持久地理解專案**，避免每次都要重複解釋歷史決策與架構。

**核心原則**：

- 保持 context **簡潔、有結構、永遠更新**。
- 所有檔案皆使用 Markdown 格式。
- **Git 版本控制**：整個 `.context` 資料夾必須納入 Git，跨三台機器透過 `git pull` 同步。
- 不要把完整大型程式碼塞進 context，只放**濃縮摘要、決策、原則、當前階段重點**。

### 資料夾結構與用途

- **`core.md`**永遠必讀的核心檔案。包含：

  - 專案整體架構
  - 設計原則與決策
  - 技術棧與重要約定
  - 非功能性需求（效能、安全、可維護性等）
  - 任何 AI 必須嚴格遵守的規則
- **`current.md`****目前正在進行**的階段完整上下文。內容應包含：當前目標、進行中的任務、關鍵程式碼摘要、待解決問題、下一小步等。保持單一檔案，內容不要過長（建議控制在 2000–4000 tokens 以內）。
- **`parked/`**目前**不活躍**但未來可能用到的模組或功能的濃縮摘要。每個重要模組一個 `.md` 檔案（例如 `auth.md`、`payment.md`、`ui-components.md`）。只放高層摘要與重要介面/決策，不放完整實作細節。
- **`archives/`**已完成的階段歸檔。檔案命名建議：`YYYY-MM-DD_phaseX-name.md`用來記錄歷史決策、完成的功能清單、重大變更理由。
- **`changelog.md`**
  類似 Git commit log 的變更日誌，記錄 context 的每次重要更新。

（可選擴充）

- **`todos.md`**：目前開放的 TODO 清單與優先順序
- **`style-guide.md`**：程式碼風格、命名約定等（若內容很多可獨立出來）
- /aa-history [keyword] 去.context找相關資訊出來，並分析做了，沒做，還需要如何做:提示選項

### 更新規則（嚴格遵守）

1. **每次階段開始前**

   - 確認已 `git pull` 拿到最新 `.context`
   - 告訴 antigravity：「請根據 current.md 開始新階段」或直接提供新任務
2. **ship階段完成時**
   你可以這樣提示選項：/aa-history update 自動完成 3階段完成  自動的所有動作
3. 階段完成。
   目前 /.context/current.md 內容如下：
   [貼上完整 current.md]

   輸出：

1. 更新後的完整 /.context/core.md
2. 更新後的完整 /.context/current.md（下一階段內容）
3. 新增的 /.context/archives/2026-04-09_xxx-complete.md
4. 更新後的 /.context/changelog.md
