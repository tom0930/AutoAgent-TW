# Phase 171 Enhanced v2.0: Multi-Agent Coordination & Omniscient Assistant
## AutoAgent-TW 多代理協作架構 + IDE 全能助手設計

**版本**: v2.0 (Discuss Phase — Enhanced with User Feedback)
**日期**: 2026-05-03
**設計者**: Tom (Senior Architect, AI Product Expert, Security Engineer)
**決策確認**: A=(c), B=(c), C=(a) — 雙端渲染 + 批量/常駐雙模 + 結構化 Event

---

## 1. 需求拆解與邊界定義

### 1.1 已確認的三大核心需求

#### 需求 A: Shared Core, Dual Renderers（核心共用、雙端渲染）
- **Web Side Panel** (Antigravity IDE): 主要介面，透過 Extension API 深度整合
- **CLI `rich` Live Display**: Fallback / 純終端機用戶使用
- **鐵律**: 兩個 Renderer **共享同一個 Omniscient Agent Core**，只差渲染層（MVC 解耦）

#### 需求 B: Dynamic Squad Composition（動態小隊組合）
- 一次性批量任務：用戶說「修 5 個 bug」→ 自動 spawn Coder + Tester + Reviewer
- 常駐專家代理：持續監控 CI、檔案變更、效能指標
- **動態組合**：根據任務自動決定需要哪些 Agent 角色

#### 需求 C: Structured Event-Only Communication
- Agent 間**禁止自然語言對話**（避免幻覺 + 成本失控）
- 所有通訊透過 Phase 170 的 `StreamingEventBus` 傳遞結構化 JSON
- 未來若需「討論」：透過 `REQUEST_FOR_DISCUSSION` Event，由 Coordinator 中轉

### 1.2 DoD (Definition of Done)
- [ ] 可同時運行 ≥ 3 個 Agent，各自獨立完成子任務
- [ ] Agent 失敗不影響整體任務（99.9% Resilience）
- [ ] IDE 全能助手在 Antigravity 啟動後 < 3 秒完成初始化
- [ ] 全能助手能感知當前文件的 Lint 錯誤並主動提示修復
- [ ] 所有 Agent 間通訊均通過 Phase 170 的 Input Sanitizer
- [ ] Max Concurrent Agents = 4（全域上限，可配置）
- [ ] 所有文字產出強制繁體中文

---

## 2. 技術選型（最終決策）

### 2.1 多代理框架: LangGraph 擴展 + 自建 Hierarchical Coordinator

**選擇理由**:
- 現有 `OrchestrationCoordinator` 已使用 LangGraph，不引入新依賴（Simplicity Check ✅）
- Phase 170 的 `StreamingEventBus` 直接作為 Agent 通訊底層
- 現有 `SpawnManager` + `PermissionEngine` 提供 Agent 生命週期與權限控制

### 2.2 Omniscient Agent: MCP Bridge + Event-Driven UI

**感知鏈**: `IDE Events → MCP workspace/status → OmniscientCore → EventBus → Renderers`

---

## 3. 系統架構圖

```
┌───────────── Antigravity IDE ──────────────────────────────────┐
│                                                                │
│  ┌──────────────────────────────────────────────────────┐     │
│  │      AI Omniscient Assistant (Web Side Panel)         │     │
│  │  - 三層介入: Passive → Proactive Gentle → Active     │     │
│  │  - Proactive Suggestion Engine                        │     │
│  │  - Natural Language → /aa-* Workflow Bridge           │     │
│  └──────────────────────┬───────────────────────────────┘     │
│                         │ MCP Protocol                         │
└─────────────────────────┼─────────────────────────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────┐
│              AutoAgent-TW Core (Phase 171)                     │
│                                                                │
│  ┌──────────────────────────────────────────────────────────┐ │
│  │          Hierarchical Coordinator Hub                     │ │
│  │                                                           │ │
│  │  Top: OrchestrationCoordinator (全局調度)                 │ │
│  │    ├── Squad-A: [Coder + Tester + Reviewer]              │ │
│  │    └── Squad-B: [Coder + Reviewer]                       │ │
│  │                                                           │ │
│  │  Omniscient Agent (常駐)                                  │ │
│  │    ├── IDE Sensor (MCP workspace/status)                  │ │
│  │    ├── Suggestion Engine (L0/L1/L2)                       │ │
│  │    └── Workflow Bridge (/aa-* 自然語言介面)                │ │
│  └──────────────────────┬───────────────────────────────────┘ │
│                         │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐ │
│  │         Phase 170 Streaming Event Bus                     │ │
│  │  新增 EventTypes:                                         │ │
│  │    AGENT_SPAWNED | AGENT_COMPLETED | AGENT_FAILED         │ │
│  │    SQUAD_PROPOSED | SQUAD_COMPLETED                       │ │
│  │    SUGGESTION_READY | CRISIS_DETECTED                     │ │
│  │    INTERVENTION_TRIGGERED                                 │ │
│  └──────────────────────┬───────────────────────────────────┘ │
│                         │                                      │
│  ┌──────────────────────▼───────────────────────────────────┐ │
│  │     Security & Persistence (Phase 170)                    │ │
│  │  InputSanitizer | SandboxEvaluator | AuditLogger          │ │
│  │  CheckpointV2   | CompressionGate  | FeatureFlags         │ │
│  └──────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
                          │
                   ┌──────▼──────┐
                   │ Dual Render │
                   ├─────────────┤
                   │ CLI (rich)  │  ← Fallback
                   │ Web (Panel) │  ← Primary
                   └─────────────┘
```

