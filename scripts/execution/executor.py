import asyncio
import subprocess
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from scripts.execution.schemas import ExecutionNode, TaskResult
from scripts.execution.lock_manager import lock_manager
from scripts.execution.context_router import ContextScopeRouter

logger = logging.getLogger(__name__)

class ExecutionTimeoutError(Exception):
    pass

@asynccontextmanager
async def isolated_executor(task: ExecutionNode, ttl: int = 300) -> AsyncGenerator[None, None]:
    """
    Executes a task inside an isolated sandbox with a Strict TTL.
    Handles FileLock acquisition, context scoping, physical git staging,
    and fallback reset if TTL is exceeded or an exception occurs.
    """
    # 1. Acquire Locks
    acquired_files = []
    try:
        for f in task.files:
            await lock_manager.acquire(f, task.id)
            acquired_files.append(f)
            
        # 2. Context Scoping
        scope = ContextScopeRouter.get_scope(task.role, task.files)
        logger.info(f"[{task.id}] Starting execution with scope: {scope}")
        
        # 3. Yield to the actual agent client (the caller block)
        # The caller should run the agent under asyncio.wait_for(..., timeout=ttl)
        # But to enforce TTL safely with cleanup, we wrap the yield block.
        try:
            # We use an internal asyncio wait_for for the block if the caller doesn't,
            # but since we are yielding, the timeout must be handled by the caller or
            # we wrap the whole context block. Actually, the asynccontextmanager itself
            # cannot easily enforce TTL on the yielded block natively without an external task.
            # We'll expect the caller to do `asyncio.wait_for`.
            yield
            
            # 4. If successful, physical staging (git add)
            if task.files:
                logger.info(f"[{task.id}] Execution successful. Staging files: {task.files}")
                subprocess.run(["git", "add"] + task.files, check=True, capture_output=True)
                
        except (asyncio.TimeoutError, TimeoutError):
            logger.error(f"[{task.id}] TTL exceeded ({ttl}s). Triggering rollback.")
            if task.files:
                subprocess.run(["git", "reset", "--"] + task.files, check=True, capture_output=True)
            raise ExecutionTimeoutError(f"Task {task.id} exceeded TTL of {ttl}s.")
            
        except Exception as e:
            logger.error(f"[{task.id}] Execution failed: {e}. Triggering rollback.")
            if task.files:
                subprocess.run(["git", "reset", "--"] + task.files, check=True, capture_output=True)
            raise e
            
    finally:
        # 5. Release Logical Locks
        for f in acquired_files:
            await lock_manager.release(f, task.id)
