**✅ 收到 Phase 171 Enhanced v2.0！**

這份文件已經寫得極為完整、嚴謹且可落地。我將在此基礎上再優化一輪，推出 **Phase 171 Ultimate v2.1**，重點強化**長期可維護性、觀測性、成本控制與極致使用者體驗**，讓它真正達到生產級工業水準。

---

### 💎 Phase 171 Ultimate v2.1 主要優化點

**1. 架構層優化**
- **Hierarchical Coordinator** 增加 **Meta-Coordinator**（輕量級），負責全局資源分配與 Squad 優先序排序，避免多 Squad 同時競爭資源。
- **Event Bus** 增加 **Event Priority Queue**（高優先危機事件先處理）。
- **Omniscient Agent** 與 Phase 170 **Evidence-Based Memory** 深度整合：所有 Suggestion 都必須附帶 `evidence` 來源，降低幻覺。

**2. Omniscient Agent 強化**
- **介入策略狀態機** 增加 **User Feedback Loop**：用戶可對 Suggestion 按 👍 / 👎，系統自動調整該類型事件的介入閾值（線上學習）。
- **L0 規則引擎** 建議使用更高效的工具：`tree-sitter`（AST 解析）取代純正則，提升準確度與速度。
- 新增 **Silence Mode**：用戶可暫時靜音助手（例如專注模式），但危機事件仍會突破。

**3. 效能與成本控制**
- **Agent Model Routing**：引入智能路由器，根據任務複雜度 + 剩餘 Token 預算自動選擇模型。
- **Squad Auto-Scaling**：根據當前系統負載動態調整 Max Concurrent Agents（預設 4，上限可調）。
- **Background Low-Priority Tasks**：常駐監控（CI、檔案變更）使用更便宜的 Flash 模型 + 較長輪詢間隔。

**4. 資安與可靠性升級**
- 所有 Agent 啟動前強制執行 **Pre-flight Security Scan**（掃描 Prompt 是否被注入）。
- Circuit Breaker 增加 **Exponential Backoff** + **Failure Pattern Detection**（若同一類錯誤重複，自動觸發更長冷卻）。
- 新增 **Agent Quarantine**：連續失敗達 5 次的 Agent 進入隔離池，需人工審核才能復用。

**5. 可觀測性（Telemetry）**
- 整合 Phase 170 Metrics 系統，新增關鍵指標：
  - Squad Success Rate
  - Average Intervention Latency
  - Token Cost per Role
  - User Satisfaction Score（基於 👍 / 👎 回饋）
- 提供 **/aa-dashboard** 指令或 Web Panel 查看即時多代理狀態。

---

### 📋 更新後的執行波次（Waves v2.1）

| Wave | 內容 | 重點新增 | 風險 | 預估工時 |
|------|------|---------|------|---------|
| **W1** | 基礎設施（Event Bus 擴展 + CapabilityCard + AgentSandbox + Meta-Coordinator） | Priority Queue、Pre-flight Scan | 低 | 1-2 天 |
| **W2** | Squad 與 Thread 模型 + Circuit Breaker v2（Exponential Backoff） | Meta-Coordinator 資源調度 | 中 | 2 天 |
| **W3** | Omniscient Core + 三層狀態機 + User Feedback Loop | Evidence 整合、Silence Mode | 中 | 2-3 天 |
| **W4** | Dual Renderers（CLI + Web）+ BaseRenderer 完整實作 | 共用核心嚴格驗證 | 中 | 2 天 |
| **W5** | Proactive Suggestion Engine（L0 tree-sitter + L1/L2）+ `.ag_prompts/` | 線上學習調整 | 中高 | 2 天 |
| **W6** | Telemetry + Dashboard + 完整測試套件（含資安滲透） | 所有 DoD 指標 | 低 | 1-2 天 |
| **W7** | 灰度發布 + Feature Flags 細調 + 文件與範例 | Rollback 機制 | 低 | 1 天 |

---

### 🔧 具體程式碼層建議

**1. CapabilityCard 優化**
```python
@dataclass
class CapabilityCard:
    agent_id: str
    role: AgentRole
    trust_level: TrustLevel
    allowed_tools: List[str]
    forbidden_tools: List[str] = field(default_factory=list)
    model_preference: str = "flash"
    max_tokens_per_task: int = 8000          # 新增：單任務 token 上限
    learning_rate: float = 0.1               # 用戶回饋調整強度
    # ...
```

**2. 新增 Meta-Coordinator 簡要介面**
```python
class MetaCoordinator:
    def __init__(self, bus: EventBus, max_agents: int = 4):
        self.active_squads: Dict[str, SquadCoordinator] = {}
        self.global_load: float = 0.0
    
    async def propose_squad(self, tasks: List[Task]) -> Optional[SquadConfig]:
        # 根據當前負載與任務類型決定是否 spawn、用幾個 Agent
        ...
```

---

### 💬 最終確認與下一步

這版 v2.1 已將**確定性、成本控制、使用者可控性**拉到最高水準，同時完美繼承 Phase 170 的非同步壓縮、Evidence Memory 與 Feature Flags。

**請確認以下兩點即可進入實作階段：**

1. 是否接受 **W7 灰度發布** 作為最終波次？（強烈建議）
2. Omniscient Agent 的**預設介入敏感度**要設為「保守」（較少主動）還是「平衡」？

---

**立即可產出項目（請指示優先序）：**

- A. Wave 1 完整實作任務清單 + 第一批程式碼框架
- B. `.ag_prompts/` 目錄下各角色 System Prompt 初稿（強制繁體中文）
- C. Omniscient Core 類別完整草稿
- D. Telemetry 指標定義與 Dashboard 介面設計

---

這份 Phase 171 Ultimate 已經非常接近可直接開發的 Production Blueprint。  
告訴我你的決定，我們立刻往前衝！🚀