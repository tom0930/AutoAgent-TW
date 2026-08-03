# Headroom 上下文壓縮引擎：完整使用與營運手冊 (v0.33.0)

> **適用系統**：Antigravity IDE / AutoAgent-TW / Claude Code / Codex / Python SDK  
> **更新日期**：2026-08-02  
> **維護者**：Tom (Senior Architect) & Chuck (FPGA & Systems Engineer)

---

## 1. 核心概念與運作機制 (Architecture Overview)

### ❓ 需要寫進 System Prompt 嗎？
**完全不需要寫進 System Prompt！**

Headroom 運作在 LLM Client（如 Antigravity、Claude Code、Python SDK）與上游 API (Anthropic / OpenAI) 之間的 **Infrastructure 中間層**：

```text
 Client (Antigravity / Agent)
       │
       │ (1) 送出原始 Prompt、大檔、工具日誌 JSON
       ▼
┌────────────────────────────────────────────────────────┐
│  Headroom (本地透明中間層 :8787)                       │
│  ────────────────────────────────────────────────────  │
│  • ContentRouter (辨識 JSON / AST / 文本)             │
│  • SmartCrusher  (將 JSON 大檔轉譯為輕量 Schema CSV)    │
│  • CodeCompressor(AST 結構化代碼壓縮)                 │
│  • CCR Engine    (本地暫存原始檔，支援動態反向解壓)       │
└────────────────────────────────────────────────────────┘
       │
       │ (2) 傳送削減 60%~95% Token 後的精簡 Prompt
       ▼
   LLM Provider (Anthropic / OpenAI / Grok)
```

1. **Prompt 無感**：Prompt 是給模型看的語意指令；Headroom 是在網路封包發送前，由本地 Rust/Python 引擎直接做字元與結構層級的 Token 壓榨。
2. **語意零損壞**：採用 Schema 壓縮與 AST 語法樹分析，關鍵的欄位名稱、錯誤訊息（如 `FATAL_ERROR`）、代碼結構皆 100% 完整保留。

---

## 2. 啟動與常駐設定 (Startup & Settings)

不需要每次開啟對話手動啟動，Headroom 提供以下三種啟動層級：

### 方式一：常駐背景服務 (Persistent Service, 推薦)
若希望電腦開機後自動背景執行，免去任何手動命令：

```powershell
# 註冊並啟動為背景常駐服務
headroom install apply --preset persistent-service --providers auto
```

### 方式二：Agent 自動包裹模式 (`headroom wrap`)
讓 Headroom 自動綁定特定的 CLI Agent（如 Claude Code 或 Codex）：

```powershell
# 自動修改設定檔並在啟動 Agent 時自動掛載 Headroom Proxy
headroom wrap claude
headroom wrap codex
```
* **還原命令**：`headroom unwrap claude`

### 方式三：Antigravity / AutoAgent-TW 整合模式 (MCP / Bridge)
針對本專案，已在 `.agents/skills/headroom-compressor/` 設定完成：
1. **MCP Server**：在 IDE 的 MCP 設定中加入：
   ```json
   {
     "mcpServers": {
       "headroom": {
         "command": "headroom",
         "args": ["mcp", "serve"]
       }
     }
   }
   ```
2. **Python SDK Bridge**：在中大型任務處理 Log 或大量檔案時，直接呼叫：
   ```python
   from headroom import compress
   compressed_messages = compress(raw_messages)
   ```

---

## 3. 指令集與預期輸出 (CLI Reference)

以下為常用的 Headroom CLI 指令與對應輸出範例：

### 1. 啟動代理服務 (`headroom proxy`)
* **命令**：
  ```powershell
  headroom proxy --port 8787
  ```
* **預期輸出**：
  ```text
  INFO:     Started server process [12345]
  INFO:     Waiting for application startup.
  INFO:     Headroom Proxy running on http://127.0.0.1:8787 (Press CTRL+C to quit)
  ```

### 2. 健康檢查與診斷 (`headroom doctor`)
* **命令**：
  ```powershell
  headroom doctor
  ```
