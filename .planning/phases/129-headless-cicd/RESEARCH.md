# RESEARCH: Phase 129 Headless CI/CD Integration

## 1. Codebase Map (相關程式碼地圖)
- `src/harness/cli/main.py`: 主程式入口，目前透過 `argparse` 解析命令。需要新增 `--headless` 參數並傳遞給各子系統。
- `src/core/security/log_sanitizer.py` (尚未建立): 預計放在此處，用來包裝 `sys.stdout` 進行正則表達式的密鑰脫敏 (Redaction)。
- `src/core/orchestration/coordinator.py`: 代理人調度中心。目前如果代理人發生錯誤可能會進行重試，在 Headless 模式下需要限制最大重試次數 (`max_loops`) 與 TTL。
- `src/core/health/checks.py`: 健康檢查，需在 Headless 模式下略過 UI / Display 相關的檢查。

## 2. API 與資料結構分析 (API & Data Structures)
- **Exit Codes**:
  - `0`: 成功完成自動化任務 (例如：Code Review Pass 或 Bug Fix 成功並 Commit)。
  - `1`: 系統性錯誤或自動化修復失敗。
  - `2`: 需要人工介入 (Human-in-the-loop)，在 CI/CD 中可視為失敗，但給予不同的提示。
- **Docker Base Image**: 
  - `python:3.13-slim` 是輕量且官方支援的首選。
  - 需要 `apt-get install -y git jq curl` 等 CI/CD 基本工具。

## 3. 陷阱與已知問題 (Pitfalls & Known Issues)
1. **Windows API 相依性**: 目前系統有部分 RVA 邏輯使用了 `pywinauto`。在 Linux Docker 或 Headless 模式下直接 `import pywinauto` 可能會導致 Crash。**解法**：在匯入時使用 `try-except ImportError` 或在執行時檢查 `os.name == 'nt'`。
2. **Interactive Prompts**: 任何 `input("Press Enter...")` 都會導致 CI/CD pipeline 卡死直到 timeout。必須嚴格封殺。
3. **stdout 緩衝區**: 在 CI/CD 中，Python 的 `stdout` 可能會有緩衝延遲，導致日誌順序錯亂。**解法**：使用 `sys.stdout.reconfigure(line_buffering=True)` 或執行時加上 `PYTHONUNBUFFERED=1`。
