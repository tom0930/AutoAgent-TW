# Implementation Plan: Phase 146 - MCP 3-Layer Integration

## Goal Description
Implement the **Data Specialist & Long-term Memory (mcp3fs)** upgrades into AutoAgent-TW. Instead of spawning 3 independent MCP skills which would cause namespace collisions and orchestration breakdown, we will deeply integrate these features into the existing `mcp_router_gateway.py`. This ensures zero-friction routing, seamless RTK token compression, and centralized security.

## User Review Required
> [!IMPORTANT]
> The **Sequential Thinking** constraint will actively block code execution if steps are not sequentially completed. Do you want this constraint enforced globally, or only for specific directories (e.g., core logic)?

## Proposed Changes

### Component: MCP Router Gateway (`mcp_router_gateway.py`)

#### [MODIFY] `z:\autoagent-TW\.agents\skills\mcp-router\gateway\mcp_router_gateway.py`
We will introduce three modular interceptor methods directly into the Gateway class:
1. `_intercept_filesystem_data()`: Checks file extensions from `params['path']`. If `.json` or `.csv`, parses the raw string response from the native MCP, applies sampling (e.g., top 20 lines/dict keys), and returns the summary.
2. `_route_to_memory_bridge()`: Intercepts pseudo-tool calls like `memory.save` or `memory.recall`. It will read/write to a highly responsive `hot_cache.json` in `.agents/memory/`, deferring heavy lifting to the global LanceDB MemPalace later if needed.
3. `_validate_sequential_thinking()`: Introduce an internal state tracker `self.thought_chain`. When the LLM requests a risky operation, it verifies if a contiguous thought process was recently registered via a pseudo-tool `sequential_thinking_step`.

### Component: Runtime Data Directory

#### [NEW] `z:\autoagent-TW\.agents\memory\hot_cache.json`
- A predefined KV store representing hot-swappable project definitions (e.g., AXI Maps).

## Verification Plan
### Automated Tests
- Inject a dummy 10MB JSON via terminal simulation to `mcp_router_gateway.py`. Verify the final string payload sent outbound is less than `2KB`.
- Invoke state machine tool skipping step 2. Verify an explicit JSON-RPC error is returned forcing step completion.

### Manual Verification
- Ask the agent to check the "Project AXI Memory Map". Wait for it to access `memory.recall` without using grep or ripgrep.