### 3.1 Agent Identity & Capability Card（核心資料模型）

```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"
    OMNISCIENT = "omniscient"

class TrustLevel(Enum):
    LOW = 1      # 只能讀取
    MEDIUM = 2   # 可執行安全命令
    HIGH = 3     # 可修改文件
    ADMIN = 4    # 可存取 .env / 系統設定

@dataclass
class CapabilityCard:
    """每個 Agent 的身份與能力清單"""
    agent_id: str
    role: AgentRole
    trust_level: TrustLevel
    allowed_tools: List[str]           # 白名單工具列表
    forbidden_tools: List[str] = field(default_factory=list)
    max_memory_mb: int = 256           # 記憶體上限
    ttl_seconds: int = 300             # 生命週期上限 (5 min)
    model_preference: str = "flash"    # 成本控制：flash/sonnet/opus
    current_load: float = 0.0          # 目前負載 (0.0 ~ 1.0)
```

**角色預設能力矩陣**:

| 角色 | 信任等級 | 允許工具 | 禁止工具 | 預設模型 |
|------|---------|---------|---------|---------|
| Coordinator | ADMIN | 全部 | 無 | opus |
| Coder | HIGH | edit_file, run_command, grep | delete_database | sonnet |
| Tester | MEDIUM | run_command, read_file | write_to_file, edit_file | flash |
| Reviewer | MEDIUM | grep_search, read_file | run_command, write_to_file | sonnet |
| Omniscient | LOW | workspace/status, mempalace_search | 所有修改類 | flash |

---

## 4. Omniscient Agent Core（全能助手核心設計）

### 4.1 三層介入策略狀態機

```
                    ┌─────────────┐
        idle > 8s   │             │ user @助手
   ┌───────────────>│   PASSIVE   │<────────────┐
   │  (無問題)       │  (靜默觀察)  │             │
   │                └──────┬──────┘             │
   │                       │                     │
   │           偵測到 Warning/Lint               │
   │                       │                     │
   │                ┌──────▼──────┐             │
   │                │  PROACTIVE  │ 用戶關閉     │
   │                │   GENTLE    │─────────────┘
   │                │(側邊欄建議)  │
   │                └──────┬──────┘
   │                       │
   │           偵測到 Error/Security
   │                       │
   │                ┌──────▼──────┐
   └────────────────│   ACTIVE    │
     問題已解決      │(強制介入)    │
                    │ 全螢幕診斷   │
                    └─────────────┘
```

### 4.2 Proactive Suggestion Engine（主動建議引擎）

**分級掃描策略（Token 成本控制）**:

| 等級 | 觸發條件 | 方法 | LLM 成本 |
|------|---------|------|---------|
| **L0** (Free) | 文件保存、切換 | 本地規則引擎（正則 + AST） | 0 |
| **L1** (Cheap) | Lint 錯誤 > 3 個 | Flash 模型 + 快取 | 低 |
| **L2** (Premium) | CRISIS (編譯失敗/安全問題) | Opus 完整分析 | 高 |

**觸發事件矩陣**:

| IDE 事件 | 觸發動作 | 介入等級 |
|---------|---------|---------|
| 文件保存 | L0 規則掃描 | Passive |
| 切換文件 | 查詢 MemPalace 歷史決策 | Passive |
| Lint 錯誤 ≥ 3 | L1 Flash 分析 | Proactive Gentle |
| 編譯失敗 | L2 Opus 診斷 | Active |
| Git Commit 前 | Preflight Check | Proactive Gentle |
| 測試失敗 | 自動啟動 /aa-fix | Active |

### 4.3 BaseRenderer 介面（共用核心原則）

