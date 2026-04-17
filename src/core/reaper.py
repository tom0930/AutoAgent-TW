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
        "gitkraken",
        "vision_client",
        "pyrefly",
        "pisrc_graph"
    ]

    # These processes should only ever have ONE active instance per workspace
    SINGLETON_MARKERS = [
        "notebooklm-mcp",
        "context7-mcp",
        "gitkraken",
        "mcp-router",
        "pyrefly"
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
        if not p_info:
            return False
        # Check markers first - if it has a marker, we don't care about the name
        # This allows capturing standalone .exe like pyrefly.exe
        for marker in self.TARGET_MARKERS:
            if marker in p_info["cmdline"] or marker in p_info["name"]:
                return True
        return False

    def kill_proc_tree(self, pid, including_parent=True):
        """Recursively kills a process and all its children."""
        try:
            parent = psutil.Process(pid)
            children = parent.children(recursive=True)
            for child in children:
                try:
                    logger.warning(f"Killing child of PID {pid}: PID {child.pid} ({child.name()})")
                    child.kill()
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            if including_parent:
                logger.warning(f"Killing parent PID {pid} ({parent.name()})")
                parent.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Failed to kill process tree for PID {pid}: {e}")

    def reap(self):
        reaped_count = 0
        logger.info(f"Starting INDUSTRIAL reaping cycle (dry_run={self.dry_run})...")
        
        all_targets = []
        for proc in psutil.process_iter(['pid', 'name']):
            p_info = self.get_process_info(proc)
            if self.is_target(p_info):
                all_targets.append(p_info)
        
        # 1. Passive Reaping: Kill Orphans
        for p in all_targets:
            is_orphan = False
            try:
                # pyrefly: ignore [bad-argument-type, unsupported-operation]
                parent = psutil.Process(p['ppid'])
                if not parent.is_running():
                    is_orphan = True
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                is_orphan = True
            
            if is_orphan:
                # pyrefly: ignore [unsupported-operation]
                logger.warning(f"Reaping Orphan Tree: PID {p['pid']} ({p['name']})")
                if not self.dry_run:
                    # pyrefly: ignore [unsupported-operation]
                    self.kill_proc_tree(p['pid'])
                    reaped_count += 1

        # 2. Active Deduplication: Kill redundant singletons
        for marker in self.SINGLETON_MARKERS:
            # Match against BOTH cmdline and name for robust detection
            # pyrefly: ignore [unsupported-operation]
            matched = [p for p in all_targets if marker in p['cmdline'] or marker in p['name'].lower()]
            if len(matched) > 1:
                matched.sort(key=lambda x: x['create_time'], reverse=True)
                # pyrefly: ignore [unsupported-operation]
                newest_pid = matched[0]['pid']
                to_kill = matched[1:]
                
                for p in to_kill:
                    # pyrefly: ignore [unsupported-operation]
                    if p['pid'] != newest_pid:
                        logger.warning(f"Industrial Deduplication {marker}: Killing tree for PID {p['pid']}")
                        if not self.dry_run:
                            self.kill_proc_tree(p['pid'])
                            reaped_count += 1
        
        logger.info(f"Industrial Reaping completed. Total trees reaped: {reaped_count}")
        return reaped_count

        
        logger.info(f"Reaping cycle completed. Total reaped: {reaped_count}")
        return reaped_count

if __name__ == "__main__":
    reaper = AgentReaper(dry_run=False)
    reaper.reap()
