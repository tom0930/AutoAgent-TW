import os
import json
import logging
from pathlib import Path

class BufferManager:
    """
    Buffer-based Execution Engine (Phase 132)
    Manages task queues using JSONL to handle large-scale operations without UI spinning.
    """
    def __init__(self, task_name: str):
        self.base_dir = Path(".agents/running_temp")
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_path = self.base_dir / f"{task_name}_manifest.jsonl"
        self.logger = logging.getLogger("BufferManager")

    def initialize(self, tasks: list):
        """
        Initialize the task queue.
        Each task should be a dict: {"id": "unique_id", "payload": ...}
        """
        if self.manifest_path.exists():
             self.logger.warning(f"Manifest {self.manifest_path} already exists. Resuming instead of initializing.")
             return

        with open(self.manifest_path, "w", encoding="utf8") as f:
            for task in tasks:
                entry = {
                    "task_id": task.get("id"),
                    "payload": task.get("payload"),
                    "status": "pending",
                    "result": None
                }
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        self.logger.info(f"Initialized buffer with {len(tasks)} tasks.")

    def get_progress(self):
        """Returns a set of completed task IDs and the full task map."""
        completed = set()
        all_tasks = []
        
        if not self.manifest_path.exists():
            return completed, all_tasks

        with open(self.manifest_path, "r", encoding="utf8") as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    all_tasks.append(data)
                    if data.get("status") == "done":
                        completed.add(data.get("task_id"))
                except json.JSONDecodeError:
                    continue
        return completed, all_tasks

    def get_next_chunk(self, chunk_size: int = 5):
        """Fetches the next batch of pending tasks."""
        completed, all_tasks = self.get_progress()
        pending = [t for t in all_tasks if t["task_id"] not in completed]
        return pending[:chunk_size]

    def mark_done(self, task_id: str, result: any = "ok"):
        """Appends a completion record to the JSONL."""
        # Note: In a true JSONL log, we append the latest state. 
        # When reading, the last occurrence of a task_id represents its latest state.
        entry = {
            "task_id": task_id,
            "status": "done",
            "result": result,
            "timestamp": "auto" # Could add real ISO time
        }
        with open(self.manifest_path, "a", encoding="utf8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def is_complete(self):
        """Checks if all unique tasks from the initial set are marked done."""
        completed, all_tasks = self.get_progress()
        # Find unique task IDs from the initial file (those with a 'payload' were likely original)
        unique_ids = {t["task_id"] for t in all_tasks if "payload" in t}
        return unique_ids.issubset(completed)

    def cleanup(self):
        """Deletes the manifest file after successful completion."""
        if self.manifest_path.exists():
            self.manifest_path.unlink()
