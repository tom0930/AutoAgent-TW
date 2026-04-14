# PLAN: Phase 125 — MCP Protocol Integration Layer (v2, Gap-Fixed)
# 讓子代理從「有大腦沒有手」升級為「有大腦 + 完整工具箱」
# 依據 p125mcp_ref.md 審查，修正版本：v1.9.1-beta

## 🎯 Phase 目標
為 AutoAgent-TW 子代理系統接入 Model Context Protocol (MCP) 標準，
使 OrchestrationCoordinator 中的子代理能夠動態調用外部工具
（GitHub API, Slack, 檔案系統, 自定義工具等）。

## 📊 Gap Analysis（參考 p125mcp_ref.md 評分 8.5/10 → 目標 9.5+/10）

| 缺口 | 嚴重度 | Wave | 原計畫 | 補強措施 |
|------|--------|------|--------|---------|
| G1: startup() 無並行連接 + 無 retry | 🔴 高 | 1 | ❌ 未涵蓋 | asyncio.gather + exponential backoff |
| G2: 無健康檢查機制 | 🔴 高 | 1 | ❌ 未涵蓋 | _health_check() + get_server_status() |
| G3: 工具發現無 filter + 無快取 | 🟡 中 | 1 | ❌ 未涵蓋 | capability filter + metadata cache |
| G4: 無內建 AutoAgent MCP Server | 🟡 中 | 1 | ❌ 未涵蓋 | FastMCP 內建 server（Phase 125.5 移至 Wave 1.5）|
| G5: 狀態機缺 tool_errors + ReAct 循環邊緣 | 🔴 高 | 2 | ❌ 未涵蓋 | conditional_edges + tool_errors 欄位 |
| G6: CLI 無 verbose/enable/install | 🟡 中 | 3 | ❌ 部分 | 新增 --verbose, install, enable 指令 |
| G7: Scheduler 無 graceful shutdown + periodic health check | 🔴 高 | 3 | ❌ 未涵蓋 | signal handler + 5min health task |
| G8: 依賴版本過舊 | 🟢 低 | Pre | ❌ 未涵蓋 | 升級至 mcp>=1.2.0, adapters>=0.2.0 |
| G9 : filesystem roots 限制 + 低權限執行 | 🔴 高 | 1 | ❌ 未涵蓋 | roots 配置，資安強化 |

---

## 📦 依賴安裝 (Pre-requisite) — 版本升級

```bash
pip install "mcp>=1.2.0" "langchain-mcp-adapters>=0.2.0"
```

`requirements.txt` 修改：
```diff
-mcp>=1.0.0
-langchain-mcp-adapters>=0.1.0
+mcp>=1.2.0                    # Streamable HTTP, MCP Tasks, Tool Search
+langchain-mcp-adapters>=0.2.0  # interceptor 注入 runtime state 支持
```

---

## 🌊 Wave 1: MCP 核心層 (Core Infrastructure) — 強化版

### Task 1.1: MCPClientManager（並行啟動 + Retry + 健康檢查）
**檔案**: `src/core/mcp/mcp_client.py` [NEW]

