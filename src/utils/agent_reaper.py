import os
import sys
import time
import logging
import psutil
from typing import List

logger = logging.getLogger("Antigravity.Reaper")

def reap_orphaned_agents(targets: List[str] = ["Antigravity", "language_server_windows_x64", "pyrefly"]):
    """
    Scans for and terminates orphaned or stale components of the Antigravity stack.
    Rules:
    1. Skip current PID.
    2. Skip processes where the parent is still active and is likely the IDE.
    3. Kill processes running for more than 4 hours (safety TTL).
    4. Kill processes with no active parent if they are background workers.
    """
    my_pid = os.getpid()
    reaped_count = 0
    
    logger.info(f"Reaper scanning for stale processes (Targets: {targets})...")
    
    for proc in psutil.process_iter(['pid', 'name', 'create_time', 'ppid']):
        try:
            p_info = proc.info
            pid = p_info['pid']
            name = p_info['name']
            
            if pid == my_pid:
                continue
                
            # Match any of the target process names
            if any(t.lower() in name.lower() for t in targets):
                # Rule 1: Staleness check (Running for > 4 hours)
                running_time = time.time() - p_info['create_time']
                if running_time > 14400: # 4 Hours
                    logger.warning(f"Reaper: Terminating stale agent PID {pid} (Running for {running_time/3600:.1f}h)")
                    proc.terminate()
                    reaped_count += 1
                    continue
                
                # Rule 2: Orphan check
                try:
                    parent = psutil.Process(p_info['ppid'])
                    if not parent.is_running():
                        logger.warning(f"Reaper: Terminating orphaned agent PID {pid} (Parent PID {p_info['ppid']} is dead)")
                        proc.terminate()
                        reaped_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    # Parent doesn't exist or we can't see it -> likely orphan if it's a background worker
                    logger.warning(f"Reaper: Terminating suspected orphan PID {pid}")
                    proc.terminate()
                    reaped_count += 1
                    
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if reaped_count > 0:
        logger.info(f"Reaper: Successfully cleaned up {reaped_count} processes.")
    else:
        logger.info("Reaper: No stale processes found.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    reap_orphaned_agents()
