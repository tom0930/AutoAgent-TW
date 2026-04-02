# CLAUDE.md — AutoAgent-TW 專案規範

## 🔴 核心設計決策 (Design Decisions)
1. **指令優先級**: 優先使用 `/aa-orchestrate` 進行大任務拆解，而非直接寫代碼。
2. **記憶隔離**: 所有敏感 API 操作必須標註 `[SECURED]` 並在執行後清除臨時記憶 (L1)。

## 📝 程式碼風格 (Coding Style)
- Python: 嚴格遵守 PEP 8，使用 `ruff` 與 `black`。
- 版本管理: 每個功能 Phase 完成後必須產出摘要並交由 `/aa-ship` 處理。

## 🧪 測試要求 (Testing)
- 靜態檢查: 通過 `ruff check` 與 `mypy`。
- 單元測試: 覆蓋率至少需達 80%。
- 禁止在 Production 分支中使用 `assert` 推理。
