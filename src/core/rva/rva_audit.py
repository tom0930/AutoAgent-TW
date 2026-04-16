import os
import json
import time
import hashlib
from typing import Dict, Any, Optional
from pathlib import Path
from PIL import Image

class RVAAuditContext:
    def __init__(self, workspace_root: str):
        self.workspace_root = Path(workspace_root)
        self.scratch_dir = self.workspace_root / ".agents" / "scratch"
        self.scratch_dir.mkdir(parents=True, exist_ok=True)
        self.audit_log = self.scratch_dir / "rva_audit.log"
        
        # Security Constants
        self.MAX_TIMEOUT_SEC = 900  # 15 minutes watchdog
        self.last_action_time = time.time()
        self.in_flight_action = False
    
    def check_watchdog(self):
        """Enforce strict 900s timeout."""
        if self.in_flight_action and (time.time() - self.last_action_time > self.MAX_TIMEOUT_SEC):
            self._log_event("WATCHDOG_TIMEOUT", {"msg": "RVA operation exceeded 900s limit."})
            raise TimeoutError("RVA Watchdog Triggered: Operation exceeded 15 minutes.")

    def log_action(self, tool_name: str, args: Dict[str, Any], status: str, details: str = ""):
        """Log operations for repudiation protection."""
        event = {
            "timestamp": time.time(),
            "tool": tool_name,
            "args": args,
            "status": status,
            "details": details
        }
        self._log_event("RVA_ACTION", event)
        
    def _log_event(self, event_type: str, data: Dict[str, Any]):
        try:
            with open(self.audit_log, "a", encoding="utf-8") as f:
                log_entry = json.dumps({"event_type": event_type, **data})
                f.write(f"{log_entry}\n")
        except Exception:
            pass # Failsafe logging should not crash the main thread
            
    def compute_image_hash(self, image_path: Path) -> Optional[str]:
        """Compute MD5 of an image footprint to detect UI jitter/staleness."""
        if not image_path.exists():
            return None
        hasher = hashlib.md5()
        with open(image_path, "rb") as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()

    def start_action(self):
        self.check_watchdog()
        self.in_flight_action = True
        self.last_action_time = time.time()
        
    def end_action(self):
        self.in_flight_action = False

# Global instance for the workspace
rva_audit = RVAAuditContext("z:/autoagent-TW/")
