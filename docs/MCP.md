# AI Harness MCP Hub 使用指南

## 概述

MCP (Model Context Protocol) Hub 是 AI Harness 的多伺服器路由中心。

## 支援的傳輸類型

| 類型 | 說明 | 用途 |
|------|------|------|
| stdio | 標準輸入/輸出 | 本地 MCP 伺服器 |
| http | HTTP 請求 | 遠程 MCP 服務 |
| websocket | WebSocket | 即時雙向通訊 |

## 配置

在 `config/mcp_servers.json` 中配置伺服器：

```json
{
  "servers": {
    "my-server": {
      "name": "My MCP Server",
      "type": "stdio",
      "command": "node",
      "args": ["server.js"],
      "enabled": true
    }
  }
}
```

## 使用方式

```python
from src.core.mcp import MCPHub

# 初始化
hub = MCPHub(config_path="config/mcp_servers.json")

# 列出伺服器
for server in hub.list_servers():
    print(f"{server['name']} ({server['type']})")

# 列出 Tools
for tool in hub.list_tools():
    print(f"  {tool['name']}: {tool['description']}")

# 呼叫 Tool
result = await hub.call_tool(MCPToolCall(
    tool_name="tool-name",
    arguments={"param": "value"}
))
```

---

*最後更新：2026-04-23*
