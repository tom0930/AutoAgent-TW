import os
import json
import time
from pathlib import Path

class StateLock:
    """
    AutoAgent-TW State Locking Mechanism (Phase 129)
    Prevents race conditions between CI Runner and Manual execution.
    """
    def __init__(self, lock_dir=".agent-state"):
        self.lock_dir = Path(lock_dir)
        self.lock_path = self.lock_dir / "lock.json"

    def acquire(self, phase, task_name="unknown"):
        """嘗試獲取鎖定 (獲取權限)"""
        if not self.lock_dir.exists():
            self.lock_dir.mkdir(parents=True, exist_ok=True)

        if self.lock_path.exists():
            with open(self.lock_path, "r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                    pid = data.get("pid")
                    # 檢查 PID 是否還存在 (簡單檢測 Stale Lock)
                    if self._is_pid_running(pid):
                        return False, data
                except (json.JSONDecodeError, KeyError):
                    pass

        # 寫入鎖定資訊
        lock_data = {
            "pid": os.getpid(),
            "phase": phase,
            "task": task_name,
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(self.lock_path, "w", encoding="utf-8") as f:
            json.dump(lock_data, f, indent=2)
        return True, lock_data

    def release(self):
        """釋放鎖定"""
        if self.lock_path.exists():
            self.lock_path.unlink()

    def _is_pid_running(self, pid):
        """檢查 PID 是否正在運作 (Windows/Linux 通用簡易版)"""
        if pid is None: return False
        try:
            # 在 Windows，若 PID 不存在會拋出存取錯誤或例外
            import psutil
            return psutil.pid_exists(pid)
        except ImportError:
            # 回退策略：若無 psutil 則假設鎖有效（保守策略）
            return True

if __name__ == "__main__":
    # 測試腳本
    lock = StateLock()
    success, info = lock.acquire(phase=129, task_name="Test-Locking")
    if success:
        print(f"[OK] Lock acquired: {info}")
        time.sleep(2)
        lock.release()
        print("[OK] Lock released.")
    else:
        print(f"[FAILED] Workspace in use by: {info}")
