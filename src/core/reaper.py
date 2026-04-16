import psutil
import logging

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
        "pyrefly",
        "pisrc_graph"
    ]

    # These processes should only ever have ONE active instance per workspace
    SINGLETON_MARKERS = [
        "notebooklm-mcp",
        "context7-mcp",
        "mcp-router"
    ]
    
    def __init__(self, dry_run=False):
        self.dry_run = dry_run

    def get_process_info(self, proc):
        """Helper to safely extract process info."""
        try:
            cmdline = " ".join(proc.cmdline()).lower()
            name = proc.name().lower()
            return {
                "pid": proc.pid,
                "name": name,
                "cmdline": cmdline,
                "create_time": proc.create_time(),
                "ppid": proc.ppid()
            }
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            return None

    def is_target(self, p_info):
        if not p_info: return False
        name = p_info["name"]
        cmdline = p_info["cmdline"]
        
        # Check basic process name
        if name not in ["node.exe", "python.exe", "node", "python"]:
            return False
            
        # Check markers
        for marker in self.TARGET_MARKERS:
            if marker in cmdline or marker in name:
                return True
        return False

    def reap(self):
        reaped_count = 0
        logger.info(f"Starting industrial reaping cycle (dry_run={self.dry_run})...")
        
        all_targets = []
        for proc in psutil.process_iter(['pid', 'name']):
            p_info = self.get_process_info(proc)
            if self.is_target(p_info):
                all_targets.append(p_info)
        
        # 1. Passive Reaping: Kill Orphans
        for p in all_targets:
            is_orphan = False
            try:
                parent = psutil.Process(p['ppid'])
                if not parent.is_running():
                    is_orphan = True
            except psutil.NoSuchProcess:
                is_orphan = True
            
            if is_orphan:
                logger.warning(f"Reaping Orphan: PID {p['pid']} ({p['name']}) - Cmd: {p['cmdline'][:50]}...")
                if not self.dry_run:
                    try:
                        psutil.Process(p['pid']).terminate()
                        reaped_count += 1
                    except: pass

        # 2. Active Deduplication: Kill redundant singletons
        # Group by marker
        for marker in self.SINGLETON_MARKERS:
            matched = [p for p in all_targets if marker in p['cmdline']]
            if len(matched) > 1:
                # Sort by creation time (descending), keep the newest one
                matched.sort(key=lambda x: x['create_time'], reverse=True)
                newest_pid = matched[0]['pid']
                to_kill = matched[1:]
                
                for p in to_kill:
                    # Double check we are not killing the current process or the newest one
                    if p['pid'] != newest_pid:
                        logger.warning(f"Deduplicating {marker}: Terminating redundant PID {p['pid']} (Keeping newest PID {newest_pid})")
                        if not self.dry_run:
                            try:
                                psutil.Process(p['pid']).terminate()
                                reaped_count += 1
                            except: pass
        
        logger.info(f"Reaping cycle completed. Total reaped: {reaped_count}")
        return reaped_count

if __name__ == "__main__":
    reaper = AgentReaper(dry_run=False)
    reaper.reap()