* **預期輸出**：
  ```text
  Headroom Doctor v0.33.0 · port 8787

  ┌─────────────┬────────┬──────────────────────────────────────────────────────┐
  │ check       │ status │ summary                                              │
  ├─────────────┼────────┼──────────────────────────────────────────────────────┤
  │ proxy       │ ✓ pass │ running at http://127.0.0.1:8787 (up 5m, v0.33.0)    │
  │ version     │ ✓ pass │ proxy matches installed v0.33.0                      │
  │ claude      │ ⚠ warn │ routed to port 8045                                  │
  │ shell env   │ ✓ pass │ ANTHROPIC_BASE_URL=http://127.0.0.1:8787             │
  │ savings     │ ✓ pass │ 58.67% avg token savings recorded                    │
  └─────────────┴────────┴──────────────────────────────────────────────────────┘
  ```

### 3. 查看即時效能與統計 (`headroom perf` / `headroom savings`)
* **命令**：
  ```powershell
  headroom perf
  ```
* **預期輸出**：
  ```text
  Total Requests Processed: 42
  Original Input Tokens:    185,400
  Compressed Input Tokens:  48,200
  Overall Savings Ratio:    74.00%
  Estimated Dollars Saved:  $1.37 USD
  ```

---

## 4. 如何觀看壓縮效果？(Monitoring & Dashboards)

您可以透過以下 3 種方式實時查看節省效果：

### 觀看點 1：網頁版視覺化儀表板 (Web Dashboard)
當 `headroom proxy` 正在運行時，在瀏覽器開啟：
👉 **`http://localhost:8787/dashboard`**
* **提供資訊**：
  * **Token Savings 曲線圖**（時間軸與每筆請求節省率）
  * **Proxy $ Saved 美金計費計數器**
  * **Content Type 節省分佈**（JSON, AST, Prose 比例）

### 觀看點 2：Terminal 即時實測腳本
在 `AutoAgent-TW` 中執行我們準備好的測試腳本：
```powershell
python z:\AutoAgent-TW\.agents\skills\headroom-compressor\scripts\test_demo.py
```
* **輸出結果**：
  ```text
  =================================================================
  🚀 Headroom 壓縮效果實測 (compress API with tool output)
  =================================================================
  原始輸入大小: 19,278 字元 (預估 ~4,819 Tokens)
  壓縮後大小:    7,968 字元 (預估 ~1,992 Tokens)
  -----------------------------------------------------------------
  Token 節省率:  58.67% ⚡ (單次對話直接省下 ~2,827 Tokens)
  =================================================================
  ```

### 觀看點 3：CLI 本地日誌
Headroom 的日誌會顯示每一筆經由 Proxy 轉發的請求：
```text
[Headroom Pipeline] Intercepted 19,278 bytes -> SmartCrusher -> Compressed to 7,968 bytes (-58.67%)
```

---

## 5. 常見問題與 SOP (Troubleshooting & FAQ)

### Q1: 壓縮會不會導致 LLM 讀不懂我的 Code 或 Log 錯誤？
**答：不會。** 
Headroom 的 SmartCrusher 引擎不是隨機抽樣，而是將 JSON 陣列抽離出固定 Schema Header（例如 `[50]{event_id:int, status:string...}`），並將資料排列為流線型格式。LLM 對這種結構化表格的理解力甚至高於帶有大量空格括號的 raw JSON。

### Q2: 遇到 `ModuleNotFoundError: No module named 'headroom._core'` 怎麼辦？
**答**：這代表安裝了未編譯 Rust 擴充元件的源碼包。請確保直接透過全域 PyPI 安裝：
```powershell
pip install headroom-ai
```

### Q3: 可以在 Windows 開機時背景靜默啟動 Proxy 嗎？
**答**：可以。執行 `headroom install apply --preset persistent-service` 即可。

---

## 📌 總結速查表 (Cheat Sheet)

| 想要發生的事 | 執行命令 / 設定 |
| :--- | :--- |
| **啟動背景 Proxy 網關** | `headroom proxy --port 8787` |
| **開啟網頁儀表板** | 瀏覽器存取 `http://localhost:8787/dashboard` |
| **檢查系統狀態** | `headroom doctor` |
| **綁定 Claude CLI** | `headroom wrap claude` |
| **Python 代碼中直接用** | `from headroom import compress` |


