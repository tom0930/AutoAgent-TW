import json
import subprocess
import sys
from pathlib import Path
from repair_loop_strategy import RepairStrategy

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = PROJECT_ROOT / ".agent-state"
HISTORY_FILE = STATE_DIR / "repair_history.json"

def load_history():
    if not HISTORY_FILE.exists():
        return {"history": []}
    with open(HISTORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def run_adaptive_fix(current_failures, modified_files):
    history_data = load_history()
    strategy = RepairStrategy(max_rounds=6)
    
    # Check if we should even start or continue
    should, reason = strategy.should_continue(history_data)
    print(f"[REPAIR MANAGER] {reason}")
    
    if not should:
        print("[REPAIR MANAGER] Adaptive loop Terminated.")
        return False

    # Simulate aa-fix action
    print(f"[REPAIR MANAGER] Executing next repair round (Round {len(history_data['history']) + 1})...")
    # For now, we mock the 'aa-fix' command as a status update
    # In practice, this would call /aa-fix
    subprocess.run([
        sys.executable, str(PROJECT_ROOT / ".agents" / "skills" / "status-notifier" / "scripts" / "status_updater.py"),
        "--task", f"Adaptive Fix: Round {len(history_data['history']) + 1}",
        "--status", "running",
        "--logs", f"History Diversity: {strategy.calculate_diversity(history_data['history']):.2f}"
    ])
    
    # Record this round after it's done (mocked data for now)
    new_round = {
        "id": len(history_data['history']) + 1,
        "failure_count": current_failures,
        "modified_files": modified_files,
        "timestamp": str(Path(__file__).stat().st_mtime) # dummy
    }
    history_data['history'].append(new_round)
    
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history_data, f, indent=2)
        
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python adaptive_fix_wrapper.py <failure_count> <modified_files_comma_separated>")
        sys.exit(1)
    
    failures = int(sys.argv[1])
    files = sys.argv[2].split(",")
    run_adaptive_fix(failures, files)
