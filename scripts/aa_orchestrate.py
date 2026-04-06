import sys
import os
import argparse
from pathlib import Path

# Add project root to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from src.core.orchestration.coordinator import OrchestrationCoordinator
import subprocess


def update_dashboard(task, status="running", next_goal="None"):
    updater_path = Path(".agents/skills/status-notifier/scripts/status_updater.py")
    if updater_path.exists():
        subprocess.run(
            [
                sys.executable,
                str(updater_path),
                "--task",
                task,
                "--status",
                status,
                "--next",
                next_goal,
            ],
            check=False,
        )


def main():
    parser = argparse.ArgumentParser(
        description="AutoAgent-TW Sub-Agent Orchestrator (v1.9.0)"
    )
    parser.add_argument(
        "prompt", type=str, help="The multi-task requirement to orchestrate."
    )
    parser.add_argument(
        "--parallel", type=int, default=3, help="Max sub-agents to run in parallel."
    )

    args = parser.parse_args()

    print(f"[*] Initializing Orchestration for: {args.prompt}")
    update_dashboard(
        f"Orchestrating: {args.prompt[:30]}...",
        status="running",
        next_goal="Splitting tasks",
    )

    try:
        coordinator = OrchestrationCoordinator(thread_id=f"run-{os.getpid()}")
        coordinator.run(args.prompt)

        print("\n[+] Orchestration Completed.")
        print("-" * 40)
        # Assuming coordinator.run returns something meaningful or we extract from state
        # For now, let's just print success
        update_dashboard(
            f"Completed: {args.prompt[:30]}...", status="idle", next_goal="Done"
        )

    except Exception as e:
        print(f"[-] Orchestration Failed: {e}")
        update_dashboard(
            f"Failed: {args.prompt[:30]}...", status="fail", next_goal="Error Recovery"
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
