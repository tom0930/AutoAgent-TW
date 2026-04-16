import psutil
import os

def cleanup_cli():
    # Targets for CLI cleanup
    # We look for cmd/powershell that are likely orphans
    # Or just clean up based on specific known markers if any
    
    current_pid = os.getpid()
    count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'ppid', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            if name in ["cmd.exe", "powershell.exe", "conhost.exe"]:
                # If cmdline is empty or just the exe, and it's not us or our parent
                if proc.info['pid'] == current_pid:
                    continue
                
                # Check for orphans (Parent process does not exist)
                try:
                    parent = psutil.Process(proc.info['ppid'])
                    if not parent.is_running():
                        is_orphan = True
                    else:
                        is_orphan = False
                        # If parent is just 'explorer.exe' or 'svchost.exe', it might be an orphan from a closed terminal
                        p_name = parent.name().lower()
                        if p_name in ["explorer.exe", "svchost.exe"]:
                            is_orphan = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    is_orphan = True
                
                if is_orphan:
                    # Additional check: skip if it has an active UI window (optional, harder in pure psutil)
                    # For now, if it's an orphan and looks like a remnant, kill it
                    print(f"Killing orphan CLI: {proc.info['pid']} ({name})")
                    proc.kill()
                    count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
            
    print(f"CLI Cleanup complete. Total {count} orphans terminated.")

if __name__ == "__main__":
    cleanup_cli()
