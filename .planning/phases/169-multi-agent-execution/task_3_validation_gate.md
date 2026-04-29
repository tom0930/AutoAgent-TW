# Task 3: Validation Gate & Context Router

**目標**: 
實作驗證門與 Context 路由器，確保併發寫入的程式碼不只要沒有 Git 衝突，還要通過語意與語法驗證。同時實作目錄限縮邏輯。

## 具體步驟
1. 建立 `scripts/execution/context_router.py`。
   - 實作 `ContextScopeRouter.get_scope(role: str, files: List[str]) -> dict`。
   - 根據 `role` (如 `ui`, `security`, `backend`) 給予對應的 `allowed_paths`。
2. 建立 `scripts/execution/validator.py`。
   - 讀取 `.validation/hooks.yaml` (建立一組簡單的預設 hook: e.g., `python -m py_compile`).
   - 實作 `ValidationGate.run_checks()` 函數。
   - 若成功，返回 True。
   - 若失敗，提取 `stderr` 與 Git Diff 作為 Payload，返回 False。
3. 更新/建立 `tests/test_validation_gate.py`。

## 驗證標準 (UAT Criteria)
- `python -m pytest tests/test_validation_gate.py -v` 通過。
- ContextScopeRouter 能正確阻擋 (`403 Forbidden`) 逾越權限的目錄存取。
