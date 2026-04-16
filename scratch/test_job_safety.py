import sys
import os
import time
import subprocess
import psutil

# Add project root to path
sys.path.append(os.getcwd())

from src.core.orchestration.spawn_manager import AgentProcess

def test_lifecycle():
    print("[Test] Spawning PyReflyService via SpawnManager...")
    mgr = AgentProcess("Safety-Test")
    
    # Run the service as a sub-process
    service_path = os.path.abspath("src/core/rva/pyrefly_service.py")
    mgr.spawn([sys.executable, service_path])
    
    child_pid = mgr.process.pid
    print(f"[Test] Child PID: {child_pid}")
    
    # Verify it's alive
    if psutil.pid_exists(child_pid):
        print("[Test] Child is ALIVE.")
    else:
        print("[Error] Child failed to start.")
        return

    print("[Test] Main process will now exit. If Job Object works, Child should die.")
    # In a real scenario, the Python interpreter exits, closing all handles.
    # We simulate this by returning and letting the script end.

if __name__ == "__main__":
    test_lifecycle()
    # Script ends here. Handles close.
