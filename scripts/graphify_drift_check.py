import os
import json
import time
import subprocess
from pathlib import Path

def get_git_head():
    try:
        return subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip()
    except:
        return None

def check_drift():
    status_path = Path(".planning/graphify-out/status.json")
    if not status_path.exists():
        print("[!] No Graphify status found. Recommendation: Run 'aa-graphify build'")
        return

    try:
        with open(status_path, 'r', encoding='utf-8') as f:
            status = json.load(f)
    except Exception as e:
        print(f"[!] Failed to read status: {e}")
        return

    last_run = status.get("last_run", 0)
    last_mode = status.get("mode", "unknown")
    
    # 1. Time-based drift (e.g., > 24 hours)
    hours_since = (time.time() - last_run) / 3600
    if hours_since > 24:
        print(f"[⚠️] Graph is stale ({hours_since:.1f} hours old).")
    
    # 2. Potential File-based drift (simplified check)
    # In a real scenario, we'd compare fingerprints, but here we just check if it's running
    if status.get("status") == "running":
        print("[*] Graphify update is currently in progress...")
        return

    print(f"[+] Knowledge Graph Status: {status.get('status', 'OK')}")
    print(f"[+] Last Update Mode: {last_mode}")
    print(f"[+] Fingerprint: {status.get('fingerprint', 'N/A')[:12]}")

if __name__ == "__main__":
    check_drift()
