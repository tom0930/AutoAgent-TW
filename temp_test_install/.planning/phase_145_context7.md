# Phase 145: Industrialized Tooling & Context7 Integration

Integrate the newly developed MCP Router Gateway with the Context7 documentation engine to provide high-fidelity, token-efficient technical research.

## Objectives
1. **Context7 Installation**: Deploy and configure the `@upstash/context7-mcp` server in the master `mcp_config.json`.
2. **Gateway Optimization**: Refine `mcp_router_gateway.py` to handle the specific semantic density of documentation queries.
3. **Connectivity Audit**: Ensure the LLM can query Context7 via the gateway with RTK compression active for large doc chunks.

## Architecture
- **Control Plane**: `mcp_config.json` (Master Registry)
- **Middleware**: `mcp_router_gateway.py` (Compression & Routing)
- **Data Source**: `Context7 MCP Server` (Hosted Documentation)

## Execution Plan

### Wave 1: Installation & Registry
1. Add `context7` entry to `C:\Users\TOM\.gemini\antigravity\mcp_config.json`.
   ```json
   "context7": {
     "command": "npx",
     "args": ["-y", "@upstash/context7-mcp"]
   }
   ```
2. Verify basic connectivity using `npx -y @upstash/context7-mcp --help`.

### Wave 2: Gateway Configuration
1. Update `z:\autoagent-TW\.agents\skills\mcp-router\config\mcp-router.toml`.
2. Add `[routing.context7]` with `max_lines = 500` and `rtk_mode = "docs"`.

### Wave 3: Validation
1. Verify `mcp_router_gateway` logs for successful documentation interception.
2. Final UAT of Phase 145.
