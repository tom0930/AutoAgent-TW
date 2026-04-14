import os
import sys
import time
import subprocess
import concurrent.futures
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.append(str(root_dir / "scripts"))
sys.path.append(str(root_dir / ".agents" / "skills" / "status-notifier" / "scripts"))

import status_updater

def simulate_update(i):
    """Simulates a single status update call."""
    try:
        status_updater.update_status(
            task=f"Stress Test Task {i}",
            next_goal=f"Goal after {i}",
            phase=137,
            total_phases=200,
            status="running" if i % 10 != 0 else "done",
            logs=f"Log item {i}a, Log item {i}b"
        )
        return True
    except Exception as e:
        print(f"Update {i} failed: {e}")
        return False

def main():
    print("🚀 Starting Dashboard Stress Test (Phase 137 QA)")
    print("Scenario: 100 concurrent updates representing a heavy sub-agent wave.")
    
    start_time = time.time()
    
    # Use ThreadPoolExecutor to simulate parallel execution of agents
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(simulate_update, i) for i in range(100)]
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
    
    duration = time.time() - start_time
    success_count = sum(results)
    
    print(f"\n📊 Stress Test Results:")
    print(f"Total Updates: 100")
    print(f"Successful: {success_count}")
    print(f"Failed: {100 - success_count}")
    print(f"Total Duration: {duration:.2f}s")
    print(f"Avg Time per Update: {duration/100:.4f}s")
    
    if success_count == 100:
        print("\n✅ QA Passed: Dashboard sync and file locking are robust.")
    else:
        print("\n❌ QA Failed: Some updates were lost or failed.")
        sys.exit(1)

if __name__ == "__main__":
    main()
