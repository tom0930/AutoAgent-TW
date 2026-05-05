import os
import sys
import argparse
import time
import shutil
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Dynamically import constants
try:
    from scripts.aa_constants import get_aa_core, get_workspace, get_planning_dir, get_state_dir
except ImportError:
    # Fallback if run standalone
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from scripts.aa_constants import get_aa_core, get_workspace, get_planning_dir, get_state_dir

def gather_skill_telemetry() -> dict:
    """Gather context related to skill execution and QA failures."""
    state_dir = get_state_dir()
    planning_dir = get_planning_dir()
    
    skill_data = {
        "qa_reports": [],
        "current_phase_context": None,
        "current_phase_plan": None
    }

    # Collect recent QA reports
    qa_dir = state_dir / "qa_reports"
    if qa_dir.exists():
        reports = list(qa_dir.glob("*.md"))
        reports.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for r in reports[:5]: # Take last 5 reports
            try:
                skill_data["qa_reports"].append({
                    "filename": r.name,
                    "content": r.read_text(encoding="utf-8", errors="ignore")
                })
            except Exception: pass

    # Collect latest phase context
    try:
        current_phase_file = state_dir / "current-phase"
        if current_phase_file.exists():
            phase_num = current_phase_file.read_text(encoding="utf-8").strip()
            phases_dir = planning_dir / "phases"
            if phases_dir.exists():
                for phase_folder in phases_dir.iterdir():
                    if phase_folder.is_dir() and phase_folder.name.startswith(f"{phase_num}-"):
                        ctx_file = phase_folder / "CONTEXT.md"
                        if ctx_file.exists():
                            skill_data["current_phase_context"] = ctx_file.read_text(encoding="utf-8", errors="ignore")
                        plan_file = phase_folder / "PLAN.md"
                        if plan_file.exists():
                            skill_data["current_phase_plan"] = plan_file.read_text(encoding="utf-8", errors="ignore")
                        break
    except Exception as e:
        print(f"[-] Warning: Failed to gather phase context: {e}")

    return skill_data

def gather_agent_telemetry() -> dict:
    """Gather context related to the AutoAgent engine's behavior and system health."""
    state_dir = get_state_dir()
    planning_dir = get_planning_dir()
    aa_core = get_aa_core()
    
    agent_data = {
        "sessions": [],
        "project_status": None,
        "roadmap": None,
        "doctor_report": None
    }

    # Collect recent session history (to analyze agent decision loop)
    sessions_dir = state_dir / "sessions"
    if sessions_dir.exists():
        sessions = list(sessions_dir.glob("*.json"))
        sessions.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        for s in sessions[:3]: # Last 3 sessions
            try:
                with open(s, "r", encoding="utf-8", errors="ignore") as f:
                    agent_data["sessions"].append(json.load(f))
            except Exception: pass

    # Collect project metadata
    project_file = planning_dir / "PROJECT.md"
    if project_file.exists():
        agent_data["project_status"] = project_file.read_text(encoding="utf-8", errors="ignore")

    roadmap_file = planning_dir / "ROADMAP.md"
    if roadmap_file.exists():
        agent_data["roadmap"] = roadmap_file.read_text(encoding="utf-8", errors="ignore")

    # Run system diagnostic (Doctor report)
    doctor_script = aa_core / "scripts" / "doctor.py"
    if doctor_script.exists():
        try:
            print("[*] Running engine diagnostic (doctor)...")
            result = subprocess.run(
                [sys.executable, str(doctor_script), "--json"],
                capture_output=True,
                text=True,
                encoding="utf-8"
            )
            if result.returncode == 0:
                agent_data["doctor_report"] = json.loads(result.stdout)
            else:
                agent_data["doctor_report"] = {"error": "Doctor script failed", "stderr": result.stderr}
        except Exception as e:
            agent_data["doctor_report"] = {"error": f"Failed to run doctor: {e}"}

    return agent_data

def gather_feedback() -> dict:
    """Gather all telemetry from the sandbox workspace."""
    workspace = get_workspace()
    
    print("[*] Gathering skill telemetry...")
    skill_telemetry = gather_skill_telemetry()
    
    print("[*] Gathering agent behavior telemetry...")
    agent_telemetry = gather_agent_telemetry()
    
    feedback_data = {
        "metadata": {
            "timestamp": datetime.now().isoformat(),
            "workspace_name": workspace.name,
            "workspace_path": str(workspace),
            "aa_core_path": str(get_aa_core()),
            "status": "completed"
        },
        "skill_telemetry": skill_telemetry,
        "agent_telemetry": agent_telemetry
    }

    return feedback_data

def submit_feedback(data: dict):
    """Write the feedback data to the core repository."""
    core_feedback_dir = get_aa_core() / "data" / "feedback"
    core_feedback_dir.mkdir(parents=True, exist_ok=True)
    
    # Subdirectories for cleaner analysis
    (core_feedback_dir / "agent").mkdir(exist_ok=True)
    (core_feedback_dir / "skill").mkdir(exist_ok=True)
    
    timestamp = int(time.time())
    ws_name = data["metadata"]["workspace_name"].replace(" ", "_")
    filename = f"telemetry_{ws_name}_{timestamp}.json"
    
    # We save the unified file in the root feedback dir
    dest_path = core_feedback_dir / filename
    
    with open(dest_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    print(f"[+] Sandbox telemetry successfully submitted to AutoAgent Core.")
    print(f"    Saved at: {dest_path}")
    print(f"    (This data will be used to independently analyze both Skill and Agent performance)")

def main():
    parser = argparse.ArgumentParser(description="Submit Workspace Telemetry to AutoAgent Core")
    parser.add_argument("--submit", action="store_true", help="Submit current workspace context")
    args = parser.parse_args()
    
    if args.submit:
        print("[*] Starting feedback loop (Global Sandbox Telemetry)...")
        data = gather_feedback()
        submit_feedback(data)
    else:
        print("Usage: aa feedback --submit")

if __name__ == "__main__":
    main()
