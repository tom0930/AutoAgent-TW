# PLAN: Phase 129 Headless CI/CD Integration

## 複雜度評估 (Complexity Assessment)
- **跨度**: 涉及主入口 (`main.py`)、安全模組 (`log_sanitizer.py`)、調度模組 (`coordinator.py`) 與 Docker/CI 設定檔。
- **複雜度**: 中等 (Medium)。不需要強制拆分為多個 Task 檔案，單一 `PLAN.md` 搭配明確的 Step-by-Step 即可。

---

## 執行步驟 (Execution Steps)

### Step 1: 實作日誌脫敏 (Log Sanitization)
- **目標**: 防止 API Keys 在 CI/CD 日誌中外洩。
- **動作**: 
  - 建立 `src/core/security/log_sanitizer.py`。
  - 實作 `LogSanitizer` 類別，使用 Regex 攔截並替換符合 `sk-ant-api*`, `AIzaSy*`, `ghp_*` 格式的字串為 `[REDACTED]`。
  - 整合至 `src/harness/cli/main.py` 的 `_setup_logging` 中。
- **UAT**: 在測試中印出包含 Dummy API Key 的字串，確認輸出被替換。

### Step 2: CLI 支援 `--headless` 標記
- **目標**: 禁用所有的互動提示與 GUI 相依性。
- **動作**:
  - 在 `main.py` 中新增 `--headless` 全域參數。
  - 確保 `--headless` 開啟時，`PYTHONUNBUFFERED` 被模擬或強制設定。
  - 傳遞 `headless=True` 到 `OrchestrationCoordinator`，關閉所有的 `input()` 提示。
- **UAT**: 執行 `aa-harness --headless doctor`，不應出現任何暫停等待。

### Step 3: 調度器防護 (Orchestration Guard)
- **目標**: 防止 CI/CD 分鐘數被耗盡。
- **動作**:
  - 在 `src/core/orchestration/coordinator.py` 中，當 `headless=True` 時，強制設定 `max_loops = 3` (或從環境變數讀取)。
  - 若達到 `max_loops` 尚未完成，拋出 `HeadlessTimeoutError` 並回傳 Exit Code `1`。
- **UAT**: 撰寫 Mock 測試，模擬一個永遠失敗的子代理人，驗證 3 次後自動中斷並退出。

### Step 4: 容器化與 CI/CD 範本
- **目標**: 支援 GitHub Actions。
- **動作**:
  - 撰寫根目錄的 `Dockerfile`，使用 `python:3.13-slim`，安裝依賴，並複製專案檔案。設定 ENTRYPOINT 為 `aa-harness --headless`。
  - 建立 `.github/workflows/autoagent-review.yml` 範本，示範如何觸發 AI 代碼審查。
- **UAT**: 能成功執行 `docker build -t autoagent-tw .`。

---

## 預期變更文件列表 (Expected File Changes)
- `[NEW] src/core/security/log_sanitizer.py`
- `[MODIFY] src/harness/cli/main.py`
- `[MODIFY] src/core/orchestration/coordinator.py`
- `[MODIFY] src/core/health/checks.py`
- `[NEW] Dockerfile`
- `[NEW] .github/workflows/autoagent-review.yml`
