# Research: Phase 144 (MCP Proxy Gateway)

## 1. JSON-RPC StdIO Interception
- **Mechanism**: LLM agents communicate with MCP servers via standard input/output. To intercept this, we must place our gateway as a middleware.
- **Challenge**: Many MCP servers are launched directly by the host environment.
- **Solution**: We will create a `mcp-proxy-launcher.py` that wraps the target server command. 
- **AutoSkill Sync**: AutoSkill should modify the `mcp-config.json` (or equivalent) to use the proxy as the entry point.

## 2. RTK Streaming Compression
- **Requirement**: RTK `v0.36.0` supports `compress` sub-command.
- **Usage**: `rtk compress --strategy [STRATEGY] --format json`.
- **Implementation**: Pipe the JSON output from the native MCP server into RTK's STDIN, and read the result from STDOUT.
- **Security**: Guardian phase must use `--verbose` or bypass directly.

## 3. AutoSkill Registration Interface
- **Interface**: A simple registry file in `.planning/codebase/mcp_registry.json`.
- **Logic**: When AutoSkill loads a new skill, it checks if it has an MCP component and registers it to the gateway.
