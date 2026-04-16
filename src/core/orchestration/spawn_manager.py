import subprocess
import json
import uuid
import os
import sys
import time
import atexit
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Global registry for active processes (PID: AgentProcess)
_ACTIVE_SUBAGENTS: List['AgentProcess'] = []

def cleanup_all_agents():
    """Safety net to kill all subagents on master exit."""
    count = 0
    for agent in _ACTIVE_SUBAGENTS[:]: 
        if agent.process and agent.process.poll() is None:
            agent.terminate()
            count += 1
    if count > 0:
        print(f"RVA Cleanup: Terminated {count} dangling sub-agents.")

atexit.register(cleanup_all_agents)

def get_iso_time():
    return datetime.now().isoformat()


class AgentProcess:
    """
    Manages the lifecycle of a sub-agent process in AutoAgent-TW v1.9.0.
    Ensures safe spawning, status tracking, and resource isolation.
    """

    def __init__(
        self,
        task_name: str,
        parent_id: str = "main",
        budget_tokens: int = 10000,
        risk_limit: int = 3,
    ):
        self.agent_id = str(uuid.uuid4())[:8]
        self.task_name = task_name
        self.parent_id = parent_id
        self.budget_tokens = budget_tokens
        self.risk_limit = risk_limit
        self.start_time = time.time()
        self.status = "pending"
        self.progress = 0
        self.process: Optional[subprocess.Popen] = None

        # State paths
        self.state_dir = Path(".agent-state/subagents")
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.state_file = self.state_dir / f"{self.agent_id}.json"

        self._initialize_state()

    def _initialize_state(self):
        """Creates initial status file for the sub-agent."""
        data = {
            "id": self.agent_id,
            "parent_id": self.parent_id,
            "task": self.task_name,
            "status": "pending",
            "progress": 0,
            "start_time": get_iso_time(),
            "budget_tokens": self.budget_tokens,
            "risk_limit": self.risk_limit,
            "logs": ["Process initialized."],
            "result": None,
        }
        self._write_state(data)

    def _write_state(self, data: Dict[str, Any]):
        """Writes state to JSON file with atomic-like overwrite."""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def spawn(self, command: list, env_ovrides: Optional[dict] = None):
        """
        Spawns the process using subprocess.Popen with Job Object protection.
        """
        from src.utils.win32_job import process_job

        env = os.environ.copy()
        if env_ovrides:
            env.update(env_ovrides)

        # Add AGENT_ID and inheritance values to env
        env["AA_SUBAGENT_ID"] = self.agent_id
        env["AA_PARENT_ID"] = self.parent_id
        env["AA_BUDGET_TOKENS"] = str(self.budget_tokens)
        env["AA_RISK_LIMIT"] = str(self.risk_limit)

        creationflags = 0
        if sys.platform == "win32":
            # 0x08000000 = CREATE_NO_WINDOW (Hides console but keeps process in job group)
            # 0x00000008 = DETACHED_PROCESS (REMOVED: Source of zombies)
            creationflags = 0x08000000

        try:
            self.process = subprocess.Popen(
                command,
                env=env,
                creationflags=creationflags,
                stdout=subprocess.DEVNULL, # Don't block on output to avoid memory build-up
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            
            # Securely link to parent lifecycle via Job Object
            if self.process:
                process_job.add_pid(self.process.pid)
                _ACTIVE_SUBAGENTS.append(self)

            self.status = "running"
            self.update_progress(
                10, f"Process spawned successfully (PID: {self.process.pid})."
            )
        except Exception as e:
            self.status = "fail"
            self.update_progress(0, f"Spawn failed: {str(e)}")
            raise

    def __del__(self):
        """Auto-terminate on object destruction."""
        self.terminate()

    def update_progress(self, progress: int, log_entry: str):
        """Updates the local state file for dashboard polling."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["progress"] = progress
                data["status"] = self.status
                data["logs"].append(f"[{get_iso_time()}] {log_entry}")
                if progress >= 100:
                    data["status"] = "done"
                    data["end_time"] = get_iso_time()
                self._write_state(data)
            except Exception:
                pass

    def terminate(self):
        """Forcefully terminates the process."""
        if self.process:
            try:
                if self.process.poll() is None:
                    self.process.terminate()
                    self.process.wait(timeout=2)
            except Exception:
                try:
                    self.process.kill()
                except:
                    pass
            self.status = "terminated"
            if self in _ACTIVE_SUBAGENTS:
                _ACTIVE_SUBAGENTS.remove(self)
            self._write_state_final() 

    def _write_state_final(self):
        """Last gasp update to state file."""
        if self.state_file.exists():
            try:
                with open(self.state_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                data["status"] = self.status
                data["logs"].append(f"[{get_iso_time()}] Process cleaned up.")
                self._write_state(data)
            except Exception:
                pass


if __name__ == "__main__":
    # Internal component test
    print(f"Testing SpawnManager (UUID: {uuid.uuid4()})")
    mgr = AgentProcess("Self-Test Task")
    print(f"Agent ID: {mgr.agent_id}")
