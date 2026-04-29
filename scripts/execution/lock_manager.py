import asyncio
from typing import Set, Tuple, List
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class FileLockManager:
    """
    Manages logical locks for files to prevent concurrent multi-agent modifications.
    """
    def __init__(self):
        self._locks = defaultdict(asyncio.Lock)
        self._active_writers: Set[Tuple[str, str]] = set() # (task_id, file_path)

    async def acquire(self, file_path: str, task_id: str):
        """
        Acquires an exclusive logical lock for a specific file path.
        """
        lock = self._locks[file_path]
        await lock.acquire()
        self._active_writers.add((task_id, file_path))
        logger.debug(f"[FileLock] Task {task_id} acquired lock on {file_path}")

    async def release(self, file_path: str, task_id: str):
        """
        Releases the logical lock for a specific file path.
        """
        if (task_id, file_path) in self._active_writers:
            lock = self._locks[file_path]
            lock.release()
            self._active_writers.remove((task_id, file_path))
            logger.debug(f"[FileLock] Task {task_id} released lock on {file_path}")
        else:
            logger.warning(f"[FileLock] Task {task_id} tried to release lock on {file_path} but it was not held.")

    def detect_conflict(self, files_a: List[str], files_b: List[str]) -> bool:
        """
        Returns True if two lists of files have an intersection.
        """
        return bool(set(files_a) & set(files_b))

# Global instance for execution orchestration
lock_manager = FileLockManager()
