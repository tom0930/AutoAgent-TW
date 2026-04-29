import subprocess
import logging
from typing import Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ValidationGate:
    """
    Acts as the final barrier before integrating parallel execution results.
    Runs defined hooks (e.g., tests, linters) to ensure semantic correctness.
    """
    
    @classmethod
    def run_checks(cls, hooks: list = None) -> Tuple[bool, Dict[str, Any]]:
        """
        Runs validation hooks. Returns (Success, Payload).
        Payload contains stdout, stderr, and git diff on failure to be used in Reflection Loop.
        """
        if hooks is None:
            # Default hooks for testing
            hooks = [
                ["python", "-m", "pytest", "tests/"]
            ]
            
        success = True
        payload = {"error_log": "", "diff": ""}
        
        for hook in hooks:
            logger.info(f"[ValidationGate] Running hook: {' '.join(hook)}")
            try:
                result = subprocess.run(hook, capture_output=True, text=True, check=True)
                logger.debug(f"[ValidationGate] Hook succeeded: {result.stdout}")
            except subprocess.CalledProcessError as e:
                logger.error(f"[ValidationGate] Hook failed: {e.cmd}")
                success = False
                payload["error_log"] = e.stderr or e.stdout
                break
                
        if not success:
            # Capture the current staged diff
            try:
                diff_result = subprocess.run(["git", "diff", "--cached"], capture_output=True, text=True, check=True)
                payload["diff"] = diff_result.stdout
            except Exception as diff_e:
                payload["diff"] = f"Failed to capture diff: {diff_e}"
                
        return success, payload
