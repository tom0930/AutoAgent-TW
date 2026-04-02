import json
import argparse
import logging
from datetime import datetime
from pathlib import Path
import sys
import io

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, 'detach'):
    sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding='utf-8', errors='replace')

# Add script dir to path for imports
sys.path.append(str(Path(__file__).parent))
import roadmap_parser
import line_notifier

def update_status(task, next_goal, phase, total_phases, status="running", logs=None, repair_round=0, custom_mermaid=""):
    version = "1.0.0"
    try:
        config_file = Path(".planning/config.json")
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                version = config.get("version", "1.0.0")
    except:
        pass

    # [v1.7.2 Fix] Phase Persistence & Intelligence
    # If phase/total are defaults (0 or 1/5), try to read current state first
    state_file = Path(".agent-state/status_state.json")
    if (phase == 1 or phase == 0) and state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                # If we are just doing a heartbeat, persist the phase
                if phase <= 1:
                    phase = old_data.get("phase_num", phase)
                if total_phases <= 5:
                    total_phases = old_data.get("total_phases", total_phases)
        except: pass

    # If still not set meaningfully, auto-detect from roadmap
    if phase <= 1:
        try:
            roadmap_file = Path(".planning/ROADMAP.md")
            if roadmap_file.exists():
                with open(roadmap_file, "r", encoding="utf-8") as f:
                    content = f.read()
                    import re
                    # Look for first unchecked phase
                    all_phases = re.findall(r'- \[ \] Phase (\d+):', content)
                    if all_phases:
                        phase = int(all_phases[0])
                    else:
                        # Maybe all checked, find last done
                        done_phases = re.findall(r'- \[X\] Phase (\d+):', content)
                        if done_phases:
                            phase = int(done_phases[-1])
        except: pass

    # Ensure current working directory is z:\AutoAgent-TW or similar
    state_dir = Path(".agent-state")
    if not state_dir.exists():
        state_dir.mkdir(parents=True, exist_ok=True)
    
    # Critical Alert on Failure
    if status == "fail":
        line_notifier.send_line_notification(f"🚨 AutoAgent-TW Failure!\nPhase {phase}: {task}\nRepair Round: {repair_round}")
    
    state_file = state_dir / "status_state.json"
    js_file = state_dir / "status_state.js"
    
    
    # Generate roadmap mermaid or use custom
    mermaid_code = custom_mermaid if custom_mermaid else roadmap_parser.get_roadmap_mermaid()
    
    # Parse logs
    log_list = logs.split(",") if logs else []
    
    # Load Scheduled Tasks
    sched_file = state_dir / "scheduled_tasks.json"
    scheduled_tasks = []
    if sched_file.exists():
        try:
            with open(sched_file, "r", encoding="utf-8") as f:
                scheduled_tasks = json.load(f)
        except: pass

    # Load Hooks
    hooks_file = state_dir / "hooks.json"
    hooks_config = {}
    if hooks_file.exists():
        try:
            with open(hooks_file, "r", encoding="utf-8") as f:
                hooks_config = json.load(f)
        except: pass

    # Load Predictions (Phase 5)
    predictions_file = state_dir / "predictions.json"
    predictions_data = []
    if predictions_file.exists():
        try:
            with open(predictions_file, "r", encoding="utf-8") as f:
                predictions_data = json.load(f)
        except: pass

    data = {
        "version": version,
        "current_task": task,
        "next_goal": next_goal,
        "phase_num": phase,
        "total_phases": total_phases,
        "status": status,
        "mermaid_code": mermaid_code,
        "logs": log_list,
        "repair_round": repair_round,
        "scheduled_tasks": scheduled_tasks,
        "hooks": hooks_config,
        "predictions": predictions_data,
        "timestamp": datetime.now().isoformat()
    }
    
    # Write JSON
    with open(state_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    
    # Write JS (for local browser preview without CORS) - Legacy fallback
    with open(js_file, "w", encoding="utf-8") as f:
        f.write(f"window.AA_STATUS = {json.dumps(data, indent=4, ensure_ascii=False)};")
    
    # [v1.7.1 Fix] Data Inlining: Injecting directly into status.html to bypass CORS/File-access limits
    template_file = Path(__file__).parent.parent / "templates" / "status.html"
    if template_file.exists():
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                html_content = f.read()
            
            # Find the script tag for data and replace its content
            import re
            data_json = json.dumps(data, indent=4, ensure_ascii=False)
            new_payload = f'<script id="status-data-payload">window.AA_STATUS = {data_json};</script>'
            
            if '<script id="status-data-payload">' in html_content:
                # Update existing payload
                html_content = re.sub(
                    r'<script id="status-data-payload">.*?</script>',
                    new_payload,
                    html_content,
                    flags=re.DOTALL
                )
            else:
                # Inject before </body>
                html_content = html_content.replace('</body>', f'{new_payload}\n</body>')
            
            with open(template_file, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info("✅ Data successfully inlined into status.html")
        except Exception as e:
            logging.error(f"❌ Failed to inline data into HTML: {e}")
    
    print(f"Status updated: {task} (Phase {phase}/{total_phases})")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update AutoAgent-TW Status Notifier state.")
    parser.add_argument("--task", type=str, required=True, help="Current task description")
    parser.add_argument("--next", type=str, default="None set", help="Next goal description")
    parser.add_argument("--phase", type=int, default=1, help="Current phase number")
    parser.add_argument("--total", type=int, default=115, help="Total phases (Default: 115)")
    parser.add_argument("--status", type=str, default="running", choices=["running", "done", "fail", "idle"], help="Current status")
    parser.add_argument("--logs", type=str, help="Recent log lines (comma separated)")
    parser.add_argument("--repair", type=int, default=0, help="Self-repair round (0..3)")
    parser.add_argument("--mermaid", type=str, default="", help="Custom mermaid diagram code")
    
    args = parser.parse_args()
    update_status(args.task, args.next, args.phase, args.total, args.status, args.logs, args.repair, args.mermaid)
