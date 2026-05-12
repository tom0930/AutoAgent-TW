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
    """AutoAgent-TW Graphify Orchestrator (v3.7.5)
    Manages debouncing, fingerprinting, and execution modes with post-processing sync.
    """
    def __init__(self, workspace=None):
        self.workspace = workspace or get_workspace()
        self.planning_dir = get_planning_dir()
        self.state_dir = get_state_dir()
        self.out_dir = self.planning_dir / "graphify-out"
        self.status_file = self.out_dir / "status.json"
        self.debounce_seconds = 600 # 10 minutes
        self.history_dir = self.planning_dir / "aa-history"
        
        # Optimization Toggles
        self.node_threshold = 5000
        self.default_includes = ["src", "lib", "core", "scripts", "openclaw", "gateway", "session", "skill"]
        self.default_excludes = ["tests", "node_modules", "build", "dist", ".git", "graphify-out", ".planning", "temp", "scratch"]

        # Ensure directories exist
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def _check_git_safety(self):
        """Ensure graphify-out is in .gitignore to prevent repo bloat."""
        gitignore_path = Path(self.workspace) / ".gitignore"
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            if "graphify-out/" not in content:
                print("[!] Git Safety Warning: graphify-out/ not found in .gitignore!")
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n# Graphify Cache\ngraphify-out/\n")
                print("[+] Auto-fixed: Added graphify-out/ to .gitignore.")

    def _get_target_paths(self):
        """Return existing core paths for selective indexing."""
        targets = []
        for p in self.default_includes:
            path = Path(self.workspace) / p
            if path.exists():
                targets.append(p)
        return targets

    def _sync_generated_files(self):
        """Relocate files from sub-directories (like src/graphify-out) to central out_dir."""
        targets = self._get_target_paths()
        for p in targets:
            src_out = Path(self.workspace) / p / "graphify-out"
            if src_out.exists():
                print(f"[Orchestrator] Relocating files from {src_out} to {self.out_dir}...")
                for f in src_out.iterdir():
                    if f.is_file():
                        dst = self.out_dir / f.name
                        shutil.copy2(f, dst)
        
        # Special check: if graphify ran in root but created a local graphify-out we didn't expect
        root_local_out = Path(self.workspace) / "graphify-out"
        if root_local_out.exists() and root_local_out.absolute() != self.out_dir.absolute():
            print(f"[Orchestrator] Syncing root-local cache {root_local_out} to {self.out_dir}...")
            for f in root_local_out.iterdir():
                if f.is_file():
                    shutil.copy2(f, self.out_dir / f.name)

    def get_fingerprint(self):
        """Generate a fingerprint of the codebase (files + mtimes)."""
        fingerprint_parts = []
        ignored = {".git", ".planning", ".agent-state", "graphify-out", "__pycache__", "node_modules", "venv", ".venv"}
        
        # Check for .graphifyignore
        ignore_file = Path(self.workspace) / ".graphifyignore"
        if ignore_file.exists():
            with open(ignore_file, "r") as f:
                ignored.update(line.strip() for line in f if line.strip() and not line.startswith("#"))

        try:
            for root, dirs, files in os.walk(self.workspace):
                dirs[:] = [d for d in dirs if d not in ignored and not d.startswith(".")]
                for f in files:
                    if f.startswith("."): continue
                    f_path = Path(root) / f
                    if f_path.suffix not in {".py", ".ts", ".js", ".cpp", ".h"}: continue
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
        """Refresh status and sync any newly generated files."""
        self._sync_generated_files()
        
        status = self.get_status()
        status.update(kwargs)
        status["last_seen"] = time.time()
        
        # Clear error if we are marking as completed
        if kwargs.get("status") == "completed":
            status.pop("error", None)
        
        # Calculate node count if graph.json exists
        graph_json = self.out_dir / "graph.json"
        if graph_json.exists():
            try:
                with open(graph_json, "r") as f:
                    data = json.load(f)
                    status["node_count"] = len(data.get("nodes", []))
            except: pass

        # Save to out_dir
        with open(self.status_file, "w") as f:
            json.dump(status, f, indent=2)

    def sync_reports(self):
        """Sync generated reports to aa-history for persistence."""
        report_src = self.out_dir / "GRAPH_REPORT.md"
        if report_src.exists():
            report_dst = self.history_dir / "GRAPH_REPORT.md"
            shutil.copy2(report_src, report_dst)
            print(f"[Orchestrator] Report persisted to {report_dst}")

    def _write_ignore_file(self):
        """Write .graphifyignore to the workspace root."""
        ignore_path = Path(self.workspace) / ".graphifyignore"
        lines = [
            "# Auto-generated by AutoAgent-TW Graphify Orchestrator",
            "tests/", "node_modules/", "build/", "dist/", ".git/", ".planning/",
            "graphify-out/", "temp/", "scratch/", "*.md", "*.txt", "*.json", "*.xlsx"
        ]
        ignore_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[+] .graphifyignore updated at {ignore_path}")

    def run(self, mode="update", background=True):
        """Execute the graphify update flow with post-processing."""
        self._check_git_safety()
        self._write_ignore_file()
        
        current_fp = self.get_fingerprint()
        status = self.get_status()
        
        # Debounce logic
        last_run = status.get("last_run", 0)
        if isinstance(last_run, str): last_run = 0
            
        last_fp = status.get("fingerprint", "")
        if time.time() - last_run < self.debounce_seconds and current_fp == last_fp:
            print("[Orchestrator] Codebase unchanged or debounced. Skipping.")
            return False

        print(f"[*] Starting Graphify {mode} update...")
        
        if mode == "full":
            cmd = ["graphify", "extract", str(self.workspace), "--backend", "gemini"]
        else:
            targets = self._get_target_paths()
            abs_targets = [str(Path(self.workspace) / t) for t in targets]
            # 'update' ignores -o, so we rely on post-processing move
            cmd = ["graphify", "update"] + abs_targets

        try:
            if background:
                # Spawn process then exit; status update will happen on next check or via side-effect
                # For robust backgrounding on Windows:
                subprocess.Popen(cmd, creationflags=0x08000000, close_fds=True)
                self.update_status(last_run=time.time(), fingerprint=current_fp, status="running", mode=mode)
                print(f"[Orchestrator] Background {mode} process spawned.")
            else:
                subprocess.run(cmd, check=True)
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
