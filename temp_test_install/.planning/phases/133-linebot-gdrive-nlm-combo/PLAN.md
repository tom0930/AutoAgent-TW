# Phase 133: LineBot x Google Drive x NotebookLM 實作計畫 (PLAN)

## 工作項目 (WBS)

### 1. 基礎架構更新 (kb_gdrive_sync.py)
*   **目標**：修改 `GDriveSync` 類別，加入 `upload_text_as_file` 方法。
*   **作法**：使用 `googleapiclient.http.MediaIoBaseUpload`，讓腳本能直接將 Python 中的字串變數 (如同 OCR 的結果) 儲存為 GDrive 中的 `.txt` 檔案。

### 2. LineBot 核心業務邏輯 (aa_kb_gateway.py)
*   **目標**：建立處理中心 (Gateway)，不依賴真實 Flask，建立一套 `MockWebhook` 來承接模擬指令 (方便在本機整合測試驗證)。
*   **作法**：
    *   **安全層 (Security Guard)**：`verify_whitelist(user_id)`，阻擋非預期用戶的呼叫。
    *   **路由層 (Router)**：
        1. 判斷是否有 `@大腦` 開頭。如果有，則走 Query 流程：取出後面字串，呼叫 `nlm notebook query`。
        2. 判斷是否上傳文字或圖片帶有 `#XXX` 標籤。如果有，若是圖片先經過 OCR，然後發給 `kb_gdrive_sync.py` 上傳。
    *   **同步層 (Sync)**：取得 GDrive 回傳的 File ID 後，呼叫 `nlm source add --drive {fileID}` 進行 NotebookLM 端新增。
    *   **整合測試入口 (main)**：提供 `--test-text` 與 `--test-sync` 模擬測試參數。

### 3. Gemini Vision OCR 萃取 (aa_kb_gateway.py 內建)
*   **目標**：實作輕量級 `ocr_image_to_text(image_path)`。
*   **作法**：使用 `google.generativeai`。提示詞限定為單純擷取文字，不進行潤飾與擴寫，以還原圖片的最原始知識，降低 Token 的發散。

## 邊界條件與假設
*   終端機中的 `nlm` 行為取決於 `pcvdep0101@gmail.com` 所成功 `login` 的 Session 狀態。(如超時需要 User 介入重新登入)。
*   環境預設有安裝並配置好 `google-genai` 與 `.env/gdrive_creds.json`。
