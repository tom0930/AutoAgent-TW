import threading
import time
import json
import logging
import psutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from .spawn_manager import _ACTIVE_SUBAGENTS

logger = logging.getLogger("Orchestration.Monitor")

class ResourceMonitor(threading.Thread):
    """
    Background thread to monitor resource usage of active sub-agents.
    Reports data to their respective state files.
    """
    def __init__(self, interval: float = 5.0):
        super().__init__()
        self.interval = interval
        self.daemon = True
        self.stop_event = threading.Event()
        self.state_dir = Path(".agent-state/subagents")

    def stop(self):
        self.stop_event.set()

    def run(self):
        logger.info(f"Resource Monitor started (Interval: {self.interval}s)")
        while not self.stop_event.is_set():
            try:
                self._scan_agents()
            except Exception as e:
                logger.error(f"Monitor scan failed: {e}")
            
            time.sleep(self.interval)

    def _scan_agents(self):
        # Create a copy to avoid concurrent modification issues
        agents = _ACTIVE_SUBAGENTS[:]
        for agent in agents:
            if not agent.process or agent.process.poll() is not None:
                continue
            
            try:
                p = psutil.Process(agent.process.pid)
                with p.oneshot():
                    cpu_percent = p.cpu_percent()
                    mem_info = p.memory_info()
                    threads = p.num_threads()
                    
                    stats = {
                        "cpu_percent": cpu_percent,
                        "memory_rss_mb": mem_info.rss / (1024 * 1024),
                        "threads": threads,
                        "timestamp": time.time()
                    }
                    
                    self._update_agent_state(agent, stats)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass

    def _update_agent_state(self, agent, stats: Dict[str, Any]):
        state_file = agent.state_file
        if state_file.exists():
            try:
                with open(state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Keep only last 10 resource snapshots to avoid file bloat
                if "resources" not in data:
                    data["resources"] = []
                
                data["resources"].append(stats)
                if len(data["resources"]) > 10:
                    data["resources"] = data["resources"][-10:]
                
                # Update current metrics for easy access
                data["current_metrics"] = stats
                
                with open(state_file, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4, ensure_ascii=False)
            except Exception:
                pass

# Global singleton monitor
_MONITOR: Optional[ResourceMonitor] = None

def start_monitor():
    global _MONITOR
    if _MONITOR is None or not _MONITOR.is_alive():
        _MONITOR = ResourceMonitor()
        _MONITOR.start()

def stop_monitor():
    global _MONITOR
    if _MONITOR:
        _MONITOR.stop()
        _MONITOR = None
