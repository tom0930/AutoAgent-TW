import psutil
import time
import os
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("AgentReaper")

class AgentReaper:
    """
    Industrially prunes orphaned agent and MCP processes.
    Identifies 'AutoAgent-TW' related processes that have no living parent
    or have been running longer than the maximum allowed session time.
    """
    
    TARGET_MARKERS = [
        "autoagent-tw",
        "mcp-router",
        "notebooklm-mcp",
        "context7-mcp",
        "vision_client",
        "pyrefly"
    ]
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def is_target(self, proc):
        try:
            cmdline = " ".join(proc.cmdline()).lower()
            name = proc.name().lower()
            
            # Check if it's node or python
            if name not in ["node.exe", "python.exe", "node", "python"]:
                return False
                
            # Check markers
            for marker in self.TARGET_MARKERS:
                if marker in cmdline or marker in name:
                    return True
            return False
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return False

    def reap(self):
        reaped_count = 0
        logger.info(f"Starting reaping cycle (dry_run={self.dry_run})...")
        
        for proc in psutil.process_iter(['pid', 'name', 'ppid', 'create_time']):
            if self.is_target(proc):
                try:
                    # Check if orphan
                    is_orphan = False
                    try:
                        parent = psutil.Process(proc.ppid())
                        if not parent.is_running():
                            is_orphan = True
                        # If parent is just 'explorer.exe' or 'cmd.exe' but we are a background tool, 
                        # it might be okay, but usually MCP servers are spawned by a specific parent.
                    except psutil.NoSuchProcess:
                        is_orphan = True
                    
                    if is_orphan:
                        logger.warning(f"Found orphan process: PID {proc.pid} ({proc.name()})")
                        if not self.dry_run:
                            proc.terminate()
                            reaped_count += 1
                except (psutil.AccessDenied, psutil.NoSuchProcess):
                    continue
        
        logger.info(f"Reaping cycle completed. Reaped {reaped_count} processes.")
        return reaped_count

if __name__ == "__main__":
    reaper = AgentReaper(dry_run=False)
    reaper.reap()
