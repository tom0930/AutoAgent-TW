# Orchestration - 子代理協調系統

**檔案：** `src/core/orchestration/coordinator.py` | **狀態：** ✅ Phase 3 內建

## 概述

`OrchestrationCoordinator` 是 AI Harness 的核心協調器，整合 LangGraph StateGraph、ReAct 推理迴圈、以及 MCP ToolNode，實現複雜任務的自動分解與並行執行。

## 架構

```
使用者輸入
    │
    ▼
┌──────────────────────┐
│   Supervisor Node    │  ← 分析任務，拆解為子任務
└──────────┬───────────┘
           ▼
┌──────────────────────┐
│  Execute Tasks Node  │  ← 為每個子任務啟動 AgentProcess
└──────────┬───────────┘
           ▼
      ┌─────────┐
      │ 有 MCP  │───┐
      │  工具？  │   │
      └─────────┘   ▼
           │   ┌─────────────────┐
           │   │  MCP Tools Node │  ← ToolNode(tools)
           │   │  (LangGraph)    │
           │   └────────┬────────┘
           │            ▼
           │   ┌─────────────────┐
           └──►│  ReAct Router   │──► 回 Supervisor / 結束
               │(should_continue) │
               └─────────────────┘
           │ (無 MCP 工具)
           ▼
┌──────────────────────┐
│   Aggregator Node    │  ← 匯總所有結果
└──────────┬───────────┘
           ▼
      任務完成
```

## 核心類別

### OrchestrationCoordinator

```python
from src.core.orchestration import OrchestrationCoordinator

orch = OrchestrationCoordinator(thread_id="my-task-001")
result = orch.run("建立 README 並生成 requirements.txt")
```

**主要方法：**
- `run(task_prompt: str)` — 同步執行協調流程
- `run_async(task_prompt: str)` — 非同步執行協調流程
- `_ensure_graph()` — 延遲建構 LangGraph（首次執行時）

### AgentProcess

```python
from src.core.orchestration import AgentProcess

p = AgentProcess(
    task_name="生成報告",
    parent_id="orchestrator-001",
    budget_tokens=10000,
    risk_limit=3,
)
p.spawn(["python", "agent.py", "--task", "生成報告"])
p.update_progress(50, "任務進行中")
p.terminate()
```

**AgentProcess 狀態機：**
```
pending → running → completed
              └→ error
              └→ killed (timeout)
```

## MCP 整合

協調器支援 MCP 工具生態：
- 透過 `MCPClientManager` 發現可用工具
- LangGraph `ToolNode` 包裝工具
- ReAct 路由器判斷是否需要回到 Supervisor

## 安全模型

- **子代理超時**：每個 AgentProcess 可設定 `budget_tokens`
- **風險等級**：每個任務有 `risk_limit` 控制
- **隔離執行**：子代理在獨立的 subprocess 中執行，透過 Win32 Job Object 隔離
- **清理機制**：`atexit` 鉤子確保所有子代理在主程式結束時被終止

## 與 OpenClaw 對齊

| OpenClaw 功能 | autoagent-TW 對應 | 狀態 |
|---------------|------------------|------|
| `sessions_spawn` | `AgentProcess.spawn()` | ✅ |
| `subagents` | `_ACTIVE_SUBAGENTS` registry | ✅ |
| `LangGraph` 整合 | `OrchestrationCoordinator` | ✅ |

---

*最後更新：2026-04-23*
