import os
import json
import time
from datetime import datetime
from pathlib import Path

# 本地導入
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "utils"))
from state_lock import StateLock

class IdleWatcher:
    """
    AutoAgent-TW Idle Watcher (Phase 129)
    監控使用者閒置時間，並在適當時機觸發自動化任務。
    """
    def __init__(self, idle_threshold_seconds=3600):
        self.state_file = Path(".agent-state/status_state.json")
        self.idle_threshold = idle_threshold_seconds
        self.lock = StateLock()

    def get_last_interaction(self):
        """讀取最後一次與使用者互動的時間"""
        if not self.state_file.exists():
            return None
        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("last_interaction")
        except Exception:
            return None

    def check_idle(self):
        """檢查是否達到閒置閾值"""
        last_time_str = self.get_last_interaction()
        if not last_time_str:
            return False, 0

        last_time = datetime.fromisoformat(last_time_str)
        elapsed = (datetime.now() - last_time).total_seconds()
        
        if elapsed >= self.idle_threshold:
            return True, elapsed
        return False, elapsed

    def run_automated_task(self, phase, task_command):
        """執行自動化任務（帶鎖定檢查）"""
        is_idle, elapsed = self.check_idle()
        if not is_idle:
            print(f"[Watcher] User is active. Idle for {elapsed:.0f}s. Skipping.")
            return False

        # 嘗試加鎖
        success, info = self.lock.acquire(phase=phase, task_name=f"Idle-Auto-{phase}")
        if not success:
            print(f"[Watcher] Workspace locked by {info.get('pid')}. Skipping.")
            return False

        try:
            print(f"[Watcher] Idle detected ({elapsed:.0f}s). Starting task: {task_command}")
            # 這裡可以使用 subprocess.run 執行指令
            # os.system(f"python {task_command} --auto --headless")
            return True
        finally:
            self.lock.release()

if __name__ == "__main__":
    # 範例執行：每小時檢查一次
    watcher = IdleWatcher(idle_threshold_seconds=10) # 測試用 10 秒
    status, elapsed = watcher.check_idle()
    print(f"Idle status: {status}, Elapsed: {elapsed:.2f}s")
