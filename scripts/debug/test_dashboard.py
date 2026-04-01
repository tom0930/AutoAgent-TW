import subprocess
import os
import sys

# [v1.7.2] Dashboard Ultimate Test Pattern Script
# Safe ASCII Output for Windows CP950

MERMAID_PATTERN = """graph TD
  classDef done fill:#238636,color:white,stroke:none
  classDef running fill:#4ade80,color:black,stroke-width:3px,stroke:#fff
  classDef pending fill:#21262d,color:#8b949e,stroke:#30363d
  
  Start[Start Dashboard Test]:::done --> CheckInlining[HTML Data Inlining]:::done
  CheckInlining --> CheckMermaid[Mermaid Rendering]:::running
  CheckMermaid -->|Render OK| CheckPhases[Phase Persistence]:::pending
  CheckPhases -->|Passed| Victory[v1.7.2 Fix Success]:::pending
"""

def run_test():
    print("[Dashboard Test] Starting...")
    
    # Task title: using safe characters to avoid Windows encoding issues in subprocess
    task_title = "[Test Mode] Verifying v1.7.2 Dashboard Resilience..."
    
    cmd = [
        "python", ".agents/skills/status-notifier/scripts/status_updater.py",
        "--task", task_title,
        "--next", "Phase 115",
        "--status", "running",
        "--phase", "114",
        "--total", "115",
        "--mermaid", MERMAID_PATTERN,
        "--logs", "Initializing test pattern...|Checking CORS bypass...|Verifying HTML inlining...|Rendering Mermaid flow...|Success!"
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("\n[SUCCESS] Test data successfully injected!")
        print("URL: http://localhost:9999/.agents/skills/status-notifier/templates/status.html")
    except Exception as e:
        print(f"\n[ERROR] Failed to run test provider: {e}")

if __name__ == "__main__":
    run_test()
