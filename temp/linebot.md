# 知識庫自動化：LineBot 整合 Google Drive 與 NotebookLM 教學指南

本指南詳細說明如何建立自動化工作流：將傳送到 LineBot 的資料（文件、網址、文字），結合 Google Drive 儲存，並導入 Google NotebookLM 作為隨時可複習的 AI 知識庫。

---

## 第一章：設計概念與架構

**為什麼需要這套系統？**
這套系統解決了「資訊碎片化」的問題。透過熟悉的 Line 介面輸入，將資料分類儲存至持久化的 Google Drive，最後藉由 NotebookLM 強大的 AI 功能轉化為可互動的學習資源（例如：自動生成測驗、學習指南或音頻播客）。

### 系統架構流
1.  **使用者 (You)** 傳送訊息/檔案至 LineBot。
2.  **LineBot 伺服器** 接收、解析並將資料存檔。
3.  **Google Drive** 作為中繼資料池，按設定分類（例如 `#教學` 或 `#技術`）。
4.  **NotebookLM (NLM)** 將資料夾中的內容導入為 Source，並供您詢問或整理。

---

## 第二章：基礎環境建設 (Installer Check)

依據 `install-skill` 的黃金準則：「安裝容易，清理難」，在開始前，請確保開發環境乾淨。

### 2.1 環境重置與安裝
1.  **建立全新虛擬環境 (Python)**
    強烈建議為此專案獨立環境，避免依賴衝突。
    ```bash
    # 建立新環境 (假設使用 uv 或內建 venv)
    python -m venv linebot-kb-env
    
    # 啟動環境 (Windows)
    .\linebot-kb-env\Scripts\activate
    ```
2.  **安裝必要套件**
    ```bash
    pip install line-bot-sdk google-api-python-client oauth2client flask
    ```

### 2.2 帳號與登入初始化 (特別注意)
*   **Google Drive 權限**：為了讓腳本能無縫上傳，建議至 Google Cloud Console 申請 **「Service Account」** 並下載 JSON 憑證，這免去了瀏覽器手動點擊授權的麻煩。
*   **Line Developer 帳號**：取得 Channel Access Token 與 Channel Secret。
*   > [!IMPORTANT]
    > **資安防護**：絕對不要將 Token 或 Secret 直接寫在程式碼中。請使用 `.env` 檔案管理，並確保建立 `.gitignore` 排除該檔案。

---

## 第三章：Line 儲存至 Google Drive 的實作方式

### 3.1 指令式標籤分類法
為了讓 AI 日後好整理，建議與 LineBot 溝通時採用「標籤開頭法」。
*   **傳送文字**：「`#教學 這是處理 PDF 的指令與步驟...`」
*   **傳送檔案**：直接上傳 PDF，並在說明文字加上 `#技術文件`。

### 3.2 Python 處理邏輯概念碼
```python
# 當 LineBot 收到文字或檔案時
def handle_message(event):
    # 1. 判斷是否有標籤 (如 #教學)
    category = parse_category(event.message.text)
    
    # 2. 如果是檔案，先下載至暫存區 (Temp)
    content = download_from_line(event.message.id)
    
    # 3. 呼叫 Google Drive API
    folder_id = get_drive_folder_id(category)
    upload_to_drive(filename, content, folder_id)
    
    # 4. 回傳確認訊息給使用者
    reply("✅ 資料已成功存入 Google Drive 的「教學」資料夾中！")
```

---

## 第四章：NotebookLM 的整合與讀回 (AI 抓知識庫)

這部份可以利用我們現有的 `nlm-skill` (NotebookLM CLI) 進行整合。

### 4.1 如何自動將資料倒進 NLM？
當 Google Drive 備妥資料後，你可以開啟終端機（或寫腳本自動執行）：

1.  **登入 NotebookLM** (只需做一次，會保留 Cookie)
    ```bash
    nlm login
    ```
2.  **建立知識庫 (Notebook)**
    ```bash
    nlm notebook create "AutoAgent 技術教學庫"
    # 取得回傳的 Notebook ID (例如 abc1234)
    ```
3.  **將 Google Drive 文件加入知識庫**
    若已經有文件 ID，透過指令直接加入：
    ```bash
    nlm source add <notebook-id> --drive <doc-id>
    ```

### 4.2 如何問 AI 讀回資訊？
當需要複習時，您無需打開網頁，可直接使用跨庫詢問 (Cross-Notebook Query)：
```bash
# 詢問全部教學筆記本內關於「installer」的事項
nlm cross query "請幫我整理關於 Installer 環境重置的步驟" --tags "教學"
```

### 4.3 終極進化：讓 AI 產生學習材料
您可以隨時下令讓 NotebookLM 將最近的資料轉為測驗題或教學指南：
```bash
# 生產學習指南
nlm report create <notebook-id> --format "Study Guide" --confirm

# 針對特定主題產出 Podcast
nlm audio create <notebook-id> --format deep_dive --confirm
```

---

## 第五章：更好的替代建議 (Tom 的架構師建議)

1.  **無代碼 (No-Code) 的替代方案：Make.com**
    如果您不想自己維護 Python Webhook 伺服器，可以使用自動化平台 **Make.com**（前 Integromat）。它可以直接拉取 Line 模組與 Google Drive 模組，不寫一行代碼即可完成「收到 Line 檔案 -> 存進 Drive 指定資料夾」的流程。
2.  **使用 `rclone` 取代複雜的 API**
    如果資料平常是在您的電腦端透過終端機操作（例如：您手邊剛看完一份技術 PDF），與其傳給 LineBot，可以直接使用 `rclone` 命令備份：
    ```bash
    rclone copy ./技術文件.pdf MyDrive:/AutoAgent_KB/技術/
    ```
    簡單且不會有伺服器維護成本。

---
> [!NOTE]
> 這份文件 `linebot.md` 已依照完整分析存檔於您的系統中。您可以隨時匯入您的 NotebookLM 中進行重點複習！
