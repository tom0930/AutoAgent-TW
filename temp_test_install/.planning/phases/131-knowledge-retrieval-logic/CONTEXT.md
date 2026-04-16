# Phase 131: 知識庫反向檢索與分享 (Knowledge Retrieval & Sharing)

## 🎯 需求分析 (Requirement Analysis)
使用者希望 LineBot 具備「主動提供」資料的能力，將儲存在 Google Drive 或 NotebookLM 內的知識分享給指定對象或群組。

## 💡 核心設計決策 (Design Decisions)

### 1. 檢索途徑 (Retrieval Paths)
*   **模式 A：文件分享 (Google Drive)**
    *   **場景**：提供原始 PDF、報告或試算表。
    *   **技術**：使用 Drive API 搜尋檔名，並產生「暫時性共用連結」或直接回傳 Link。
*   **模式 B：AI 問答回報 (NotebookLM)**
    *   **場景**：根據群組內的問題，讓 AI 總結知識庫後回報答案。
    *   **技術**：調用 NLM MCP 的 `notebook_query` 獲得文本答案，再由 LineBot 呈現。

### 2. 接口設計 (User Interface)
*   **關鍵字觸發**：採用特殊前綴符號。
    *   `? [問題]` -> 觸發 NLM AI 檢索。
    *   `get: [檔名]` -> 觸發 GDrive 檔案連結檢索。
*   **呈現格式**：使用 Line **Flex Message** 以確保美觀且具備進度感（如顯示「AI 檢索中...」）。

### 3. 資安考量 (Security & Privacy)
*   **權限限制**：僅回應來自「管理者白名單 (Admin Whitelist)」或「授權群組」的請求，防止知識庫洩漏給外部陌生人。
*   **檔案限制**：限制上傳/分享的檔案大小，避免頻寬暴走。

### 4. 實作架構
*   **語言**：Python (Flask/FastAPI)
*   **庫**：`google-api-python-client` (Drive), `mcp-sdk` (NLM Integration), `line-bot-sdk-v3`.

---

## 🛠 任務拆解 (Task Decomposition)
1.  **Task 1**: 擴充 `kb_gdrive_sync.py` 增加 `search_and_share` 函數。
2.  **Task 2**: 實作 `NLM_Query_Bridge`，將 NLM 的回答透過 LineBot 送出。
3.  **Task 3**: 整合路由邏輯至 LineBot Webhook。

---
## Tom 的架構師洞見：
「這將使您的知識庫從『靜態資料夾』進化為『主動服務的 AI 秘書』。別人不必登入您的 Drive，只要在 Line 群組問一句話，AI 就會代表您回答。這就是數位員工的最佳體現。」
