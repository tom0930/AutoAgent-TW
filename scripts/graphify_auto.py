import os
import sys
from pathlib import Path

# Import AA constants
sys.path.append(os.path.dirname(__file__))
from graphify_orchestrator import GraphifyOrchestrator

def main():
    """Triggered by Git Hooks or aa-resume."""
    orch = GraphifyOrchestrator()
    # Background update with smart mode
    orch.run(mode="smart", background=True)

if __name__ == "__main__":
    main()
