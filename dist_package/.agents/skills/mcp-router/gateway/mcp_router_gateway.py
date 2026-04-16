#!/usr/bin/env python3
import sys
import asyncio
import json
import os
from pathlib import Path
from typing import Dict, Any

class MCPProxyGateway:
    def __init__(self):
        self.config_path = Path(__file__).parent.parent / "config" / "mcp-router.toml"
        self.metrics_file = Path(__file__).parent.parent / "metrics.json"
        self.rtk_bin = r"z:\autoagent-TW\bin\rtk.exe" if os.name == "nt" else "rtk"
        self.phase = os.getenv("AUTOAGENT_PHASE", "Builder")

    async def get_strategy(self, tool_name: str) -> str:
        # Simple strategy resolver based on phase and tool name
        if self.phase == "Guardian":
            return "verbose"
        if self.phase == "Research" or "context7" in tool_name.lower():
            return "ultra-compact"
        
        # Hardcoded defaults for V1
        if "git" in tool_name.lower():
            return "compact"
        if "browser" in tool_name.lower():
            return "summary"
        return "compact"

    async def compress_payload(self, raw_data: Any, strategy: str) -> Any:
        """Calls RTK to compress JSON payload."""
        if strategy == "verbose" or "--raw" in str(raw_data):
            return raw_data

        try:
            cmd = [self.rtk_bin, "compress", "--strategy", strategy, "--format", "json"]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            # Convert raw_data to string if it isn't already
            input_str = json.dumps(raw_data) if not isinstance(raw_data, str) else raw_data
            stdout, stderr = await proc.communicate(input_str.encode("utf-8"))
            
            if proc.returncode == 0:
                return json.loads(stdout.decode("utf-8"))
            else:
                return raw_data # Fallback to raw on error
        except Exception:
            return raw_data

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any], raw_call: Dict[str, Any]):
        """
        Intercepts the tool call, executes the real MCP tool (faking it for now as this is a gateway logic),
        and returns compressed result.
        """
        # In a real proxy scenario, this script would be the entry point in mcp-config.
        # It would forward the STDIN to the actual MCP binary.
        # For our Phase 144 integration within AutoAgent-TW, we use this as a library/service.
        
        strategy = await self.get_strategy(tool_name)
        
        # This is where the integration with existing MCP tools happens.
        # In this first version, we simulate the return from a tool.
        # But for actual production, we will use it as a wrapper in the skill.
        
        return {
            "status": "intercepted",
            "strategy_applied": strategy,
            "original_tool": tool_name
        }

    async def run_stdio(self):
        """Standard IO listener for JSON-RPC messages."""
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        while True:
            line = await reader.readline()
            if not line:
                break
            
            try:
                data = json.loads(line.decode("utf-8").strip())
                # Handle routing
                response = await self.handle_tool_call(
                    data.get("method", "unknown"),
                    data.get("params", {}),
                    data
                )
                print(json.dumps(response))
                sys.stdout.flush()
            except Exception:
                pass

if __name__ == "__main__":
    gateway = MCPProxyGateway()
    # If called with arguments, treat as CLI wrapper
    if len(sys.argv) > 1:
        # CLI wrapping logic (Stage 1.2)
        pass
    else:
        # StdIO logic
        asyncio.run(gateway.run_stdio())
