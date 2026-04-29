import pytest
import asyncio
import subprocess
from scripts.execution.lock_manager import lock_manager
from scripts.execution.executor import isolated_executor, ExecutionTimeoutError
from scripts.execution.schemas import ExecutionNode

@pytest.mark.asyncio
async def test_lock_manager_acquire_release():
    file_path = "test_file.txt"
    task_id = "task_1"
    
    await lock_manager.acquire(file_path, task_id)
    assert (task_id, file_path) in lock_manager._active_writers
    
    await lock_manager.release(file_path, task_id)
    assert (task_id, file_path) not in lock_manager._active_writers

@pytest.mark.asyncio
async def test_lock_manager_conflict():
    assert lock_manager.detect_conflict(["a.txt", "b.txt"], ["b.txt", "c.txt"]) is True
    assert lock_manager.detect_conflict(["a.txt"], ["b.txt"]) is False

@pytest.mark.asyncio
async def test_executor_success_git_add(tmp_path, monkeypatch):
    # Mock subprocess.run to avoid actual git commands
    run_calls = []
    def mock_run(cmd, *args, **kwargs):
        run_calls.append(cmd)
        class MockCompletedProcess:
            returncode = 0
        return MockCompletedProcess()
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    task = ExecutionNode(id="t1", role="dev", files=["mock_file.txt"])
    
    async with isolated_executor(task):
        # simulate some work
        await asyncio.sleep(0.01)
        
    # Check if git add was called
    assert ["git", "add", "mock_file.txt"] in run_calls
    # Check if lock was released
    assert ("t1", "mock_file.txt") not in lock_manager._active_writers

@pytest.mark.asyncio
async def test_executor_timeout_git_reset(monkeypatch):
    run_calls = []
    def mock_run(cmd, *args, **kwargs):
        run_calls.append(cmd)
        class MockCompletedProcess:
            returncode = 0
        return MockCompletedProcess()
        
    monkeypatch.setattr(subprocess, "run", mock_run)
    
    task = ExecutionNode(id="t2", role="dev", files=["mock_file_timeout.txt"])
    
    with pytest.raises(ExecutionTimeoutError):
        async with isolated_executor(task, ttl=1):
            try:
                # The caller enforcing timeout
                async def mock_agent_work():
                    await asyncio.sleep(2)
                await asyncio.wait_for(mock_agent_work(), timeout=0.1)
            except asyncio.TimeoutError:
                # Propagate to context manager to trigger rollback
                raise
                
    # Check if git reset was called
    assert ["git", "reset", "--", "mock_file_timeout.txt"] in run_calls
    # Check if lock was released in finally
    assert ("t2", "mock_file_timeout.txt") not in lock_manager._active_writers
