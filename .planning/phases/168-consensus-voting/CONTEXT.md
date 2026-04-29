# Phase 168: Multi-Agent Consensus & Voting (Axis 2) - 核心決策與上下文

## 1. 任務意圖與邊界 (Intent & Boundaries)

**目標 (DoD)**:
在 Phase 167 (Parallel Planning) 的基礎上，實作一個健壯的 **共識與投票引擎 (Consensus & Voting Engine)**。當平行執行的子代理 (如 Architect, Security, UX) 產出衝突的決策或規劃時，系統能透過自動化的協商或權重投票機制達成一致，減少對人類介入的依賴。

**邊界約束**:
- **不可陷入無限迴圈 (No Infinite Loops)**: 協商過程必須有明確的輪次上限 (Max Rounds)。
- **角色權重 (Role-Based Weighting)**: 資安 (Security) 等級的否決權必須高於一般功能性決策。
- **透明度 (Transparency)**: 決策矩陣與共識過程必須透過 `rich` UI 清晰展示給使用者。

## 2. 歷史上下文與技術債 (Context & Tech Debt)
- **Phase 167 遺產**: 目前的 `MapReflectReduceOrchestrator` 僅能做到結果合成，並在發生衝突時直接拋出供人類決策 (Decision Matrix)。
- **技術債**: 缺乏自動化的內部協商機制，若子代理間存在微小分歧，頻繁的人類中斷會降低自動化效益。

## 3. 架構選型與 Trade-off (Architecture)

### 方案 A: 簡單多數決 (Simple Majority Voting)
- **優點**: 實作極簡，速度快。
- **缺點**: 無法處理複雜的程式碼或設計決策，且忽略了專業角色的特殊性 (例如資安的絕對否決權)。

### 方案 B: 角色權重與迭代協商引擎 (Role-Weighted Consensus & Iterative Negotiation) [✅ 決定採用]
- **設計**: 
  1. 導入 `ConsensusEngine` 取代單純的 `Reduce`。
  2. 定義 `ConsensusStrategy` (如 `Veto`, `WeightedAverage`, `Negotiation`)。
  3. **協商迴圈 (Negotiation Loop)**: 當檢測到重大衝突時，自動將各方的論點整理後，發起一輪 (限 1-2 次) 的內部交叉反思。
  4. **絕對否決 (Absolute Veto)**: 若 `Security` 代理偵測到 STRIDE 高風險項目，將觸發絕對否決，強制退回或阻斷該方案。
- **Simplicity Check**: 避免實作過於複雜的博弈論演算法，僅採用「角色權重打分」與「單次重試協商」，兼顧自動化與複雜度。

## 4. 資安威脅建模 (STRIDE)

| 威脅類型 | 描述 | 防禦策略 |
| :--- | :--- | :--- |
| **Spoofing** | 代理偽裝高權重角色進行惡意投票。 | 在 `Orchestrator` 層級鎖死角色與身分驗證，拒絕來自非預期 Agent ID 的投票。 |
| **Tampering** | 協商過程中竄改歷史紀錄。 | 採用 Immutable Message History，各代理的原始論點不可修改。 |
| **Repudiation** | 無法追溯最終決策是由誰妥協或否決。 | 將完整的投票與協商日誌寫入 `.agent-state/consensus_audit.log`。 |
| **Denial of Service** | 惡意或異常代理導致無窮協商迴圈，耗盡 Token。 | 硬性規定 `MAX_NEGOTIATION_ROUNDS = 2`，超時即進入 Fallback (Human-in-the-loop)。 |
| **Elevation of Privilege** | UX 代理覆蓋 Security 代理的安全否決。 | 實作 `RoleHierarchy`，Security 具有不可覆寫的 `VETO` 權限。 |

## 5. 編排與下一步 (Orchestration)
- **路徑**: 
  1. `src/core/orchestration/consensus.py` (實作核心邏輯)
  2. 整合至 `MapReflectReduceOrchestrator`。
  3. 更新 `ParallelPlanningCLI` 以顯示協商狀態。
- 此階段不涉及底層基礎建設改動，專注於邏輯層的演算法升級。
