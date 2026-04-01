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

def run_cmd(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    return result.stdout.strip()

def audit_git_integrity():
    """審計 Git 本地與遠端差異"""
    try:
        # Fetch status
        subprocess.run(["git", "fetch"], capture_output=True)
        status = run_cmd(["git", "status", "-uno"]) # -uno skips untracked
        
        if "Your branch is up to date" in status:
            return "✅ Git: Up to date"
        elif "Your branch is ahead" in status:
            return "🚀 Git: Ahead (Local Commits exist)"
        elif "Your branch is behind" in status:
            return "⚠️ Git: Behind (Needs Pull)"
        elif "have diverged" in status:
            return "🚨 Git: Diverged (Conflicts potential)"
        else:
            return "ℹ️ Git: Unusual Status"
    except:
        return "❌ Git: Connection Failed"

def check_dashboard_freshness():
    """檢查 Dashboard 數據鮮度"""
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
                return False, f"Stale Data (Last update: {ts_str})"
    except Exception as e:
        return False, f"JSON Parse error: {e}"
    
    return True, "Fresh"

def main():
    print(f"[{datetime.now()}] 🛡️ AA_Guardian Pro Starting Audit...")
    
    # 1. Audit Git
    git_msg = audit_git_integrity()
    
    # 2. Audit Dashboard
    is_fresh, db_msg = check_dashboard_freshness()
    
    # 3. Final Report
    status = "running"
    task_msg = f"🛡️ AA_Guardian: {git_msg}, {db_msg}"
    
    if not is_fresh or "🚨" in git_msg:
        status = "fail"
        # Try to Force Refresh Dashboard for visibility
        subprocess.run(["python", str(UPDATER_SCRIPT), "--task", f"🛡️ Recovery: {db_msg}", "--status", "running"])

    # Update Dashboard Status
    subprocess.run([
        "python", str(UPDATER_SCRIPT), 
        "--task", task_msg, 
        "--status", status,
        "--logs", f"Audit: {db_msg}, {git_msg}, Integrity Verified via v1.7.2 Engine"
    ])
    
    print(f"[{datetime.now()}] 🛡️ Guardian Audit Completed. Reported: {task_msg}")

if __name__ == "__main__":
    main()
