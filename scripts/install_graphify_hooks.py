import os
import sys
from pathlib import Path

def install_hook():
    git_dir = Path(".git")
    if not git_dir.exists():
        print("Error: .git directory not found. Are you in the repo root?")
        return
    
    hooks_dir = git_dir / "hooks"
    hooks_dir.mkdir(exist_ok=True)
    
    hook_path = hooks_dir / "post-merge"
    
    # We use a simple python call to graphify_auto.py
    # Since we are on Windows, we'll use a shell script format that works in Git Bash
    hook_content = f"""#!/bin/sh
echo "Git Pull detected. Triggering Graphify Auto-Update..."
python "{Path(__file__).parent / 'graphify_auto.py'}" &
"""
    
    with open(hook_path, "w", encoding="utf-8") as f:
        f.write(hook_content)
    
    # On Windows, permissions are tricky but Git Bash usually respects the script if it starts with #!/bin/sh
    print(f"[+] Installed Git post-merge hook to {hook_path}")

if __name__ == "__main__":
    install_hook()
