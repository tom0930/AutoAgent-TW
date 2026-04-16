# Plan: Phase 144 (MCP Proxy Gateway)

## 📋 Wave 1: Core Gateway Infrastructure
- [ ] Task 1.1: Create `.agents/skills/mcp-router/config/mcp-router.toml` with Vivado-optimized filters.
- [ ] Task 1.2: Implement `.agents/skills/mcp-router/gateway/mcp_router_gateway.py` using `asyncio` for non-blocking JSON-RPC proxying.
- [ ] Task 1.3: Integrate RTK streaming compression logic into the gateway handler.

## 📋 Wave 2: AutoSkill & Runtime Integration
- [ ] Task 2.1: Implement `gateway/auto_register.py` for dynamic MCP server discovery.
- [ ] Task 2.2: Add a global hook or instructions to `SKILL.md` to ensure any new MCP tool usage is routed through the gateway.
- [ ] Task 2.3: Update `status-notifier` to include MCP Token Savings metrics.

## 📋 Wave 3: Validation & UAT
- [ ] Task 3.1: Create `tests/test_gateway.py` to simulate large JSON responses (e.g., 5MB Git Log).
- [ ] Task 3.2: Verify Phase-aware strategy switching (Builder vs Guardian).
- [ ] Task 3.3: Conduct a dry-run with a real MCP tool (e.g., `git_log_or_diff`) to confirm transparency.

## 🚩 UAT (Verification Criteria)
1. **Transparency**: The LLM shouldn't know the proxy exists; tool calls should result in valid (but compressed) JSON.
2. **Performance**: Overhead per call < 15ms.
3. **Efficiency**: Token saving > 80% for large data tool responses.
