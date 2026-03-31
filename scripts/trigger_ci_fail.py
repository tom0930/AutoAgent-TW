import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
EVENT_HANDLER = PROJECT_ROOT / "scripts" / "event_handler.py"

def trigger_ci():
    print("Simulating CI Failure...")
    subprocess.run([sys.executable, str(EVENT_HANDLER), "ci.failure"])

if __name__ == "__main__":
    trigger_ci()