```python
"""
AutoAgent-TW MCP Client Manager v2
- asyncio.gather 並行啟動所有 server（避免單一 server 阻塞）
- Exponential backoff retry（3 次，30s timeout）
- 依設定的 roots 限制 filesystem 存取範圍
- get_server_status() 暴露給 Dashboard 與 Scheduler
"""
import asyncio
import json
import logging
from pathlib import Path
from typing import Any
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.tools import BaseTool
from src.core.mcp.registry import MCPToolRegistry

logger = logging.getLogger(__name__)

MAX_RETRIES: int = 3
CONNECT_TIMEOUT: float = 30.0
TOOL_CACHE_TTL_SEC: int = 300  # 工具列表快取 5 分鐘


class ServerStatus:
    """連接狀態快照，供 Dashboard 輪詢"""
    name: str
    connected: bool
    tool_count: int
    error: str | None
    last_health_check: float  # unix timestamp


class MCPClientManager:
    """
    生命週期管理器，負責：
    1. 從 .agents/mcp_servers.json 讀取配置（${VAR} 環境變數替換）
    2. asyncio.gather 並行啟動所有已啟用的 MCP Server
    3. 向 MCPToolRegistry 注冊所有工具（server_name::tool_name 命名空間）
    4. 提供健康狀態供 Dashboard 面板輪詢
    """
    def __init__(self, config_path: str = ".agents/mcp_servers.json"):
        self.config_path = Path(config_path)
        self.registry: MCPToolRegistry = MCPToolRegistry()
        self._client: MultiServerMCPClient | None = None
        self._status: dict[str, ServerStatus] = {}
        self._tool_cache: dict[str, list[BaseTool]] = {}
        self._cache_timestamp: float = 0.0

    async def startup(self) -> None:
        """並行啟動所有已啟用 server，單一失敗不影響其他"""
        config = self._load_config()
        enabled_servers = [s for s in config["servers"] if s.get("enabled", True)]

        # 並行連接所有 server（G1 補強）
        results = await asyncio.gather(
            *[self._connect_server_with_retry(s) for s in enabled_servers],
            return_exceptions=True
        )
        for server, result in zip(enabled_servers, results):
            if isinstance(result, Exception):
                logger.warning(f"[MCP] Server '{server['name']}' failed: {result}. Graceful degradation.")

    async def _connect_server_with_retry(self, server_cfg: dict) -> None:
        """單個 server 連接，含 exponential backoff（G1 補強）"""
        name = server_cfg["name"]
        for attempt in range(MAX_RETRIES):
            try:
                tools = await asyncio.wait_for(
                    self._do_connect(server_cfg), timeout=CONNECT_TIMEOUT
                )
                self.registry.register(name, tools)
                self._status[name] = ServerStatus(name=name, connected=True, tool_count=len(tools))
                logger.info(f"[MCP] '{name}' connected. {len(tools)} tools registered.")
                return
            except Exception as e:
                wait = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"[MCP] '{name}' attempt {attempt+1}/{MAX_RETRIES} failed: {e}. Retry in {wait}s.")
                await asyncio.sleep(wait)
        self._status[name] = ServerStatus(name=name, connected=False, error=str(e))

    async def _do_connect(self, cfg: dict) -> list[BaseTool]:
        """實際連接並獲取工具列表"""
        ...  # 使用 langchain_mcp_adapters 建立連接並回傳 tools

    async def shutdown(self) -> None:
        """優雅關閉所有連接（G7 補強）"""
        if self._client:
            await self._client.__aexit__(None, None, None)
        logger.info("[MCP] All connections closed gracefully.")

    def get_tools_for_agent(
        self,
        server_names: list[str] | None = None,
        capability_filter: str | None = None,
    ) -> list[BaseTool]:
        """
        取得工具列表（G3 補強）：
        - server_names: 指定 server 過濾
        - capability_filter: 如 'read'/'write'，按 tool name 前綴過濾
        - 工具列表帶快取（避免每次重新 list）
        """
        tools = (
            self.registry.get_server_tools(server_names)
            if server_names else
            self.registry.get_all_tools()
        )
        if capability_filter:
            tools = [t for t in tools if capability_filter in t.name]
        return tools

    def get_server_status(self) -> list[dict]:
        """回傳所有 server 的連接狀態（G2 補強），供 Dashboard/Scheduler 使用"""
        return [
            {
                "name": s.name,
                "connected": s.connected,
                "tool_count": s.tool_count,
                "error": s.error,
            }
            for s in self._status.values()
        ]

    async def health_check(self) -> dict[str, bool]:
        """
        定期健康檢查（G2 補強）：
        呼叫各 server 的 tools/list 驗證連接存活
        """
        results = {}
        for name, status in self._status.items():
            if status.connected:
                try:
                    await asyncio.wait_for(self._ping_server(name), timeout=5.0)
                    results[name] = True
                except Exception:
                    results[name] = False
                    self._status[name].connected = False
        return results

    async def _ping_server(self, server_name: str) -> None:
        """發送 tools/list 作為 ping 驗證連接存活"""
        ...

    def _load_config(self) -> dict:
        """讀取 mcp_servers.json，並替換 ${VAR} 環境變數"""
        import os, re
        raw = self.config_path.read_text(encoding="utf-8")

        def replace_env(m: re.Match) -> str:
            val = os.environ.get(m.group(1), "")
            if not val:
                logger.warning(f"[MCP] Env var '{m.group(1)}' not set!")
            return val

        return json.loads(re.sub(r"\$\{([^}]+)\}", replace_env, raw))
```

