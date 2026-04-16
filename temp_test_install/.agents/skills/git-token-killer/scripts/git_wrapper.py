#!/usr/bin/env python3
import sys
import subprocess
import os

def main():
    if len(sys.argv) < 2:
        print("Usage: git_wrapper.py <git args...>")
        sys.exit(1)
  
    phase = os.getenv("AUTOAGENT_PHASE", "Builder")
    # Mapping based on rtk v0.36.0: Default is compact. --ultra-compact is also available.
    # --verbose is for more detail.
    strategy = {
        "Builder": "",
        "Research": "--ultra-compact",
        "QA": "",
        "Guardian": "--verbose"
    }.get(phase, "")
  
    # Find rtk binary
    rtk_bin = "rtk"
    if os.name == "nt":
        rtk_bin = r"z:\autoagent-TW\bin\rtk.exe"

    # Construction of command: rtk [strategy] git [args...]
    cmd = [rtk_bin]
    if "--raw" not in " ".join(sys.argv):
        if strategy:
            cmd.append(strategy)
    
    cmd.append("git")
    cmd.extend(sys.argv[1:])
  
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
        print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
    except Exception as e:
        print(f"Error executing git wrapper: {e}", file=sys.stderr)
        # Fallback to normal git if rtk fails
        subprocess.run(["git"] + sys.argv[1:])

if __name__ == "__main__":
    main()
