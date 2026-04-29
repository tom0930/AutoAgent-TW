# CONTEXT: Phase 129 (Headless CI/CD Integration)

## 1. 任務目標與意圖 (Objectives & Intent)
將 AutoAgent-TW 轉型為可在 CI/CD 流水線中全自動執行的無頭 (Headless) 引擎。這不僅是為了消除交互提示，更是為了打造一條**高效、安全、無頭的自動化道路**。
結合 Phase 169 (Execution & Validation) 的「車檢系統」，Phase 129 將專注於提供基礎設施 (Infrastructure) 與運行時環境 (Runtime Environment)，實現無人值守 (Unattended) 的 AI 自動修復、自動化審查與測試整合。

## 2. 邊界定義與約束 (Boundaries & Constraints)

### Definition of Done (DoD)
- 實作 `--headless` 標記，全面禁用 `input()`、GUI 操作與任何阻塞式交互。
- 支援標準 Exit Codes：`0` (成功), `1` (失敗), `2` (需人工介入)。
- 提供官方 GitHub Actions Template (`action.yml`)，支援 `on: [pull_request, push]`。
- stdout 輸出結構化 JSON 日誌，API Keys/Git Tokens 自動遮蔽 (***MASKED***)。
- 容器化支援：提供 `Dockerfile` (debian-slim) 與 `docker-compose.ci.yml`。

### 非功能性需求 (Non-Functional Requirements)
- **環境隔離與優雅降級**：在 CI/CD Runner 中無法依賴全域 Windows GUI，RVA 相關功能需能優雅降級或依賴虛擬顯示 (Xvfb / Headless Browser)。
- **資源受控 (Stealth Mode)**：CI 執行時記憶體佔用 `<50MB` (不含 LLM 呼叫)，透過 `--lite-context` 啟用。
- **TTL 與防死鎖保護**：單一 CI Job 絕對超時 `15min`，Agent 內部迴圈 `max_loops=3`。
- **效能可視化**：內建 Pipeline Metrics Exporter，輸出 `ci_metrics.json` 支援監控。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)

### 方案 A: Native CLI Headless Mode (原生命令列無頭模式)
- **說明**：攔截 `input()` 與 GUI 操作，直接在 Runner 實體機或現有 OS 上運行。
- **優點**：輕量，不改變現有部署邏輯。
- **缺點**：平台依賴性高，缺乏統一環境。

### 方案 B: Containerized Execution (容器化執行)
- **說明**：提供官方 Docker Image 並內建無頭依賴 (如 `xvfb`)。
- **優點**：跨平台一致性，完美隔離環境，最適合 GitHub Actions。
- **缺點**：無法運行原生的 Windows UIA/Win32 RVA 引擎。

**架構決策**：採用 **混合方案 (Hybrid)**。主程式實作 `HeadlessRuntime` 作為基礎路由攔截，並同步提供 Linux Docker Image，針對 GUI 功能實作自動降級 (Graceful Degradation)。

## 4. 資安威脅建模 (STRIDE Analysis)

| Threat | Description | Mitigation Strategy |
| :--- | :--- | :--- |
| **Spoofing (偽裝)** | 惡意的 CI/CD Pipeline 嘗試偽造身份提交代碼 | 強制依賴 GitHub OIDC 或短期 Token，無長期憑證落地。 |
| **Information Disclosure (資訊洩漏)** | CI 日誌中洩漏 LLM API Key 或 Git Token | 實作 `LogSanitizer` 中介層，以正則攔截並替換 `sk-.*`, `ghp_.*` 為 `***MASKED***`。 |
| **Denial of Service (阻斷服務)** | Agent 陷入自我修復死循環，耗盡 CI Action Minutes | 實作絕對 TTL (`15min`) 與 `max_loops=3`，觸發限流時採 `ExponentialBackoff`，失敗回傳 Exit Code 2。 |
| **Tampering (篡改)** | CI 過程中的日誌或產出被竄改 | 將所有 Tool Calls 與 Diffs 寫入 `.agent-state/ci_audit.json`，作為不可篡改之審計記錄。 |

## 5. CI/CD 性能優化五步驟整合
1. **Measurement**: `MetricsExporter` 輸出 `ci_metrics.json`。
2. **Identification**: `DiffScanner` 分析 `git diff` 標註高頻變更檔案。
3. **Optimization**: 啟用 `--lite-context`、增量執行與依賴快取 (`actions/cache`)。
4. **Reliability**: 實作 TTL、最大迴圈數與 flaky test 隔離。
5. **Iteration**: 若執行時間超過 baseline 1.5 倍，自動發送告警通知。

## 6. 編排策略與自動化模式 (Orchestration Strategy)

將依循以下三波浪 (Wave) 進行並行開發：
- **Wave 1: Core Headless Flag**: `HeadlessRuntime`, `ExitCode` Mapping, `LogSanitizer`, JSON Logging。
- **Wave 2: Containerization & Resource Control**: `Dockerfile.ci`, `Stealth Mode`, GUI 降級, TTL 迴圈保護。
- **Wave 3: CI/CD Templates & Performance**: `action.yml`, `MetricsExporter`, 增量執行策略。

## 7. 後續行動
- 將執行 Git Commit 儲存本次 `CONTEXT.md` 變更。
- （可選）準備進入 `/aa-plan 129` 階段。
