# Phase 169: Multi-Agent Execution Engine (Axis 2) - 核心決策與上下文

## 1. 任務意圖與邊界 (Intent & Boundaries)

**目標 (DoD)**:
在 Phase 168 (Consensus & Voting) 達成決策後，實作一個健壯的 **多代理執行引擎 (Multi-Agent Execution Engine)**。系統需能根據共識計畫 (Consensus Plan) 拆解並分配任務給對應的專職子代理 (如 Developer, UI, Security) 進行並行或依賴性循序執行，並最終整合代碼變更。

**邊界約束**:
- **資源隔離 (Resource Isolation)**: 各子代理只能讀寫被分配或授權的檔案路徑。
- **防止競態條件 (Race Condition Prevention)**: 多代理並行修改代碼時，必須具備檔案鎖 (FileLock) 機制。
- **嚴格超時 (Strict TTL)**: 單一代理執行任務不得超過預設時間上限，超時強制 Reap (回收)。

## 2. 歷史上下文與技術債 (Context & Tech Debt)
- **Phase 167/168 遺產**: 系統已經具備強大的平行規劃 (Parallel Planning) 與自動共識 (Consensus) 能力，產出了帶有 `adopted_decision` 與任務關聯的 `ConsensusResult`。
- **技術債**: 目前系統缺乏一個能將 `ConsensusResult` 自動映射為實際代碼修改工具調用 (Tool Calls) 的分配器。若是直接讓多個 Agent 呼叫 Bash/File 寫入，會引發嚴重的 Git 衝突與檔案損壞。

## 3. 架構選型與 Trade-off (Architecture)

### 方案 A: 循序執行鏈 (Sequential Chain)
- **優點**: 實作極簡，完全沒有檔案衝突問題。
- **缺點**: 放棄了 Axis 2 最核心的並行化優勢，執行時間將隨任務數線性增長。

### 方案 B: 基於 DAG 的並行執行器 (DAG-based Parallel Executor) [✅ 決定採用]
- **設計**: 
  1. **任務解析 (Task Parser)**: 將共識計畫轉換為具備相依性 (Dependencies) 的有向無環圖 (DAG)。
  2. **鎖定管理器 (File Lock Manager)**: 在檔案層級實作 Mutex，宣告修改意圖。若兩代理需修改同一檔案，透過 DAG 強制轉為循序執行。
  3. **隔離執行箱 (Isolated Sandbox)**: 各代理在執行期間的 Context Window 被隔離，只能看到與自己任務相關的程式碼。
- **Simplicity Check**: 避免實作過於複雜的 Git Branch per Agent 合併邏輯，而是採用輕量級的「記憶體層級 DAG 排序與 FileLock」，確保在同一個 Branch 下能安全並行寫入。

## 4. 資安威脅建模 (STRIDE)

| 威脅類型 | 描述 | 防禦策略 |
| :--- | :--- | :--- |
| **Spoofing** | 惡意任務偽裝成 Security 代理執行高權限操作。 | 在 `TaskDispatcher` 強制驗證 Agent Identity Token。 |
| **Tampering** | A 代理竄改 B 代理正在執行的工作目錄或檔案。 | 引入 `FileLockManager`，違反鎖定規則的寫入操作直接拋出異常並阻斷。 |
| **Repudiation** | 執行失敗或覆寫程式碼後無法追溯是哪個代理所為。 | 實作 `execution_audit.log`，紀錄每個 Agent 的 Tool Calls 與 Diffs。 |
| **Denial of Service** | 子代理產生無限迴圈或卡死在等待外部回應。 | 每個 Agent Executor 封裝於 `asyncio.wait_for`，設定嚴格 TTL (如 300s)。 |
| **Elevation of Privilege** | 代理嘗試透過 Bash Tool 執行 `sudo` 或系統層級變更。 | 結合 Phase 162 Guardrails，在 Tool Use 層級攔截危險指令。 |

## 5. 內部多 Agent 思考 (L1 Tactical Reflection)
- **[ASSUMPTION] 假設**: 我們假設所有 Agent 共用同一個 Workspace。
- **架構師視角**: DAG 排序是必須的。我們不能讓 Frontend 和 Backend 同時改同一支 API Schema 檔案，否則會發生資料遺失。依賴圖解析必須在執行前確立。
- **資安工程師視角**: 必須嚴格審查代理的輸出。如果代理注入了後門，誰來把關？(解答: Phase N+1 的 QA 階段會進行，但執行階段本身需有指令黑名單)。
- **AI 產品視角**: 執行時間可能很長，使用者需要即時的進度回饋。`cli.py` 需要有一個 `Live` Tree 顯示哪些任務正在排隊、哪些正在執行。

## 6. 編排與下一步 (Orchestration)
- **路徑**: 
  1. `scripts/execution/dag.py` (實作相依性解析與圖排序)
  2. `scripts/execution/lock_manager.py` (實作檔案層級鎖定)
  3. `scripts/execution/executor.py` (實作核心分派與生命週期管理)
- **下一步**: 啟動 Phase 169 的 Plan 階段，撰寫 8 維度執行清單。
