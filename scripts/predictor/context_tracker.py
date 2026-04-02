import json
import os
import portalocker
from pathlib import Path
from datetime import datetime

class ContextTracker:
    """
    持續追蹤開發者的操作序列，維護即時開發上下文
    """
    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.state_dir = self.project_root / ".agent-state"
        self.snapshot_file = self.state_dir / "context_snapshot.json"
        self.state_dir.mkdir(parents=True, exist_ok=True)
        self._ensure_snapshot_file()

    def _ensure_snapshot_file(self):
        if not self.snapshot_file.exists():
            default_context = {
                "last_action": "init",
                "files_changed": [],
                "git_status": "clean",
                "test_status": "unknown",
                "active_task": "None"
            }
            self._write_snapshot(default_context)

    def _read_snapshot(self) -> dict:
        try:
            with portalocker.Lock(self.snapshot_file, 'r', timeout=2, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"[ContextTracker] Read error: {e}")
            return {}

    def _write_snapshot(self, data: dict):
        try:
            with portalocker.Lock(self.snapshot_file, 'w', timeout=2, encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[ContextTracker] Write error: {e}")

    def track_file_change(self, file_path: str, change_type: str = "modified"):
        """記錄檔案變更"""
        ctx = self._read_snapshot()
        if ctx:
            ctx["last_action"] = "file_change"
            ctx["last_updated"] = datetime.now().isoformat()
            if "files_changed" not in ctx:
                ctx["files_changed"] = []
            if file_path not in ctx["files_changed"]:
                ctx["files_changed"].append({
                    "path": file_path,
                    "type": change_type,
                    "timestamp": datetime.now().isoformat()
                })
            # Limit history
            if len(ctx["files_changed"]) > 10:
                ctx["files_changed"] = ctx["files_changed"][-10:]
            self._write_snapshot(ctx)

    def track_command(self, command: str, result: str):
        """記錄指令執行結果"""
        ctx = self._read_snapshot()
        if ctx:
            ctx["last_action"] = "command_execution"
            ctx["last_command"] = {
                "command": command,
                "result": result,
                "timestamp": datetime.now().isoformat()
            }
            ctx["last_updated"] = datetime.now().isoformat()
            self._write_snapshot(ctx)

    def track_git_event(self, event_type: str, details: dict):
        """記錄 Git 事件"""
        ctx = self._read_snapshot()
        if ctx:
            ctx["git_status"] = event_type
            ctx["git_details"] = details
            ctx["last_updated"] = datetime.now().isoformat()
            self._write_snapshot(ctx)

    def get_current_context(self) -> dict:
        """取得當前開發上下文快照"""
        return self._read_snapshot()