### Task 1.2: MCPToolRegistry（命名空間 + Capability 查詢）
**檔案**: `src/core/mcp/registry.py` [NEW]

```python
"""
MCPToolRegistry v2
- server_name::tool_name 命名空間防衝突
- get_server_tools() 按 server 過濾
- list_summary() 供 /aa-mcp list --verbose 使用（含 schema）
"""
from dataclasses import dataclass, field
from langchain_core.tools import BaseTool


@dataclass
class MCPToolRegistry:
    _tools: dict[str, BaseTool] = field(default_factory=dict)
    _tool_to_server: dict[str, str] = field(default_factory=dict)

    def register(self, server_name: str, tools: list[BaseTool]) -> None:
        for tool in tools:
            namespaced = f"{server_name}::{tool.name}"
            self._tools[namespaced] = tool
            self._tool_to_server[namespaced] = server_name

    def get_all_tools(self) -> list[BaseTool]:
        return list(self._tools.values())

    def get_server_tools(self, server_names: list[str]) -> list[BaseTool]:
        return [t for k, t in self._tools.items() if self._tool_to_server[k] in server_names]

    def list_summary(self, verbose: bool = False) -> list[dict]:
        """
        verbose=False: [{name, server, description}]
        verbose=True:  + input_schema, output_schema（G6 補強）
        """
        result = []
        for key, tool in self._tools.items():
            entry = {
                "name": key,
                "server": self._tool_to_server[key],
                "description": tool.description,
            }
            if verbose:
                entry["input_schema"] = getattr(tool, "args_schema", None)
            result.append(entry)
        return result
```

### Task 1.3: MCP Server 配置檔（含 roots 安全限制）
**檔案**: `.agents/mcp_servers.json` [NEW]

```json
{
  "_comment": "AutoAgent-TW MCP Server 配置 v2。API Keys 使用 ${VAR_NAME} 環境變數。filesystem 使用 roots 限制存取範圍（G9 安全加強）",
  "servers": [
    {
      "name": "filesystem",
      "transport": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem"],
      "roots": ["./src", "./scripts", "./.planning", "./docs"],
      "env": {},
      "enabled": true,
      "description": "本地檔案系統讀寫（限 roots 目錄）"
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
    },
    {
      "name": "autoagent-internal",
      "transport": "stdio",
      "command": "python",
      "args": ["scripts/mcp_internal_server.py"],
      "env": {},
      "enabled": true,
      "description": "AutoAgent-TW 內建工具（排程查詢、記憶庫、狀態報告）"
    }
  ]
}
```

### Task 1.4: 內建 AutoAgent MCP Server（G4 新增）
**檔案**: `scripts/mcp_internal_server.py` [NEW]

```python
"""
AutoAgent-TW 內建 MCP Server（G4 補強）
使用 FastMCP 快速暴露 AutoAgent-TW 特有功能為 MCP 工具：
- get_schedule(): 查詢當前排程任務
- get_phase_status(): 查詢當前 Phase 進度
- get_status_report(): 取得系統狀態摘要
所有 AutoAgent-TW 工具走 MCP 統一協議，Phase 126+ 也可複用此架構
"""
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("autoagent-internal")

@mcp.tool()
def get_phase_status() -> dict:
    """查詢當前 Phase 執行進度與狀態"""
    ...

@mcp.tool()
def get_schedule_tasks() -> list:
    """查詢 scheduler_daemon 目前的排程任務列表"""
    ...

@mcp.tool()
def create_status_report(phase: str) -> str:
    """為指定 Phase 生成狀態報告文字"""
    ...

if __name__ == "__main__":
    mcp.run()
```

