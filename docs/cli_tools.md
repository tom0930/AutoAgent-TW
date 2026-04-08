# 🛠️ 資深架構師推薦：必備 CLI 神器清單 (CLI Tools for AutoAgent-TW)

這份清單由架構師 Tom 精選，涵蓋了提升生產力、AI 整合及自動化工作流的關鍵工具。

---

## 🤖 1. AI 與 知識管理 (AI & Knowledge)

### **NotebookLM CLI (nlm)**
*   **用途**: 與 Google NotebookLM 互動，管理來源、生成 Podcast。
*   **安裝**: `pip install notebooklm-mcp-cli`
*   **推薦理由**: 知識庫自動化的核心門戶。

### **Mods (by Charm)**
*   **用途**: 將 AI LLM (GPT-4, Gemini) 整合進 Pipeline。
*   **安裝**: `brew install charmbracelets/tap/mods` (或透過 Go 安裝)
*   **範例**: `cat logs.txt | mods "幫我分析這段 LOG 的異常"`
*   **對 Agent 的價值**: 讓指令行具備「大腦」，可直接過濾與處理文本。

---

## ☁️ 2. 資料同步與穿透 (Sync & Tunneling)

### **Rclone (rclone)**
*   **用途**: 將雲端硬碟掛載為本地磁碟。
*   **安裝**: 已透過 `install_rclone.ps1` 完成。
*   **推薦理由**: 離線開發與雲端存檔的最佳橋樑。

### **Zrok / Ngrok**
*   **用途**: 將本地 Port 暴露至公網（測試 LineBot Webhook 必備）。
*   **安裝**: `zrok.io` 或 `ngrok.com`
*   **對 Agent 的價值**: 免去部署部署伺服器的麻煩，直接在 PC 上開發 LineBot。

---

## 📦 3. 開發環境與套件 (Dev & Environment)

### **uv (Fast Python Loader)**
*   **用途**: 地表最快的 Python 二進位管理與包管理工具。
*   **安裝**: `powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`
*   **推薦理由**: 建立虛擬環境只需 0.1 秒，裝套件速度是 pip 的 10 倍以上。

### **Lazygit**
*   **用途**: 超好用的 Git 終端機 UI。
*   **安裝**: `scoop install lazygit`
*   **推薦理由**: 讓寫 Commit、處理 Conflict 變得非常直覺且快速。

---

## 🎞️ 4. 多媒體與文件處理 (Multimedia & Doc)

### **FFmpeg**
*   **用途**: 處理音訊、影片、截圖。
*   **對 Agent 的價值**: LineBot 收到語音訊息後，可用它轉成 MP3 給 AI 辨識。

### **Pandoc**
*   **用途**: 文件格式通吃（Markdown 轉 Word, PDF 轉 Markdown 等）。
*   **對 Agent 的價值**: 自動將 Line 上的長篇文章轉成精美的 PDF 存檔。

---

## ⌨️ 5. 終端機增強 (Terminal Polish)

### **Micro (Text Editor)**
*   **用途**: 現代化的終端機文字編輯器（支援 Ctrl+S, Ctrl+C）。
*   **推薦理由**: 懶得開 VSCode 時，它是終端機裡最舒服的編輯器。

---

> [!TIP]
> **如何選擇？**
> 優先安裝 **uv** 和 **Lazygit**，這會讓您的開發效率有感提升。如果需要測試 LineBot，請務必安裝 **Ngrok/Zrok**。
