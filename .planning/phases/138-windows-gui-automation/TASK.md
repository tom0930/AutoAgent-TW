# Phase 138 Execution Tasks: Windows GUI Automation

### Wave 1: Core Automation Logic
- [x] Implement `src/core/rva/rva_audit.py` (Kill-switch, Logging, ImageHash Caching, Watchdog)
- [x] Implement `src/core/rva/vision_client.py` (Gemini vision API integration for normalized `[0.0, 1.0]` bbox)
- [x] Implement `src/core/rva/rva_engine.py` (Hybrid: pywinauto UIA fast path → Active Window Cropping fallback)

### Wave 2: MCP Server Encapsulation
- [x] Implement `src/core/mcp/rva_server.py` (Expose `rva_click` tool)
- [x] Integrate Human-in-the-loop authorization logic within MCP Server for "Erase", "Program" keywords.

### Wave 3: Integration & Testing
- [x] Register `rva-mcp` in `C:\Users\TOM\.gemini\antigravity\mcp_config.json`
- [x] Verification: Test UI automation (dry run) with Failsafe exception.
- [x] Produce QA / Walkthrough
