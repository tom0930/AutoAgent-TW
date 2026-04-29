這份 Phase 168 的規劃已具備高度成熟度，邏輯清晰且嚴格遵守 GSD 的「Simplicity Check」。為確保工程落地時的穩定性、成本控制與自動化效益，我針對現有藍圖提出 **5 項關鍵優化** 與 **升級版工作流**，直接補齊技術債與潛在風險。

---

### 🔹 一、 5 項關鍵優化建議 (Better Plan)

| 優化維度                          | 現況痛點                                  | 優化方案                                                                                                                                                                                                                                      | 預期效益                                    |
| :-------------------------------- | :---------------------------------------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | :------------------------------------------ |
| **1. 衝突分級與策略路由**   | 所有衝突一律進入協商，浪費 Token 與時間   | 前置 `ConflictClassifier` 將衝突分為三級：`<br>`• `CRITICAL` (資安/合規) → `Veto` (立即阻斷)`<br>`• `MAJOR` (架構/效能) → `Negotiation Loop` (max 2 rounds)`<br>`• `MINOR` (命名/樣式) → `Weighted Vote` (自動採納) | 節省 60%+ 協商 Token，避免「殺雞用牛刀」    |
| **2. 量化共識閾值**         | 缺乏「何時算達成共識」的數學標準          | 定義 `Consensus Score = Σ(Confidence × RoleWeight × DomainRelevance) / Σ(RoleWeight)<br>`設定 `THRESHOLD = 0.75`，達標即自動通過                                                                                                      | 決策可量化、可測試、可預測                  |
| **3. 動態權重與領域相關性** | 權重寫死易僵化，UX 可能在資安議題過度發聲 | 從 `.agent-config/role_weights.yaml` 讀取基礎權重。協商時乘上 `DomainRelevance` (0.5~1.5)，資安議題自動放大 Security 權重，縮小 UX 權重                                                                                                   | 符合 STRIDE EoP 防禦，角色專業性最大化      |
| **4. 預算感知 Fallback**    | 協商超時或 Budget 耗盡時缺乏明確退路      | 整合 Phase 143 `ResourceMonitor`：`<br>`• 若 `budget_remaining < 20%` → 強制終止協商，採納最高分方案並標記 `[BUDGET_FALLBACK]<br>`• 若 `rounds > MAX_NEGOTIATION_ROUNDS` → 寫入 `.planning/pending_review.md` 交 User         | 嚴格遵守資源管控，永不卡死流程              |
| **5. 不可變稽核協議**       | 日誌格式未定義，事後難以追溯妥協點        | 強制輸出 `consensus_audit.json`，結構包含：`<br>{round_id, conflict_dimension, votes, weights, reasoning_snapshot, final_decision}``<br>`所有記錄以 Append-Only 寫入                                                                    | 滿足 Repudiation 防禦，支援事後 AI/人類覆盤 |

---

### 🔹 二、 升級版共識工作流 (Consensus Pipeline)

```text
[Phase 167 Map Reflect 產出]
        ↓
1. ConflictClassifier → 提取 conflict_dimensions 並分級 (Critical/Major/Minor)
        ↓
2. Strategy Routing → 依分級分配協商策略
   ├─ CRITICAL → 觸發 Security Veto → 若觸發 → 直接退回 Fallback/標記阻斷
   ├─ MAJOR   → 進入 Negotiation Loop (max 2 rounds)
   │    ├─ Round 1: 各 Agent 針對衝突點補充論據 + 調整 Confidence
   │    ├─ Round 2: Synthesizer 彙整妥協方案，Agent 最終投票
   │    └─ 計算 Consensus Score → 若 ≥ 0.75 → 通過
   └─ MINOR   → 直接執行 Weighted Vote → 採納最高分
        ↓
3. Fallback & Audit → 若未達標/預算不足 → 寫入 audit log + 標記 PENDING_REVIEW
        ↓
4. CLI Live 更新 → `rich.Live` 顯示投票進度條、分數、最終決策狀態
```

---

### 🔹 三、 核心實作骨架提示 (`consensus.py`)

```python
from pydantic import BaseModel, Field
from typing import List, Literal, Dict, Any

class AgentVote(BaseModel):
    agent_role: str
    confidence: float = Field(ge=0.0, le=1.0)
    decision: str
    reasoning: str
    domain_relevance: float = Field(ge=0.5, le=1.5, default=1.0)

class ConsensusResult(BaseModel):
    status: Literal["CONSENSUS", "VETO", "FALLBACK", "PENDING_REVIEW"]
    score: float
    adopted_decision: str
    audit_path: str
    notes: List[str] = []

class ConsensusEngine:
    def __init__(self, config: Dict, monitor: Any):
        self.config = config
        self.monitor = monitor
        self.max_rounds = 2
        self.threshold = 0.75

    def classify_conflict(self, conflict: Dict) -> Literal["CRITICAL", "MAJOR", "MINOR"]:
        # 基於關鍵字、STRIDE 風險等級、依賴影響範圍分類
        pass

    async def resolve(self, votes: List[AgentVote], conflict_type: str) -> ConsensusResult:
        if conflict_type == "CRITICAL":
            return self._apply_veto(votes)
      
        for round_idx in range(self.max_rounds):
            if not self.monitor.can_spend_tokens(est_tokens=2000):
                return self._budget_fallback(votes)
          
            # 執行交叉反思或重新投票邏輯
            votes = await self._negotiate_round(votes, round_idx)
            score = self._calculate_score(votes)
          
            if score >= self.threshold:
                return ConsensusResult(status="CONSENSUS", score=score, ...)
              
        return self._timeout_fallback(votes)
```

---

### 🔹 四、 DoD 強化對齊清單

| DoD 項目         | Phase 168 實作對應                                             | 狀態   |
| :--------------- | :------------------------------------------------------------- | :----- |
| ✅ 無無限迴圈    | `MAX_NEGOTIATION_ROUNDS = 2` + Token 預算硬截斷              | 已強化 |
| ✅ 角色權重否決  | `CRITICAL` 路由觸發 Security Veto，權重不可覆蓋              | 已強化 |
| ✅ 透明度        | `rich.Live` 投票儀表板 + `consensus_audit.json` 不可變日誌 | 已強化 |
| ✅ 防呆 Fallback | 預算/輪次雙觸發 Fallback，標記 `PENDING_REVIEW` 不中斷 GSD   | 已強化 |
| ✅ 整合相容      | 定義明確 `ConsensusPayload` 與 Phase 167 無縫對接            | 已納入 |

---

### 🔹 五、 下一步行動建議

1. **定義 `role_weights.yaml` 與分類規則**：明確寫出各領域基礎權重與 `ConflictClassifier` 的判斷邏輯（建議基於正則/關鍵字+依賴圖影響節點數）。
2. **實作 `_calculate_score` 與 `_negotiate_round`**：先寫單元測試驗證加權公式與閾值收斂行為。
3. **串接 CLI `rich.Live`**：實現即時分數條與狀態轉換視覺化。
4. **撰寫 `consensus_audit.json` Schema**：確保每一輪投票、妥協理由、最終決策可被後續 Phase 169 (Execution) 直接讀取。

是否需要我提供：

- `ConflictClassifier` 的具體規則表與 Prompt 模板？
- `ConsensusEngine` 的完整單元測試骨架？
- `rich` CLI 進度條與投票儀表板的實作程式碼？

可直接指定切入點，我將輸出可複製執行的完整模組。
