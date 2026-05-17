import os
import sys
import argparse
import subprocess
from pathlib import Path

# Add project root to path for imports
AA_CORE = Path(os.getenv("AA_CORE", Path(__file__).resolve().parent.parent))
sys.path.append(str(AA_CORE))

from scripts.aa_constants import get_aa_core, get_workspace

def run_l3(args):
    """Run the L3 skill cache."""
    script_path = get_aa_core() / "scripts" / "l3_skill_cache.py"
    if not script_path.exists():
        print(f"[-] Error: {script_path} not found.")
        sys.exit(1)
        
    cmd = [sys.executable, str(script_path)] + args.l3_args
    subprocess.run(cmd, cwd=str(get_workspace()))

def run_feedback(args):
    """Run the telemetry/feedback tool."""
    script_path = get_aa_core() / "scripts" / "aa_feedback.py"
    if not script_path.exists():
        print(f"[-] Error: {script_path} not found.")
        sys.exit(1)
        
    cmd = [sys.executable, str(script_path), "--submit"]
    subprocess.run(cmd, cwd=str(get_workspace()))

def run_doctor(args):
    """Run the diagnostic doctor tool."""
    script_path = get_aa_core() / "scripts" / "doctor.py"
    if not script_path.exists():
        print(f"[-] Error: {script_path} not found.")
        sys.exit(1)
        
    cmd = [sys.executable, str(script_path)]
    subprocess.run(cmd, cwd=str(get_workspace()))

def run_clear_session(args, unknown_args):
    """Run the dynamic context reset tool."""
    script_path = get_aa_core() / "scripts" / "aa_clear_session.py"
    if not script_path.exists():
        print(f"[-] Error: {script_path} not found.")
        sys.exit(1)
        
    cmd = [sys.executable, str(script_path)] + unknown_args
    subprocess.run(cmd, cwd=str(get_workspace()))

def main():
    parser = argparse.ArgumentParser(
        description="AutoAgent-TW Global CLI Router",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(title="Commands", dest="command")
    
    # aa l3 ...
    parser_l3 = subparsers.add_parser("l3", help="Manage and search L3 Skill Cache")
    
    # aa feedback
    parser_fb = subparsers.add_parser("feedback", help="Submit workspace bugs/fixes back to AutoAgent core")
    
    # aa doctor
    parser_doc = subparsers.add_parser("doctor", help="Run system diagnostics")
    
    # aa clear-session
    parser_clear = subparsers.add_parser("clear-session", help="Prune historical session messages and recover token budget")
    
    args, unknown = parser.parse_known_args()
    
    if args.command == "l3":
        args.l3_args = unknown
        run_l3(args)
    elif args.command == "feedback":
        run_feedback(args)
    elif args.command == "doctor":
        run_doctor(args)
    elif args.command == "clear-session":
        run_clear_session(args, unknown)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
