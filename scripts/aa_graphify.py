import argparse
import sys
from pathlib import Path

# Add script dir to path
sys.path.append(str(Path(__file__).parent))
from graphify_orchestrator import GraphifyOrchestrator

def main():
    parser = argparse.ArgumentParser(description="AutoAgent-TW Graphify CLI (v3.7.5)")
    parser.add_argument("command", choices=["status", "update", "full-index", "serve", "serve-lite", "query"], help="Command to run")
    parser.add_argument("query", nargs="?", help="Query string for 'query' command")
    args = parser.parse_args()

    orch = GraphifyOrchestrator()

    if args.command == "status":
        status = orch.get_status()
        import datetime
        last_run_raw = status.get('last_run', 0)
        last_run_str = datetime.datetime.fromtimestamp(last_run_raw).strftime('%Y-%m-%d %H:%M:%S') if last_run_raw else 'never'
        
        print("[*] Knowledge Graph Status:")
        print(f"    Mode:         {status.get('mode', 'N/A')}")
        print(f"    Status:       {status.get('status', 'unknown')}")
        print(f"    Nodes:        {status.get('node_count', 'unknown')}")
        print(f"    Last Updated: {last_run_str}")
        if status.get("error"):
            print(f"    Error:        {status.get('error')}")

    elif args.command == "update":
        print("[*] Triggering incremental code graph update...")
        orch.run(mode="update", background=False)
        
    elif args.command == "full-index":
        print("[!] Triggering FULL semantic indexing (Gemini API costs apply)...")
        orch.run(mode="full", background=False)
        
    elif args.command == "serve":
        status = orch.get_status()
        node_count = status.get("node_count", 0)
        
        if node_count > orch.node_threshold:
            print(f"[!] Warning: Graph is VERY large ({node_count} nodes).")
            print(f"[!] Opening this in a browser may consume several GBs of RAM.")
            print("[*] Recommendation: Use the 'Arch-Lite' viz instead:")
            print("    python scripts/aa_graphify.py serve-lite")
            return

        viz_path = orch.out_dir / "graph.html"
        if viz_path.exists():
            print(f"[*] Opening Graphify visualization: {viz_path}")
            import webbrowser
            webbrowser.open(f"file:///{viz_path.absolute()}")
        else:
            print("[!] Visualization file not found in central out_dir.")
            print("[*] Try running 'update' first to collect results.")
            
    elif args.command == "serve-lite":
        # Launch pre-generated small demo graph
        lite_path = Path("z:/AutoAgent-TW/scratch/demo-graph/graphify-out/graph.html")
        if lite_path.exists():
            print(f"[*] Opening LITE visualization (Core Orchestration only): {lite_path}")
            import webbrowser
            webbrowser.open(f"file:///{lite_path.absolute()}")
        else:
            print("[!] Lite visualization not found. Run a targeted demo index first.")

    elif args.command == "query":
        if not args.query:
            print("[!] Error: 'query' command requires a query string.")
            return
        # Note: 'graphify query' needs the graph.json path
        graph_json = orch.out_dir / "graph.json"
        if not graph_json.exists():
            print("[!] Error: graph.json not found. Run 'update' first.")
            return
        
        import subprocess
        subprocess.run(["graphify", "query", str(graph_json), args.query])

if __name__ == "__main__":
    main()
