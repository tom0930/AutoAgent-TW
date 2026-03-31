import subprocess
import sys
import os
import re
from pathlib import Path

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
UPDATER_SCRIPT = PROJECT_ROOT / ".agents" / "skills" / "status-notifier" / "scripts" / "status_updater.py"

def update_status(step_name, status, log_msg=""):
    if UPDATER_SCRIPT.exists():
        subprocess.run([
            sys.executable, str(UPDATER_SCRIPT),
            "--task", f"Chain: {step_name}",
            "--status", status,
            "--logs", log_msg
        ])

def execute_chain(chain_str):
    # Regex to split while keeping operators: &&, ||, |
    # We want to match: (cmd) (op) (cmd) (op) ...
    # This is a simplification. For robust parsing we'd use a real tokenizer.
    parts = re.split(r'(\s+&&\s+|\s+\|\|\s+|\s+\|\s+)', chain_str)
    
    current_cmd = parts[0].strip()
    last_success = True
    
    print(f"\n[ORCHESTRATOR] Starting chain: {chain_str}")
    update_status("Starting", "running", f"Full Chain: {chain_str}")
    
    # Initial command execution
    last_success = run_step(current_cmd)
    
    # Process subsequent pairs: (operator, command)
    for i in range(1, len(parts), 2):
        operator = parts[i].strip()
        next_cmd = parts[i+1].strip()
        
        should_run = False
        if operator == "&&":
            should_run = last_success
        elif operator == "||":
            should_run = not last_success
        elif operator == "|":
            should_run = True
        
        if should_run:
            print(f"[ORCHESTRATOR] Operator '{operator}' triggered: {next_cmd}")
            last_success = run_step(next_cmd)
        else:
            print(f"[ORCHESTRATOR] Skipping '{next_cmd}' (Operator '{operator}' condition not met)")

    print("[ORCHESTRATOR] Chain execution complete.\n")
    update_status("Finished", "done", "Execution chain completed.")

def run_step(cmd):
    print(f"  > Step: {cmd}")
    update_status(cmd, "running", "Executing step...")
    
    try:
        # Run the command and wait for completion
        # Use shell=True for 'aa-' aliases
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"    SUCCESS (code {result.returncode})")
            update_status(cmd, "done", f"Step completed successfully (code {result.returncode}).")
            return True
        else:
            print(f"    FAILED (code {result.returncode})")
            update_status(cmd, "fail", f"Step failed (code {result.returncode}). Error: {result.stderr[:200]}")
            return False
            
    except Exception as e:
        print(f"    EXCEPTION: {e}")
        update_status(cmd, "fail", f"Exception: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python aa_chain_orchestrator.py \"cmd1 && cmd2 || cmd3\"")
        sys.exit(1)
    
    full_chain = " ".join(sys.argv[1:])
    execute_chain(full_chain)
