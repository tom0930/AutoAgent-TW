# Phase 125 Research: MCP Protocol Integration Layer

## 🔍 現狀差距分析

### 當前架構限制
Phase 124 完成了 Sub-Agent 引擎核心，但子代理「能思考卻不能行動」：
- 外部工具整合全部硬編碼（Git, Slack, REST API 各自獨立腳本）
- 子代理無法動態調用外部工具
- `OrchestrationCoordinator` 內部任務只能 `echo` 類型操作

### MCP (Model Context Protocol) 概覽
Anthropic 的開放標準協議，讓 LLM 以統一方式與外部工具溝通：
- **傳輸層**: stdio（本地進程）/ HTTP SSE（遠端服務）
- **核心 JSON-RPC**: `tools/list`, `tools/call`, `resources/list`, `resources/read`
- **Python SDK**: `mcp>=1.0.0` (官方)
- **langchain-mcp-adapters**: 將 MCP tools 轉換為 LangChain Tool 格式（已可與 LangGraph 節點整合）

## 🏗️ 技術選型評估

### Option A: 純官方 MCP SDK（手動整合）
- **優點**: 最靈活，完全控制協議行為
- **缺點**: 需要手動實現 stdio/SSE 連接邏輯，與 LangGraph 整合需要自己寫 adapter
- **工程量**: 2-3 天

### Option B: langchain-mcp-adapters（推薦 ✅）
- **優點**: 官方出品，直接產生 `@tool` 格式，可立即插入 LangGraph 節點
- **缺點**: 略高層抽象，但缺口極小
- **工程量**: 0.5-1 天
- **依賴**: `langchain-mcp-adapters>=0.1.0`, `mcp>=1.0.0`

### Option C: Windows-MCP（系統控制）
- **優點**: 本地 GUI 控制
- **缺點**: Windows 特定，不在本 Phase 範圍（留給 Phase 126）

**決策：採用 Option B (langchain-mcp-adapters)** — 與現有 LangGraph 架構完美銜接。

## 📦 核心依賴
```
mcp>=1.0.0
langchain-mcp-adapters>=0.1.0
```

## 🌐 支援的 MCP Server（初期目標）
| Server | 用途 | 傳輸 |
|--------|------|------|
| `@modelcontextprotocol/server-filesystem` | 檔案讀寫操作 | stdio |
| `@modelcontextprotocol/server-github` | GitHub PR/Issue/Repo | stdio |
| `@anthropic/mcp-server-slack` | Slack 訊息發送 | stdio |
| `mcp-server-linear` | Linear 任務追蹤 | stdio |
| Custom Python MCP Server | AutoAgent-TW 內建工具 | stdio |

## 🔧 架構整合點
1. `src/core/orchestration/coordinator.py` — 從固定任務→動態 MCP 工具調用
2. `scripts/scheduler_daemon.py` — 啟動時自動初始化 MCP 連接池
3. `.agents/skills/status-notifier/templates/status.html` — Dashboard 新增 MCP 工具面板
