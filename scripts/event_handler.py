import json
import subprocess
import os
import sys
from pathlib import Path
from datetime import datetime

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = PROJECT_ROOT / ".agent-state"
HOOKS_FILE = STATE_DIR / "hooks.json"
LOG_DIR = PROJECT_ROOT / ".agents" / "logs"
LOG_FILE = LOG_DIR / "events.log"

STATE_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

def log_event(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] [EVENT] {msg}"
    print(formatted)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(formatted + "\n")

def handle_event(event_name):
    if not HOOKS_FILE.exists():
        log_event(f"No hooks.json found. Skipping {event_name}")
        return

    try:
        with open(HOOKS_FILE, "r", encoding="utf-8") as f:
            hooks_config = json.load(f)
        
        event_actions = hooks_config.get("on", {}).get(event_name, [])
        if not event_actions:
            log_event(f"No actions defined for {event_name}.")
            return

        log_event(f"Triggering {len(event_actions)} actions for {event_name}...")
        for action in event_actions:
            log_event(f"Executing: {action}")
            # Background execution to not block the caller (like git commit)
            # Use shell=True for 'aa-' command aliases or full commands
            subprocess.Popen(
                action,
                shell=True,
                cwd=PROJECT_ROOT,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            
    except Exception as e:
        log_event(f"Error handling event {event_name}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python event_handler.py <event_name>")
        sys.exit(1)
    
    event_to_trigger = sys.argv[1]
    handle_event(event_to_trigger)