### Task 1.5: `__init__.py`
**檔案**: `src/core/mcp/__init__.py` [NEW]

---

## 🌊 Wave 2: Coordinator 升級（ReAct 循環 + 修正狀態機）

### Task 2.1: coordinator.py 升級（加入條件邊緣 ReAct）
**檔案**: `src/core/orchestration/coordinator.py` [MODIFY]

```python
from langgraph.prebuilt import ToolNode, tools_condition
from src.core.mcp import MCPClientManager

class OrchestrationCoordinator:
    def _build_graph(self) -> StateGraph:
        builder = StateGraph(AgentState)
        builder.add_node("supervisor", self.supervisor_node)
        builder.add_node("execute_tasks", self.execute_tasks_node)
        builder.add_node("aggregator", self.aggregator_node)

        if self.mcp_manager:
            tools = self.mcp_manager.registry.get_all_tools()
            self.tool_node = ToolNode(tools)
            builder.add_node("tools", self.tool_node)

            # G5 補強：ReAct 條件邊緣（tool 呼叫後可回到 supervisor 多輪推理）
            builder.add_conditional_edges(
                "execute_tasks",
                tools_condition,  # 若 last message 有 tool_calls → tools node，否則 → aggregator
            )
            builder.add_conditional_edges(
                "tools",
                lambda state: "supervisor" if self._needs_more_reasoning(state) else "aggregator"
            )
        else:
            builder.add_edge("execute_tasks", "aggregator")

        builder.add_edge(START, "supervisor")
        builder.add_edge("supervisor", "execute_tasks")
        builder.add_edge("aggregator", END)
        return builder.compile()

    def _needs_more_reasoning(self, state: AgentState) -> bool:
        """判斷是否需要繼續推理（避免無限循環，最多 5 輪）"""
        tool_use_count = len(state.get("mcp_tools_used", []))
        return tool_use_count < 5 and bool(state.get("tool_errors"))
```

### Task 2.2: AgentState 補強（G5 新增欄位）
**檔案**: `src/core/state.py` [MODIFY]

```python
# 新增欄位（在原始 TypedDict 基礎上）
mcp_tools_used: list[str]       # 已調用工具名稱列表
tool_outputs: list[dict]         # 工具調用成功結果
tool_errors: list[dict]          # 工具調用失敗記錄（G5 新增）
pending_tasks: list[str]         # 待執行子任務（用於多輪循環追蹤）
interceptor_context: dict        # langchain-mcp-adapters interceptor 注入 context
```

---

## 🌊 Wave 3: CLI + Dashboard + Scheduler（完整運維體驗）

### Task 3.1: aa_mcp.py CLI（G6 擴展）
**檔案**: `scripts/aa_mcp.py` [NEW]

```bash
# 基本指令（原計畫）
python scripts/aa_mcp.py list                              # 列出所有工具
python scripts/aa_mcp.py list --verbose                    # G6: 含 input/output schema
python scripts/aa_mcp.py status                            # 顯示連接狀態
python scripts/aa_mcp.py logs [--server <name>] [--n 50]  # G6: 按 server filter

# 工具測試
python scripts/aa_mcp.py test <server> <tool> '<json_args>'  # JSON 輸入

# G6 新增：安裝/啟用管理
python scripts/aa_mcp.py install <server_name>             # 自動 npm install + 更新配置
python scripts/aa_mcp.py enable <server_name>              # 更新 enabled:true + 重連
python scripts/aa_mcp.py disable <server_name>             # 更新 enabled:false + 斷連
```

### Task 3.2: Dashboard MCP 面板增強（G6 補強）
**檔案**: `.agents/skills/status-notifier/templates/status.html` [MODIFY]

