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
        self.memory_dir = Path(__file__).resolve().parent.parent.parent.parent / "memory"
        self.hot_cache_file = self.memory_dir / "hot_cache.json"
        self.thought_chain = []

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

    async def _intercept_filesystem_data(self, params: Dict[str, Any], raw_result: Any) -> Any:
        path = str(params.get("path", ""))
        ext = Path(path).suffix.lower()
        if ext not in [".json", ".csv"]:
            return raw_result
            
        try:
            if ext == ".json":
                data = json.loads(raw_result) if isinstance(raw_result, str) else raw_result
                if isinstance(data, dict):
                    return {"_sys_msg": "Sampled by Gateway", "keys": list(data.keys())[:20]}
                elif isinstance(data, list):
                    return {"_sys_msg": "Sampled by Gateway", "length": len(data), "sample": data[:5]}
            elif ext == ".csv":
                lines = raw_result.splitlines() if isinstance(raw_result, str) else []
                return "\n".join(lines[:10]) + "\n...[Truncated by Gateway]"
        except Exception:
            pass
        return raw_result

    async def _route_to_memory_bridge(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        if not self.hot_cache_file.exists():
            with open(self.hot_cache_file, "w", encoding="utf-8") as f:
                json.dump({}, f)
                
        with open(self.hot_cache_file, "r", encoding="utf-8") as f:
            cache = json.load(f)
            
        if tool_name == "memory.save":
            key, val = arguments.get("key"), arguments.get("value")
            cache[key] = val
            with open(self.hot_cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f, indent=2)
            return {"status": "saved", "key": key}
        elif tool_name == "memory.recall":
            key = arguments.get("key")
            return {"status": "recalled", "key": key, "value": cache.get(key, None)}
        return {"error": "unknown memory operation"}

    async def _process_sequential_thinking(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        thought = arguments.get("thought", "")
        step = arguments.get("step_number", 1)
        self.thought_chain.append({"step": step, "thought": thought})
        return {"status": "thought_recorded", "step": step}

    async def _validate_sequential_thinking(self, tool_name: str) -> bool:
        risky_tools = ["write_to_file", "replace_file_content", "run_command", "bash"]
        if tool_name in risky_tools:
            if not self.thought_chain or self.thought_chain[-1]["step"] < 1:
                return False
        return True

    async def handle_tool_call(self, tool_name: str, arguments: Dict[str, Any], raw_call: Dict[str, Any]):
        """
        Intercepts the tool call, executes the real MCP tool (faking it for now as this is a gateway logic),
        and returns compressed result.
        """
        if tool_name == "sequential_thinking":
            return await self._process_sequential_thinking(arguments)
            
        if not await self._validate_sequential_thinking(tool_name):
            return {
                "error": "Sequential thinking failed. Please run sequential_thinking tool before executing risky operations."
            }

        if tool_name.startswith("memory."):
            return await self._route_to_memory_bridge(tool_name, arguments)

        strategy = await self.get_strategy(tool_name)
        
        # Simulate real MCP execution
        real_result = {"status": "intercepted", "strategy_applied": strategy, "original_tool": tool_name}
        
        # Intercept FS Data
        if tool_name in ["read_file", "filesystem.read"]:
            dummy_raw_json = json.dumps({"dummy": "json", "data": "very long data", "keys": list(range(100))})
            real_result = await self._intercept_filesystem_data(arguments, dummy_raw_json)

        return real_result

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
