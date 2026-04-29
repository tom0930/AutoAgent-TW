import os
import time
import json
from src.core.orchestration.spawn_manager import AgentProcess
from src.core.orchestration.monitor import start_monitor, stop_monitor

def test_monitoring():
    print("Testing Resource Monitoring...")
    start_monitor()
    
    # Spawn a process that stays alive for a bit
    payload = "import time; time.sleep(10)"
    test_script = "tests/monitor_test.py"
    with open(test_script, "w") as f: f.write(payload)
    
    agent = AgentProcess("Monitor Test")
    agent.spawn(["python", test_script])
    
    print(f"Waiting for monitor to catch PID {agent.process.pid}...")
    time.sleep(7) # Wait for > 5s interval
    
    stop_monitor()
    
    with open(agent.state_file, "r", encoding="utf-8") as f:
        data = json.load(f)
        if "current_metrics" in data:
            print(f"Monitor caught metrics: {data['current_metrics']}")
            return True
        else:
            print("Monitor did NOT catch metrics.")
            return False

if __name__ == "__main__":
    if test_monitoring():
        print("Monitoring Test: PASSED")
    else:
        print("Monitoring Test: FAILED")
        os._exit(1)
