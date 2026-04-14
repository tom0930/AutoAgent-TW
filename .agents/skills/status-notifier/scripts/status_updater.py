import json
import argparse
import logging
import re
import shutil
from datetime import datetime
from pathlib import Path
import sys
import io
import os
import time

# Force UTF-8 for console output on Windows
if hasattr(sys.stdout, "detach"):
    sys.stdout = io.TextIOWrapper(
        sys.stdout.detach(), encoding="utf-8", errors="replace"
    )
    sys.stderr = io.TextIOWrapper(
        sys.stderr.detach(), encoding="utf-8", errors="replace"
    )

# Add script dir to path for imports
script_dir = Path(__file__).parent.resolve()
sys.path.append(str(script_dir))
# Add project root scripts dir
sys.path.append(str(script_dir.parent.parent.parent.parent / "scripts"))

try:
    import aa_constants
except ImportError:
    # Fallback if aa_constants is not in path yet
    import scripts.aa_constants as aa_constants

import roadmap_parser
import line_notifier


def update_status(
    task,
    next_goal,
    phase,
    total_phases,
    status="running",
    logs=None,
    repair_round=0,
    custom_mermaid="",
):
    version = "1.0.0"
    try:
        config_file = aa_constants.get_planning_dir() / "config.json"
        if config_file.exists():
            with open(config_file, "r", encoding="utf-8") as f:
                config = json.load(f)
                version = config.get("version", "1.0.0")
    except Exception:
        pass

    # [v1.7.2 Fix] Phase Persistence & Intelligence
    # If phase/total are defaults (0 or 1/5), try to read current state first
    state_file = aa_constants.get_state_dir() / "status_state.json"
    if (phase == 1 or phase == 0) and state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                # If we are just doing a heartbeat, persist the phase
                if phase <= 1:
                    phase = old_data.get("phase_num", phase)
                if total_phases <= 5:
                    total_phases = old_data.get("total_phases", total_phases)
        except Exception:
            pass

    # If still not set meaningfully, auto-detect from roadmap
    if phase <= 1:
        try:
            roadmap_file = aa_constants.get_planning_dir() / "ROADMAP.md"
            if roadmap_file.exists():
                with open(roadmap_file, "r", encoding="utf-8") as f:
                    content = f.read()

                    # Look for first unchecked phase
                    all_phases = re.findall(r"- \[ \] Phase (\d+):", content)
                    if all_phases:
                        phase = int(all_phases[0])
                    else:
                        # Maybe all checked, find last done
                        done_phases = re.findall(r"- \[X\] Phase (\d+):", content)
                        if done_phases:
                            phase = int(done_phases[-1])
        except Exception:
            pass

    # Ensure current working directory is z:\AutoAgent-TW or similar
    state_dir = aa_constants.get_state_dir()
    if not state_dir.exists():
        state_dir.mkdir(parents=True, exist_ok=True)

    # Critical Alert on Failure
    if status == "fail":
        line_notifier.send_line_notification(
            f"🚨 AutoAgent-TW Failure!\nPhase {phase}: {task}\nRepair Round: {repair_round}"
        )

    state_file = state_dir / "status_state.json"
    js_file = state_dir / "status_state.js"
    html_file = aa_constants.get_aa_home() / "status.html"

    # Generate roadmap mermaid or use custom
    mermaid_code = (
        custom_mermaid if custom_mermaid else roadmap_parser.get_roadmap_mermaid()
    )

    # --- Initialize default empty states ---
    scheduled_tasks = []
    hooks_config = {}
    predictions_data = []
    subagents_data = []
    log_list = logs.split(",") if logs else []

    # [v1.8.0] Professional Title Refinement
    display_task = task
    if "Stress Task" in task:
        display_task = f"Dashboard Performance Load Test ({task})"
    elif not task or task == "task":
        # Try to auto-detect from project context
        try:
            project_file = aa_constants.get_aa_home() / "PROJECT.md"
            if project_file.exists():
                with open(project_file, "r", encoding="utf-8") as f:
                    first_line = f.readline().strip()
                    if first_line.startswith("# "):
                        display_task = first_line[2:]
        except:
            display_task = "AutoAgent-TW Instance"

    # --- Load persistence data if files exist ---
    try:
        sched_file = state_dir / "scheduled_tasks.json"
        if sched_file.exists():
            with open(sched_file, "r", encoding="utf-8") as f:
                scheduled_tasks = json.load(f)
    except: pass

    try:
        hooks_file = state_dir / "hooks.json"
        if hooks_file.exists():
            with open(hooks_file, "r", encoding="utf-8") as f:
                hooks_config = json.load(f)
    except: pass

    try:
        predictions_file = state_dir / "predictions.json"
        if predictions_file.exists():
            with open(predictions_file, "r", encoding="utf-8") as f:
                predictions_data = json.load(f)
    except: pass

    # Load Subagents (Phase 1)
    subagents_dir = state_dir / "subagents"
    subagents_data = []
    if subagents_dir.exists():
        for f_path in subagents_dir.glob("*.json"):
            # Aggressive retry for reading subagent JSON (might be locked by child)
            for _ in range(3):
                try:
                    with open(f_path, "r", encoding="utf-8") as f:
                        subagents_data.append(json.load(f))
                    break
                except Exception:
                    time.sleep(0.1)

    # [v2.3.1 Feature] Execution History (Rolling Buffer 50)
    execution_history = []
    if state_file.exists():
        try:
            with open(state_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                execution_history = old_data.get("execution_history", [])
        except Exception:
            pass

    # Add current entry to history if task changed or status changed
    current_entry = {
        "timestamp": datetime.now().isoformat(),
        "task": display_task,
        "phase": f"P{phase}",
        "status": status,
        "repair_round": repair_round
    }

    # Only append if different from last entry to avoid spam
    if not execution_history or execution_history[0]["task"] != display_task or execution_history[0]["status"] != status:
        execution_history.insert(0, current_entry)

    # Cap at 50
    execution_history = execution_history[:50]

    import portalocker

    data = {
        "version": version,
        "current_task": display_task,
        "next_goal": next_goal,
        "phase_num": phase,
        "total_phases": total_phases,
        "status": status,
        "mermaid_code": mermaid_code,
        "logs": log_list,
        "repair_round": repair_round,
        "execution_history": execution_history, # New Field
        "scheduled_tasks": scheduled_tasks,
        "hooks": hooks_config,
        "predictions": predictions_data,
        "subagents": subagents_data,
        "timestamp": datetime.now().isoformat(),
        "last_interaction": datetime.now().isoformat(),
    }

    # 1. Update status_state.json, JS and Global Sync in ONE transaction
    lock_path = state_dir / "dashboard.lock"
    success = False
    max_lock_attempts = 200 # 20 seconds total
    for attempt in range(max_lock_attempts):
        try:
            with open(lock_path, "a") as f_lock:
                # Use non-blocking + manual retry to support all portalocker versions
                portalocker.lock(f_lock, portalocker.LOCK_EX | portalocker.LOCK_NB)
                
                # --- INTERNAL STATE ---
                def safe_atomic_write(target, content, is_json=True):
                    tmp = target.with_suffix(".tmp")
                    with open(tmp, "w", encoding="utf-8") as f:
                        if is_json: json.dump(content, f, indent=4, ensure_ascii=False)
                        else: f.write(content)
                        f.flush()
                        try: os.fsync(f.fileno())
                        except: pass
                    # Windows safe rename: might need retry or delete first
                    if target.exists():
                        try: os.replace(tmp, target)
                        except OSError:
                            # Fallback for extreme contention
                            import time
                            for _ in range(5):
                                try:
                                    time.sleep(0.01)
                                    os.replace(tmp, target)
                                    break
                                except: continue
                    else:
                        os.rename(tmp, target)

                safe_atomic_write(state_file, data)
                js_content = f"window.AA_STATUS = {json.dumps(data, indent=4, ensure_ascii=False)};"
                safe_atomic_write(js_file, js_content, is_json=False)

                # --- GLOBAL SYNC ---
                try:
                    global_public = Path(os.path.expandvars(r"%USERPROFILE%\.gemini\antigravity\dashboard\skills\public"))
                    if global_public.exists():
                        global_status = global_public / "aa-status.json"
                        safe_atomic_write(global_status, data)
                except Exception as e:
                    logging.warning(f"Warning: Failed to sync with global dashboard: {e}")
                success = True
                break # Lock acquired and tasks done
        except (portalocker.exceptions.LockException, OSError):
            # Lock is busy, wait and retry
            time.sleep(0.1)
    
    if not success:
        logging.error("❌ Update failed: Final lock failure after 20 seconds of contention.")

    # [v1.7.1 Fix] Data Inlining: Injecting directly into status.html to bypass CORS/File-access limits
    template_file = html_file
    if not template_file.exists():
        # Auto-recovery from skill templates
        source_template = script_dir.parent / "templates" / "status.html"
        if source_template.exists():
            try:
                shutil.copy2(source_template, template_file)
                logging.info(f"🔄 Recovered status.html from template: {source_template}")
            except Exception as e:
                logging.error(f"❌ Failed to recover status.html: {e}")

    if template_file.exists():
        try:
            with open(template_file, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Update existing payload or inject
            new_payload = f'<script id="status-data-payload">window.AA_STATUS = {json.dumps(data, indent=4, ensure_ascii=False)};</script>'
            
            # Use global dashboard lock for HTML too
            lock_path = state_dir / "dashboard.lock"
            with open(lock_path, "a") as f_lock:
                portalocker.lock(f_lock, portalocker.LOCK_EX)
                if '<script id="status-data-payload">' in html_content:
                    html_content = re.sub(
                        r'<script id="status-data-payload">.*?</script>',
                        new_payload,
                        html_content,
                        flags=re.DOTALL,
                    )
                else:
                    html_content = html_content.replace("</body>", f"{new_payload}\n</body>")

                # Atomic write for HTML template
                temp_html = template_file.with_suffix(".tmp.html")
                with open(temp_html, "w", encoding="utf-8") as f:
                    f.write(html_content)
                    f.flush()
                    try: os.fsync(f.fileno())
                    except: pass
                os.replace(temp_html, template_file)
            logging.info("✅ Data successfully inlined into status.html with locking")
        except Exception as e:
            logging.error(f"❌ Failed to inline data into HTML: {e}")

    print(f"Status updated: {task} (Phase {phase}/{total_phases})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Update AutoAgent-TW Status Notifier state."
    )
    parser.add_argument(
        "--task", type=str, required=True, help="Current task description"
    )
    parser.add_argument(
        "--next", type=str, default="None set", help="Next goal description"
    )
    parser.add_argument("--phase", type=int, default=1, help="Current phase number")
    parser.add_argument(
        "--total", type=int, default=115, help="Total phases (Default: 115)"
    )
    parser.add_argument(
        "--status",
        type=str,
        default="running",
        choices=["running", "done", "fail", "idle"],
        help="Current status",
    )
    parser.add_argument("--logs", type=str, help="Recent log lines (comma separated)")
    parser.add_argument(
        "--repair", type=int, default=0, help="Self-repair round (0..3)"
    )
    parser.add_argument(
        "--mermaid", type=str, default="", help="Custom mermaid diagram code"
    )

    args = parser.parse_args()
    update_status(
        args.task,
        args.next,
        args.phase,
        args.total,
        args.status,
        args.logs,
        args.repair,
        args.mermaid,
    )
