# CONTEXT: Phase 129 (Headless CI/CD Integration)

## 1. 任務目標與意圖 (Objectives & Intent)
將 AutoAgent-TW 轉型為可在 CI/CD 流水線中全自動執行的無頭 (Headless) 引擎。這將允許我們將 AI 自動修復、自動化審查 (AI Code Review) 與測試整合到 GitHub Actions 或 GitLab CI 中，實現真正的無人值守 (Unattended) 自動化。

## 2. 邊界定義與約束 (Boundaries & Constraints)
### Definition of Done (DoD)
- 實作 `--headless` 標記，全面禁用任何阻塞式的交互提示 (Interactive Prompts)。
- 支援標準 Exit Codes：`0` (成功), `1` (失敗), `2` (需人工介入)。
- 提供官方 GitHub Actions Template (`action.yml`)。
- 在 `stdout` 輸出結構化日誌 (JSON 或精簡文字)，並確保任何 API Keys 在日誌中被屏蔽 (Masked)。

### 非功能性需求 (Non-Functional Requirements)
- **環境隔離**：在 CI/CD Runner 中無法依賴全域的 Windows GUI 狀態，RVA (GUI Automation) 相關功能需能優雅降級或依賴虛擬顯示 (Xvfb / Headless Browser)。
- **資源限制**：CI/CD 執行個體通常記憶體有限，必須強制啟用 Stealth Mode (< 50MB 記憶體佔用策略)。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)

### 方案 A: Native CLI Headless Mode (原生命令列無頭模式)
- **說明**：修改現有的 `main.py` 與路由層，攔截所有 `input()` 與 GUI 操作。
- **優點**：輕量，不改變現有部署邏輯，適合現有 Windows Runner。
- **缺點**：如果依賴的第三方庫 (如 `pywinauto`) 強制呼叫 Windows API 可能導致 Crash。

### 方案 B: Containerized Execution (容器化執行 - 推薦)
- **說明**：封裝 AutoAgent-TW 為官方 Docker Image (`alpine` 或 `debian-slim` base)，並內建無頭依賴。
- **優點**：跨平台一致性，完美隔離環境，最適合 GitHub Actions。
- **缺點**：需要處理 Linux 環境下的路徑與檔案權限問題，且 UIA/Win32 相關的 RVA 引擎將無法在此模式運行。

**架構決策**：採用 **混合方案 (Hybrid)**。主程式實作 `--headless` (方案 A) 作為基礎，並同步提供 Linux Docker Image (方案 B) 專門處理純代碼分析與 API 操作。

## 4. 資安威脅建模 (STRIDE Analysis)

| Threat | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Spoofing** | 惡意的 CI/CD Pipeline 嘗試偽造身份提交代碼 | 強制依賴 Git Provider 的 OIDC 或短期 Token 進行身份驗證，不長期儲存憑證。 |
| **Information Disclosure** | CI/CD 日誌 (Logs) 中洩漏 Gemini API Key 或 Git Token | 實作 `LogSanitizer` 中介層，攔截並替換 `stdout` 中的密鑰格式。 |
| **Denial of Service** | Agent 陷入自我修復死循環，耗盡 CI/CD Action Minutes | 實作絕對的 TTL (Time-To-Live) 與 Max Iterations (例如 `max_loops=3`)。超過即強制 `exit(1)`。 |

## 5. 編排策略與自動化模式 (Orchestration Strategy)

我們將採用 Wave 模式進行並行開發：
- **Wave 1: Core Headless Flag**: 實作 `--headless`、`LogSanitizer` 與 Exit Code mapping。
- **Wave 2: Dockerization**: 撰寫 `Dockerfile` 與 `docker-compose.yml`。
- **Wave 3: CI/CD Templates**: 建立 `.github/workflows/autoagent-review.yml` 範本。

## 6. 後續行動
- 提交本計畫後，準備執行 `/aa-plan 129` 以產出具體的實作步驟 (PLAN.md)。
