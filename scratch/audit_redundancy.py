import psutil
import os

def audit_mcp_redundancy():
    print("=" * 80)
    print(f"{'MCP Redundancy Audit':^80}")
    print("-" * 80)
    
    mcp_targets = {
        "notebooklm-mcp": 0,
        "context7-mcp": 0,
        "gitkraken-mcp": 0,
        "pyrefly": 0
    }
    
    details = []

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'memory_info']):
        try:
            cmdline = " ".join(proc.info['cmdline']) if proc.info['cmdline'] else ""
            rss = proc.info['memory_info'].rss / (1024 * 1024)
            name = proc.info['name'].lower()
            
            found_key = None
            if "notebooklm" in cmdline.lower():
                found_key = "notebooklm-mcp"
            elif "context7" in cmdline.lower():
                found_key = "context7-mcp"
            elif "gitkraken" in cmdline.lower():
                found_key = "gitkraken-mcp"
            elif "pyrefly" in name or "pyrefly" in cmdline.lower():
                found_key = "pyrefly"

            if found_key:
                mcp_targets[found_key] += 1
                details.append({
                    "key": found_key,
                    "pid": proc.info['pid'],
                    "rss": rss,
                    "cmd": cmdline[:100] + "..." if len(cmdline) > 100 else cmdline
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    print(f"{'MCP Server':<20} {'Count':<10} {'Status'}")
    print("-" * 80)
    for server, count in mcp_targets.items():
        status = "✅ CLEAN (SINGLETON)" if count == 1 else "✅ IDLE" if count == 0 else f"❌ STACKED ({count})"
        print(f"{server:<20} {count:<10} {status}")

    if details:
        print("\n" + "-" * 80)
        print(f"{'PID':<10} {'Server':<20} {'RSS (MB)':<12} {'Command Snippet'}")
        for det in details:
            print(f"{det['pid']:<10} {det['key']:<20} {det['rss']:<12.2f} {det['cmd']}")

if __name__ == "__main__":
    audit_mcp_redundancy()
