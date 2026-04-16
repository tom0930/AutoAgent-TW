# Phase 155: PC 資源優化 (PC Memory Optimization) - CONTEXT

## 1. 目標 (Goals)
建立全域排除清單，解決 PC 記憶體使用量過高、Token 浪費及掃描效能低下的問題。

## 2. 決策記錄 (Decisions)
- **.antigravityignore**：作為 AI 代理人專用的全域排除路徑，強制所有 AI 工具（Grep, LS, Browser）忽略大型雜訊。
- **.gitignore**：由 AI 自動同步使用者指定的路徑，保持代碼庫整潔。
- **.geminiignore**：專門針對模型 Token 優化，清理重複且無效的規則。

## 3. 排除清單 (Exclusion List)
- **全域：** `node_modules/`, `venv/`, `env/`, `.venv/`, `__pycache__/`, `*.pyc`
- **產物：** `dist/`, `build/`
- **日誌與快取：** `*.log`, `.pytest_cache/`
- **安全考慮：** `.env`, `*.key`, `secrets/`

## 4. DoD (Definition of Done)
- [ ] `.antigravityignore` 檔案建立並包含所有清單。
- [ ] `.gitignore` 檔案更新。
- [ ] `.geminiignore` 檔案重構完成。
- [ ] 執行 `grep_search` 測試不再讀取到忽略的路徑。

## 5. 資安考量
- 確保 STRIDE 分析中標註的洩漏風險被路徑過濾。
