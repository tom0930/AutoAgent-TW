# PLAN: Phase 125 — MCP Protocol Integration Layer
# 讓子代理從「有大腦沒有手」升級為「有大腦 + 完整工具箱」
# 版本: v1.9.1-alpha

## 🎯 Phase 目標
為 AutoAgent-TW 子代理系統接入 Model Context Protocol (MCP) 標準，
使 OrchestrationCoordinator 中的子代理能夠動態調用外部工具
（GitHub API, Slack, 檔案系統, 自定義工具等）。

---

## 📦 依賴安裝 (Pre-requisite)
```bash
pip install mcp>=1.0.0 langchain-mcp-adapters>=0.1.0
```
- `requirements.txt` 需新增上述兩行

---

## 🌊 Wave 1: MCP 核心層 (Core Infrastructure)
**目標**: 建立通訊核心與工具發現機制

### Task 1.1: 建立 MCP Client 核心
**檔案**: `src/core/mcp/mcp_client.py` [NEW]
```python
"""
AutoAgent-TW MCP Client
支援 stdio / SSE 兩種傳輸模式
使用 langchain-mcp-adapters 橋接 LangGraph
"""
import asyncio
from typing import Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from src.core.mcp.registry import MCPToolRegistry


class MCPClientManager:
    """
    生命週期管理器，負責：
    1. 從 .agents/mcp_servers.json 讀取配置
    2. 初始化 MultiServerMCPClient 連接
    3. 向 MCPToolRegistry 注册所有工具
    """
    def __init__(self, config_path: str = ".agents/mcp_servers.json"):
        self.config_path = config_path
        self.registry: MCPToolRegistry = MCPToolRegistry()
        self._client: MultiServerMCPClient | None = None

    async def startup(self) -> None:
        """啟動所有 MCP 連接並填充工具註冊表"""
        ...

    async def shutdown(self) -> None:
        """優雅關閉所有 MCP 連接"""
        ...

    def get_tools_for_agent(self, server_names: list[str] | None = None) -> list:
        """供 Coordinator 節點調用，取得指定 server 的工具列表"""
        ...
```

### Task 1.2: 建立 MCP 工具註冊中心
**檔案**: `src/core/mcp/registry.py` [NEW]
```python
"""
MCPToolRegistry: 統一工具命名空間
避免不同 server 工具名稱衝突
實現 tool_name -> server_name 映射
"""
from dataclasses import dataclass, field
from langchain_core.tools import BaseTool


@dataclass
class MCPToolRegistry:
    _tools: dict[str, BaseTool] = field(default_factory=dict)
    _tool_to_server: dict[str, str] = field(default_factory=dict)

    def register(self, server_name: str, tools: list[BaseTool]) -> None:
        """以 server_name::tool_name 命名空間注册工具，避免衝突"""
        ...

    def get_all_tools(self) -> list[BaseTool]:
        """回傳所有已注册工具，供 LangGraph 節點使用"""
        ...

    def get_server_tools(self, server_name: str) -> list[BaseTool]:
        """按 Server 過濾工具"""
        ...

    def list_summary(self) -> list[dict]:
        """供 /aa-mcp list 指令使用，回傳工具摘要"""
        ...
```

### Task 1.3: MCP Server 配置檔
**檔案**: `.agents/mcp_servers.json` [NEW]
```json
{
  "_comment": "AutoAgent-TW MCP Server 配置。API Keys 使用環境變數替換語法 ${VAR_NAME}",
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "."],
      "env": {},
      "enabled": true,
      "description": "本地檔案系統讀寫"
    },
    {
      "name": "github",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}" },
      "enabled": false,
      "description": "GitHub PR/Issue/Repo 操作"
    },
    {
      "name": "slack",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-slack"],
      "env": { "SLACK_BOT_TOKEN": "${SLACK_BOT_TOKEN}" },
      "enabled": false,
      "description": "Slack 訊息發送"
    }
  ]
}
```

### Task 1.4: __init__.py 模組化
**檔案**: `src/core/mcp/__init__.py` [NEW]
```python
from src.core.mcp.mcp_client import MCPClientManager
from src.core.mcp.registry import MCPToolRegistry

__all__ = ["MCPClientManager", "MCPToolRegistry"]
```

---

## 🌊 Wave 2: Coordinator 升級 (LangGraph Integration)
**目標**: 讓 OrchestrationCoordinator 的子代理能動態調用 MCP 工具

### Task 2.1: 升級 coordinator.py
**檔案**: `src/core/orchestration/coordinator.py` [MODIFY]

