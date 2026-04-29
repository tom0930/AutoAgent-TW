# tests/test_phase167_uat.py
import asyncio
import sys
import os
from unittest.mock import MagicMock

# Add scripts/planning to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../scripts/planning")))

from engine import ParallelPlanner
from orchestrator import MapReflectReduceOrchestrator
from security import filter_read_only_tools

async def test_concurrency():
    print("Testing 3 concurrent agents...")
    planner = ParallelPlanner(context={}, resource_monitor=None)
    agents = [
        {"id": "arch", "role": "Architect"},
        {"id": "sec", "role": "Security"},
        {"id": "ux", "role": "UX"}
    ]
    start_time = asyncio.get_event_loop().time()
    valid_plans, failed = await planner.run(agents)
    end_time = asyncio.get_event_loop().time()
    
    print(f"Time taken: {end_time - start_time:.2f}s")
    assert len(valid_plans) == 3
    assert len(failed) == 0
    # _mock_api_call takes 2s. If parallel, it should take ~2s, not 6s.
    assert (end_time - start_time) < 3.0
    print("✓ Concurrency test passed.")

async def test_conflict_detection():
    print("Testing conflict detection...")
    planner = ParallelPlanner(context={}, resource_monitor=None)
    orch = MapReflectReduceOrchestrator(context={}, planner=planner)
    
    # Mock plans with a conflict
    from schemas import AgentPlan
    plans = [
        AgentPlan(role="Architect", confidence=0.9, plan_section="Use Rust", conflicts_with=["Python"]),
        AgentPlan(role="Security", confidence=0.9, plan_section="Use Python", conflicts_with=["Rust"])
    ]
    
    conflicts = await orch._extract_conflicts(plans)
    assert conflicts.has_conflict is True
    assert "Rust" in conflicts.conflict_dimensions or "Python" in conflicts.conflict_dimensions
    
    matrix = await orch.synthesize(plans, conflicts)
    assert len(matrix.options) >= 2
    print("✓ Conflict detection test passed.")

def test_security_filter():
    print("Testing tool security filter...")
    tools = [
        {"name": "read_url_content"},
        {"name": "write_to_file"},
        {"name": "run_command"},
        {"name": "list_dir"}
    ]
    safe_tools = filter_read_only_tools(tools)
    safe_names = [t["name"] for t in safe_tools]
    
    assert "read_url_content" in safe_names
    assert "list_dir" in safe_names
    assert "write_to_file" not in safe_names
    assert "run_command" not in safe_names
    print("✓ Security filter test passed.")

async def main():
    try:
        await test_concurrency()
        await test_conflict_detection()
        test_security_filter()
        print("\nALL UAT TESTS PASSED.")
    except Exception as e:
        print(f"\nUAT TEST FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
