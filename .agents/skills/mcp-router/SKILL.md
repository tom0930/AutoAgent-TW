---
name: mcp-router
description: AutoAgent-TW Total MCP Router & Token Killer. Intercepts all tool_use (GitKraken, Filesystem, Browser, search) and forces them through RTK compression for 85-95% token savings.
trigger: Any MCP tool use call (e.g., git_log_or_diff, read_file, web_search, fetch_page).
priority: highest
---

# MCP Router Gateway v1.0 (Phase 144)

## Goal
Centralize all MCP tool interactions through a single routing engine that applies **RTK Token Killer** compression. This ensures that even with complex multi-agent workflows, the context window remains lean.

## 📦 How to Use
When you intend to use an MCP tool, pre-process the call through the `mcp-router` if the task is data-heavy (e.g., viewing logs or large files).

### 1. Dynamic Routing Logic
The router automatically selects the RTK strategy based on your current `AUTOAGENT_PHASE`:
- **Builder**: `compact` (Optimized for code generation context).
- **Research**: `ultra-compact` (Optimized for horizontal scanning).
- **QA**: `summary` (Focuses on failures and coverage).
- **Guardian**: `verbose` (Zero-loss for security audits).

### 2. Manual Raw Override
If you need 100% of the raw output for critical debugging, append `--raw` to your internal request or environment, and the router will bypass compression.

## 🛠️ Components
- **Config**: `.agents/skills/mcp-router/config/mcp-router.toml` (Rules for Vivado/FPGA/MFC).
- **Gateway**: `.agents/skills/mcp-router/gateway/mcp_router_gateway.py` (JSON-RPC Middleware).
- **Auto-Register**: Enables automatic discovery of new MCP tools added via AutoSkill.

## 🚀 Execution Instructions
1. Before finishing the "Execute" phase, ensure the `mcp-router` metrics are pushed to the status notifier.
2. For large tool responses, if the output exceeds 2000 tokens, the router will automatically trigger secondary summarization.
