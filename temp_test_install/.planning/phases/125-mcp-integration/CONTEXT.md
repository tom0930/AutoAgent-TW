# CONTEXT: Phase 125 — MCP Protocol Integration Layer v2 (Gap-Fixed)

## 🎯 核心目標
讓 AutoAgent-TW 子代理從「有大腦沒有手」（Phase 124 遺留問題）升級為
「有大腦 + 完整工具箱」，以 MCP 標準協議橋接所有外部工具。

---

## ✅ 最終技術決策（與 p125mcp_ref.md 比對後確認）

### 1. 技術選型
- **MCP 驅動**: `langchain-mcp-adapters>=0.2.0` + `mcp>=1.2.0`（升級版本以支援 Streamable HTTP、MCP Tasks）
- **理由**: 官方出品，BaseTool 直接餵給 ToolNode，工程量最低、相容性最高

### 2. 啟動策略
- **並行連接**: `asyncio.gather()` 同時啟動所有 server，單一失敗不阻塞
- **重試機制**: Exponential backoff（3 次，1/2/4 秒間隔），30 秒 timeout
- **優雅降級**: 部分 server 失敗 → 只移除該 server 工具，系統繼續運行

### 3. 工具命名空間
- 格式：`server_name::tool_name`（如 `filesystem::read_file`）
- **理由**: 多 Server 同名工具防衝突，且 CLI `list` 輸出可快速識別來源

### 4. 子代理推理模型
- **ReAct 條件邊緣**：`execute_tasks → tools → supervisor (if needs_more_reasoning) → aggregator`
- 最大推理輪次：5（防止無限循環）
- **理由**: 真實 Agent 任務常需要工具結果後重新規劃，純線性流程不夠

### 5. 資安邊界
- `filesystem` server 使用 **roots 限制**（只允許 `./src`, `./scripts`, `./.planning`, `./docs`）
- Permission Engine **LEVEL 3+** 才能觸發外部 MCP 工具調用
- 所有 API Key 使用 `${VAR_NAME}` 環境變數替換，**configfile 內不含明文**

### 6. 內建 AutoAgent MCP Server（新決策）
- 新增 `scripts/mcp_internal_server.py`（FastMCP）
- 暴露：`get_phase_status()`, `get_schedule_tasks()`, `create_status_report()`
- **理由**: AutoAgent-TW 自身功能也走 MCP 統一協議，Phase 126+ 可直接複用

### 7. Scheduler 整合
- 非阻塞啟動：`asyncio.create_task(mcp_manager.startup())`
- Graceful shutdown：signal handler → `await mcp_manager.shutdown()`
- Periodic health check：每 5 分鐘 ping 各 server

---

## 📁 新增/修改檔案清單

| 檔案 | 動作 | Wave |
|------|------|------|
| `src/core/mcp/__init__.py` | NEW | 1 |
| `src/core/mcp/mcp_client.py` | NEW | 1 |
| `src/core/mcp/registry.py` | NEW | 1 |
| `.agents/mcp_servers.json` | NEW | 1 |
| `scripts/mcp_internal_server.py` | NEW | 1 |
| `src/core/orchestration/coordinator.py` | MODIFY | 2 |
| `src/core/state.py` | MODIFY | 2 |
| `scripts/aa_mcp.py` | NEW | 3 |
| `.agents/skills/status-notifier/templates/status.html` | MODIFY | 3 |
| `scripts/scheduler_daemon.py` | MODIFY | 3 |
| `requirements.txt` | MODIFY | Pre |

---

## 🏗️ 架構圖

```
┌─────────────────── AutoAgent-TW Sub-Agent Orchestration ──────────────────┐
│                                                                             │
│  /aa-orchestrate                                                            │
│       ↓                                                                     │
│  OrchestrationCoordinator (LangGraph)                                       │
│  ┌─────────┐    ┌───────────────┐    ┌──────────────┐                      │
│  │supervisor│→→→│ execute_tasks │→→→ │ ToolNode     │ ←─ MCP Tools         │
│  └─────────┘    └───────────────┘    │  (ReAct loop)│                      │
│       ↑                              └──────┬───────┘                      │
│       └──────────(needs_more_reasoning)──────┘                              │
│                          ↓                                                  │
│                    ┌──────────┐                                             │
│                    │aggregator│→→→ result                                   │
│                    └──────────┘                                             │
│                                                                             │
│  MCPClientManager                                                           │
│  ├─ filesystem (stdio, roots limited)  🟢                                  │
│  ├─ github     (stdio, disabled)       ⚪                                  │
│  ├─ slack      (stdio, disabled)       ⚪                                  │
│  └─ autoagent-internal (FastMCP)       🟢                                  │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ⏱️ 估時
- **總工程量**: ~2h45min（原 2h + gap fix 額外 45min）
- **前置**: `npm` 環境需可用（npx）；Windows 開發機確認 Node.js 安裝
