# Task 2: Containerization & Resource Control (Wave 2)

## 🎯 目標 (Objective)
提供跨平台一致的執行環境，並實作資源限制與 UI 功能的優雅降級。

## 📝 具體步驟 (Steps)
1. 撰寫 `Dockerfile.ci`，基於 `python:3.11-slim`，並安裝 CI 必需的系統依賴 (如 git)。
2. 撰寫 `requirements-ci.txt`，僅包含 headless 所需套件。
3. 實作 `src/core/context_scoper.py` (`StealthMode`)，於 `--lite-context` 啟用時強制減少載入的模組並限制 `max_tokens`。
4. 實作 `src/integrations/rva/headless_adapter.py`，當偵測到無頭模式時取代真實的 RVA 操作，避免 `pywinauto` 報錯。

## 📁 預期變更 (Expected Changes)
- `[NEW] Dockerfile.ci`
- `[NEW] requirements-ci.txt`
- `[NEW] src/core/context_scoper.py`
- `[NEW] src/integrations/rva/headless_adapter.py`
- `[NEW] tests/test_stealth_mode.py`

## ✅ 驗證標準 (UAT Criteria)
- Docker build 成功：`docker build -f Dockerfile.ci -t autoagent-ci:latest .`
- `pytest tests/test_stealth_mode.py` 驗證 Token 限制器正確觸發。
