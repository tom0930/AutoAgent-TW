# /.context/core.md (Project Constitution)

## 專案概覽（Project Overview）

- **專案名稱**： [在此填入專案名稱]
- **主要目標**： [一句話描述專案最終要解決的問題或達成的價值]
- **目前開發階段**： [例如：Phase N - 特徵開發]
- **技術棧**： [後端 / 前端 / DB 等架構定義]

## 設計原則與決策（Design Principles & Decisions）

**核心準則（永遠優先遵守）：**

1. **簡潔與可維護性優先**：程式碼必須易讀、易改。寧可多寫一點註解說明 "Why"，也不要寫過度聰明的程式碼。
2. **模組化設計設計（Low Coupling, High Cohesion）**：職責單一，依賴關係明確。避免循環依賴與共用全域變數。
3. **安全為第一要務**：邊緣情況 (edge cases) 必須考慮（null, undefined, error）。避免 Injection（SQLi, XSS），實踐 Zero Trust。
4. **階段式開發 (GSD Method)**：一次專注一個階段。依序 Validate -> Execute -> Test -> Ship。

## 程式碼約定與程式碼審查標準（Code Conventions & Review Standards）

此區融合了本專案的 `Code Review Checklist`，無論是 AI 還是實體人類開發者，**均需以此作為輸出與審查的標準底線。**

### 1. 程式碼品質與風格 (Code Quality)
- **命名清晰**：變數、函式命名必須自包含意義 (Self-documenting)。
- **不寫重複代碼 (DRY)**：超過三次出現的邏輯必須抽象成函式或元件。
- **巢狀控制**：程式碼過度巢狀 (超過 3 層) 必須拆分 early return 或提取。
- **Lint 與 Formatter**：100% 通過預設的風格檢查（ESLint, Prettier, Ruff, Black）。

### 2. 錯誤處理與穩定性 (Error Handling & Stability)
- **異常防護**：重要節點或會失敗的操作必須包裝 `try-catch` 或利用 `Result` 模式處理。
- **非同步安全**：妥善處理 Promise、Async/Await，預防 Race conditions 與死鎖。
- **效能地雷迴避**：不寫 N+1 Query，注意大量資料迴圈的 CPU Block，注意 Event Listeners 造成的 Memory Leak。

### 3. 可測試性與註解 (Testing & Doc)
- 任何 Public API 或元件，必須帶有 JSDoc 或 Docstring。
- 測試覆蓋：關鍵邏輯必須具備 Unit/Integration Test。PR 需確保通過 Regression。

## 給 AI (Agent/Antigravity) 的永久指令

**每次互動必須遵守以下記憶提取規則：**

1. **Context 分層檢索規則**：
   - AI 需要知道**當前脈絡**：必須讀取 `/.context-[專案名]/current.md` 及 `STATE.md`。
   - AI 需要查閱**歷史**：應使用 `/aa-history [keyword]` 調閱 `/.context-[專案名]/archives/`，而非要求用戶貼上歷史。
2. **行為準則**：
   - 每次產出程式碼，內部必須假想通過了上方「程式碼約定與審查標準」，確認無 Blocking issue (安全性、Memory leak) 才能輸出。
   - 不要假設自己擁有上一個 session 的完整對話紀錄，請高度依賴你讀取到的 Markdown 檔案，隨時主動提出更新文件。

## 維護與更新

- 本檔案是整個專案的「開發當地憲法」。修改架構與技術棧時才需更新本檔。
- 當完成重構或決定新設計規範時，記錄於 `changelog.md` 甚至歸檔至 ADR。
