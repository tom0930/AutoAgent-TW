# Task 1: Core Headless Flag (Wave 1)

## 🎯 目標 (Objective)
在不改動核心決策與執行引擎的前提下，實作無頭模式基礎設施，攔截所有的 CLI 互動與終端輸出。

## 📝 具體步驟 (Steps)
1. 實作 `src/core/exit_codes.py`，定義 `ExitCode(IntEnum)`: SUCCESS(0), FAILURE(1), NEEDS_HUMAN(2)。
2. 實作 `src/core/runtime/headless.py` (`HeadlessRuntime`)，提供 `override_input` 方法以強制返回預設值，拒絕阻塞等待。
3. 實作 `src/utils/log_sanitizer.py`，作為全域的 `sys.stdout`/`sys.stderr` 包裝器，使用 Regex 過濾 `sk-.*` 與 `ghp_.*`。
4. 撰寫 `tests/test_headless_runtime.py` 驗證 I/O 攔截與日誌脫敏功能。

## 📁 預期變更 (Expected Changes)
- `[NEW] src/core/exit_codes.py`
- `[NEW] src/core/runtime/headless.py`
- `[NEW] src/utils/log_sanitizer_ci.py` (避免與既有 `log_sanitizer` 衝突，專為 CI 設計)
- `[NEW] tests/test_headless_runtime.py`

## ✅ 驗證標準 (UAT Criteria)
- `python -m pytest tests/test_headless_runtime.py -v` 必須全數 PASS。
- Stdout 包含密鑰時必須被成功替換為 `***MASKED***`。
