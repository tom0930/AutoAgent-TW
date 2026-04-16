#!/usr/bin/env python3
import asyncio
import json
import os
import sys
from pathlib import Path

# Add gateway to path
sys.path.append(str(Path(__file__).parent.parent / "gateway"))
from mcp_router_gateway import MCPProxyGateway

async def test_compression():
    print("🧪 Running MCP Gateway Compression Test...")
    gateway = MCPProxyGateway()
    
    # Sample large payload (simulated Git Log with 10 entries)
    raw_data = {
        "commits": [
            {"hash": f"abc{i}", "msg": f"Feature bitstream optimization part {i}", "author": "tom0930"}
            for i in range(10)
        ]
    }
    
    # Test Builder Phase (Compact)
    os.environ["AUTOAGENT_PHASE"] = "Builder"
    compact_res = await gateway.compress_payload(raw_data, "compact")
    print(f"📦 Builder (Compact) Result Size: {len(json.dumps(compact_res))} bytes")
    
    # Test Guardian Phase (Verbose)
    os.environ["AUTOAGENT_PHASE"] = "Guardian"
    verbose_res = await gateway.compress_payload(raw_data, "verbose")
    print(f"📦 Guardian (Verbose) Result Size: {len(json.dumps(verbose_res))} bytes")
    
    if len(json.dumps(compact_res)) <= len(json.dumps(verbose_res)):
        print("✅ Success: Compact mode produced smaller or equal output than Verbose.")
    else:
        print("❌ Error: Compact mode produced larger output than Verbose.")

if __name__ == "__main__":
    asyncio.run(test_compression())
