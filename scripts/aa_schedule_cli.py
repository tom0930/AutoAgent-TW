import json
import argparse
import os
import sys
import subprocess
import signal
from pathlib import Path
from uuid import uuid4

# Path setup
PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATE_DIR = PROJECT_ROOT / ".agent-state"
TASKS_FILE = STATE_DIR / "scheduled_tasks.json"
DAEMON_SCRIPT = PROJECT_ROOT / "scripts" / "scheduler_daemon.py"
PID_FILE = STATE_DIR / "scheduler.pid"

STATE_DIR.mkdir(parents=True, exist_ok=True)

def load_tasks():
    if not TASKS_FILE.exists():
        return []
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No scheduled tasks found.")
        return
    
    print(f"\n{'ID':<36} {'Name':<20} {'Trigger':<10} {'Command':<30}")
    print("-" * 100)
    for t in tasks:
        print(f"{t['id']:<36} {t['name']:<20} {t['trigger_type']:<10} {t['command']:<30}")
    print("-" * 100)

def add_task(name, trigger, params, command):
    tasks = load_tasks()
    try:
        # Validate params
        param_dict = json.loads(params)
    except Exception as e:
        print(f"Error parsing params JSON: {e}")
        return

    new_task = {
        "id": str(uuid4()),
        "name": name,
        "trigger_type": trigger,
        "params": param_dict,
        "command": command
    }
    tasks.append(new_task)
    save_tasks(tasks)
    print(f"Task '{name}' added successfully. (ID: {new_task['id']})")

def remove_task(task_id):
    tasks = load_tasks()
    updated = [t for t in tasks if t['id'] != task_id and t['name'] != task_id]
    if len(updated) == len(tasks):
        print(f"No task found with ID/Name: {task_id}")
    else:
        save_tasks(updated)
        print(f"Task '{task_id}' removed.")

def start_daemon():
    if PID_FILE.exists():
        print("Daemon is possibly already running (PID file exists).")
        return

    print("Starting AutoAgent-TW Scheduler Daemon in background...")
    # Using subprocess.Popen with DETACHED_PROCESS for Windows backgrounding
    # Standard: CREATE_NEW_PROCESS_GROUP = 0x00000200, DETACHED_PROCESS = 0x00000008
    try:
        process = subprocess.Popen(
            [sys.executable, str(DAEMON_SCRIPT)],
            creationflags=0x00000008 | 0x00000200,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            close_fds=True,
            cwd=PROJECT_ROOT
        )
        with open(PID_FILE, "w") as f:
            f.write(str(process.pid))
        print(f"Daemon started with PID {process.pid}.")
    except Exception as e:
        print(f"Failed to start daemon: {e}")

def stop_daemon():
    if not PID_FILE.exists():
        print("No PID file found. Daemon might not be running.")
        return

    try:
        with open(PID_FILE, "r") as f:
            pid = int(f.read().strip())
        
        os.kill(pid, signal.SIGTERM)
        PID_FILE.unlink()
        print(f"Stopped daemon (PID {pid}).")
    except Exception as e:
        print(f"Failed to stop daemon: {e}")
        if PID_FILE.exists():
            PID_FILE.unlink()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AutoAgent-TW Scheduler CLI")
    subparsers = parser.add_subparsers(dest="subcommand")

    # List subcmd
    subparsers.add_parser("list", help="List all scheduled tasks")

    # Add subcmd
    add_p = subparsers.add_parser("add", help="Add a new task")
    add_p.add_argument("--name", required=True, help="Task name")
    add_p.add_argument("--trigger", choices=["cron", "interval"], default="interval", help="Trigger type")
    add_p.add_argument("--params", required=True, help="Trigger params in JSON format (e.g. '{\"minutes\": 10}')")
    add_p.add_argument("--command", required=True, help="Command string to execute (e.g. 'python scripts/test.py' or 'aa-progress')")

    # Remove subcmd
    rem_p = subparsers.add_parser("remove", help="Remove a task by ID or Name")
    rem_p.add_argument("task_id", help="UUID or Name of the task to remove")

    # Daemon control
    subparsers.add_parser("start", help="Start the scheduler daemon in background")
    subparsers.add_parser("stop", help="Stop the scheduler daemon")

    args = parser.parse_args()

    if args.subcommand == "list":
        list_tasks()
    elif args.subcommand == "add":
        add_task(args.name, args.trigger, args.params, args.command)
    elif args.subcommand == "remove":
        remove_task(args.task_id)
    elif args.subcommand == "start":
        start_daemon()
    elif args.subcommand == "stop":
        stop_daemon()
    else:
        parser.print_help()
