import json
import argparse
from datetime import datetime
from pathlib import Path
import sys

# Add script dir to path for imports
sys.path.append(str(Path(__file__).parent))
import roadmap_parser

def update_status(task, next_goal, phase, total_phases, status="running"):
    # Ensure current working directory is z:\AutoAgent-TW or similar
    state_dir = Path(".agent-state")
    if not state_dir.exists():
        state_dir.mkdir(parents=True, exist_ok=True)
    
    state_file = state_dir / "status_state.json"
    js_file = state_dir / "status_state.js"
    
    # Generate roadmap mermaid
    mermaid_code = roadmap_parser.get_roadmap_mermaid()
    
    data = {
        "current_task": task,
        "next_goal": next_goal,
        "phase_num": phase,
        "total_phases": total_phases,
        "status": status,
        "mermaid_code": mermaid_code,
        "timestamp": datetime.now().isoformat()
    }
    
    # Write JSON
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Write JS (for local browser preview without CORS)
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(f"window.AA_STATUS = {json.dumps(data, indent=4, ensure_ascii=False)};")
    
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
