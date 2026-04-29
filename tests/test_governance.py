import os
import time
import json
import pytest
import subprocess
import win32job
import win32api
import win32con
from pathlib import Path
from src.core.orchestration.spawn_manager import AgentProcess

def test_resource_limits_memory():
    """驗證 Job Object 記憶體限制"""
    if os.name != 'nt':
        pytest.skip("Windows only test")
    
    payload = """
import time
import os
import sys
print(f"Sub-agent PID: {os.getpid()}")
try:
    print("Attempting to allocate 1.5GB...")
    size = 1500 * 1024 * 1024
    data = bytearray(size)
    print("Touching pages...")
    for i in range(0, size, 4096):
        data[i] = 1
    print("SUCCESS: Allocation and touch worked (BAD!)")
except MemoryError:
    print("MemoryError caught (GOOD!)")
    sys.exit(1)
except Exception as e:
    print(f"Caught other exception: {e}")
    sys.exit(2)
time.sleep(1)
"""
    test_script = Path("tests/memory_hog.py")
    test_script.write_text(payload)
    
    agent = AgentProcess("Memory Test", role="architect")
    
    # 使用 Pipe 捕獲
    agent.spawn(["python", str(test_script)], env_overrides={
        "_capture_stdout": subprocess.PIPE,
        "_capture_stderr": subprocess.PIPE
    })
    
    pid = agent.process.pid
    print(f"Spawned agent with PID: {pid}")
    
    stdout, stderr = agent.process.communicate(timeout=20)
    print("--- Sub-agent STDOUT ---")
    print(stdout)
    print("--- Sub-agent STDERR ---")
    print(stderr)
    print(f"Agent Process Return Code: {agent.process.returncode}")
    
    assert agent.process.returncode != 0

def test_ttl_expiry():
    """驗證 TTL 超時自動終止"""
    payload = "import time; time.sleep(60)"
    test_script = Path("tests/long_running.py")
    test_script.write_text(payload)
    
    agent = AgentProcess("TTL Test", role="architect")
    agent.spawn(["python", str(test_script)], env_overrides={"AA_AGENT_TTL": "2"})
    
    print(f"Spawned TTL agent with PID: {agent.process.pid}")
    time.sleep(4)
    
    assert agent.process.poll() is not None
    assert agent.status == "terminated"
    print("TTL Test: PASSED")

if __name__ == "__main__":
    try:
        test_ttl_expiry()
        test_resource_limits_memory()
        print("ALL TESTS PASSED")
    except Exception as e:
        print(f"Test FAILED: {e}")
        os._exit(1)
