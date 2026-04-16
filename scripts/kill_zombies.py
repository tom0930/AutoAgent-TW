import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from core.reaper import AgentReaper

def main():
    print("=== AutoAgent-TW Zombie Slayer v1.0 ===")
    reaper = AgentReaper(dry_run=False)
    count = reaper.reap()
    print(f"Cleaned up {count} zombie processes. System is now leaner.")

if __name__ == "__main__":
    main()
