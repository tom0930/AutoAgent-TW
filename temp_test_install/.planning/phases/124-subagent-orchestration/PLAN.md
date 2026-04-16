# Phase 124 Plan: Sub-Agent Orchestration Engine

## 🏁 UAT 標準 (Criteria)
1. `/aa-orchestrate` 能成功解析多任務 Prompt。
2. 子代理能在獨立進程 (Isolated Process) 中平行執行，且不阻塞主介面。
3. Dashboard (status.html) 需能即時顯示至少 2 個子代理的進度條。
4. 即使子代理發生 `ZeroDivisionError` 或 `SyntaxError`，Dashboard 不得掛掉。

---

## 🌊 Wave 1: 基礎架構與進程管理 (Core Infra)
### Task 1.1: 實作 Spawn Manager
- 建立 `src/core/orchestration/spawn_manager.py`。
- 提供 `AgentProcess` 類別，封裝 `subprocess.Popen`。
- 支援自動生成 `.agent-state/subagents/{uuid}.json` 初始模板。
- **預計變更**: `src/core/orchestration/spawn_manager.py`

### Task 1.2: 強化 Status Notifier 健壯性
- 修改 `status_updater.py`，加入對子代理 JSON 的 Try-Except 讀取保護。
- 實作寫入鎖 (File Locking) 機制確保 Data Integrity。
- **預計變更**: `.agents/skills/status-notifier/scripts/status_updater.py`

---

## 🌊 Wave 2: LangGraph 編排邏輯 (Intelligence)
### Task 2.1: 實作 Coordinator 核心
- 建立 `src/core/orchestration/coordinator.py`。
- 定義 LangGraph `StateGraph`，包含 Supervisor 節點邏輯。
- 實作任務拆解解析器 (Task Splitting Prompt)。
- **預計變更**: `src/core/orchestration/coordinator.py`

### Task 2.2: 權限與預算繼承
- 整合 `permission_engine.py` 到子代理啟動參數中。
- 實現子代理每一步執行前的 `budget_monitor` 檢查。
- **預計變更**: `src/core/orchestration/spawn_manager.py`

---

## 🌊 Wave 3: CLI 與 Dashboard 整合 (UI/UX)
### Task 3.1: 實作 `/aa-orchestrate` 指令
- 將 `scripts/aa_orchestrate.py` 連結至 Coordinator。
- 支援 `--parallel` 參數控制最大併算數。
- **預計變更**: `scripts/aa_orchestrate.py`

### Task 3.2: Dashboard 熱更新驗證
- 更新 `status.html` 模板，優化子代理進度清單的顯示樣式（精緻化 UI）。
- 執行併發壓力測試，確認 Dashboard 不會掛掉。
- **預計變更**: `.agents/skills/status-notifier/templates/status.html`

---

## 🧪 驗證計畫
1. 執行 `python scripts/aa_orchestrate.py "Create a README and a Hello, World script in parallel"`。
2. 開啟 Dashboard 觀察 subagents 分頁或區塊。
3. 模擬子代理手動被刪除或損壞 JSON，確認主控台與 Dashboard 具備容錯能力。