核心變更：
1. `__init__` 接受可選的 `MCPClientManager`
2. `execute_tasks_node` 不再只是 `echo`，改為調用 LangGraph 工具節點
3. 新增 `tool_node` (ToolNode from langgraph.prebuilt) 作為工具執行層

```python
# 新增導入
from langgraph.prebuilt import ToolNode
from src.core.mcp import MCPClientManager

class OrchestrationCoordinator:
    def __init__(self, thread_id: str = "orchestrator-001",
                 mcp_manager: MCPClientManager | None = None):
        self.thread_id = thread_id
        self.mcp_manager = mcp_manager
        self.tool_node: ToolNode | None = None
        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("execute_tasks", self.execute_tasks_node)

        # NEW: MCP 工具執行節點 (僅在 mcp_manager 存在時啟用)
        if self.mcp_manager:
            tools = self.mcp_manager.registry.get_all_tools()
            self.tool_node = ToolNode(tools)
            builder.add_node("tools", self.tool_node)
            builder.add_edge("execute_tasks", "tools")
            builder.add_edge("tools", "aggregator")
        else:
            builder.add_edge("execute_tasks", "aggregator")

        builder.add_node("aggregator", self.aggregator_node)
        builder.add_edge(START, "supervisor")
        builder.add_edge("aggregator", END)
        return builder.compile()
```

### Task 2.2: 更新 AgentState (state.py)
**檔案**: `src/core/state.py` [MODIFY]
- 新增 `mcp_tools_used: list[str]` 欄位，追蹤本次執行調用了哪些 MCP 工具
- 新增 `tool_outputs: list[dict]` 欄位，儲存工具調用結果

---

## 🌊 Wave 3: CLI + Dashboard 整合 (User Experience)
**目標**: `/aa-mcp` 指令 + Dashboard 面板

### Task 3.1: aa_mcp.py CLI 工具
**檔案**: `scripts/aa_mcp.py` [NEW]
```
用法:
  python scripts/aa_mcp.py list                     列出所有工具
  python scripts/aa_mcp.py test <server> <tool>     測試指定工具
  python scripts/aa_mcp.py status                   顯示連接狀態
  python scripts/aa_mcp.py logs [n]                 查看最近 n 條日誌
```

### Task 3.2: Dashboard MCP 狀態面板
**檔案**: `.agents/skills/status-notifier/templates/status.html` [MODIFY]
- 新增「MCP Servers」面板卡片，顯示：
  - 各 server 連接狀態（🟢/🔴）
  - 可用工具總數
  - 本次 session 工具調用次數

### Task 3.3: scheduler_daemon 整合
**檔案**: `scripts/scheduler_daemon.py` [MODIFY]
- 啟動時自動初始化 `MCPClientManager` (非阻塞)
- 關閉時呼叫 `MCPClientManager.shutdown()` 優雅清理

### Task 3.4: 更新 requirements.txt
**檔案**: `requirements.txt` [MODIFY]
```
mcp>=1.0.0
langchain-mcp-adapters>=0.1.0
```

---

## 🔒 資安設計 (STRIDE Analysis)
| 威脅 | 描述 | 防護措施 |
|------|------|---------|
| **Spoofing** | 偽造 MCP Server 回應 | JSON Schema 驗證工具輸出 |
| **Tampering** | 注入惡意工具指令 | Permission Engine LEVEL 3+ 才能調用外部 MCP |
| **Info Disclosure** | MCP Server 洩露 API Key | 環境變數替換，絕不明文寫入配置 |
| **Elevation of Privilege** | stdio 子進程提升權限 | MCP 進程以非提升權限運行 |

---

## ✅ UAT 驗證指標 (Acceptance Criteria)

| 測試 | 期望結果 |
|------|---------|
| `aa_mcp.py list` | 顯示 filesystem server 的至少 5 個工具 |
| `aa_mcp.py test filesystem read_file {"path": "README.md"}` | 正確讀出 README 內容 |
| Coordinator 調用工具 | `review_reports` 中包含 `mcp_tools_used` 欄位 |
| Dashboard 面板 | MCP Servers 卡片顯示正確連接狀態 |
| 連接失敗回退 | server 無法連接時，系統降級但不崩潰 |
| API Key 安全 | `mcp_servers.json` 中不含任何明文 token |

---

## 📊 執行估時
| Wave | 任務 | 估時 |
|------|------|------|
| Wave 1 | MCP 核心層 (3 個新檔 + 1 配置) | ~45 min |
| Wave 2 | Coordinator 升級 (2 個改動) | ~30 min |
| Wave 3 | CLI + Dashboard + 整合 (4 個改動) | ~45 min |
| **合計** | | **~2h** |
