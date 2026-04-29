# Phase 169: Multi-Agent Execution Engine (Axis 2) - RESEARCH

## 領域研究 (Session Research)

**1. Context Scope & Isolation**
依據 Phase 169 Qwen 的建議，需要實作 `ContextScopeRouter`，避免將整個 Repository 交給每個 Subagent，以降低 40% 的 Token 消耗。
- 前端 (UI) Agent 僅需 `src/components/`, `src/app/`。
- 後端 (API) Agent 僅需 `src/api/`, `src/core/`。

**2. Physical Git Index Staging**
為解決多代理寫入衝突與故障復原，必須採用 Git Index 暫存 (物理鎖)。
- 原先：各子代理 `git commit` 或直接 `write_to_file`。
- 新版：各子代理執行 `subprocess.run(["git", "add"] + task.files)`。
- 若失敗：`subprocess.run(["git", "reset", "--"] + task.files)`。

**3. Execution Validation Gate**
單憑 DAG 並行依賴，不代表「語義相容」。
例如 Backend 修改了 API，Frontend 即使沒有 Git 衝突，也可能發生 TypeScript 編譯錯誤。
因此在全部 Agent 暫存完畢後，必須加入一道 Validation Gate。
- 若 `npm run typecheck` 或 `pytest` 通過：`git commit -m "Auto-exec: [Phase 169] ..."`
- 若失敗：收集 Diff 與 STDERR 進入 Reflection Loop (max 2)。

**已識別陷阱 (Pitfalls)**:
1. 若 DAG 節點遇到循環相依 (`CycleError`)，不能直接報錯中斷，應自動降級為 Sequential 模式 (`ExecutionNode` 平鋪)。
2. asyncio 的 `TimeoutError` 中斷時，Subprocess 的 Git 暫存若未清除，會污染下一個任務，故必須放在 `finally` 或 `except TimeoutError` 區塊強制 `git reset`。
