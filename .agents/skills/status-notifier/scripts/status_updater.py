import json
import argparse
from datetime import datetime
from pathlib import Path

def update_status(task, next_goal, phase, total_phases, status="running"):
    # Ensure current working directory is z:\AutoAgent-TW or similar
    # or use absolute paths for consistency
    state_dir = Path(".agent-state")
    if not state_dir.exists():
        state_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = state_dir / "status_state.json"
    
    data = {
        "current_task": task,
        "next_goal": next_goal,
        "phase_num": phase,
        "total_phases": total_phases,
        "status": status,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    print(f"Status updated: {task} (Phase {phase}/{total_phases})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update AutoAgent-TW Status Notifier state.")
    parser.add_argument("--task", type=str, required=True, help="Current task description")
    parser.add_argument("--next", type=str, default="None set", help="Next goal description")
    parser.add_argument("--phase", type=int, default=1, help="Current phase number")
    parser.add_argument("--total", type=int, default=5, help="Total phases")
    parser.add_argument("--status", type=str, default="running", choices=["running", "done", "fail", "idle"], help="Current status")
    
    args = parser.parse_args()
    update_status(args.task, args.next, args.phase, args.total, args.status)
