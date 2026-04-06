import sys
from typing import Dict, Optional
from pathlib import Path

# Constants
PLANNING_DIR = Path(".planning")
PHASES_DIR = PLANNING_DIR / "phases"
STATE_FILE = PLANNING_DIR / "STATE.md"

def get_current_phase() -> Optional[int]:
    """Extracts the latest phase number from STATE.md."""
    if not STATE_FILE.exists():
        return None
    
    try:
        content = STATE_FILE.read_text(encoding="utf-8")
        # Find the last "Phase XXX" in the text
        import re
        matches = re.findall(r"Phase (\d+)", content)
        if matches:
            return int(matches[-1])
    except Exception:
        pass
    return None

def check_audit_status(phase_id: int) -> Dict[str, bool]:
    """Checks if a phase has a CC audit report (QA-REPORT.md)."""
    # Find phase directory
    if not PHASES_DIR.exists():
        return {"exists": False, "audited": False}
    
    # Locate directory starting with padded phase ID (e.g., 117-)
    phase_prefix = f"{phase_id:03d}"
    target_dir = None
    for item in PHASES_DIR.iterdir():
        if item.is_dir() and item.name.startswith(phase_prefix):
            target_dir = item
            break
            
    if not target_dir:
        return {"exists": False, "audited": False}
        
    qa_report = target_dir / "QA-REPORT.md"
    return {"exists": True, "audited": qa_report.exists()}

def main():
    import argparse
    parser = argparse.ArgumentParser(description="CC Manager: Bridge between AA and CC Agents.")
    parser.add_argument("--check-audit", action="store_true", help="Check if current phase is audited by CC.")
    parser.add_argument("--phase", type=int, help="Specify phase ID to check.")
    
    args = parser.parse_args()
    
    phase_id = args.phase or get_current_phase()
    
    if phase_id is None:
        print("⚠️ [CC-Link] Unable to determine current phase state.")
        sys.exit(1)
        
    if args.check_audit:
        status = check_audit_status(phase_id)
        if not status["exists"]:
            print(f"❓ [CC-Link] Phase {phase_id} documentation not found.")
        elif not status["audited"]:
            print(f"🔶 [CC-Link] Warning: Phase {phase_id} implementation found but lacks /cc-qa audit report.")
            print(f"👉 Suggestion: Run '/cc-qa {phase_id}' to verify architectural integrity.")
        else:
            print(f"✅ [CC-Link] Phase {phase_id} has been audited and approved by Code Consultant.")

if __name__ == "__main__":
    main()
