# Phase 167 Context: Multi-Agent Parallel Planning

## 1. 目標 (Objective)
實現「多代理並行規劃 (Multi-Agent Parallel Planning)」架構。在 GSD (Get Shit Done) 框架的 Plan 階段，啟動多個領域專家 Agent（如架構師、資安專家、UX 專家）同時進行背景調查與草案規劃，並透過 Synthesizer (合成器) Agent 進行衝突排解與最終計畫融合，以大幅縮短規劃時間並提升計畫的全面性。

## 2. 邊界與約束 (Boundaries & Constraints)
* **DoD (Definition of Done)**:
  - 成功實作 Map-Reduce 風格的並行規劃引擎 (`parallel_planner.py`)。
  - 規劃用的 Subagent 必須強制運行於「唯讀模式 (Read-Only)」，嚴禁在規劃階段直接修改專案原始碼。
  - 具備防呆機制：當子代理解析超時或遭遇 API Rate Limit 時，能自動降級 (Fallback) 至單一 Agent 規劃模式。
* **非功能性需求**:
  - 並行執行時的 Token 消耗監控（結合 Phase 143/165 的資源管控）。
  - 必須有明確的 CLI 進度顯示，避免使用者誤判系統當機。

## 3. 架構選型與 Trade-off (Architecture & Trade-offs)
經過內部多 Agent 思考 (架構師、資安工程師、AI 產品專家) 的辯論，提出以下方案：

* **方案 A：沙盒隔離與獨立工作區 (Sandbox Cloning)**
  - *作法*：為每個 Agent 複製一份專案 Context 快照，Agent 在隔離區內生成計畫。
  - *缺點*：I/O 負擔過重，且合併 (Merge) 多個 `.md` 檔案的邏輯過於複雜。
* **方案 B：唯讀子代理與 Map-Reduce 合成 (Read-Only Subagents + Synthesizer)** [✅ 獲選]
  - *作法*：主控節點發送相同的 Context 給多個 Subagent（賦予不同 System Prompt：資安、架構等）。Subagents 僅返回 Markdown/JSON 規劃片段（無 File Write 權限）。最後交由 Synthesizer Agent 融合。
  - *優點*：沒有 File Lock 衝突，利用現有 Phase 165 的資源管控限制子代裡的耗用。符合 "Simplicity Check"，單純透過 Prompting 與 API 併發即可達成。

## 4. 資安威脅建模 (STRIDE)
* **Spoofing (欺騙)**: 確保子代理的 System Prompt 無法被 User Prompt Injection 覆寫。
* **Tampering (篡改)**: 強制子代理的 Tool Access 拔除 `write_to_file` 與 `run_command`，確保它們無法在規劃期植入惡意後門。
* **Repudiation (否認)**: 每個子代理的產出必須記錄在 `.agent-state/parallel_planning_logs/` 以供稽核。
* **Information Disclosure (資訊洩漏)**: 避免將敏感的環境變數傳遞給規劃子代理。
* **Denial of Service (阻斷服務)**: 並發 3-4 個 Agent 容易觸發 LLM API HTTP 429。必須實作 Exponential Backoff 與 Jitter 重試機制。
* **Elevation of Privilege (擴權)**: 嚴格限縮 `Synthesizer` 的權限，僅允許其寫入 `.planning/phases/` 內的計畫文件。

## 5. 編排策略 (Orchestration)
* **Wave 並行化**: 是。使用 `asyncio.gather` 或 `ThreadPoolExecutor` 發出 API 請求。
* **自動化模式**: 當處於 `--auto` 模式時，預設啟用 `[Architect, Security]` 雙節點並行；若需深度規劃，則啟用完整節點矩陣。

## 6. Open Questions / Assumptions [ASSUMPTION]
* **Q1**: 是否要將此功能整合入現有的 `aa-plan` Workflow，還是建立全新的 `/aa-parallel-plan`？ (假設：直接升級 `aa-plan`，透過 flag `--parallel` 觸發，保持向後相容)。
* **Q2**: Synthesizer 如果判定兩個 Agent 提出完全相左的架構 (例如：Rust vs Python)，該如何裁決？ (假設：交回給 User 確認，或依據 `PROJECT.md` 的技術棧優先順序自動裁決)。