```python
# src/core/renderers/base.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseRenderer(ABC):
    """所有渲染器的合約介面（CLI 與 Web 共用）"""
    
    @abstractmethod
    def update_state(self, status: str, context: Dict[str, Any]) -> None:
        """處理狀態變更 (IDLE, ACTIVE, CRISIS)"""
        ...
        
    @abstractmethod
    def display_suggestion(self, suggestion: Dict[str, Any]) -> None:
        """渲染主動建議（含嚴重度、修復方案）"""
        ...
    
    @abstractmethod
    def display_agent_status(self, agents: list) -> None:
        """渲染多代理狀態儀表板"""
        ...
```

---

## 5. 並行與效能設計

### 5.1 Hierarchical Thread Model

```python
class SquadCoordinator(threading.Thread):
    """Mid-level: 管理單一任務的 Agent 小隊"""
    def __init__(self, squad_id: str, tasks: List[Task], bus: EventBus):
        super().__init__(daemon=True)
        self.squad_id = squad_id
        self.workers: List[AgentWorker] = []
        self.bus = bus
        self.max_agents = 4  # 全域上限

    def run(self):
        self.bus.emit(WorkflowEvent(EventType.SQUAD_PROPOSED, self.squad_id))
        
        # 並行啟動所有 Worker
        for task in self.tasks[:self.max_agents]:
            worker = AgentWorker(task=task, bus=self.bus)
            worker.start()
            self.workers.append(worker)
        
        # 等待所有 Worker 完成（含 TTL 保護）
        results = []
        for w in self.workers:
            w.join(timeout=w.capability.ttl_seconds)
            if w.is_alive():
                self.bus.emit(WorkflowEvent(EventType.AGENT_FAILED, w.agent_id,
                    data={"reason": "TTL exceeded"}))
                # 安全終止超時 Agent
            results.append(w.result)
        
        self.bus.emit(WorkflowEvent(EventType.SQUAD_COMPLETED, self.squad_id,
            data={"results": results}))
```

### 5.2 Circuit Breaker（熔斷器）

```python
class CircuitBreaker:
    """防止 Agent 無限重試"""
    def __init__(self, max_failures=3, cooldown_seconds=60):
        self.failure_count = 0
        self.max_failures = max_failures
        self.cooldown = cooldown_seconds
        self.state = "CLOSED"  # CLOSED → OPEN → HALF_OPEN
        self.last_failure_time = 0
    
    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.max_failures:
            self.state = "OPEN"
    
    def can_execute(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            elapsed = time.time() - self.last_failure_time
            if elapsed > self.cooldown:
                self.state = "HALF_OPEN"
                return True
            return False
        return True  # HALF_OPEN: 允許一次嘗試
```

### 5.3 死鎖預防
- Agent 間**禁止直接呼叫**，只能透過 Event Bus 發布事件
- 所有任務有 TTL（預設 5 分鐘），超時自動 Kill 並記錄 Audit Log
- Event Bus Queue 上限 1000 條，滿時丟棄最舊事件（Back Pressure）

---

## 6. 資安設計與威脅建模 (STRIDE)

| 威脅類型 | 攻擊向量 | 防禦措施 |
|---------|---------|---------|
| **Spoofing** | 偽裝高信任 Agent | CapabilityCard + UUID 身份驗證 |
| **Tampering** | 修改其他 Agent 輸出 | Event Bus 消息帶 HMAC 簽名 |
| **Repudiation** | 否認執行操作 | AuditLogger (L7) 全記錄 |
| **Info Disclosure** | 低信任讀取高信任上下文 | Session 隔離 + Tool 白名單 |
| **DoS** | 無限循環 Agent | TTL + Circuit Breaker + Max 4 |
| **Privilege Escalation** | Tester 嘗試 write_to_file | PermissionEngine 強制攔截 |
| **Prompt Injection** | 透過代碼注入惡意指令 | InputSanitizer (L1) 前置掃描 |

### 6.1 Agent 權限沙箱（與 PermissionEngine 整合）

```python
class AgentSandbox:
    """基於 CapabilityCard 的工具存取控制"""
    def __init__(self, card: CapabilityCard, permission_engine: PermissionEngine):
        self.card = card
        self.engine = permission_engine
    
    def can_use_tool(self, tool_name: str) -> bool:
        # 1. 白名單檢查
        if tool_name not in self.card.allowed_tools:
            return False
        # 2. 黑名單檢查
        if tool_name in self.card.forbidden_tools:
            return False
        # 3. PermissionEngine 風險評估
        risk = self.engine.get_risk_level(tool_name)
        return risk <= self.card.trust_level.value
```

