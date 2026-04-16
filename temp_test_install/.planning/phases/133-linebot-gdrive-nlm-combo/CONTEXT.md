# Phase 133: LineBot x Google Drive x NotebookLM 全端整合架構

## 🎯 需求背景
結合先前的基礎（Phase 130 的 GDrive 同步與 Phase 131 的檢索機制），本次探討如何將三者 (LineBot 作為入口、GDrive 作為儲存池、NotebookLM 作為大腦) 進行端到端的完美融合。

## 💡 核心設計與決策點 (Decision Points)

### 1. 知識匯入流 (Ingestion Flow)
*   **流程**：`User (Line) -> LineBot Webhook -> 自動上傳至 Google Drive -> NotebookLM 自動新增 Source`。
*   **決策點 A：NotebookLM 同步機制**
    *   *方案 1 (推薦)*：LineBot 上傳檔案至 Drive 後，主動呼叫 NotebookLM MCP 的 `source_add` (type: drive)，實時將該文檔納入筆記本。
    *   *方案 2*：定時排程 (Cron) 去掃描 Drive 資料夾，批次呼叫 NotebookLM 同步。
*   **我的建議**：採用 **方案 1**，能夠滿足使用者「上傳後即可立刻詢問」的即時體感。

### 2. 知識查詢流 (Query Flow)
*   **流程**：`User (Line，如 "@呼叫大腦...") -> LineBot 辨識指令 -> 呼叫 NotebookLM MCP ('notebook_query') -> LineBot 回覆結果`。
*   **決策點 B：觸發條件**
    *   *方案 1 (推薦)*：前綴觸發，例如使用者傳送「`@AI`」或「`#知識庫`」開頭的語句，LineBot 才會呼叫 NotebookLM 進行 RAG 查詢，其餘一般聊天不觸發。
    *   *方案 2*：全自動意圖辨識 (Intent Classification)，分析每一句話是不是在問知識庫。
*   **我的建議**：採用 **方案 1 (前綴觸發)**，不僅省 Token，更能精準防範 Agent 誤判。

### 3. 多媒體與圖片處理 (Image Handling)
*   **考量**：LineBot 使用者常傳送圖片（如前次提到的「Line 圖片中的三層指令架構」）。
*   **決策點 C：如何讓 NotebookLM 看懂圖片**
    *   *限制*：NotebookLM 原生對某些圖像格式支援有限。
    *   *方案*：在上傳 Drive 之前，若偵測為圖片，可以使用基礎的 Gemini Vision API (或 OCR) 先將圖片「重點文字化」，將圖片原檔 + 文字解析結果一起存入 Drive，然後將文字檔灌入 NotebookLM。

## ⚙️ 系統安全性與權限 (Security)
*   必須設置 **Line User ID 白名單**，只有授權的維護人員（例如 Tom）才能觸發同步與查詢，避免公司機密外洩或被惡意耗損 Token。

---
> 此為初始討論草案，請見對話視窗了解更詳盡的方案比較。
