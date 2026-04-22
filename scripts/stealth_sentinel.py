import psutil
import time
import sys
import os
import json

# pyrefly: ignore [missing-import]
from scripts.autocli_guard import load_policy

def monitor_process(proc_name_or_pid, threshold_mb=50, interval=0.5, duration=30):
    """
    Monitors a process's memory usage and kills it if it exceeds the threshold.
    """
    print(f"[*] Stealth Sentinel active for: {proc_name_or_pid} (Threshold: {threshold_mb}MB)")
    
    start_time = time.time()
    while time.time() - start_time < duration:
        found = False
        for proc in psutil.process_iter(['pid', 'name', 'memory_info']):
            try:
                # Match by name or PID
                if (isinstance(proc_name_or_pid, int) and proc.info['pid'] == proc_name_or_pid) or \
                   (isinstance(proc_name_or_pid, str) and proc_name_or_pid.lower() in proc.info['name'].lower()):
                    
                    found = True
                    rss_mb = proc.info['memory_info'].rss / (1024 * 1024)
                    
                    if rss_mb > threshold_mb:
                        print(f"[!] ALERT: Memory limit exceeded! {rss_mb:.1f}MB > {threshold_mb}MB")
                        proc.kill()
                        print(f"[+] Process {proc.info['pid']} terminated to maintain stealth.")
                        return False
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        if not found and time.time() - start_time > 2: # Give it some time to start
            # If we were monitoring a specific PID and it's gone, we're done
            if isinstance(proc_name_or_pid, int):
                return True
        
        time.sleep(interval)
    return True

if __name__ == "__main__":
    policy = load_policy()
    limit = policy.get("max_memory_mb", 50)
    
    if len(sys.argv) > 1:
        target = sys.argv[1]
        # Check if target is numeric PID
        if target.isdigit():
            monitor_process(int(target), threshold_mb=limit)
        else:
            monitor_process(target, threshold_mb=limit)
    else:
        # Default: monitor any autocli instance
        monitor_process("autocli.exe", threshold_mb=limit)