新增 MCP Servers 面板卡片，顯示：
- 各 server 連接狀態（🟢/🔴 + 錯誤訊息）
- 可用工具總數
- **最近 5 次工具呼叫歷史**（tool_name + success/fail + latency ms）
- 警告標紅：連接失敗或錯誤率 > 10% 的 server
- stdio 進程 CPU/Memory 監控指標

### Task 3.3: Scheduler Daemon 整合（G7 完整 graceful shutdown）
**檔案**: `scripts/scheduler_daemon.py` [MODIFY]

```python
import signal, asyncio

async def main():
    mcp_manager = MCPClientManager()
    # G7: 非阻塞啟動 MCP
    mcp_task = asyncio.create_task(mcp_manager.startup())

    # G7: Graceful shutdown signal handler
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown(mcp_manager)))

    # G7: Periodic health check every 5 minutes
    async def periodic_health():
        while True:
            await asyncio.sleep(300)
            results = await mcp_manager.health_check()
            logger.info(f"[MCP Health] {results}")

    asyncio.create_task(periodic_health())
    await mcp_task  # 等待初始連接完成

async def shutdown(mcp_manager: MCPClientManager):
    await mcp_manager.shutdown()
    asyncio.get_event_loop().stop()
```

### Task 3.4: requirements.txt 版本升級
**檔案**: `requirements.txt` [MODIFY]
```
mcp>=1.2.0
langchain-mcp-adapters>=0.2.0
```

---

## 🔒 資安設計（完整 STRIDE — G9 補強）

| 威脅 | 描述 | 防護措施 |
|------|------|---------|
| **Spoofing** | 偽造 MCP Server 回應 | JSON Schema 驗證工具輸出 |
| **Tampering** | 注入惡意工具指令 | Permission Engine LEVEL 3+，ToolNode 前加 whitelist filter |
| **Info Disclosure** | MCP Server 洩露 API Key | ${VAR} 環境變數替換，絕不明文配置 |
| **Elevation of Privilege** | stdio 子進程提升權限 | **filesystem roots 限制存取範圍（G9 新增）**，低權限 user 運行 daemon |
| **DoS** | 惡意工具 CPU/Memory 佔用 | npx 子進程超時殺死，stdio 進程資源監控 |

---

## ✅ UAT 驗證指標（原有 6 項 + 新增 4 項）

| 測試 | 期望結果 |
|------|---------|
| `aa_mcp.py list` | filesystem server ≥ 5 工具 |
| `aa_mcp.py list --verbose` | 顯示 input_schema |
| `aa_mcp.py test filesystem read_file '{"path": "README.md"}'` | 正確讀出內容 |
| Coordinator 調用工具 | `review_reports` 含 `mcp_tools_used` 欄位 |
| Dashboard 面板 | MCP 卡片顯示 🟢 狀態 + 工具調用歷史 |
| 連接失敗回退 | 優雅降級，不崩潰 |
| API Key 安全 | mcp_servers.json 無明文 token |
| **[G1]** startup 並行測試 | 同時啟動 3 個 server，總時間 < 最慢+5s |
| **[G5]** ReAct 循環測試 | 工具失敗後 supervisor 重試（最多 5 輪）|
| **[G7]** Graceful shutdown | Ctrl+C 後所有 MCP 連接正確關閉 |
| **[G9]** roots 安全測試 | 嘗試讀取 roots 外路徑時返回 Permission Error |

---

## 📊 執行估時（含 Gap 修正：+30-45 分鐘）

| Wave | 任務 | 原估時 | 修正估時 |
|------|------|--------|---------|
| Wave 1 | MCP 核心層（含 retry/health/內建 server） | ~45 min | **~75 min** |
| Wave 2 | Coordinator（ReAct 條件邊緣 + state 欄位） | ~30 min | **~40 min** |
| Wave 3 | CLI（verbose/install）+ Dashboard + Scheduler graceful shutdown | ~45 min | **~60 min** |
| **合計** | | **~2h** | **~2h45min** |
