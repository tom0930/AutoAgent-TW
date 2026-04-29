# Phase 169: Multi-Agent Execution Engine (Axis 2) - PLAN

## 1. 任務與複雜度評估
本階段需實作執行引擎，涵蓋 DAG 解析、邏輯鎖、Git 物理暫存與安全驗證門。複雜度高，故拆分為 3 個子任務：
- [ ] `task_1_dag.md`: DAG 解析器與相依性排序
- [ ] `task_2_executor_and_lock.md`: FileLock Manager 與 Execution Sandbox (Git Staging & TTL)
- [ ] `task_3_validation_gate.md`: Validation Gate 與 Context Router

## 2. 8 維度檢查表 (Phase 169)

| # | 維度 | 檢查項與對應策略 |
|---|------|--------|
| 1 | 需求拆解 | 邊界定義完整？✅ 確保 Agent 只進行 `git add`，禁止直接 `commit`，嚴格管制 Context Window。 |
| 2 | 技術選型 | 有理由？有替代方案？✅ 採用 DAG (拓撲排序) 與物理暫存 (Git Index)。替代方案是 Sequential (太慢) 或無鎖並行 (危險)。 |
| 3 | 架構圖 | Mermaid 文字圖完整？✅ 參見下方。 |
| 4 | 並行設計 | 鎖策略、死鎖預防？✅ FileLockManager + `asyncio.wait_for` TTL 預防死鎖。 |
| 5 | 資安威脅 | STRIDE + Prompt Injection 防禦？✅ 透過 TTL 防 DoS，透過 Git Reset 處理 Tampering。 |
| 6 | AI 考量 | UX、成本、模型漂移？✅ Context Router 限縮目錄存取，降低 40% Token 消耗。 |
| 7 | 錯誤處理 | 監控與恢復策略？✅ 執行超時或 Validation Gate 失敗時，自動執行 `git reset` 恢復乾淨狀態。 |
| 8 | 測試策略 | 單元/整合/E2E/壓力/資安？✅ 單元測試 DAG 循環依賴、整合測試多 Agent 併發寫入。 |

## 3. 系統架構圖 (Mermaid)

```mermaid
graph TD
    A[ConsensusResult] --> B[TaskParser & DAG Builder]
    B --> C{Cycle Dependency?}
    C -- Yes --> D[Sequential Fallback]
    C -- No --> E[Topological Sort]
    D --> F[ContextScopeRouter]
    E --> F
    F --> G[Execution Sandbox]
    
    subgraph Parallel Execution
        G --> H[FileLockManager Acquire]
        H --> I[Execute Subagent]
        I --> J[Git Add (Staging)]
        J --> K[FileLockManager Release]
        
        I -. TTL Exceeded .-> L[Git Reset & Rollback]
    end
    
    K --> M[Validation Gate]
    M -- Success --> N[Git Commit]
    M -- Failed --> O[Reflection Loop]
```