---

## 7. AI 產品考量

### 7.1 Omniscient UX 原則
**「主動感知，按需介入，永不打擾」**

- **個性化**: 預設「專業、謙遜、主動但不煩人」，可透過設定調整介入頻率
- **繁體中文強制**: 所有 System Prompt 內建 `## 強制在地化：所有輸出必須使用繁體中文`
- **成本透明**: Agent Activity Dashboard 即時顯示每個 Agent 的 Token 消耗

### 7.2 動態 Squad 組合 UX

用戶輸入: `「幫我修這 5 個 bug」`
系統行為:
1. Omniscient Agent 分析 5 個 bug 的類型
2. 自動 spawn Squad: [Coder×2, Tester×1, Reviewer×1]
3. Side Panel 顯示 Squad 進度儀表板
4. 完成後 Reviewer 聚合結果並產出修復報告

### 7.3 Prompt 系統管理
- **位置**: `.ag_prompts/` 目錄（每個角色一個 `.md` 文件）
- **與 `PROMPT_LIBRARY.md` 的關係**: PROMPT_LIBRARY.md 紀錄設計理念，`.ag_prompts/` 存放實際運行的 System Prompt
- **載入順序**: `base.md` → `role_specific.md` → `task_override.md`

---

## 8. Event Bus 擴展（Phase 170 → 171）

### 8.1 新增 EventTypes

```python
class EventType(Enum):
    # Phase 170 (現有)
    TOOL_START = "tool_start"
    TOOL_END = "tool_end"
    MODEL_THINKING = "model_thinking"
    CHECKPOINT_SAVED = "checkpoint_saved"
    CONTEXT_COMPRESSED = "context_compressed"
    WORKFLOW_PAUSED = "workflow_paused"
    WORKFLOW_RESUMED = "workflow_resumed"
    ERROR = "error"
    
    # Phase 171 (新增)
    AGENT_SPAWNED = "agent_spawned"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    SQUAD_PROPOSED = "squad_proposed"
    SQUAD_COMPLETED = "squad_completed"
    SUGGESTION_READY = "suggestion_ready"
    CRISIS_DETECTED = "crisis_detected"
    INTERVENTION_TRIGGERED = "intervention_triggered"
    CIRCUIT_BREAKER_OPEN = "circuit_breaker_open"
    CIRCUIT_BREAKER_RESET = "circuit_breaker_reset"
```

---

## 9. 測試策略

### 9.1 Multi-Agent 測試
- **單元**: 每個 Agent 角色的 CapabilityCard 權限驗證
- **整合**: Coordinator 在 3 Agent 並行下的任務分配與聚合
- **壓力**: 4 Agent 同時運行，驗證 Event Bus 吞吐量
- **資安滲透**: 注入惡意 Agent 嘗試越權（Tester 呼叫 write_to_file）

### 9.2 Omniscient Agent 測試
- **模擬 IDE 事件**: Mock `workspace/status` MCP 回應
- **UX 響應時間**: Suggestion 在文件保存後 < 500ms
- **Token 效率**: L0 掃描攔截 90% 常見 Lint 錯誤

---

## 10. 執行波次 (Waves)

| Wave | 內容 | 新增/修改文件 | 風險 |
|------|------|-------------|------|
| **W1** | Event Bus 擴展 + CapabilityCard + AgentSandbox | `streaming.py`, `agent_identity.py`, `agent_sandbox.py` | 低 |
| **W2** | SquadCoordinator + AgentWorker 線程模型 + CircuitBreaker | `squad_coordinator.py`, `circuit_breaker.py` | 中 |
| **W3** | Omniscient Agent Core + 三層介入狀態機 | `omniscient/core.py`, `omniscient/suggestion_engine.py` | 中高 |
| **W4** | BaseRenderer + CLI Rich Renderer + Web Panel Bridge | `renderers/base.py`, `renderers/cli.py`, `renderers/web.py` | 中 |
| **W5** | Proactive Suggestion Engine + `.ag_prompts/` 系統 | `suggestion_engine.py`, `.ag_prompts/*.md` | 中 |
| **W6** | 整合測試 + 壓力測試 + 資安滲透測試 | `tests/test_multi_agent.py`, `tests/test_omniscient.py` | 低 |

---

## 11. 開放問題（已全部解決）

✅ ASSUMPTION A: (c) 雙端渲染 — 已確認
✅ ASSUMPTION B: (c) 批量 + 常駐 — 已確認
✅ ASSUMPTION C: (a) 結構化 Event — 已確認

**無剩餘阻塞問題，可直接進入 `/aa-plan 171`。**
