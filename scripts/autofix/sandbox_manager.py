import subprocess
import logging
from typing import Optional, Tuple

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class SandboxManager:
    """Manages Git branches, checkpoints, and merges for the AutoFix innovation sandbox."""
    
    def __init__(self, base_branch: str = "master"):
        self.base_branch = base_branch
        self.current_sandbox: Optional[str] = None
        
    def _run_git(self, *args) -> Tuple[int, str, str]:
        """Utility wrapper for executing Git commands."""
        cmd = ["git"] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        return result.returncode, result.stdout.strip(), result.stderr.strip()

    def create_sandbox(self, feature_name: str) -> bool:
        """Creates and checks out a new isolated branch for innovation or fixes."""
        branch_name = f"auto-fix/{feature_name}"
        # Ensure we are on the stable base branch first
        self._run_git("checkout", self.base_branch)
        
        # Create and switch to the new branch
        code, out, err = self._run_git("checkout", "-b", branch_name)
        if code == 0:
            self.current_sandbox = branch_name
            logging.info(f"✅ Sandbox created and isolated: {branch_name}")
            return True
        
        # Branch might already exist
        if "already exists" in err:
            logging.warning(f"⚠️ Branch {branch_name} already exists. Attempting to switch and hard reset.")
            self._run_git("checkout", branch_name)
            self._run_git("reset", "--hard", f"{self.base_branch}")
            self.current_sandbox = branch_name
            return True
            
        logging.error(f"❌ Failed to create sandbox: {err}")
        return False

    def create_checkpoint(self, message: str = "chore: autofix checkpoint") -> bool:
        """Create a safe Git commit acting as an anchor before attempting high-risk modifications."""
        self._run_git("add", ".")
        code, out, err = self._run_git("commit", "-m", message)
        
        if "nothing to commit" in out or "nothing to commit" in err:
            logging.info("ℹ️ Working directory clean. No new checkpoint required.")
            return True
        
        if code == 0:
            logging.info(f"✅ Safe point checkpointed: {message}")
            return True
            
        logging.error(f"❌ Failed to create checkpoint: {err}")
        return False

    def rollback_checkpoint(self, steps: int = 1) -> bool:
        """Executes a hard reset to n-steps backward when AI is trapped in an infinitely failing repair loop."""
        code, out, err = self._run_git("reset", "--hard", f"HEAD~{steps}")
        if code == 0:
            logging.warning(f"🔙 Emergency Rollback executed. Reverted {steps} steps in history.")
            return True
            
        logging.error(f"❌ Emergency Rollback failed: {err}")
        return False

    def abort_sandbox(self) -> bool:
        """Discards the entire sandbox environment, deletes the branch and resets state."""
        if not self.current_sandbox:
            logging.info("ℹ️ No active sandbox to abort.")
            return True
        
        # Nuke local changes
        self._run_git("reset", "--hard")
        self._run_git("clean", "-fd")
        self._run_git("checkout", self.base_branch)
        
        code, out, err = self._run_git("branch", "-D", self.current_sandbox)
        if code == 0:
            logging.info(f"🗑️ Sandbox {self.current_sandbox} fully obliterated.")
            self.current_sandbox = None
            return True
            
        logging.error(f"❌ Failed to delete branch {self.current_sandbox}: {err}")
        return False

    def merge_sandbox(self, squash: bool = True) -> bool:
        """Commit the changes and merge the successful sandbox back safely into the base branch."""
        if not self.current_sandbox:
            logging.error("❌ No active sandbox to merge.")
            return False
            
        # Commit any dangling artifacts
        self.create_checkpoint("feat(autofix): finalize changes before merge")
            
        # Switch to stable master
        self._run_git("checkout", self.base_branch)
        
        merge_args = ["merge", "--squash"] if squash else ["merge", "--no-ff"]
        code, out, err = self._run_git(*(merge_args + [self.current_sandbox]))
        
        if code == 0:
            if squash:
                # Squash requires explicit commit afterwards
                self._run_git("commit", "-m", f"feat(autofix): Integrate innovation from {self.current_sandbox}")
            logging.info(f"🎉 Successfully integrated {self.current_sandbox} back into {self.base_branch}!")
            # Clean up the sandbox branch
            self._run_git("branch", "-D", self.current_sandbox)
            self.current_sandbox = None
            return True
            
        # Fallback Mechanism: Rollback merge if conflicts arise.
        logging.error(f"⚠️ Merge Conflict Detected! Aborting branch integration. Human intervention required.\n{err}\n{out}")
        self._run_git("merge", "--abort")
        self._run_git("checkout", self.current_sandbox)
        return False
