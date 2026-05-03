# Phase 171 Ultimate v2.1: Multi-Agent Coordination & Omniscient Assistant
## AutoAgent-TW 多代理協作架構 + 全能助手 (工業增強版)

**版本**: v2.1 (Ultimate Phase — Production Ready)
**日期**: 2026-05-03
**設計者**: Tom (Senior Architect, AI Product Expert, Security Engineer)
**決策確認**: A=(c), B=(c), C=(a) | W7 Gray Rollout: YES | Sensitivity: Balanced

---

## 1. 核心優化亮點 (v2.1)

### 1.1 Meta-Coordinator (全局調度器)
- **職責**: 輕量級資源管家。負責跨 Squad 的優先序排序與全域資源分配（CPU/Memory/Token）。
- **資源動態調整**: 若系統負載過高，自動延遲 Low-Priority 背景監控任務。

### 1.2 Event Priority Queue (高優先級事件隊列)
- **核心機制**: Event Bus 升級為支援優先級的隊列。
- **優先級定義**: `CRISIS` (最高) > `USER_INPUT` > `TOOL_END` > `LOG` (最低)。
- **效益**: 確保在大量日誌湧入時，危機事件能第一時間被渲染器處理。

### 1.3 Evidence-Based Omniscient Agent
- **幻覺抑制**: 所有 Suggestion 必須附帶來自 Phase 170 `evidence_memory.py` 的來源連結。
- **User Feedback Loop**: 支援 👍 / 👎 反饋。系統記錄反饋至記憶庫，動態調整該類建議的觸發閾值。
- **L0 效能提升**: 引入 `tree-sitter` 進行 AST 解析（優先級高於正則），更精準地識別代碼異味。

---

## 2. 系統架構與資料模型

### 2.1 CapabilityCard (身份與能力模型)
```python
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict

class AgentRole(Enum):
    COORDINATOR = "coordinator"
    META_COORDINATOR = "meta_coordinator"
    CODER = "coder"
    TESTER = "tester"
    REVIEWER = "reviewer"
    OMNISCIENT = "omniscient"

class TrustLevel(Enum):
    LOW = 1      # 唯讀
    MEDIUM = 2   # 安全執行
    HIGH = 3     # 修改文件
    ADMIN = 4    # 系統配置

@dataclass
class CapabilityCard:
    agent_id: str
    role: AgentRole
    trust_level: TrustLevel
    allowed_tools: List[str]
    model_preference: str = "flash"
    max_tokens_per_task: int = 8000
    learning_rate: float = 0.1               # 反饋學習率
    resource_limits: Dict[str, int] = field(default_factory=lambda: {"memory_mb": 256})
    priority: int = 10                       # 預設優先權 (越小越高)
```

---

## 3. 執行波次 (Waves v2.1)

| Wave | 名稱 | 核心任務 | 風險 |
|------|------|---------|------|
| **W1** | **Foundation+** | 擴展 Event Bus (Priority Queue) + CapabilityCard + Pre-flight Security Scan | 低 |
| **W2** | **Squad & Meta** | 實作 Meta-Coordinator 調度邏輯 + Squad Thread Pool + Exponential Backoff | 中 |
| **W3** | **Omniscient Core** | 實作三層介入狀態機 + Evidence 整合 + Feedback Loop 存儲層 | 中 |
| **W4** | **Dual Renderers** | 實作 BaseRenderer + CLI (rich) + Web Bridge (WebSocket) | 中 |
| **W5** | **Suggestion 2.0** | L0 (Tree-sitter) + L1/L2 模型路由 + `.ag_prompts/` 繁中庫 | 中高 |
| **W6** | **Telemetry** | 指令 `/aa-dashboard` + 指標收集 (Squad Success Rate, Token Cost) | 低 |
| **W7** | **Ship (Gray)** | Feature Flags 分批開放 + Canary 測試 + 自動 Rollback 機制 | 低 |

---

## 4. 資安防禦與可靠性

### 4.1 Pre-flight Security Scan
- **流程**: 在 Agent 載入 System Prompt 之後、發送給 LLM 之前，先由 `InputSanitizer` 進行一次「提示詞注入」掃描，防止 Prompt Leaking 或被惡意代碼竄改意圖。

### 4.2 Agent Quarantine (代理隔離池)
- **機制**: 連續失敗達 5 次的 Agent 會被標記為 `QUARANTINED`。
- **恢復**: 必須由用戶執行 `/aa-rehab [agent_id]` 進行手動審核或重置。

---

## 5. 結論
Phase 171 Ultimate v2.1 定位為**高度自動化且可量化的生產級系統**。透過 Meta-Coordinator 與 Telemetry，我們不僅能運行多代理，還能「知道它們跑得好不好」以及「花了多少錢」。
