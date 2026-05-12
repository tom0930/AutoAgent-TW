import os
import sys
import time
import json
import hashlib
import subprocess
import shutil
from pathlib import Path

# Import AA constants
sys.path.append(os.path.dirname(__file__))
from aa_constants import get_workspace, get_planning_dir, get_state_dir

class GraphifyOrchestrator:
    """AutoAgent-TW Graphify Orchestrator (v3.7.2)
    Manages debouncing, fingerprinting, and execution modes.
    """
    def __init__(self, workspace=None):
        self.workspace = workspace or get_workspace()
        self.planning_dir = get_planning_dir()
        self.state_dir = get_state_dir()
        self.out_dir = self.planning_dir / "graphify-out"
        self.status_file = self.state_dir / "graphify_orchestrator_status.json"
        self.debounce_seconds = 600 # 10 minutes
        self.history_dir = self.planning_dir / "aa-history"
        
        # Ensure directories exist
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def get_fingerprint(self):
        """Generate a fingerprint of the codebase (files + mtimes)."""
        fingerprint_parts = []
        ignored = {".git", ".planning", ".agent-state", "graphify-out", "__pycache__", "node_modules", "venv", ".venv"}
        
        # Check for .graphifyignore
        ignore_file = self.planning_dir / ".graphifyignore"
        if ignore_file.exists():
            with open(ignore_file, "r") as f:
                ignored.update(line.strip() for line in f if line.strip() and not line.startswith("#"))

        try:
            for root, dirs, files in os.walk(self.workspace):
                dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
                for f in files:
                    if f.startswith("."): continue
                    f_path = Path(root) / f
                    try:
                        mtime = f_path.stat().st_mtime
                        fingerprint_parts.append(f"{f_path.relative_to(self.workspace)}:{mtime}")
                    except (OSError, ValueError):
                        continue
        except Exception as e:
            print(f"[Orchestrator] Fingerprint error: {e}")
            
        return hashlib.md5("\n".join(sorted(fingerprint_parts)).encode()).hexdigest()

    def get_status(self):
        if self.status_file.exists():
            try:
                with open(self.status_file, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def update_status(self, **kwargs):
        status = self.get_status()
        status.update(kwargs)
        status["last_seen"] = time.time()
        
        # Save to state dir (persistent across sessions)
        with open(self.status_file, "w") as f:
            json.dump(status, f, indent=2)
            
        # Also save to out_dir for local context
        local_status = self.out_dir / "status.json"
        with open(local_status, "w") as f:
            json.dump(status, f, indent=2)

    def sync_reports(self):
        """Sync generated reports to aa-history."""
        report_src = self.out_dir / "GRAPH_REPORT.md"
        if report_src.exists():
            report_dst = self.history_dir / "GRAPH_REPORT.md"
            shutil.copy2(report_src, report_dst)
            print(f"[Orchestrator] Report synced to {report_dst}")

    def run(self, mode="smart", background=True):
        """Execute the graphify update flow."""
        current_fp = self.get_fingerprint()
        status = self.get_status()
        
        # Debounce logic
        last_run = status.get("last_run", 0)
        last_fp = status.get("fingerprint", "")
        
        if time.time() - last_run < self.debounce_seconds and current_fp == last_fp:
            print("[Orchestrator] Codebase unchanged. Skipping update.")
            return False

        print(f"[Orchestrator] Starting {mode} update...")
        
        if mode == "full":
            cmd = ["graphify", "extract", str(self.workspace), "--backend", "gemini"]
        else:
            # Smart mode uses 'update' (AST-only, fast, no API cost)
            cmd = ["graphify", "update", str(self.workspace)]

        try:
            if background:
                CREATE_NO_WINDOW = 0x08000000
                # Use a small wrapper to sync after background run finishes
                cmd_str = json.dumps(cmd)
                sync_script = f"import subprocess; subprocess.run({cmd_str}, check=True); from graphify_orchestrator import GraphifyOrchestrator; GraphifyOrchestrator().sync_reports()"
                
                subprocess.Popen([sys.executable, "-c", sync_script], 
                               cwd=self.planning_dir, 
                               creationflags=CREATE_NO_WINDOW,
                               close_fds=True)
                
                self.update_status(last_run=time.time(), fingerprint=current_fp, status="running", mode=mode)
                print(f"[Orchestrator] Background {mode} process + sync spawned in {self.planning_dir}")
            else:
                subprocess.run(cmd, cwd=self.planning_dir, check=True)
                self.update_status(last_run=time.time(), fingerprint=current_fp, status="completed", mode=mode)
                self.sync_reports()
            return True
        except Exception as e:
            print(f"[Orchestrator] Execution failed: {e}")
            self.update_status(status="failed", error=str(e))
            return False

if __name__ == "__main__":
    orch = GraphifyOrchestrator()
    orch.run(background=False)
