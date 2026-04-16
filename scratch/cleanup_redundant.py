import psutil
import os
import signal

def cleanup():
    targets = ["context7-mcp", "notebooklm-mcp", "@upstash/context7-mcp"]
    cli_targets = ["powershell.exe", "cmd.exe"]
    
    count = 0
    # 1. Cleanup MCP
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = " ".join(proc.info['cmdline'] or [])
            if any(t in cmdline for t in targets):
                print(f"Killing redundant MCP: {proc.info['pid']} - {proc.info['name']}")
                proc.kill()
                count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 2. Cleanup Orphaned CLI (Those with very low CPU time and no active window usually)
    # Be careful not to kill the current shell
    current_pid = os.getpid()
    for proc in psutil.process_iter(['pid', 'name', 'ppid']):
        try:
            if proc.info['name'].lower() in cli_targets:
                # If it's an orphan (PPID is 1 or just disconnected)
                # Or just kill anything redundant that isn't us
                if proc.info['pid'] != current_pid:
                    # Logic check: if it's a child of an IDE or similar it might be okay
                    # but for this audit, we focus on background orphans
                    # Actually, simple taskkill for demo
                    pass
        except:
             pass

    print(f"Cleanup complete. Total {count} MCP processes terminated.")

if __name__ == "__main__":
    cleanup()
