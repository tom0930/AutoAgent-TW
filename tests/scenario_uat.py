import os
import sys
# Set PYTHONPATH
sys.path.append(os.getcwd())

# pyrefly: ignore [missing-import]
from src.core.graph import compile_ira_graph

def run_test_scenario(tool_name: str, expected_pending: bool):
    print(f"\n>>> Running Scenario: {tool_name} (Expected Pending: {expected_pending})")
    app = compile_ira_graph("temp/scenario_test.sqlite")
    
    test_state = {
        "messages": [],
        "task_input": f"Testing {tool_name}",
        "last_action": {"name": tool_name, "args": {}},
        "failure_count": 0,
        "last_errors": [],
        "current_version": "v1.0",
        "risk_level": 1,
        "pending_approval": False,
        "approval_result": None,
        "thread_id": f"thread-{tool_name}",
        "review_reports": [],
        "success_rate": 0.0
    }
    
    config = {"configurable": {"thread_id": f"thread-{tool_name}"}}
    
    # Execute
    for event in app.stream(test_state, config=config):
        print(f"Update: {event}")
    
    # Verify result
    snapshot = app.get_state(config)
    is_pending = snapshot.values.get("pending_approval")
    
    if is_pending == expected_pending:
        print(f"PASSED: {tool_name} behaved correctly.")
    else:
        print(f"FAILED: {tool_name} pending={is_pending}, expected={expected_pending}")

if __name__ == "__main__":
    # Task 4.1: Level 5 - Should block
    run_test_scenario("delete_database", expected_pending=True)
    
    # Task 4.2: Level 1 - Should pass
    run_test_scenario("get_time", expected_pending=False)