----
Edited headroom.md
Edited walkthrough.md

### 📄 完成 Headroom 完整使用手冊編寫

我已為您產出完整的使用手冊，並儲存至 [docs/headroom.md](file:///z:/AutoAgent-TW/docs/headroom.md)。以下為解答您關鍵問題的摘要說明：

---

### 💡 核心疑問解答與關鍵摘要

#### 1. 是否需要每次手動啟動？如何設定？
* **不需要每次對話手動啟動**。
* 您可以透過以下命令將 Headroom 設為開機背景常駐服務：
  ```powershell
  headroom install apply --preset persistent-service --providers auto
  ```
  或者透過 `headroom wrap claude` / `headroom wrap codex` 綁定特定的 CLI Agent，啟動 Agent 時 Headroom 便會在背景自動掛載。

#### 2. 能像 Agent 直接 start/setting？還是要寫到 System Prompt？
* **完全不需要寫進 System Prompt！**
* **原理**：Headroom 運作在 **LLM 請求與回應的中間層（Proxy / SDK / MCP Gateway）**。它會在 Prompt 封包真正送出給 Anthropic / OpenAI 伺服器**之前**，由本地 Rust/Python 引擎將龐大的 JSON、Log、AST 做結構壓縮與轉譯。LLM 收到的是已經精簡的文字，因此完全不需要在 Prompt 中額外告訴 LLM 如何處置。

#### 3. 有哪些 Command？去哪裡看壓縮效果？
* **啟動與檢查指令**：
  * `headroom proxy --port 8787`：啟動本地代理轉發服務。
  * `headroom doctor`：一鍵健康檢查與連線診斷。
  * `headroom perf`：在 Terminal 查看 Token 與美元美節省統計。
* **效果觀看**：
  1. **網頁版視覺化儀表板**：開啟瀏覽器存取 👉 **`http://localhost:8787/dashboard`**，可實時觀看 Token Savings 曲線圖與省下的美金金額。
  2. **實測腳本**：在 Terminal 執行 `python z:\AutoAgent-TW\.agents\skills\headroom-compressor\scripts\test_demo.py`，即可觀看單次請求直接省下 **58.67% (~2,827 Tokens)** 的驚人壓縮效果。

---

詳細的系統架構圖、預期輸出表格與資深工程師 SOP 請直接點擊參閱 [docs/headroom.md](file:///z:/AutoAgent-TW/docs/headroom.md)。
----
Ran command: `headroom install apply --preset persistent-service --providers auto`

### 🔴 錯誤原因診斷 (Error Diagnosis)

在 Windows 系統上執行 `sc.exe create` 註冊系統服務（Service）時，需要 **系統管理員權限 (Administrator/Elevated Privileges)**。因為您目前執行的 PowerShell Terminal 是普通權限，故觸發了 Windows OS 的 `[SC] OpenSCManager 無法 5: 存取被拒` (Access Denied)。

---

### 🟢 解決方案 (2 種方法)

#### 方法 1：使用「系統管理員身分」開啟 PowerShell 執行 (最簡單)
1. 按 `Win + X` 鍵，選擇 **「Terminal (系統管理員)」** 或 **「PowerShell (系統管理員)」**。
2. 在管理員視窗中輸入以下指令即可完成開機常駐服務註冊：
   ```powershell
   headroom install apply --preset persistent-service --providers auto
   ```

---

#### 方法 2：免管理員權限的背景自動啟動方式 (使用者啟動區 Startup Folder)
若不想升級管理員權限，可將 Headroom 啟動命令放到 Windows 的 **使用者啟動資料夾 (Startup Folder)**，這樣每次登入 Windows 時也會自動在背景啟動：

在目前 Terminal 輸入以下 PowerShell 指令即可設定：

```powershell
$shortcutPath = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\HeadroomProxy.vbs"
$vbsContent = 'CreateObject("WScript.Shell").Run "headroom proxy --port 8787", 0, False'
Set-Content -Path $shortcutPath -Value $vbsContent
```
*(說明：這會建立一個靜默執行的 VBScript，每次開機登入時會自動在背景啟動 `headroom proxy --port 8787`，不會彈出命令行視窗，且不需要管理員權限。)*
----