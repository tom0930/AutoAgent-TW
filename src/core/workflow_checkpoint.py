import os
import json
import hmac
import hashlib
import time
import logging
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict, field

logger = logging.getLogger("Core.WorkflowCheckpoint")

class CheckpointSecret:
    """Manages the system-level HMAC secret for checkpoint integrity."""
    
    @staticmethod
    def get_key() -> bytes:
        # Use home directory for system-level persistence
        # Windows: %USERPROFILE%\.autoagent\config\
        # Linux/Mac: ~/.autoagent/config/
        config_dir = Path.home() / ".autoagent" / "config"
        key_file = config_dir / "checkpoint_key"
        
        if not key_file.exists():
            if not config_dir.exists():
                config_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate a random 32-byte key
            key = os.urandom(32)
            try:
                with open(key_file, "wb") as f:
                    f.write(key)
                # Set permissions (Unix: 600)
                if os.name != "nt":
                    os.chmod(key_file, 0o600)
            except Exception as e:
                logger.error(f"Failed to save checkpoint key: {e}")
                return b"default_fallback_key_not_secure"
        
        try:
            return key_file.read_bytes()
        except Exception:
            return b"read_error_fallback"

@dataclass
class WorkflowCheckpoint:
    """Checkpoint V2 Schema"""
    workflow_id: str
    step_id: str
    action: str
    status: str  # pending, completed, failed, paused
    artifacts: List[str] = field(default_factory=list)
    requires_hitl: bool = False
    active_tools: List[str] = field(default_factory=list)
    capability_mode: str = "explore" # explore, code, test, review
    partial_state: Optional[Dict[str, Any]] = None
    timestamp: float = field(default_factory=time.time)
    hmac: str = ""

class CheckpointManager:
    """
    Manages workflow checkpoints with integrity verification.
    """
    def __init__(self, project_root: Optional[Union[str, Path]] = None):
        self.project_root = Path(project_root or os.getcwd())
        # If project_root is already .agent-state, don't append it again
        if self.project_root.name == ".agent-state":
            self.state_dir = self.project_root / "checkpoints"
        else:
            self.state_dir = self.project_root / ".agent-state" / "checkpoints"
        self._secret_key = CheckpointSecret.get_key()
        self._lock = threading.Lock()

    def _calculate_hmac(self, data: Dict[str, Any]) -> str:
        # Sort keys to ensure consistent serialization
        serialized = json.dumps(data, sort_keys=True, ensure_ascii=False).encode("utf-8")
        return hmac.new(self._secret_key, serialized, hashlib.sha256).hexdigest()

    def save(self, checkpoint: WorkflowCheckpoint) -> Path:
        """Saves a checkpoint to disk with HMAC."""
        checkpoint_data = asdict(checkpoint)
        # Remove HMAC before calculation if it exists
        checkpoint_data.pop("hmac", None)
        
        checkpoint.hmac = self._calculate_hmac(checkpoint_data)
        checkpoint_data["hmac"] = checkpoint.hmac
        
        workflow_dir = self.state_dir / checkpoint.workflow_id
        if not workflow_dir.exists():
            workflow_dir.mkdir(parents=True, exist_ok=True)
            
        file_path = workflow_dir / f"step_{checkpoint.step_id}.json"
        
        with self._lock:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(checkpoint_data, f, indent=4, ensure_ascii=False)
                # Also maintain a 'latest.json' symlink-like file or copy
                latest_path = workflow_dir / "latest.json"
                with open(latest_path, "w", encoding="utf-8") as f:
                    json.dump(checkpoint_data, f, indent=4, ensure_ascii=False)
            except Exception as e:
                logger.error(f"Failed to save checkpoint {checkpoint.step_id}: {e}")
                
        return file_path

    def load(self, workflow_id: str, step_id: str = "latest") -> Optional[WorkflowCheckpoint]:
        """Loads a checkpoint and verifies its integrity."""
        workflow_dir = self.state_dir / workflow_id
        file_path = workflow_dir / (f"step_{step_id}.json" if step_id != "latest" else "latest.json")
        
        if not file_path.exists():
            return None
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            
            stored_hmac = data.pop("hmac", "")
            calculated_hmac = self._calculate_hmac(data)
            
            if not hmac.compare_digest(stored_hmac, calculated_hmac):
                logger.error(f"Integrity check failed for checkpoint {workflow_id}/{step_id}!")
                raise ValueError("Checkpoint integrity verification failed (Tampering detected)")
            
            data["hmac"] = stored_hmac
            return WorkflowCheckpoint(**data)
        except Exception as e:
            logger.error(f"Failed to load checkpoint: {e}")
            return None

    def get_all_steps(self, workflow_id: str) -> List[str]:
        """Returns sorted list of step IDs for a workflow."""
        workflow_dir = self.state_dir / workflow_id
        if not workflow_dir.exists():
            return []
        
        steps = []
        for f in workflow_dir.glob("step_*.json"):
            steps.append(f.stem.replace("step_", ""))
        return sorted(steps)
