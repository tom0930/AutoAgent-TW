import psutil
import json

def audit():
    targets = ["node", "python"]
    results = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            if any(t in name for t in targets):
                cmdline = " ".join(proc.info['cmdline'] or [])
                # Only care about MCP or Antigravity related
                if "mcp" in cmdline.lower() or "autoagent" in cmdline.lower() or "antigravity" in cmdline.lower():
                    results.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cmdline": cmdline
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    audit()
