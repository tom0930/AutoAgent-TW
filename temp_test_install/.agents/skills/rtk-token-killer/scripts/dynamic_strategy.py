#!/usr/bin/env python3
import os
import sys
from pathlib import Path

def get_strategy(phase: str) -> str:
    """
    Returns the RTK flag based on the current agent phase.
    """
    strategies = {
        "Builder": "--compact",
        "QA": "--summary",
        "Guardian": "--verbose",
        "Research": "--compact"
    }
    return strategies.get(phase, "--compact")

def main():
    # Detect phase from environment or default to Builder
    phase = os.getenv("AUTOAGENT_PHASE", "Builder")
    
    # Optional: Look into .planning/STATE.md to verify if env is missing
    if not os.getenv("AUTOAGENT_PHASE"):
        try:
            state_file = Path(".planning/STATE.md")
            if state_file.exists():
                content = state_file.read_text(encoding="utf-8")
                if "Phase: QA" in content:
                    phase = "QA"
                elif "Phase: Guardian" in content:
                    phase = "Guardian"
        except Exception:
            pass
            
    print(get_strategy(phase))

if __name__ == "__main__":
    main()
