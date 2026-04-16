# Phase 155: PC 資源優化 (PC Memory Optimization) - PLAN

## 1. 任務清單 (Task List)

### Task 1: 建立根目錄忽略清單
- [ ] 1.1 建立 `.antigravityignore`：
  ```text
  node_modules/
  venv/
  env/
  .venv/
  __pycache__/
  *.pyc
  dist/
  build/
  *.log
  .pytest_cache/
  ```
- [ ] 1.2 更新 `.gitignore` (保留原有規則，附加新項並清理重複)：
  - [ ] 附加 `node_modules/`, `venv/`, `env/`, `.venv/`, `__pycache__`, `*.pyc`, `dist/`, `build/`, `*.log`, `.pytest_cache/`
- [ ] 1.3 優化 `.geminiignore`：
  - [ ] 清理重複規則。
  - [ ] 確保包含 `.pytest_cache/`。

### Task 2: 驗證效果 (QA)
- [ ] 2.1 檢查檔案存在：
  - [ ] `ls .antigravityignore, .gitignore, .geminiignore`
- [ ] 2.2 模擬搜尋測試 (確認是否攔截)：
  - [ ] 嘗試搜尋 `node_modules` 下的內容（如有的話），確認被忽略。

### Task 3: 交付與 Commit (Ship)
- [ ] 3.1 執行 convention commit：
  - [ ] `feat: 配置全域忽略清單以優化 PC 資源使用量 v0.1.0`
- [ ] 3.2 更新進度文件。

## 2. 驗證指令 (Verify Commands)
- `Get-ChildItem -Path .antigravityignore, .gitignore, .geminiignore`
- `rg "node_modules" --stats` (若安裝有 ripgrep)

## 3. 相依性 (Dependencies)
- 無顯著相依，可直接執行。
