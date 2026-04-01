import subprocess
import logging
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

class ErrorAnalyzer:
    """Catches runtime execution errors and extracts actionable tracebacks for AI repair."""
    
    def __init__(self, timeout: int = 120, token_limit: int = 5000):
        self.timeout = timeout
        self.token_limit = token_limit
        
    def run_with_capture(self, cmd: List[str]) -> Dict[str, Any]:
        """Runs an arbitrary shell command (e.g. pytest, gcc) and captures all stdout/stderr."""
        logging.info(f"🚀 Running Sandbox Verification: {' '.join(cmd)}")
        try:
            # We strictly capture the output and prevent it from cascading into the active shell
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=self.timeout
            )
            
            return {
                "success": result.returncode == 0,
                "return_code": result.returncode,
                "stdout": result.stdout[:self.token_limit],  # Truncate to prevent token exhaustion
                "stderr": result.stderr[:self.token_limit],
            }
            
        except subprocess.TimeoutExpired:
            logging.error(f"⏳ Verification Timed Out ({self.timeout}s). Possible infinite loop or deadlock detected!")
            return {
                "success": False,
                "return_code": -1,
                "stdout": "Command timed out internally.",
                "stderr": f"Error: Command timed out after {self.timeout}s.\nAction required: Fix the deadlocked logic."
            }
            
        except Exception as e:
            logging.error(f"💣 Execution Crash: {e}")
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"System execution failed with generic error:\n{str(e)}"
            }

    def generate_repair_prompt(self, target_file: str, exec_result: Dict[str, Any]) -> str:
        """Translates the raw traceback into an actionable, strict prompt for the QA-Agent LLM."""
        if exec_result["success"]:
            return "No errors detected. Sandbox verification succeeded."

        # Typically Python exceptions go to stderr, while test frameworks (like pytest) write to stdout
        error_msg = exec_result["stderr"] if exec_result["stderr"].strip() else exec_result["stdout"]
        
        # Format the system prompt according to AutoAgent-TW's global constraint rules
        prompt = f"""You are an elite System Software/Firmware Engineer acting within the AutoAgent-TW AutoFix Engine.
Your objective is to debug and surgically repair the file `{target_file}`.
The code was executed within an isolated Git Sandbox but resulted in the following critical failure:

<test_execution_traceback_logs>
{error_msg}
</test_execution_traceback_logs>

## Your Mission Instructions:
1. **Identify the root cause**: Evaluate the traceback log step by step to identify the bug.
2. **Enforce Global Safety Constraints**:
   - C/C++: Never use raw new/delete or insecure formats (sprintf). Fallback to std::unique_ptr or std::format.
   - Python 3.10+: Force type hints and avoid os.system/eval.
   - Embedded: Ensure memory strictness (no dynamic allocations) if resolving firmware files.
3. **Produce a Surgical Patch**: Output ONLY the exact code modification. Do not write filler documentation.
4. **Resilience Awareness**: This branch will be rolled back automatically if your code fails again. Think before you commit.
"""
        return prompt
