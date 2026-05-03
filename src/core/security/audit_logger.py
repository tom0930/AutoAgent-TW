import time
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger("Core.Security.AuditLogger")

class AuditLogger:
    """
    L7 Defense: Immutable Audit Logging.
    Each entry is chained to the previous one via hash for integrity.
    """
    def __init__(self, log_dir: Path):
        self.log_dir = log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.current_log_file = self.log_dir / f"audit_{int(time.time())}.jsonl"
        self._last_hash = "0" * 64

    def log(self, event_type: str, actor: str, action: str, metadata: Optional[Dict[str, Any]] = None):
        """
        Logs an event with a cryptographic chain link.
        """
        entry = {
            "timestamp": time.time(),
            "event_type": event_type,
            "actor": actor,
            "action": action,
            "metadata": metadata or {},
            "prev_hash": self._last_hash
        }
        
        # Calculate current hash
        entry_json = json.dumps(entry, sort_keys=True)
        current_hash = hashlib.sha256(entry_json.encode()).hexdigest()
        entry["hash"] = current_hash
        self._last_hash = current_hash

        try:
            with open(self.current_log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")

    def verify_integrity(self) -> bool:
        """
        Verifies the hash chain integrity of the current log file.
        """
        if not self.current_log_file.exists():
            return True

        last_ver_hash = "0" * 64
        try:
            with open(self.current_log_file, "r", encoding="utf-8") as f:
                for line in f:
                    entry = json.loads(line)
                    provided_hash = entry.pop("hash")
                    prev_hash = entry.get("prev_hash")
                    
                    if prev_hash != last_ver_hash:
                        return False # Chain broken
                    
                    # Re-calculate hash
                    calc_json = json.dumps(entry, sort_keys=True)
                    calc_hash = hashlib.sha256(calc_json.encode()).hexdigest()
                    
                    if calc_hash != provided_hash:
                        return False # Data tampered
                    
                    last_ver_hash = provided_hash
            return True
        except Exception:
            return False
