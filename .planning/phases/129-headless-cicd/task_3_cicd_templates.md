# Task 3: CI/CD Templates & Performance (Wave 3)

## 🎯 目標 (Objective)
提供官方的 GitHub Actions Template，並整合 5 步驟性能優化 (尤其是 Metrics 測量與增量掃描)。

## 📝 具體步驟 (Steps)
1. 建立 `.github/workflows/auto-review.yml` (範例檔案，放在 `examples/` 供參考)。
2. 建立 `action.yml` 於根目錄，定義 Custom Action 參數與 Docker entrypoint。
3. 實作 `src/utils/metrics_exporter.py`，於 AutoAgent 結束時寫入執行時長與 Token 消耗至 `.agent-state/ci_metrics.json`。
4. 實作 `src/core/diff_scanner.py`，封裝 `git diff --name-only`，作為 Agent 決策的前置過濾器。

## 📁 預期變更 (Expected Changes)
- `[NEW] action.yml`
- `[NEW] examples/auto-review.yml`
- `[NEW] src/utils/metrics_exporter.py`
- `[NEW] src/core/diff_scanner.py`
- `[NEW] tests/test_ci_metrics.py`

## ✅ 驗證標準 (UAT Criteria)
- 執行 `pytest tests/test_ci_metrics.py -v` 必須通過，確認 JSON 正確寫出。
- 測試執行 Dummy Diff Scanner 確保只返回修改的檔案。
