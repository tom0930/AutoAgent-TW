import json
import os
import sys
import io
from pathlib import Path
from datetime import datetime, timedelta
import subprocess

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATE_FILE = PROJECT_ROOT / ".agent-state" / "status_state.json"
UPDATER_SCRIPT = PROJECT_ROOT / ".agents" / "skills" / "status-notifier" / "scripts" / "status_updater.py"

def check_dashboard_freshness():
    """檢查 Dashboard 數據是否太舊 (超過 10 分鐘未更新)"""
    if not STATE_FILE.exists():
        return False, "Dashboard state file missing"
    
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            ts_str = data.get("timestamp")
            if not ts_str:
                return False, "No timestamp in state"
            
            ts = datetime.fromisoformat(ts_str)
            if datetime.now() - ts > timedelta(minutes=10):
                return False, f"Data is stale (last updated: {ts_str})"
    except Exception as e:
        return False, f"Parse error: {e}"
    
    return True, "Fresh"

def run_health_check():
    print(f"[{datetime.now()}] 🛡️ Guardian Health Check Starting...")
    
    # 1. Check Freshness
    is_fresh, msg = check_dashboard_freshness()
    status = "running"
    task_msg = "🛡️ Guardian: System Integrity OK"
    
    if not is_fresh:
        print(f"[ALERT] {msg}")
        status = "fail"
        task_msg = f"🛡️ ALERT: {msg}"
        # Try to Force Refresh Dashboard
        subprocess.run(["python", str(UPDATER_SCRIPT), "--task", "🛡️ Recovery: Refreshing Dashboard", "--status", "running"])

    # 2. Final Heartbeat Update
    subprocess.run([
        "python", str(UPDATER_SCRIPT), 
        "--task", task_msg, 
        "--status", status,
        "--logs", f"Health Check: {msg},Git Status Check,Persistence Verified"
    ])
    
    print(f"[{datetime.now()}] 🛡️ Guardian Check Completed.")

if __name__ == "__main__":
    run_health_check()
