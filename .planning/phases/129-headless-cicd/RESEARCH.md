# Phase 129: Domain Research (Headless CI/CD Integration)

## 1. 模組定位與依賴分析
從 `CONTEXT.md` 的 Wave 1 定義可知，需要建立以下模組：
- **CLI Entrypoint (`main.py`)**: 必須處理 `--headless` 解析。若偵測到該標記，需要覆寫標準 I/O。
- **Runtime 覆寫 (`src/core/runtime/headless.py`)**: 取代互動式 `input()` 與 rich Prompt。
- **日誌脫敏 (`src/utils/log_sanitizer.py`)**: 全域的 stdout/stderr Hook，攔截所有 API 輸出，替換敏感字串為 `***MASKED***`。
- **狀態退出碼 (`src/core/exit_codes.py`)**: 必須使用 Enum 定義 `0` (Success), `1` (Failure), `2` (Needs Human)。

## 2. CI/CD 環境限制
- 在 GitHub Actions (`debian-slim` 或 `ubuntu-latest`) 下，`DISPLAY` 變數不存在，任何嘗試載入 `pywinauto` 或 `tkinter` 的動作都會導致 RuntimeError。
- 必須在 `src/integrations/rva/` 中實作 `headless_adapter.py`，作為 GUI 引擎在無頭模式下的 Dummy 替身或降級模組。
- Docker Image 需要包含 `chromium` (如果需要 headless RVA) 或 `xvfb` 以便欺騙顯示伺服器。

## 3. GitHub Actions Template 參數設計
- `action.yml` 需要以下輸入參數 (inputs)：
  - `headless_args`: 傳遞給 AutoAgent-TW 的參數 (如 `--lite-context`)。
  - `ttl_minutes`: 確保 Job 不會超時掛起 (Hang)。
  - GitHub Token 或其他 OIDC 必須由 CI 環境注入環境變數 (`GITHUB_TOKEN`)。

## 4. 常見陷阱 (Pitfalls)
- **日誌編碼問題**: 在 Docker 內 `sys.stdout` 的編碼可能不是 UTF-8，導致中文字元噴出 `UnicodeEncodeError`，需要強制設定 `PYTHONIOENCODING=utf-8`。
- **快取失效**: Python 的 Pip Cache 若沒有搭配正確的 `hashFiles('requirements.txt')`，會導致每次 CI 都重新下載。
- **LLM Rate Limit**: CI 環境常併發執行多個 PR 的 Workflow，極易觸發 Gemini 或 Claude 的 429 Error。這凸顯了 `ExponentialBackoff` 在 Headless 模式中的絕對必要性。

## 5. 結論
本階段實作不會改變 AutoAgent-TW 的大腦邏輯，重點是**外殼與邊界**的加固。將任務嚴格拆分為 3 個子任務是最穩妥的做法。
