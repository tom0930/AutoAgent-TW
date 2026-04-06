"""
AutoAgent-TW MCP CLI v1.0
Usage:
  python scripts/aa_mcp.py list [--verbose]
  python scripts/aa_mcp.py status
"""
import asyncio
import sys
import argparse
from src.core.mcp.mcp_client import MCPClientManager

async def list_tools(verbose: bool):
    manager = MCPClientManager()
    await manager.startup()
    summary = manager.registry.list_summary(verbose=verbose)
    
    print(f"\n--- Registered MCP Tools ({len(summary)}) ---")
    for tool in summary:
        print(f"[{tool['server']}] {tool['name']}")
        print(f"  Description: {tool['description']}")
        if verbose and 'input_schema' in tool:
            print(f"  Schema: {tool['input_schema']}")
        print("-" * 20)

async def check_status():
    manager = MCPClientManager()
    await manager.startup()
    status = manager.get_server_status()
    
    print("\n--- MCP Server Health Status ---")
    for s in status:
        icon = "🟢" if s['connected'] else "🔴"
        print(f"{icon} {s['name']} (Tools: {s['tool_count']})")
        if s['error']:
            print(f"   Error: {s['error']}")

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW MCP Management CLI")
    subparsers = parser.add_subparsers(dest="command")
    
    # List tools
    list_parser = subparsers.add_parser("list", help="List all registered MCP tools")
    list_parser.add_argument("--verbose", action="store_true", help="Show input schemas")
    
    # Status
    subparsers.add_parser("status", help="Show connection status of MCP servers")
    
    args = parser.parse_args()
    
    if args.command == "list":
        asyncio.run(list_tools(args.verbose))
    elif args.command == "status":
        asyncio.run(check_status())
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
