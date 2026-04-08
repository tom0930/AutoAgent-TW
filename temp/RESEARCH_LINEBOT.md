# RESEARCH: LineBot & NotebookLM Integration Strategy

## 1. 任務需求解析
- **目標**：設計一個將 LineBot 訊息 / 文件存儲並分類到 Google Drive 的機制。
- **目標 2**：結合 NotebookLM 使得存儲的檔案可以被 AI 擷取並成為可以「隨時讀回複習的知識庫與教學材料」。
- **附加條件**：確保安裝過程 (installer) 的環境乾淨。
- **產出要求**：一份完整的教學文件 (PROJECT_KNOWLEDGE_SOP.md)。

## 2. 架構設計 (Architecture)
### 組件
1. **User (Line)**：傳送文字、網址或檔案 (PDF, Doc) 給 LineBot。
2. **LineBot 伺服器 (Webhook)**：
   - 接收 Line 訊息。
   - 解析內容並下載檔案。
   - 透過 Google Drive API上傳檔案，或呼叫 NLM 原生工具新增內容。
3. **Google Drive (Storage)**：
   - 作為知識庫的原始資料池 (Data Lake)。
   - 按標籤/日期自動分類資料夾。
4. **NotebookLM (Knowledge Base)**：
   - 連結至 Google Drive 資料夾或指定檔案。
   - 以 `nlm` CLI 工具管理與觸發 AI 分析（生成重點、測驗或 Audio Overview）。

### 痛點與解法
- **登入問題**：
  - NLM 工具主要依靠使用者 Cookie (`nlm login`)。如果是 LineBot 自動執行，需確保 Server 環境配置好無頭 (headless) 登入，或透過 MCP fallback 手動保留 token。
  - Google Drive 可使用 Service Account (設定較麻煩但最穩)，或者使用 `rclone` (CLI 環境下較容易化繁為簡)。
- **安裝問題 (Installer-Skill)**：
  - 根據 `install-skill.md` 規範，Python 開發環境必須先清理。
  - 虛擬環境建立 (`uv venv` 或 `python -m venv`)，並處理好 `.env` 中的 Line Channel Token 與 Secret。

## 3. 安裝與部署流程分析
1. **環境重設**：隔離新舊依賴套件。
2. **依賴準備**：安裝 `line-bot-sdk`, `google-api-python-client`, `rclone` 或使用 `mcp_notebooklm` 的底層工具。
3. **初始化登入**：
   - 預先取得 OAuth2 Refresh Token，或設定好 Service Account JSON。

## 4. 教學文件的結構設計 (SOP)
這將作為使用者與未來的 AI 一起學習的入口：
- 簡介與目標
- Phase 1: 基礎環境建設 (Installation & Reset)
- Phase 2: LineBot 的設定與連動 (Google Drive)
- Phase 3: 自動化整理至 NotebookLM
- Phase 4: AI 智慧回答與教學應用
