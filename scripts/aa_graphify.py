import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add core path
sys.path.append(os.path.dirname(__file__))
from aa_constants import get_workspace, get_planning_dir
from graphify_orchestrator import GraphifyOrchestrator

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Graphify CLI (v3.7.2)")
    parser.add_argument("command", choices=["build", "update", "query", "status", "repair", "serve"], help="Action to perform")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Additional arguments for graphify")
    
    args = parser.parse_args()
    orch = GraphifyOrchestrator()
    
    if args.command == "status":
        status = orch.get_status()
        print(f"[*] Knowledge Graph Status:")
        print(f"    Last Updated: {status.get('last_run', 'Never')}")
        print(f"    Fingerprint:  {status.get('fingerprint', 'N/A')}")
        print(f"    State:        {status.get('status', 'Unknown')}")
        if status.get("error"):
            print(f"    Error:        {status.get('error')}")
            
    elif args.command == "build":
        orch.run(mode="full", background=False)
        
    elif args.command == "update":
        orch.run(mode="smart", background=False)
        
    elif args.command == "query":
        if not args.args:
            print("Usage: aa-graphify query \"your question\"")
            return
        # Forward query to graphify
        cmd = ["graphify", "query", args.args[0], "--out", str(orch.out_dir)]
        subprocess.run(cmd)
        
    elif args.command == "repair":
        print("[!] Repairing graph: clearing cache and rebuilding...")
        if orch.out_dir.exists():
            import shutil
            shutil.rmtree(orch.out_dir)
        orch.run(mode="full", background=False)
        
    elif args.command == "serve":
        # Launch graphify visualization server
        cmd = ["graphify", "serve", "--out", str(orch.out_dir)]
        print(f"[*] Starting Graphify visualization server...")
        subprocess.run(cmd)

if __name__ == "__main__":
    main()
